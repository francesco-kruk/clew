"""Original synthetic course; no textbook or learner material."""

import hashlib
import json
from pathlib import Path


def refresh_manifest(package):
    package = Path(package)
    path = package / "course-package.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["files"] = [
        {"path": file.relative_to(package).as_posix(),
         "sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
        for file in sorted(package.rglob("*"))
        if file.is_file() and file != path
    ]
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def make_course(root, course="Synthetic mechanics", rights="confirmed"):
    package = Path(root) / "courses" / course
    prefix = f"courses/{course}"
    files = {
        "hub.md": f"""---
type: course
course: {course}
primary_domains: [Physics]
prerequisite_domains: [Algebra]
sources: []
---
# {course}

Original synthetic examples of distance.

## Chapters

1. [[{prefix}/chapters/SYN - 01 - Motion|Motion]]

## Concept index

| Concept ID | Concept | Domain | Location |
| --- | --- | --- | --- |
| null | Distance | Physics | [[{prefix}/chapters/SYN - 01 - Motion#Distance]] |

## Resources

- [[{prefix}/Map.canvas]]

## Content notes

Concept IDs are unmapped; examples are synthetic.
""",
        "chapters/SYN - 01 - Motion.md": f"""---
type: course-chapter
course: {course}
chapter: "1"
hub: "[[{prefix}/hub]]"
sources: []
---
# Motion

[[{prefix}/hub|Back to course]]

## Distance

A synthetic traveller moves three metres. ^distance
""",
        "reports/attribution.md": "# Attribution\nOriginal synthetic test material by Clew contributors.\n",
        "reports/rights.md": "# Rights\nOriginal synthetic material, provided under MIT for these tests.\n",
        "reports/verification.json": '{"scope":"synthetic structural fixture; not textbook fidelity"}\n',
        "Map.canvas": json.dumps({
            "nodes": [{"id": "chapter", "type": "file",
                       "file": f"{prefix}/chapters/SYN - 01 - Motion.md",
                       "subpath": "#Distance", "x": 0, "y": 0, "width": 320, "height": 200}],
            "edges": [],
        }),
    }
    for name, text in files.items():
        path = package / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    manifest = {
        "schema_version": 1, "id": "synthetic-mechanics", "course": course,
        "course_root": prefix, "hub": "hub.md", "files": [],
        "attribution": "reports/attribution.md",
        "rights": {"status": rights, "evidence": "reports/rights.md"},
        "reports": ["reports/verification.json"],
    }
    (package / "course-package.json").write_text(json.dumps(manifest), encoding="utf-8")
    refresh_manifest(package)
    catalog = Path(root) / "catalog.json"
    catalog.write_text(json.dumps({"schema_version": 1, "courses": [{
        "id": manifest["id"], "title": course, "path": prefix,
    }]}), encoding="utf-8")
    return package
