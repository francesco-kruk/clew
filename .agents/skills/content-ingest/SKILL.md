---
name: content-ingest
description: Ingest PDF course materials, extracting text, structure, mathematical notation, editable graphs/charts, and interactive exercise callouts into Markdown files in the content/ folder.
compatibility: Requires Python environment with the Clew ingestion engine dependencies installed.
---

# Content Ingestion Skill

Ingest PDF documents and produce clean, modifiable Markdown files for Clew's learner adaptation pipeline.

## Operating Instructions

1. **Locate Target Files**:
   Ensure the input PDF exists on the local filesystem.
2. **Execute Ingestion Command**:
   Run the CLI engine:
   ```bash
   python -m src.ingest.cli "<pdf_path>" --output content/ --assets content/assets/
   ```
3. **Artifact Standards**:
   - **Exercises**: Must be encapsulated in Obsidian callout format `> [!exercise] ...` with interactive task lists `- [ ] Your Answer:` and collapsible solution hints.
   - **Graphs & Charts**: Must include Mermaid code (`> ```mermaid ...`) or tabular data where data points are known, backed by high-resolution image captures in `content/assets/<doc-slug>/`.
   - **Mathematical formulas**: Standard LaTeX format ($...$ for inline, $$...$$ for display blocks).
   - **Frontmatter**: Standardized YAML header with course, domain, and artifact metrics.
