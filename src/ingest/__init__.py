"""
Clew PDF Ingestion Engine.
Converts PDFs into structured, modifiable Markdown artifacts (exercises, charts, notes).
"""

from .engine import IngestionEngine
from .formatters import MarkdownArtifactFormatter

__all__ = ["IngestionEngine", "MarkdownArtifactFormatter"]
