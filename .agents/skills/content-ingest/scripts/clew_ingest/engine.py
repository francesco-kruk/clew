"""
Core Ingestion Engine for converting PDFs into one Markdown document per chapter.
Formulas, diagrams, and exercises are embedded as photos, not transcribed.

Originally authored by Alexandra Pletea; see the package LICENSE and provenance.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

import pymupdf

from .formatters import MarkdownArtifactFormatter

_EXERCISE_PATTERN = re.compile(
    r"\b(tutorial\s+exercises?|practice\s+problems?|problem\s+set|answers?\s+to\s+tutorial\s+exercises?)\b",
    re.IGNORECASE,
)

# Characters that reliably indicate an equation rather than prose, even when short.
_FORMULA_OPERATORS = set("=\u00d7\u00f7\u222b\u2264\u2265\u00b1")


def _slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]+", "-", text).strip("-").lower()


def _document_slug(path: Path) -> str:
    slug = _slugify(path.stem) or "document"
    # Windows reserves these names even when an extension is present.
    if re.fullmatch(r"con|prn|aux|nul|com[1-9]|lpt[1-9]", slug, re.IGNORECASE):
        slug = f"document-{slug}"
    return slug


def _normalize(text: str) -> str:
    """Collapse whitespace and strip non-alphanumeric characters for loose text comparisons."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _extract_prose(page: pymupdf.Page) -> Tuple[List[Tuple[float, str]], List[pymupdf.Rect]]:
    """Keep prose with its vertical position and collect formula-like blocks for photos."""
    kept: List[Tuple[float, str]] = []
    dropped_rects: List[pymupdf.Rect] = []
    for block in page.get_text("blocks"):
        block_text = block[4]
        if not block_text.strip():
            continue
        word_count = len(re.findall(r"[A-Za-z]{3,}", block_text))
        formula_like = any(ch in block_text for ch in _FORMULA_OPERATORS)
        if word_count >= 8 or (word_count >= 2 and not formula_like):
            kept.append((block[1], block_text.strip()))
        else:
            dropped_rects.append(pymupdf.Rect(*block[:4]))
    return kept, dropped_rects


def _cluster_rects(rects: List[pymupdf.Rect], margin: float = 10.0) -> List[pymupdf.Rect]:
    """Merge overlapping or neighboring rectangles into cohesive visual regions to crop."""
    clusters: List[pymupdf.Rect] = []
    for r in rects:
        expanded = pymupdf.Rect(r.x0 - margin, r.y0 - margin, r.x1 + margin, r.y1 + margin)
        for i, c in enumerate(clusters):
            c_expanded = pymupdf.Rect(c.x0 - margin, c.y0 - margin, c.x1 + margin, c.y1 + margin)
            if c_expanded.intersects(expanded):
                clusters[i] = c | r
                break
        else:
            clusters.append(pymupdf.Rect(r))
    return [c for c in clusters if c.width > 10 and c.height > 8]


def _extract_chapters(doc: pymupdf.Document) -> List[Tuple[str, int, int]]:
    """Locate dotted-leader contents entries, or use one chapter for the whole PDF.

    Page indices are zero-based and inclusive. Printed-page offsets use the original
    first-title heuristic; this is not a general-purpose chapter recognition system.
    """
    toc_entry_pattern = re.compile(r"(.{3,90}?)\s*\.{4,}\s*(\d{1,4})\b")
    entries: List[Tuple[str, int]] = []
    toc_page_idx: Optional[int] = None

    for i, page in enumerate(doc[:8]):
        text = page.get_text("text")
        if not re.search(r"\bcontents\b", text, re.IGNORECASE):
            continue
        toc_page_idx = i
        normalized = re.sub(r"\s+", " ", text)
        normalized = re.sub(r"(?i)^.*?\bcontents\b(?:\s+page)?\s*", "", normalized, count=1)
        for match in toc_entry_pattern.finditer(normalized):
            title = match.group(1).strip(" .")
            title = re.sub(r"^\d{1,2}\.\s*", "", title).strip()
            printed_page = int(match.group(2))
            if title and len(title) > 2:
                entries.append((title, printed_page))

    if not entries:
        return [("Full Document", 0, len(doc) - 1)]

    first_title, first_printed_page = entries[0]
    target = _normalize(first_title)
    min_idx = (toc_page_idx or 0) + 1
    offset = 0
    for candidate_offset in range(0, 10):
        idx = first_printed_page - 1 + candidate_offset
        if idx < min_idx or idx >= len(doc):
            continue
        if target and target in _normalize(doc[idx].get_text("text")[:400]):
            offset = candidate_offset
            break

    resolved = sorted(
        ((title, printed_page - 1 + offset) for title, printed_page in entries),
        key=lambda entry: entry[1],
    )
    for title, start in resolved:
        if not 0 <= start < len(doc):
            raise ValueError(f"Contents entry {title!r} resolves outside the PDF (page {start + 1}).")

    # Short sections sharing a physical page remain in the same chapter.
    merged: List[Tuple[str, int]] = []
    for title, start in resolved:
        if merged and merged[-1][1] == start:
            merged[-1] = (f"{merged[-1][0]} / {title}", start)
        else:
            merged.append((title, start))

    chapters: List[Tuple[str, int, int]] = []
    for i, (title, start) in enumerate(merged):
        end = merged[i + 1][1] - 1 if i + 1 < len(merged) else len(doc) - 1
        chapters.append((title, start, max(end, start)))
    return chapters


