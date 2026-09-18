"""Read Git objects from exactly one resolved commit, without checking out code."""

from __future__ import annotations

import re
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

from .storage import CourseError, plain_path

DEFAULT_SOURCE = "francesco-kruk/clew-content"
MAX_BLOB = 256 * 1024 * 1024
MAX_PACKAGE = 1024 * 1024 * 1024


def git(directory: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-c", "core.hooksPath=", "-c", "protocol.ext.allow=never",
             "-C", str(directory), *arguments],
            capture_output=True, check=False,
        )
    except OSError as exc:
        raise CourseError(f"Git is required for course sources: {exc}") from exc
    if result.returncode:
        raise CourseError(f"Course source Git operation failed: {result.stderr.decode('utf-8', errors='replace').strip()}")
    return result.stdout


class Source:
    def __init__(self, directory: Path, commit: str, identity: str, ref: str):
        self.directory = directory
        self.commit = commit
        self.identity = identity
        self.ref = ref

    def blob(self, path: str) -> bytes:
        spec = f"{self.commit}:{path}"
        size = int(git(self.directory, "cat-file", "-s", spec))
        if size > MAX_BLOB:
            raise CourseError(f"Source file exceeds the 256 MiB limit: {path}")
        if git(self.directory, "cat-file", "-t", spec).strip() != b"blob":
            raise CourseError(f"Not a regular source file: {path}")
        return git(self.directory, "cat-file", "blob", spec)

    def export(self, prefix: str, destination: Path, safe_relative) -> None:
        entries = git(self.directory, "ls-tree", "-rz", "--full-tree", self.commit, "--", prefix)
        total = 0
        count = 0
        folded = set()
        for entry in entries.split(b"\0"):
            if not entry:
                continue
            header, raw_path = entry.split(b"\t", 1)
            mode, kind, _ = header.split()
            if mode != b"100644" or kind != b"blob":
                raise CourseError("Published courses may contain only non-executable regular files.")
            path = raw_path.decode("utf-8")
            safe_relative(path)
            if not path.startswith(prefix + "/"):
                raise CourseError(f"Source path escaped the course prefix: {path}")
            if path.casefold() in folded:
                raise CourseError(f"Case-insensitive source collision: {path}")
            folded.add(path.casefold())
            content = self.blob(path)
            total += len(content)
            count += 1
            if total > MAX_PACKAGE or count > 10000:
                raise CourseError("Course exceeds the 1 GiB / 10,000-file import limit.")
            target = plain_path(destination / path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        if count == 0:
            raise CourseError(f"No course files at {prefix} in source commit {self.commit}.")


@contextmanager
def open_source(repository: str = DEFAULT_SOURCE, ref: str | None = None,
                checkout: Path | None = None):
    requested = ref or ("HEAD" if checkout else "main")
    if not requested or requested.startswith("-") or any(c.isspace() for c in requested):
        raise CourseError("Use a nonempty Git ref or immutable commit without whitespace or options.")
    if checkout:
        directory = plain_path(checkout)
        if not directory.is_dir():
            raise CourseError(f"Local source checkout does not exist: {directory}")
        commit = git(directory, "rev-parse", "--verify", "--end-of-options",
                     requested + "^{commit}").decode().strip()
        identity = str(directory)
        yield Source(directory, commit, identity, requested)
    else:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise CourseError("Source must be a GitHub owner/repository name.")
        with tempfile.TemporaryDirectory(prefix="clew-source-") as temporary:
            directory = Path(temporary)
            git(directory, "init", "--bare", "--quiet")
            git(directory, "fetch", "--quiet", "--depth=1", "--no-tags",
                f"https://github.com/{repository}.git", requested)
            commit = git(directory, "rev-parse", "--verify", "FETCH_HEAD^{commit}").decode().strip()
            yield Source(directory, commit, repository, requested)
