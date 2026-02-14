from __future__ import annotations

from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from types import SimpleNamespace
from typing import Any

from gdlex_anonimizzatore.core.models import EntityFinding, EntityType


def _app_version() -> str:
    try:
        return version("gdlex-anonimizzatore")
    except PackageNotFoundError:
        return "0.1.0"


def _state_settings(state: Any) -> Any:
    return getattr(state, "settings", state)


def _normalize_mapping_entries(state: Any) -> list[dict[str, Any]]:
    settings = _state_settings(state)
    entries: list[dict[str, Any]] = []

    for original, replacement in sorted(getattr(settings, "societa_session_mapping", {}).items()):
        entries.append(
            {
                "original": str(original),
                "entity_type": EntityType.SOCIETA.value,
                "replacement": str(replacement),
                "anonymize": True,
            }
        )

    for original, replacement in sorted(getattr(settings, "persona_session_mapping", {}).items()):
        entries.append(
            {
                "original": str(original),
                "entity_type": EntityType.PERSONA.value,
                "replacement": str(replacement),
                "anonymize": True,
            }
        )

    jobs = getattr(state, "jobs", [])
    for job in jobs:
        for finding in getattr(job, "findings", []):
            entries.append(
                {
                    "original": str(finding.value),
                    "entity_type": str(finding.entity_type.value),
                    "replacement": str(finding.replacement),
                    "anonymize": bool(finding.anonymize),
                }
            )

    # deterministic unique entries preserving first occurrence
    unique: dict[tuple[str, str, str, bool], dict[str, Any]] = {}
    for item in entries:
        key = (item["original"], item["entity_type"], item["replacement"], item["anonymize"])
        if key not in unique:
            unique[key] = item
    return list(unique.values())


def export_session(state: Any) -> dict[str, Any]:
    settings = _state_settings(state)
    whitelist = sorted(str(x) for x in getattr(settings, "session_whitelist", set()))
    return {
        "app_version": _app_version(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mapping": _normalize_mapping_entries(state),
        "whitelist_session": whitelist,
    }


def import_session(data: dict, state: Any) -> None:
    if not isinstance(data, dict):
        return

    settings = _state_settings(state)

    whitelist = data.get("whitelist_session")
    if isinstance(whitelist, list):
        settings.session_whitelist = {str(item) for item in whitelist if isinstance(item, (str, int, float))}

    mapping = data.get("mapping")
    if not isinstance(mapping, list):
        return

    if hasattr(settings, "societa_session_mapping"):
        settings.societa_session_mapping.clear()
    if hasattr(settings, "persona_session_mapping"):
        settings.persona_session_mapping.clear()

    # exact override map for current findings (if any)
    overrides: dict[tuple[str, str], tuple[str, bool]] = {}

    for entry in mapping:
        if not isinstance(entry, dict):
            continue
        original = entry.get("original")
        entity_type = entry.get("entity_type")
        replacement = entry.get("replacement")
        anonymize = entry.get("anonymize", True)
        if not isinstance(original, str) or not isinstance(entity_type, str) or not isinstance(replacement, str):
            continue
        anonymize_bool = bool(anonymize)

        if entity_type == EntityType.SOCIETA.value and hasattr(settings, "societa_session_mapping"):
            if original.casefold() == original:
                settings.societa_session_mapping[original] = replacement
        elif entity_type == EntityType.PERSONA.value and hasattr(settings, "persona_session_mapping"):
            if "|" in original:
                settings.persona_session_mapping[original] = replacement

        overrides[(entity_type, original)] = (replacement, anonymize_bool)

    jobs = getattr(state, "jobs", [])
    for job in jobs:
        findings = getattr(job, "findings", None)
        if findings is None:
            continue
        for finding in findings:
            key = (finding.entity_type.value, finding.value)
            if key in overrides:
                repl, anon = overrides[key]
                finding.replacement = repl
                finding.anonymize = anon
