"""Filesystem boundaries and explicit external-vault configuration."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / ".clew.local.json"
PRIVATE = ("model", "artifacts", ".clew")


class CourseError(Exception):
    """An actionable configuration or import failure."""


def plain_path(path: Path) -> Path:
    """Check existing ancestors without following symlinks or Windows junctions."""
    path = Path(os.path.abspath(path))
    for ancestor in reversed((path, *path.parents)):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise CourseError(f"Symlink/reparse path is not allowed: {ancestor}")
    return path


def read_json(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise CourseError(f"Duplicate JSON key {key!r} in {path}")
            result[key] = value
        return result

    plain_path(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    except (OSError, ValueError) as exc:
        raise CourseError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CourseError(f"Expected a JSON object: {path}")
    return value


def atomic_json(path: Path, value: dict) -> None:
    plain_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".clew-write-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def vault_path(explicit: str | Path | None = None) -> Path:
    if explicit is None:
        if not CONFIG.exists():
            raise CourseError("Configure an external vault first: python -m src.courses.cli configure --vault PATH")
        configuration = read_json(CONFIG)
        explicit = configuration.get("vault")
        if configuration.get("version") != 1 or not isinstance(explicit, str):
            raise CourseError(f"Invalid configuration: {CONFIG}; run configure --vault PATH")
    path = Path(explicit).expanduser()
    if not path.is_absolute():
        raise CourseError("The vault must be an explicit absolute path.")
    path = plain_path(path)
    root = ROOT.resolve()
    if path == root or root in path.parents or path in root.parents:
        raise CourseError("The vault must be outside this clone and cannot contain it.")
    if path.exists() and not path.is_dir():
        raise CourseError(f"Vault is not a directory: {path}")
    return path


def protect_private_paths(vault: Path) -> None:
    """Inspect Git's index only, never learner files or their content."""
    command = ["git", "-C", str(vault), "rev-parse", "--show-toplevel"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
    if result.returncode:
        if "not a git repository" in result.stderr.lower():
            return
        raise CourseError(f"Cannot determine vault Git status: {result.stderr.strip()}")
    git_root = Path(result.stdout.strip()).resolve()
    relative = vault.relative_to(git_root).as_posix()
    prefix = "" if relative == "." else relative + "/"
    paths = [":(icase,literal)" + prefix + name for name in PRIVATE]
    tracked = subprocess.run(
        ["git", "-C", str(git_root), "ls-files", "-z", "--", *paths],
        capture_output=True, check=False,
    )
    if tracked.returncode:
        raise CourseError("Cannot inspect the vault Git index; private-data protection was not applied.")
    if tracked.stdout:
        raise CourseError(
            "Private vault paths are already tracked by Git. Stop tracking model/, artifacts/, "
            "and .clew/ explicitly and review repository history before continuing. "
            "Ignore rules do not untrack data, erase history, or encrypt files."
        )
    ignore = plain_path(vault / ".gitignore")
    existing = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    rules = [f"/{name}/" for name in PRIVATE]
    missing = [rule for rule in rules if rule not in existing.splitlines()]
    if missing:
        with ignore.open("a", encoding="utf-8", newline="\n") as stream:
            if existing and not existing.endswith("\n"):
                stream.write("\n")
            stream.write("# Clew private local state (not encryption)\n" + "\n".join(missing) + "\n")


def configure(explicit: str | Path) -> Path:
    vault = vault_path(explicit)
    vault.mkdir(parents=True, exist_ok=True)
    protect_private_paths(vault)
    atomic_json(CONFIG, {"version": 1, "vault": str(vault)})
    return vault
