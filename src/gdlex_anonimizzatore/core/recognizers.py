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

UPPER_SURNAME = r"[A-ZÀ-ÖØ-Ý'’]{2,30}"
TITLE_NAME = r"[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ'’]{1,29}"
PERSONA_A_RE = re.compile(rf"\b(?P<surname>{UPPER_SURNAME})\s+(?P<name>{TITLE_NAME})\b")
PERSONA_B_RE = re.compile(rf"\b(?P<name>{TITLE_NAME})\s+(?P<surname>{UPPER_SURNAME})\b")
PERSONA_C_RE = re.compile(
    rf"\b(?P<title>Sig\.|Sig\.ra|Avv\.|Dott\.|Dott\.ssa)\s+(?P<name1>{TITLE_NAME})\s+(?P<name2>{TITLE_NAME})\b"
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

PERSONA_MALE = ["Tizio", "Caio", "Sempronio", "Mevio", "Filano", "Sicuro", "Beltrame", "Martino", "Nerio", "Pippo"]
PERSONA_FEMALE = [
    "Tizia",
    "Caia",
    "Sempronia",
    "Mevia",
    "Filana",
    "Sicura",
    "Beltramia",
    "Martina",
    "Neria",
    "Pippa",
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
ROLE_DENYLIST = [
    "giudice",
    "cancelleria",
    "pubblico ministero",
    "presidente",
    "dirigente",
    "responsabile",
]

FEMALE_TITLES = {"sig.ra", "dott.ssa"}
MALE_TITLES = {"sig.", "avv.", "dott."}

REPLACEMENT_BY_TYPE: dict[EntityType, str] = {
    EntityType.EMAIL: "[EMAIL]",
    EntityType.CODICE_FISCALE: "[CF]",
    EntityType.PARTITA_IVA: "[PIVA]",
    EntityType.SOCIETA: "Alfa",
    EntityType.PERSONA: "Tizio",
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
    return re.sub(r"\s+", " ", value.replace(".", " ")).strip().casefold()


def _normalize_person_key(name: str, surname: str) -> str:
    return f"{name.casefold()}|{surname.casefold()}"


def _contains_denied_term(value: str) -> bool:
    lowered = value.casefold()
    return any(term in lowered for term in [*INSTITUTION_DENYLIST, *ROLE_DENYLIST])


def _is_institutional_context(text: str, start: int, end: int) -> bool:
    context = text[max(0, start - 40) : min(len(text), end + 20)].casefold()
    return any(term in context for term in [*INSTITUTION_DENYLIST, *ROLE_DENYLIST])


def _societa_placeholder(index: int) -> str:
    if index < len(SOCIETA_LABELS):
        return SOCIETA_LABELS[index]
    return str(index + 1)


def _next_persona_placeholder(settings: Settings, female: bool) -> str:
    mapping_values = set(settings.persona_session_mapping.values())
    labels = PERSONA_FEMALE if female else PERSONA_MALE
    for label in labels:
        if label not in mapping_values:
            return label
    return labels[-1]


def _detect_societa(text: str, settings: Settings) -> list[EntityFinding]:
    findings: list[EntityFinding] = []
    mapping = settings.societa_session_mapping
    for match in SOCIETA_RE.finditer(text):
        value = match.group(0).strip()
        if (
            _is_whitelisted(value, settings)
            or _contains_denied_term(value)
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


def _build_persona_finding(
    *,
    text: str,
    settings: Settings,
    start: int,
    end: int,
    name: str,
    surname: str,
    female: bool,
) -> EntityFinding | None:
    value = text[start:end]
    if _is_whitelisted(value, settings) or _contains_denied_term(value) or _is_institutional_context(text, start, end):
        return None

    key = _normalize_person_key(name, surname)
    mapping = settings.persona_session_mapping
    if key not in mapping:
        # Conservative rule: if no explicit female title, default to male placeholder list.
        mapping[key] = _next_persona_placeholder(settings, female=female)
    return EntityFinding(
        value=value,
        entity_type=EntityType.PERSONA,
        start=start,
        end=end,
        replacement=mapping[key],
    )


def _detect_persona(text: str, settings: Settings) -> list[EntityFinding]:
    findings: list[EntityFinding] = []

    for match in PERSONA_A_RE.finditer(text):
        finding = _build_persona_finding(
            text=text,
            settings=settings,
            start=match.start(),
            end=match.end(),
            name=match.group("name"),
            surname=match.group("surname"),
            female=False,
        )
        if finding:
            findings.append(finding)

    for match in PERSONA_B_RE.finditer(text):
        finding = _build_persona_finding(
            text=text,
            settings=settings,
            start=match.start(),
            end=match.end(),
            name=match.group("name"),
            surname=match.group("surname"),
            female=False,
        )
        if finding:
            findings.append(finding)

    for match in PERSONA_C_RE.finditer(text):
        title = match.group("title").casefold()
        female = title in FEMALE_TITLES
        finding = _build_persona_finding(
            text=text,
            settings=settings,
            start=match.start(),
            end=match.end(),
            name=match.group("name1"),
            surname=match.group("name2"),
            female=female,
        )
        if finding:
            findings.append(finding)

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

    for finder in (_detect_societa, _detect_persona):
        for finding in finder(text, settings):
            key = (finding.start, finding.end, finding.entity_type)
            if key in seen:
                continue
            findings.append(finding)
            seen.add(key)

    findings.sort(key=lambda item: item.start)
    return findings
