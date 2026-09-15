"""
Core Ingestion Engine for converting PDFs into modifiable Markdown documents.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .formatters import MarkdownArtifactFormatter


class IngestionEngine:
    """PDF Ingestion and parsing engine with Docling support and lightweight fallbacks."""

    def __init__(
        self,
        output_dir: str = "content",
        assets_dir: str = "content/assets",
        course_name: Optional[str] = None,
        default_domain: Optional[str] = None,
    ):
        self.output_dir = Path(output_dir)
        self.assets_dir = Path(assets_dir)
        self.course_name = course_name or "General"
        self.default_domain = default_domain or "General"
        self.formatter = MarkdownArtifactFormatter(
            course_name=self.course_name,
            default_domain=self.default_domain,
        )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def ingest_pdf(self, pdf_path: str | Path) -> Tuple[Path, Dict[str, Any]]:
        """Ingest a single PDF file and write structured Markdown to the output directory."""
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_file}")

        slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", pdf_file.stem).strip("-").lower()
        doc_assets_dir = self.assets_dir / slug
        doc_assets_dir.mkdir(parents=True, exist_ok=True)

        extracted_text, stats = self._extract_content(pdf_file, doc_assets_dir)

        # Enhance with modifiable callout blocks for exercises and artifacts
        enhanced_text = self.formatter.enhance_markdown_with_artifacts(extracted_text)

        # Generate frontmatter
        title = pdf_file.stem.replace("-", " ").replace("_", " ").title()
        frontmatter = self.formatter.format_frontmatter(
            source_name=pdf_file.name,
            title=title,
            domains=[self.default_domain],
            concepts=[],
            stats=stats,
        )

        full_content = frontmatter + enhanced_text
        output_file = self.output_dir / f"{slug}.md"
        output_file.write_text(full_content, encoding="utf-8")

        return output_file, stats

    def _extract_content(self, pdf_path: Path, doc_assets_dir: Path) -> Tuple[str, Dict[str, int]]:
        """Attempt extraction using Docling first, then fall back to pymupdf4llm / PyMuPDF."""
        stats = {"exercises": 0, "charts": 0, "images": 0, "tables": 0}

        # 1. Try Docling
        try:
            from docling.document_converter import DocumentConverter

            converter = DocumentConverter()
            result = converter.convert(str(pdf_path))
            markdown = result.document.export_to_markdown()

            # Inspect docling items for stats
            for item, _ in result.document.iterate_items():
                label = getattr(item, "label", "")
                if "table" in label.lower():
                    stats["tables"] += 1
                elif "picture" in label.lower() or "figure" in label.lower() or "chart" in label.lower():
                    stats["charts"] += 1

            return markdown, stats
        except Exception:
            pass

        # 2. Try PyMuPDF4LLM / PyMuPDF fallback
        try:
            import fitz
            import pymupdf4llm

            # Extract markdown via pymupdf4llm
            md_text = pymupdf4llm.to_markdown(
                str(pdf_path),
                write_images=True,
                image_path=str(doc_assets_dir),
                image_format="png",
            )

            # Count extracted images
            image_files = list(doc_assets_dir.glob("*.png")) + list(doc_assets_dir.glob("*.jpg"))
            stats["images"] = len(image_files)
            stats["charts"] = len(image_files)

            return md_text, stats
        except Exception:
            pass

        # 3. Last-resort fallback: Pure text extraction via PyMuPDF/pypdf
        try:
            import fitz

            doc = fitz.open(str(pdf_path))
            pages = []
            for i, page in enumerate(doc):
                pages.append(f"## Page {i + 1}\n\n" + page.get_text("text"))
            return "\n\n".join(pages), stats
        except Exception as e:
            raise RuntimeError(f"Failed to extract content from {pdf_path}: {e}") from e
