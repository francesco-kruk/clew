"""Original miniature course; contains no textbook or learner data."""

import hashlib
import json
from pathlib import Path

COURSE = "Original Examples"
PREFIX = "courses/" + COURSE


def write_package(root: Path) -> Path:
    package = root / "courses" / COURSE
    files = {
        "hub.md": """---
type: course
course: Original Examples
primary_domains: [Mathematics]
prerequisite_domains: []
sources: []
---
# Original Examples

An original synthetic counting lesson, written only for tests.

## Chapters
1. [[courses/Original Examples/chapters/EX - 01|Counting]]

## Concept index
| Concept ID | Concept | Domain | Location |
| --- | --- | --- | --- |
| null | Counting | Mathematics | [[courses/Original Examples/chapters/EX - 01#Counting]] |

## Resources
[[courses/Original Examples/map.canvas]]

## Content notes
Concept IDs are not assigned; this is original synthetic material.
""",
        "chapters/EX - 01.md": """---
type: course-chapter
course: Original Examples
chapter: "1"
hub: "[[courses/Original Examples/hub]]"
sources: []
---
# One
[[courses/Original Examples/hub|Course]]

## Counting
A blue token and a red token make two tokens.
""",
        "map.canvas": json.dumps({"nodes": [{"id": "one", "type": "file",
            "file": PREFIX + "/chapters/EX - 01.md", "x": 0, "y": 0,
            "width": 400, "height": 300}], "edges": []}),
        "reports/attribution.md": "Original synthetic test material authored for Clew's importer tests.\n",
        "reports/rights.md": "Source: original test fixture. Rights holder: Clew contributors. "
            "Permission: repository MIT license covers this original fixture; no third-party textbook.\n",
        "reports/verification.json": '{"scope":"original synthetic structural fixture, not PDF fidelity"}\n',
    }
    for name, content in files.items():
        path = package / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    manifest = {
        "schema_version": 1, "id": "original-examples", "course": COURSE,
        "course_root": PREFIX, "hub": "hub.md", "files": [],
        "attribution": "reports/attribution.md",
        "rights": {"status": "confirmed", "evidence": "reports/rights.md"},
        "reports": ["reports/verification.json"],
    }
    (package / "course-package.json").write_text(json.dumps(manifest), encoding="utf-8")
    rehash(package)
    (root / "catalog.json").write_text(json.dumps({
        "schema_version": 1, "courses": [
            {"id": "original-examples", "title": COURSE, "path": PREFIX}
        ]}), encoding="utf-8")
    return package


def rehash(package: Path) -> None:
    path = package / "course-package.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["files"] = [
        {"path": file.relative_to(package).as_posix(),
         "sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
        for file in sorted(package.rglob("*"))
        if file.is_file() and file != path
    ]
    path.write_text(json.dumps(manifest), encoding="utf-8", newline="\n")
