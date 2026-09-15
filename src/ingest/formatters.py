"""
Markdown and modifiable artifact formatting for Clew content.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any, Dict, List, Optional
import yaml


class MarkdownArtifactFormatter:
    """Formats parsed document elements into modifiable Markdown artifacts."""

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
    ) -> str:
        """Generate YAML frontmatter for the ingested markdown file."""
        frontmatter_dict: Dict[str, Any] = {
            "type": "course-content",
            "title": title,
            "source": source_name,
            "ingested_at": str(date.today()),
            "course": self.course_name,
            "domains": domains or [self.default_domain],
            "concepts": concepts or [],
            "artifacts": stats or {"exercises": 0, "charts": 0, "tables": 0},
        }
        yaml_content = yaml.dump(frontmatter_dict, sort_keys=False, default_flow_style=False)
        return f"---\n{yaml_content}---\n\n"

    def format_exercise(
        self,
        title: str,
        prompt: str,
        solution: Optional[str] = None,
        exercise_id: Optional[str] = None,
    ) -> str:
        """Format an exercise or problem as an editable Obsidian callout."""
        lines = [f"> [!exercise] {title}"]
        for line in prompt.strip().splitlines():
            lines.append(f"> {line}")
        lines.append(">")
        lines.append("> - [ ] **Your Answer / Solution:**")
        lines.append(">   ")
        if solution:
            lines.append(">")
            lines.append("> > [!tip]- Reference Solution / Hint")
            for s_line in solution.strip().splitlines():
                lines.append(f"> > {s_line}")
        lines.append("\n")
        return "\n".join(lines)

    def format_exercise_as_image(
        self,
        title: str,
        image_path: str,
        text_summary: Optional[str] = None,
    ) -> str:
        """Format an exercise section with its visual image crop as an interactive Obsidian callout."""
        lines = [f"> [!exercise] {title}"]
        if text_summary:
            lines.append(f"> *{text_summary[:180]}...*")
            lines.append(">")
        lines.append(f"> ![{title}]({image_path})")
        lines.append(">")
        lines.append("> - [ ] **Your Answer / Solution:**")
        lines.append(">   ")
        lines.append("\n")
        return "\n".join(lines)

    def format_chart(
        self,
        caption: str,
        chart_data: Optional[Dict[str, Any]] = None,
        image_path: Optional[str] = None,
        mermaid_type: str = "xychart-beta",
    ) -> str:
        """Format a graph or chart as an editable Mermaid diagram or data table with image backup."""
        lines = [f"> [!graph] {caption}"]

        # Try to render Mermaid if structured data is provided
        if chart_data and "x_categories" in chart_data and "y_values" in chart_data:
            x_cats = chart_data["x_categories"]
            y_vals = chart_data["y_values"]
            title = chart_data.get("title", caption)
            x_label = chart_data.get("x_label", "Categories")
            y_label = chart_data.get("y_label", "Values")

            lines.append("> ```mermaid")
            lines.append(f"> {mermaid_type}")
            lines.append(f'>   title "{title}"')
            lines.append(f">   x-axis [{', '.join(str(c) for c in x_cats)}]")
            lines.append(f'>   y-axis "{y_label}"')
            lines.append(f">   bar [{', '.join(str(v) for v in y_vals)}]")
            lines.append("> ```")
            lines.append(">")
            lines.append(f"> | {x_label} | {y_label} |")
            lines.append("> | --- | --- |")
            for x, y in zip(x_cats, y_vals):
                lines.append(f"> | {x} | {y} |")
        elif image_path:
            lines.append(f"> ![{caption}]({image_path})")

        lines.append(">")
        lines.append("> *Editable diagram artifact: Modify data points or Mermaid code above to adjust visualization.*")
        lines.append("\n")
        return "\n".join(lines)

    def enhance_markdown_with_artifacts(self, raw_markdown: str) -> str:
        """Post-process raw markdown to detect and wrap exercises, formulas, and callouts."""
        lines = raw_markdown.splitlines()
        output_lines: List[str] = []
        in_exercise = False
        current_exercise_title = ""
        current_exercise_body: List[str] = []

        exercise_pattern = re.compile(
            r"^(#{1,4}\s+)?(Exercise|Problem|Practice\s+Question|Question|Task)\s*(\d+[\.\d*]*)?[:\.\-]?\s*(.*)",
            re.IGNORECASE,
        )

        for line in lines:
            match = exercise_pattern.match(line.strip())
            if match:
                if in_exercise and current_exercise_body:
                    output_lines.append(
                        self.format_exercise(
                            title=current_exercise_title,
                            prompt="\n".join(current_exercise_body),
                        )
                    )
                    current_exercise_body = []

                in_exercise = True
                prefix, ex_type, ex_num, ex_desc = match.groups()
                num_part = f" {ex_num}" if ex_num else ""
                desc_part = f": {ex_desc}" if ex_desc else ""
                current_exercise_title = f"{ex_type}{num_part}{desc_part}".strip()
                continue

            if in_exercise:
                # If a new major heading begins, close the exercise
                if line.startswith("# ") or line.startswith("## ") or line.startswith("---"):
                    output_lines.append(
                        self.format_exercise(
                            title=current_exercise_title,
                            prompt="\n".join(current_exercise_body),
                        )
                    )
                    in_exercise = False
                    current_exercise_body = []
                    output_lines.append(line)
                else:
                    current_exercise_body.append(line)
            else:
                output_lines.append(line)

        if in_exercise and current_exercise_body:
            output_lines.append(
                self.format_exercise(
                    title=current_exercise_title,
                    prompt="\n".join(current_exercise_body),
                )
            )

        return "\n".join(output_lines)
