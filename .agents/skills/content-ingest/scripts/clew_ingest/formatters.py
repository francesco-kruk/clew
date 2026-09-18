"""Markdown frontmatter and plain image embeds; originally authored by Alexandra Pletea."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

import yaml


class MarkdownArtifactFormatter:
    """Format extraction artifacts. Formulas/exercises are photos, not transcriptions."""

    def __init__(self, course_name: Optional[str] = None, default_domain: Optional[str] = None):
        self.course_name = course_name or "General"
        self.default_domain = default_domain or "General"

    def format_frontmatter(
        self,
        source_name: str,
        title: str,
        domains: Optional[List[str]] = None,
        concepts: Optional[List[str]] = None,
        stats: Optional[Dict[str, int]] = None,
        chapter_index: Optional[int] = None,
        chapter_count: Optional[int] = None,
    ) -> str:
        """Generate legacy extraction metadata, not a validated course contract."""
        frontmatter_dict: Dict[str, Any] = {
            "type": "course-content",
            "title": title,
            "source": source_name,
            "ingested_at": str(date.today()),
            "course": self.course_name,
            "domains": domains or [self.default_domain],
            "concepts": concepts or [],
            "artifacts": stats or {"exercises": 0, "images": 0},
        }
        if chapter_index is not None:
            frontmatter_dict["chapter_index"] = chapter_index
        if chapter_count is not None:
            frontmatter_dict["chapter_count"] = chapter_count
        yaml_content = yaml.safe_dump(frontmatter_dict, sort_keys=False, default_flow_style=False)
        return f"---\n{yaml_content}---\n\n"

    def format_image(self, caption: str, image_path: str) -> str:
        """Embed a page/region photo without attempting to transcribe its content."""
        return f"![{caption}]({image_path})\n"