class IngestionEngine:
    """PDF ingestion engine that splits a document into per-chapter Markdown files."""

    def __init__(
        self,
        output_dir: str = "content",
        assets_dir: str = "content/assets",
        course_name: Optional[str] = None,
        default_domain: Optional[str] = None,
        dpi: int = 150,
    ):
        self.output_dir = Path(output_dir).resolve()
        self.assets_dir = Path(assets_dir).resolve()
        self.course_name = course_name or "General"
        self.default_domain = default_domain or "General"
        if dpi <= 0:
            raise ValueError("DPI must be positive.")
        self.dpi = dpi
        self.formatter = MarkdownArtifactFormatter(
            course_name=self.course_name,
            default_domain=self.default_domain,
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def ingest_pdf(self, pdf_path: str | Path) -> List[Tuple[Path, Dict[str, int]]]:
        """Write one Markdown file per chapter. Errors propagate to the CLI."""
        pdf_file = Path(pdf_path)
        if not pdf_file.is_file():
            raise FileNotFoundError(f"PDF file not found: {pdf_file}")

        doc_slug = _document_slug(pdf_file)
        doc_assets_dir = self.assets_dir / doc_slug
        doc_output_dir = self.output_dir / doc_slug

        with pymupdf.open(str(pdf_file)) as doc:
            if not doc.is_pdf:
                raise ValueError(f"Not a PDF document: {pdf_file}")
            if doc.needs_pass:
                raise ValueError("Password-protected PDFs must be unlocked before ingestion.")
            if not len(doc):
                raise ValueError("PDF document has no pages.")
            chapters = _extract_chapters(doc)
            doc_assets_dir.mkdir(parents=True, exist_ok=True)
            doc_output_dir.mkdir(parents=True, exist_ok=True)
            results: List[Tuple[Path, Dict[str, int]]] = []
            for chapter_index, (chapter_title, start_idx, end_idx) in enumerate(chapters, start=1):
                is_exercise_chapter = bool(_EXERCISE_PATTERN.search(chapter_title))
                body, stats = self._render_chapter_pages(
                    doc, start_idx, end_idx, doc_assets_dir, doc_slug, is_exercise_chapter
                )
                frontmatter = self.formatter.format_frontmatter(
                    source_name=pdf_file.name,
                    title=chapter_title,
                    domains=[self.default_domain],
                    concepts=[],
                    stats=stats,
                    chapter_index=chapter_index,
                    chapter_count=len(chapters),
                )
                chapter_slug = _slugify(chapter_title) or f"chapter-{chapter_index}"
                output_file = doc_output_dir / f"{chapter_index:02d}-{chapter_slug}.md"
                output_file.write_text(frontmatter + body, encoding="utf-8")
                results.append((output_file, stats))
        return results

    def _render_chapter_pages(
        self,
        doc: pymupdf.Document,
        start_idx: int,
        end_idx: int,
        doc_assets_dir: Path,
        doc_slug: str,
        is_exercise_chapter: bool,
    ) -> Tuple[str, Dict[str, int]]:
        """Render a page range, embedding formulas/diagrams/exercises as plain photos."""
        stats = {"exercises": 0, "diagrams": 0, "images": 0, "pages": end_idx - start_idx + 1}
        page_blocks: List[str] = []
        for page_idx in range(start_idx, end_idx + 1):
            page = doc[page_idx]
            page_num = page_idx + 1
            raw_text = page.get_text("text").strip()
            is_exercise_page = is_exercise_chapter or bool(_EXERCISE_PATTERN.search(raw_text))
            lines = [f"<!-- Page {page_num} -->"]
            if is_exercise_page:
                stats["exercises"] += 1
                image_path = self._save_page_photo(page, doc_assets_dir, doc_slug, page_num, "exercise")
                lines.append(self.formatter.format_image(f"Exercise - Page {page_num}", image_path))
            else:
                prose_blocks, dropped_rects = _extract_prose(page)
                drawing_rects = [d["rect"] for d in page.get_drawings()]
                regions = _cluster_rects(drawing_rects + dropped_rects)
                # Preserve the source engine's vertical interleaving of prose and photos.
                positioned: List[Tuple[float, str]] = list(prose_blocks)
                for region_idx, rect in enumerate(regions, start=1):
                    if not (rect & page.rect).is_empty:
                        image_path = self._save_region_photo(
                            page, rect, doc_assets_dir, doc_slug, page_num, region_idx
                        )
                        positioned.append(
                            (rect.y0, self.formatter.format_image(f"Diagram / Formula - Page {page_num}", image_path))
                        )
                        stats["diagrams"] += 1
                positioned.sort(key=lambda item: item[0])
                lines.extend(text for _, text in positioned)
                for img_idx, img in enumerate(page.get_images(), start=1):
                    image_path = self._save_embedded_image(
                        doc, page_idx, img, doc_assets_dir, doc_slug, page_num, img_idx
                    )
                    lines.append(self.formatter.format_image(f"Figure - Page {page_num}", image_path))
                    stats["images"] += 1
            page_blocks.append("\n\n".join(lines))
        return "\n\n---\n\n".join(page_blocks), stats

    def _asset_link(self, asset: Path, doc_slug: str) -> str:
        """Link from the chapter directory, including custom or cross-volume asset roots."""
        asset = asset.resolve()
        try:
            relative = os.path.relpath(asset, self.output_dir / doc_slug)
        except ValueError:
            # Windows cannot express a relative path across drive letters.
            return asset.as_uri()
        return quote(Path(relative).as_posix(), safe="/")

    def _save_region_photo(
        self,
        page: pymupdf.Page,
        rect: pymupdf.Rect,
        doc_assets_dir: Path,
        doc_slug: str,
        page_num: int,
        region_idx: int,
    ) -> str:
        """Crop a single diagram/formula region and save it as its own photo."""
        padded = pymupdf.Rect(rect.x0 - 6, rect.y0 - 6, rect.x1 + 6, rect.y1 + 6) & page.rect
        image_file = doc_assets_dir / f"page-{page_num}-fig-{region_idx}.png"
        page.get_pixmap(clip=padded, dpi=self.dpi).save(str(image_file))
        return self._asset_link(image_file, doc_slug)

    def _save_page_photo(
        self,
        page: pymupdf.Page,
        doc_assets_dir: Path,
        doc_slug: str,
        page_num: int,
        kind: str,
    ) -> str:
        """Render the full page as a photo and save it to the assets directory."""
        image_file = doc_assets_dir / f"page-{page_num}-{kind}.png"
        page.get_pixmap(dpi=self.dpi).save(str(image_file))
        return self._asset_link(image_file, doc_slug)

    def _save_embedded_image(
        self,
        doc: pymupdf.Document,
        page_idx: int,
        img: tuple,
        doc_assets_dir: Path,
        doc_slug: str,
        page_num: int,
        img_idx: int,
    ) -> str:
        """Extract and save a raster image already embedded in the PDF page."""
        base_image = doc.extract_image(img[0])
        if not base_image:
            raise ValueError(f"Cannot extract image {img_idx} on page {page_num}.")
        image_file = doc_assets_dir / f"page-{page_num}-img-{img_idx}.{base_image['ext']}"
        image_file.write_bytes(base_image["image"])
        return self._asset_link(image_file, doc_slug)
