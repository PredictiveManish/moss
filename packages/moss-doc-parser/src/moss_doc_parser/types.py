"""Data types for Moss document parser."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class MossDocument:
    """Represents a document ready for ingestion into Moss."""

    id: str
    text: str
    metadata: Dict[str, Any]


@dataclass
class ParseResult:
    """Result of parsing a file."""

    documents: List[MossDocument]
    source_path: str
    parse_time_ms: float
