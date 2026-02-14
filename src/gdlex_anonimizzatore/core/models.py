from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Protocol


class FileStatus(str, Enum):
    PENDING = "PENDING"
    ANALYZED = "ANALYZED"
    PROCESSED = "PROCESSED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


class EntityType(str, Enum):
    EMAIL = "EMAIL"
    CODICE_FISCALE = "CODICE_FISCALE"
    PARTITA_IVA = "PARTITA_IVA"
    SOCIETA = "SOCIETA"
    MANUALE = "MANUALE"


@dataclass(slots=True)
class EntityFinding:
    value: str
    entity_type: EntityType
    start: int
    end: int
    confidence: float = 0.99
    replacement: str = ""
    anonymize: bool = True
    manual: bool = False


@dataclass(slots=True)
class FileJob:
    input_path: Path
    file_type: str = "TXT"
    status: FileStatus = FileStatus.PENDING
    findings: list[EntityFinding] = field(default_factory=list)
    output_path: Path | None = None
    error: str = ""
    original_text: str = ""


@dataclass(slots=True)
class Settings:
    output_folder: Path | None = None
    global_whitelist: list[str] = field(
        default_factory=lambda: [
            r"Tribunale",
            r"Procura",
            r"Corte",
            r"Giudice",
            r"Cancelleria",
        ]
    )
    session_whitelist: set[str] = field(default_factory=set)
    version: str = "0.1"


class DocumentHandler(Protocol):
    """Extension point for future file handlers (DOCX/PDF/EML/MSG)."""

    def can_handle(self, path: Path) -> bool:
        ...

    def read_text(self, path: Path) -> str:
        ...

    def write_text(self, path: Path, content: str) -> None:
        ...
