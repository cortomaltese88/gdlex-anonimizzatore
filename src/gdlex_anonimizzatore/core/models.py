from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Protocol

import re





def get_app_version() -> str:
    try:
        return version("gdlex-anonimizzatore")
    except PackageNotFoundError:
        try:
            pyproject = Path(__file__).resolve().parents[3] / "pyproject.toml"
            content = pyproject.read_text(encoding="utf-8")
            match = re.search(r'^version\s*=\s*"([^"]+)"', content, flags=re.MULTILINE)
            return match.group(1) if match else "0.0.0"
        except Exception:  # noqa: BLE001
            return "0.0.0"


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
    PERSONA = "PERSONA"
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
    societa_session_mapping: dict[str, str] = field(default_factory=dict)
    persona_session_mapping: dict[str, str] = field(default_factory=dict)
    version: str = field(default_factory=get_app_version)


class DocumentHandler(Protocol):
    """Extension point for future file handlers (DOCX/PDF/EML/MSG)."""

    def can_handle(self, path: Path) -> bool:
        ...

    def read_text(self, path: Path) -> str:
        ...

    def write_text(self, path: Path, content: str) -> None:
        ...
