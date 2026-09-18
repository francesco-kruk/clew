"""Transactional immutable snapshots; never read learner state."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

from .source import Source
from .storage import CourseError, atomic_json, plain_path, protect_private_paths, read_json
from .validation import require_valid, safe_relative


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inventory(directory: Path) -> dict[str, str]:
    result = {}
    folded = set()
    for parent, dirs, files in os.walk(directory, followlinks=False):
        for name in dirs + files:
            path = plain_path(Path(parent) / name)
            relative = safe_relative(path.relative_to(directory).as_posix())
            if relative.casefold() in folded:
                raise CourseError(f"Case-insensitive installed path collision: {relative}")
            folded.add(relative.casefold())
            if not path.is_dir() and not path.is_file():
                raise CourseError(f"Not a regular installed file: {path}")
        for name in files:
            path = Path(parent) / name
            result[path.relative_to(directory).as_posix()] = digest(path)
    return result


def receipt_valid(receipt: dict, course_id: str, course_root: str) -> None:
    if (
        receipt.get("version") != 1 or receipt.get("id") != course_id
        or receipt.get("course_root") != course_root
        or not isinstance(receipt.get("commit"), str)
        or not re.fullmatch(r"[0-9a-f]{40,64}", receipt["commit"])
        or not isinstance(receipt.get("files"), dict)
        or not receipt["files"] or "course-package.json" not in receipt["files"]
    ):
        raise CourseError("Invalid import receipt; refusing to treat this course as managed.")
    for path, sha in receipt["files"].items():
        safe_relative(path)
        if not isinstance(sha, str) or not re.fullmatch("[0-9a-f]{64}", sha):
            raise CourseError("Invalid file hash in import receipt.")


def intact(path: Path, receipt: dict) -> bool:
    return path.is_dir() and inventory(path) == receipt["files"]


@contextmanager
def import_lock(control: Path):
    lock = plain_path(control / "import.lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise CourseError(
            f"Another import or an interrupted process owns {lock}. "
            "After confirming no import is running, remove only this lock and retry; "
            "pending receipts are recovered automatically."
        ) from exc
    try:
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        lock.unlink()


def catalog(source: Source, directory: Path, validator) -> dict:
    path = directory / "catalog.json"
    try:
        path.write_bytes(source.blob("catalog.json"))
    except CourseError as exc:
        raise CourseError(
            f"Catalog unavailable at {source.identity}@{source.commit}. "
            "The teacher must publish catalog.json after validation and rights confirmation, "
            "or select a committed local --source-checkout. " + str(exc)
        ) from exc
    require_valid(validator.validate_catalog(path, packages=False), "Catalog")
    return read_json(path)


def import_course(source: Source, course_id: str, vault: Path, validator) -> dict:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", course_id):
        raise CourseError("Course ID must use lowercase letters, digits, and single hyphens.")
    vault = plain_path(vault)
    vault.mkdir(parents=True, exist_ok=True)
    protect_private_paths(vault)
    control = plain_path(vault / ".clew")
    control.mkdir(exist_ok=True)
    with import_lock(control), tempfile.TemporaryDirectory(prefix="clew-validate-") as scratch:
        source_root = Path(scratch)
        entries = catalog(source, source_root, validator)["courses"]
        entry = next((item for item in entries if item["id"] == course_id), None)
        if entry is None:
            raise CourseError(f"Course {course_id!r} is not in the selected catalog.")
        prefix = safe_relative(entry["path"])
        if len(prefix.split("/")) != 2 or not prefix.startswith("courses/"):
            raise CourseError("A published course must have a courses/<course> prefix.")
        source.export(prefix, source_root, safe_relative)
        package = source_root / prefix
        require_valid(validator.validate_package(package, mode="publish"), "Course package")
        manifest = read_json(package / "course-package.json")
        if (manifest["id"], manifest["course"], manifest["course_root"]) != (
            course_id, entry["title"], prefix
        ):
            raise CourseError("Catalog and package metadata disagree.")
        receipt = {
            "version": 1, "id": course_id, "course_root": prefix,
            "source": source.identity, "ref": source.ref, "commit": source.commit,
            "files": inventory(package),
        }
        destination = plain_path(vault / prefix)
        receipts = plain_path(control / "imports")
        receipts.mkdir(exist_ok=True)
        saved = plain_path(receipts / f"{course_id}.json")
        pending = plain_path(receipts / f"{course_id}.pending.json")
        if pending.exists():
            interrupted = read_json(pending)
            receipt_valid(interrupted, course_id, prefix)
            if destination.exists():
                if not intact(destination, interrupted):
                    raise CourseError("Interrupted install conflicts with existing files or receipt; preserve them for manual review.")
                if saved.exists():
                    if read_json(saved) != interrupted:
                        raise CourseError("Interrupted receipt conflicts with the installed receipt; preserve both for manual review.")
                else:
                    atomic_json(saved, interrupted)
            pending.unlink()
        if destination.exists():
            if not saved.exists():
                raise CourseError(f"Unrecognized existing course: {destination}; no files were replaced.")
            previous = read_json(saved)
            receipt_valid(previous, course_id, prefix)
            if not intact(destination, previous):
                raise CourseError(f"Locally modified course: {destination}; preserve your changes before comparing revisions.")
            if previous["files"] == receipt["files"] and previous["commit"] == receipt["commit"]:
                return {"status": "unchanged", "path": str(destination), "commit": source.commit}
            return stage_revision(control, package, receipt)
        if saved.exists():
            raise CourseError("Import receipt exists but the installed course is missing; manual reconciliation is required.")
        courses = plain_path(vault / "courses")
        courses.mkdir(exist_ok=True)
        for child in courses.iterdir():
            if child.name.casefold() == destination.name.casefold():
                raise CourseError(f"Destination case collision: {child}")
        # Copy on the destination volume, then publish the whole directory in one rename.
        with tempfile.TemporaryDirectory(prefix="install-", dir=control) as temporary:
            prepared = Path(temporary) / "course"
            shutil.copytree(package, prepared)
            if inventory(prepared) != receipt["files"]:
                raise CourseError("Prepared snapshot changed before installation.")
            atomic_json(pending, receipt)
            os.rename(prepared, destination)
            atomic_json(saved, receipt)
            pending.unlink()
        return {"status": "installed", "path": str(destination), "commit": source.commit}


def stage_revision(control: Path, package: Path, receipt: dict) -> dict:
    root = plain_path(control / "staging" / receipt["id"])
    root.mkdir(parents=True, exist_ok=True)
    revision = receipt["commit"] + "-" + receipt["files"]["course-package.json"][:16]
    destination = plain_path(root / revision)
    if destination.exists():
        staged_receipt = read_json(destination / "receipt.json")
        if staged_receipt != receipt or not intact(destination / receipt["course_root"], receipt):
            raise CourseError(f"Existing staged revision was modified: {destination}")
    else:
        with tempfile.TemporaryDirectory(prefix="stage-", dir=control) as temporary:
            prepared = Path(temporary) / "candidate"
            prepared.mkdir()
            candidate = prepared / receipt["course_root"]
            shutil.copytree(package, candidate)
            atomic_json(prepared / "receipt.json", receipt)
            if not intact(candidate, receipt):
                raise CourseError("Prepared staged snapshot changed before publication.")
            os.rename(prepared, destination)
    return {"status": "staged", "path": str(destination / receipt["course_root"]), "commit": receipt["commit"],
            "message": "Compare this candidate with the installed course. It has NOT been activated."}
