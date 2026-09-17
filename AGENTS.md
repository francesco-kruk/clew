# Working in Clew

Before architectural changes, read the [ADR process and index](docs/adr/README.md),
applicable records, and relevant specifications such as the
[learner model](docs/LEARNER_MODEL.md).

## Ingesting Course Content & PDFs

When ingesting PDFs, textbooks, worksheets, or course materials:
- **Never write ad-hoc Python scripts or raw `pypdf` text extractors.**
- Always use Clew's built-in ingestion CLI:
  ```bash
  python -m src.ingest.cli "<path_to_pdf>" --course "<course_name>" --domain "<domain_name>"
  ```
- If ingesting a folder of PDFs:
  ```bash
  python -m src.ingest.cli "<path_to_folder>" --course "<course_name>"
  ```
- Output is written to `content/<slug>.md` with editable diagrams (Mermaid / data tables), interactive exercise callouts (`> [!exercise]`), and image assets in `content/assets/`.

## Architecture & Skills

For significant architectural decisions, use the APM-managed
[create-architectural-decision-record skill](.agents/skills/create-architectural-decision-record/SKILL.md)
and [ADR template](docs/adr/template.md). Ask for missing context, options,
rationale, or stakeholders rather than inventing them. New records start
Proposed; acceptance and other lifecycle changes require explicit human approval.
Acceptance is not authorization to implement. Keep the index and supersession
links consistent, and preserve historical records.

Do not edit generated files under `.agents/skills/`. Manage dependency changes
through `apm.yml` and APM, preserving pinned versions, the lockfile, and license
notices. Keep Clew-specific guidance outside the generated skills.
