"""
Clew's image-first PDF ingestion engine, originally authored by Alexandra Pletea.
See LICENSE and references/provenance.md in the content-ingest skill package.
"""

from .engine import IngestionEngine
from .formatters import MarkdownArtifactFormatter

__all__ = ["IngestionEngine", "MarkdownArtifactFormatter"]
