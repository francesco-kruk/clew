# Course distribution contract v1

This preserved legacy API is for explicitly requested package/catalog
distribution and validation, not ordinary student Markdown reading. No package
manifest, catalog or validator run is required to use a manually copied bundle.

This contract belongs to `course-content`. For this explicit format, the structure in
`structure.md` remains authoritative; chapter order exists only in `hub.md`.
JSON paths use `/`, even on Windows. Text and JSON are UTF-8.

## Catalog

`catalog.json` at a source repository root:

```json
{"schema_version":1,"courses":[{"id":"trigonometry","title":"Trigonometry","path":"courses/Trigonometry"}]}
```

An empty `courses` list is valid. IDs match `[a-z0-9]+(?:-[a-z0-9]+)*`.
Each entry identifies a publishable package. IDs and paths are unique
case-insensitively. `title` equals the package's `course`; `path` equals its
`course_root`. No chapter order or learner metadata belongs in the catalog.

## Package

`courses/Trigonometry/course-package.json`:

```json
{
  "schema_version": 1,
  "id": "trigonometry",
  "course": "Trigonometry",
  "course_root": "courses/Trigonometry",
  "hub": "hub.md",
  "files": [
    {"path":"hub.md","sha256":"<64 lowercase hexadecimal characters>"},
    {"path":"chapters/TRIG - 01.md","sha256":"<64 lowercase hexadecimal characters>"},
    {"path":"reports/attribution.md","sha256":"<64 lowercase hexadecimal characters>"},
    {"path":"reports/rights.md","sha256":"<64 lowercase hexadecimal characters>"},
    {"path":"reports/verification.json","sha256":"<64 lowercase hexadecimal characters>"}
  ],
  "attribution": "reports/attribution.md",
  "rights": {"status":"pending","evidence":"reports/rights.md"},
  "reports": ["reports/verification.json"]
}
```

Inventory paths, `hub`, `attribution`, `rights.evidence`, and `reports` are
relative to the package directory. `course_root` is exactly `courses/<course>`
(the final component equals `course`). `hub` is always `hub.md`.
All files except `course-package.json` must appear exactly once in `files`.
The manifest must not inventory itself. Hash the actual file bytes using SHA256.
No scripts, tooling, private learner records, hidden files, symlinks/reparse
points, unsafe Windows names, traversal, or case-insensitive path collisions
are permitted. Allowed extensions: `.md`, `.json`, `.canvas`, `.pdf`, `.png`,
`.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.txt`, `.csv`, `.mp3`, `.wav`,
`.mp4`, `.webm`. HTML and executable files are not course distribution files.

`attribution` and `rights.evidence` identify nonempty inventoried documents.
`reports` is a nonempty list of inventoried verification report paths. Historical
reports must label their scope; structural validation cannot establish source
fidelity or legally verify a permission assertion.

`rights.status` is `pending` or `confirmed`. `pending` is valid only for local
draft validation; publish validation requires `confirmed`. The evidence document
must record source, rights holder/attribution, permission or license scope, and
actual evidence without inventing a content license. Confirmation is a human
publication gate, not a conclusion produced by this validator.

Local links must resolve inside this inventory, including Markdown links,
wikilinks/embeds, headings/blocks, frontmatter sources and Canvas file nodes.
Canvas paths are vault-root-relative under `course_root`. Reader-facing notes
and assets must be reachable from the hub; attribution, rights and reports are
also entry points for closure. Source PDF `#page=N` references require a
positive page number; page count/source fidelity is outside structural checks.
External URLs are citations and are never fetched.

## Stable validator interface

Use Python 3.11 or newer and install `requirements.txt` from this skill
(PyYAML; no learner-model dependency).
Run from any working directory:

```powershell
python "<installed course-content>\scripts\validate_course.py" --package "<package directory>" --mode draft
python "<installed course-content>\scripts\validate_course.py" --package "<package directory>"
python "<installed course-content>\scripts\validate_course.py" --catalog "<source root>\catalog.json"
```

Default mode is `publish`. `--catalog` validates its entries and their packages
in publish mode, including when `--mode draft` is selected for an additional
`--package`. At least one of `--package` or `--catalog` is required.
Both may be supplied; neither infers a learner vault or reads private state.
Use `--catalog-only` with `--catalog` to validate discovery metadata without
reading package directories (for remote listing/selection). This is not
publication validation or proof that a selected package is safe to import.

Stdout is exactly one JSON object:

```json
{"schema_version":1,"ok":false,"errors":[{"code":"rights","path":"course-package.json","message":"Publication requires confirmed rights."}]}
```

Successful reports have `ok:true` and `errors:[]`. Additional informational
fields may be added; consumers must not depend on error ordering or prose.
Exit status is 0 for success, 1 for validation/dependency/I/O failure, and 2 for
CLI syntax errors. No failure is reported as success.

Python callers may load `scripts/validate_course.py` by explicit installed path
and call `validate_package(package_dir, mode="publish")` or
`validate_catalog(catalog_path, packages=True)`. Set `packages=False` for
catalog-only discovery checks. Arguments accept strings or pathlib Paths;
both return the report object above, without printing or exiting. They perform
read-only validation and never import from a Clew checkout.
`valid_path(value)` returns a boolean for Windows-safe serialized relative-path
syntax only; callers must still check filesystem confinement and exclusions.
