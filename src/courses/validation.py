"""Load the single course contract from the pinned APM deployment."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path, PurePosixPath

from .storage import ROOT, CourseError

VALIDATOR = ROOT / ".agents" / "skills" / "course-content" / "scripts" / "validate_course.py"


def safe_relative(value: str) -> str:
    """Constrain filesystem writes before untrusted material reaches validation."""
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise CourseError(f"Unsafe relative path: {value!r}")
    components = value.split("/")
    if PurePosixPath(value).is_absolute() or any(
        not part or part in (".", "..") or part.endswith((".", " "))
        or any(ord(c) < 32 or c in '<>"|?*' for c in part)
        or re.fullmatch(r"(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part)
        for part in components
    ):
        raise CourseError(f"Unsafe relative path: {value!r}")
    return value


def load_validator():
    if not VALIDATOR.is_file():
        raise CourseError("Course validator is missing. Restore pinned skills with APM 0.28.0: apm install --frozen")
    spec = importlib.util.spec_from_file_location("clew_course_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise CourseError(f"Cannot load pinned course validator: {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ModuleNotFoundError as exc:
        raise CourseError(
            "Course validator dependency is missing. Run python -m pip install -r requirements.txt "
            f"({exc}). PDF dependencies are not required."
        ) from exc
    return module


def require_valid(report: dict, description: str) -> None:
    if report.get("ok") is not True:
        details = "; ".join(
            f"{error.get('path', '')}: {error.get('message', 'validation failed')}"
            for error in report.get("errors", [])
        )
        raise CourseError(f"{description} failed validation: {details}")
