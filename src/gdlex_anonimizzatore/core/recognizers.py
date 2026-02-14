from __future__ import annotations

import re
from typing import Iterable

from gdlex_anonimizzatore.core.models import EntityFinding, EntityType, Settings

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
CF_RE = re.compile(r"\b[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]\b", re.IGNORECASE)
PIVA_RE = re.compile(r"\b\d{11}\b")

REPLACEMENT_BY_TYPE: dict[EntityType, str] = {
    EntityType.EMAIL: "[EMAIL]",
    EntityType.CODICE_FISCALE: "[CF]",
    EntityType.PARTITA_IVA: "[PIVA]",
    EntityType.MANUALE: "[MASK]",
}


def _is_whitelisted(value: str, settings: Settings) -> bool:
    if value in settings.session_whitelist:
        return True
    return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in settings.global_whitelist)


def _find_with_pattern(text: str, regex: re.Pattern[str], entity_type: EntityType) -> Iterable[EntityFinding]:
    for match in regex.finditer(text):
        value = match.group(0)
        yield EntityFinding(
            value=value,
            entity_type=entity_type,
            start=match.start(),
            end=match.end(),
            replacement=REPLACEMENT_BY_TYPE[entity_type],
        )


def detect_entities(text: str, settings: Settings) -> list[EntityFinding]:
    findings: list[EntityFinding] = []
    seen: set[tuple[int, int, EntityType]] = set()
    for regex, entity_type in (
        (EMAIL_RE, EntityType.EMAIL),
        (CF_RE, EntityType.CODICE_FISCALE),
        (PIVA_RE, EntityType.PARTITA_IVA),
    ):
        for finding in _find_with_pattern(text, regex, entity_type):
            key = (finding.start, finding.end, finding.entity_type)
            if key in seen or _is_whitelisted(finding.value, settings):
                continue
            findings.append(finding)
            seen.add(key)
    findings.sort(key=lambda item: item.start)
    return findings
