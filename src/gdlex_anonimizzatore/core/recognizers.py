from __future__ import annotations

import re
from typing import Iterable

from gdlex_anonimizzatore.core.models import EntityFinding, EntityType, Settings

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
CF_RE = re.compile(r"\b[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]\b", re.IGNORECASE)
PIVA_RE = re.compile(r"\b\d{11}\b")
SOCIETA_RE = re.compile(
    r"\b"
    r"(?:[A-ZÀ-Ý][A-Za-zÀ-ÖØ-öø-ÿ0-9'’&-]*"
    r"(?:\s+(?:[A-ZÀ-Ý][A-Za-zÀ-ÖØ-öø-ÿ0-9'’&-]*|&)){0,5})"
    r"\s+"
    r"(?i:(?:S\.?\s*P\.?\s*A\.?)|(?:S\.?\s*R\.?\s*L\.?)|Spa|Srl)"
    r"(?=\W|$)",
)

SOCIETA_LABELS = [
    "Alfa",
    "Beta",
    "Gamma",
    "Delta",
    "Epsilon",
    "Zeta",
    "Eta",
    "Theta",
    "Iota",
    "Kappa",
    "Lambda",
    "Mu",
    "Nu",
    "Xi",
    "Omicron",
    "Pi",
    "Rho",
    "Sigma",
    "Tau",
    "Upsilon",
    "Phi",
    "Chi",
    "Psi",
    "Omega",
]

INSTITUTION_DENYLIST = [
    "tribunale",
    "corte",
    "procura",
    "comune",
    "regione",
    "prefettura",
    "ministero",
    "inps",
    "inail",
    "agenzia delle entrate",
    "questura",
    "polizia",
    "carabinieri",
    "guardia di finanza",
    "asl",
    "ulss",
]

REPLACEMENT_BY_TYPE: dict[EntityType, str] = {
    EntityType.EMAIL: "[EMAIL]",
    EntityType.CODICE_FISCALE: "[CF]",
    EntityType.PARTITA_IVA: "[PIVA]",
    EntityType.SOCIETA: "Alfa",
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


def _normalize_societa(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.replace(".", " ")).strip().casefold()
    return normalized


def _is_institutional_company(value: str) -> bool:
    lowered = value.casefold()
    return any(term in lowered for term in INSTITUTION_DENYLIST)

def _is_institutional_context(text: str, start: int, end: int) -> bool:
    context = text[max(0, start - 40) : end].casefold()
    return any(term in context for term in INSTITUTION_DENYLIST)


def _societa_placeholder(index: int) -> str:
    if index < len(SOCIETA_LABELS):
        return SOCIETA_LABELS[index]
    return str(index + 1)


def _detect_societa(text: str, settings: Settings) -> list[EntityFinding]:
    findings: list[EntityFinding] = []
    mapping: dict[str, str] = {}
    for match in SOCIETA_RE.finditer(text):
        value = match.group(0).strip()
        if (
            _is_whitelisted(value, settings)
            or _is_institutional_company(value)
            or _is_institutional_context(text, match.start(), match.end())
        ):
            continue
        key = _normalize_societa(value)
        if key not in mapping:
            mapping[key] = _societa_placeholder(len(mapping))
        findings.append(
            EntityFinding(
                value=value,
                entity_type=EntityType.SOCIETA,
                start=match.start(),
                end=match.end(),
                replacement=mapping[key],
            )
        )
    return findings


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

    for finding in _detect_societa(text, settings):
        key = (finding.start, finding.end, finding.entity_type)
        if key in seen:
            continue
        findings.append(finding)
        seen.add(key)

    findings.sort(key=lambda item: item.start)
    return findings
