# Runtime and CLI reference

## Installation

Python 3.10 or newer is required. Use a dedicated environment; no package
installation, editable repository install, `PYTHONPATH`, or source checkout is
needed beyond the four dependencies declared in `requirements.txt`.

From a workspace containing the skill (PowerShell):

```powershell
python -m venv '.\skills\content-ingest\.venv'
& '.\skills\content-ingest\.venv\Scripts\python.exe' -m pip install -r '.\skills\content-ingest\requirements.txt'
$python = (Resolve-Path '.\skills\content-ingest\.venv\Scripts\python.exe').Path
$ingest = (Resolve-Path '.\skills\content-ingest\scripts\ingest.py').Path
& $python $ingest --help
& $python $ingest 'D:\Authorized PDFs' -o 'D:\Staging Area\markdown' -a 'D:\Staging Area\assets' -c 'Calculus' -d 'Mathematics'
```

On POSIX use the environment's `bin/python` and native absolute paths. The
launcher imports its adjacent `clew_ingest` package, independently of the caller's
working directory. The package is not a top-level `src` dependency.

## Compatibility contract

| Argument/option | Default | Meaning |
| --- | --- | --- |
| `PATH` | required | One PDF or a nonrecursive directory of PDFs |
| `--output`, `-o` | `content` | Markdown root, relative to the caller's cwd if not absolute |
| `--assets`, `-a` | `content/assets` | Asset root, independently relative to cwd |
| `--course`, `-c` | omitted → `General` | Course metadata label |
| `--domain`, `-d` | omitted → `General` | Default domain metadata label |

The original defaults are retained for compatibility, **not** recommended as
implicit authorization to write into an arbitrary cwd. Specify both roots in
agent workflows. Changing `--output` alone does **not** change `--assets`.
The Python API still defaults to 150 DPI, with no added CLI DPI option.

Outputs:

```text
<output>/<document-slug>/01-<chapter-slug>.md
<assets>/<document-slug>/page-<physical-page>-fig-<region>.png
<assets>/<document-slug>/page-<physical-page>-exercise.png
<assets>/<document-slug>/page-<physical-page>-img-<index>.<source-extension>
```

For a document with no recognized contents entries the chapter is
`01-full-document.md`. Slugs retain the original lowercase ASCII convention.
An entirely non-ASCII/punctuation document name uses `document`; reserved
Windows device slugs are prefixed with `document-`. Batch slug collisions fail
before extraction to avoid silent overwrite. Separate runs can still overwrite
the same slug: use new explicit roots for different sources and for revisions.

All asset links are computed from the actual chapter directory, use Markdown
forward slashes, and percent-encode spaces, parentheses, and URI delimiters.
Same-volume links are relative. Across Windows drive letters, links become
absolute `file:` URLs; viewers may restrict those, and they are not portable
course assets. Copy/relink assets inside the authorized course at publishing
time. Default layout links remain `../assets/<document-slug>/<asset>`.

Directories recognize every case variant of `.pdf`, once each, in deterministic
filename order. Nested directories are not traversed.

Exit codes: `0` for successful extraction or an empty-directory warning; `1`
for invalid input, output setup errors, collisions, encrypted/unreadable/invalid
documents, or **any** per-document failure; `2` for invalid CLI syntax. Batch
processing continues after a document failure, but the final status stays
nonzero. Errors can leave partial files; inspect staging before reusing it.

## Original extraction behavior and limitations

- The engine looks for the word `contents` in the first eight physical pages,
  dotted leaders, and numeric printed page labels. It estimates an offset using
  the first title and offsets zero through nine, merges starts on the same page,
  or falls back to the whole document. PDF bookmarks are not used. Front matter
  preceding a recognized first chapter is not automatically emitted.
- The original English-word/operator heuristic keeps prose, crops formula-like
  blocks and drawings, and interleaves these by vertical position. Multi-column
  order, non-English prose, tables, labels, unusual typesetting, and complex
  figure groupings can be wrong or incomplete. No extraction redesign is made.
- English exercise markers select entire pages (or chapters) for photos. Those
  images may include supplied answers. There is no exercise/answer parser.
- Embedded rasters are extracted as source image bytes and appended after prose.
  Scanned pages may survive as images, **not** OCR text. Raster transparency,
  rotation, clipping, and masks are not reconstructed as a page-rendering system.
- Crop PNGs and exercise photos use 150 DPI. There is no OCR, equation
  transcription, semantic diagram conversion, table recovery, or LLM call.
- Password-protected documents must be unlocked externally by an authorized user.
  No password guessing, external resource fetching, or automatic uploads occur.
- Markdown metadata preserves the legacy schema. `type: course-content` is only
  an extraction tag, not a validator result or a claim of canonical course shape.
- Large documents and full-page images may consume substantial disk/memory.
  No resource sandbox, concurrency, transactional output, or stale-file cleanup
  is provided. Use bounded, authorized inputs and inspect every reported failure.

## Run the synthetic suite

From the repository root:

```powershell
& '.\skills\content-ingest\.venv\Scripts\python.exe' -m unittest discover -s '.\skills\content-ingest\tests' -v
```

Tests generate their own PDFs beneath `tests/.runs`, remove their work afterward,
and never require private courses, learner records, internet access, or the
original repository. Dependencies must already be installed.
