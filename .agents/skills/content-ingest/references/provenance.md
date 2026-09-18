# Provenance and bounded migration

The engine and formatter were migrated from `src/ingest/` in
`francesco-kruk/clew` at revision
`6b03b5e8fdaefc16478de179bac00e9baa188c20`. Source inspection also included
`.agents/skills/content-ingest/SKILL.md` and
`.agents/agents/content-ingest.agent.md`.

**Alexandra Pletea authored the original ingestion implementation**, including
image-first extraction, per-chapter output, and formula image positioning.
Relevant history includes `b4aabb1`, `c9d6f7f`, `78a797f`, and `e515efd`.
All original copyright holders remain in the unmodified MIT [LICENSE](../LICENSE).
This package does not claim the original engine as new work.

The original skill/agent prose promised editable exercise callouts, Mermaid, and
LaTeX that the inspected implementation did not generate. This package documents
the implementation truthfully instead of carrying those promises forward.

Changes are limited to packaging and closely coupled correctness:

- A standalone `scripts/ingest.py` launcher and adjacent `clew_ingest` package.
- Actual runtime dependencies only: PyMuPDF, PyYAML, Typer, Rich.
- Links based on explicit output/asset roots, URI escaping, cross-volume links,
  nonempty document slugs, and reserved Windows device-name handling.
- Case-insensitive PDF inventory without duplicate Windows matches,
  deterministic processing, and batch slug collision rejection.
- Nonzero status for document failures; escaped diagnostics for filenames with
  Rich markup; clear invalid/encrypted/range errors; context-managed PDF closure.
- Avoid empty crops outside the page and detect unextractable image references.
- Synthetic regression tests and extraction-to-course publishing boundaries.

Chapter/prose/formula/exercise heuristics, page ordering, default options, output
names for ordinary inputs, metadata, 150 DPI, and the image-first strategy remain.
There is no extraction redesign, OCR stack, hosted ingestion dependency, or
automatic course/learner-model modification.
