---
name: content-ingest
description: Ingest PDF course materials, extracting text, structure, mathematical notation, editable graphs/charts, and interactive exercise callouts into Markdown files in the content/ folder. Use whenever asked to ingest, parse, convert, or import PDF files, lecture notes, textbooks, or worksheets.
---

# Content Ingestion Skill

Ingest PDF documents and produce clean, modifiable Markdown files with editable exercise callouts, Mermaid graphs, and data tables for Clew's learner adaptation pipeline.

## Crucial Rule
- **NEVER generate or run ad-hoc inline Python scripts with `pypdf` or `pdfminer`.**
- **ALWAYS execute Clew's built-in ingestion CLI:**

```bash
python -m src.ingest.cli "<pdf_path>" --course "<course_name>" --domain "<domain_name>"
```

If ingesting a directory of PDFs:
```bash
python -m src.ingest.cli "<folder_path>" --course "<course_name>"
```

## Post-Ingestion Verification
1. Verify the generated output in `content/<slug>.md`.
2. Confirm:
   - Metadata frontmatter contains `course`, `domains`, and `artifacts`.
   - Exercises are formatted as `> [!exercise]` callout blocks with task checkboxes `- [ ]`.
   - Graphs/diagrams are formatted as Mermaid blocks (`> ```mermaid`) or data tables, with source image captures in `content/assets/<slug>/`.
   - Math equations retain proper LaTeX formatting (`$...$` and `$$...$$`).
