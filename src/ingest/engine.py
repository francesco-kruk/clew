"""
Core Ingestion Engine for converting PDFs into modifiable Markdown documents with visual artifacts.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pymupdf

from .formatters import MarkdownArtifactFormatter


def cluster_bounding_boxes(rects: List[pymupdf.Rect], margin: float = 12.0) -> List[pymupdf.Rect]:
    """Merge overlapping or neighboring drawing/formula bounding boxes into cohesive visual clusters."""
    if not rects:
        return []

    clusters: List[pymupdf.Rect] = []
    for r in rects:
        expanded = pymupdf.Rect(r.x0 - margin, r.y0 - margin, r.x1 + margin, r.y1 + margin)
        merged = False
        for i, c in enumerate(clusters):
            c_expanded = pymupdf.Rect(c.x0 - margin, c.y0 - margin, c.x1 + margin, c.y1 + margin)
            if c_expanded.intersects(expanded):
                clusters[i] = c | r
                merged = True
                break
        if not merged:
            clusters.append(pymupdf.Rect(r))

    final_clusters: List[pymupdf.Rect] = []
    for c in clusters:
        merged = False
        for j, fc in enumerate(final_clusters):
            if fc.intersects(pymupdf.Rect(c.x0 - margin, c.y0 - margin, c.x1 + margin, c.y1 + margin)):
                final_clusters[j] = fc | c
                merged = True
                break
        if not merged:
            final_clusters.append(c)

    return [c for c in final_clusters if c.width > 12 and c.height > 8]


class IngestionEngine:
    """PDF Ingestion and parsing engine with visual formula/diagram extraction."""

    def __init__(
        self,
        output_dir: str = "content",
        assets_dir: str = "content/assets",
        course_name: Optional[str] = None,
        default_domain: Optional[str] = None,
        dpi: int = 150,
    ):
        self.output_dir = Path(output_dir)
        self.assets_dir = Path(assets_dir)
        self.course_name = course_name or "General"
        self.default_domain = default_domain or "General"
        self.dpi = dpi
        self.formatter = MarkdownArtifactFormatter(
            course_name=self.course_name,
            default_domain=self.default_domain,
        )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def ingest_pdf(self, pdf_path: str | Path) -> Tuple[Path, Dict[str, Any]]:
        """Ingest a PDF file, extracting clean text alongside visual images of formulas, diagrams, and exercises."""
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_file}")

        slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", pdf_file.stem).strip("-").lower()
        doc_assets_dir = self.assets_dir / slug
        doc_assets_dir.mkdir(parents=True, exist_ok=True)

        doc = pymupdf.open(str(pdf_file))
        stats = {"exercises": 0, "charts": 0, "images": 0, "formulas": 0, "pages": len(doc)}

        markdown_pages: List[str] = []

        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text").strip()
            drawings = [d["rect"] for d in page.get_drawings()]
            images = page.get_images()

            clusters = cluster_bounding_boxes(drawings, margin=15.0)
            page_figures: List[str] = []

            # 1. Render all drawing / formula clusters as images
            for c_idx, cluster in enumerate(clusters, start=1):
                padded_rect = cluster + (-6, -6, 6, 6)
                padded_rect = padded_rect & page.rect

                pix = page.get_pixmap(clip=padded_rect, dpi=self.dpi)
                fig_filename = f"page-{page_num}-fig-{c_idx}.png"
                fig_path = doc_assets_dir / fig_filename
                pix.save(str(fig_path))

                rel_asset_path = f"assets/{slug}/{fig_filename}"
                page_figures.append(rel_asset_path)
                stats["formulas"] += 1

            # 2. Extract embedded raster images
            for img_idx, img in enumerate(images, start=1):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                img_filename = f"page-{page_num}-img-{img_idx}.{image_ext}"
                img_path = doc_assets_dir / img_filename
                img_path.write_bytes(image_bytes)

                rel_asset_path = f"assets/{slug}/{img_filename}"
                page_figures.append(rel_asset_path)
                stats["images"] += 1

            # 3. Check if this page is an actual Exercise / Problem page (exclude Table of Contents)
            is_toc_page = bool(re.search(r"\b(contents\s+page|table\s+of\s+contents)\b", page_text, re.I)) or page_num <= 2
            is_exercise_page = (
                not is_toc_page
                and bool(re.search(r"\b(tutorial\s+exercises?|practice\s+problems?|problem\s+set)\b", page_text, re.I))
            )

            page_lines: List[str] = []
            page_lines.append(f"<!-- Page {page_num} -->")

            if is_exercise_page:
                stats["exercises"] += 1
                ex_filename = f"exercise-page-{page_num}.png"
                ex_path = doc_assets_dir / ex_filename
                page_pix = page.get_pixmap(dpi=self.dpi)
                page_pix.save(str(ex_path))
                ex_rel_path = f"assets/{slug}/{ex_filename}"

                title_match = re.search(r"(Tutorial\s+Exercises?|Exercises?|Problem\s+Set[^\n]*)", page_text, re.I)
                ex_title = title_match.group(1).strip() if title_match else f"Exercise Set (Page {page_num})"

                page_lines.append(
                    self.formatter.format_exercise_as_image(
                        title=f"{ex_title} - Page {page_num}",
                        image_path=ex_rel_path,
                        text_summary=page_text[:300].strip(),
                    )
                )
            else:
                if page_text:
                    cleaned_text = re.sub(r"\n{3,}", "\n\n", page_text)
                    page_lines.append(cleaned_text)

                if page_figures:
                    page_lines.append("\n**Visual Diagrams & Formulas:**\n")
                    for fig_path in page_figures:
                        page_lines.append(f"![Figure]({fig_path})\n")

            markdown_pages.append("\n\n".join(page_lines))

        title = pdf_file.stem.replace("-", " ").replace("_", " ").title()
        frontmatter = self.formatter.format_frontmatter(
            source_name=pdf_file.name,
            title=title,
            domains=[self.default_domain],
            concepts=[],
            stats=stats,
        )

        full_content = frontmatter + "\n\n---\n\n".join(markdown_pages)
        output_file = self.output_dir / f"{slug}.md"
        output_file.write_text(full_content, encoding="utf-8")

        return output_file, stats

