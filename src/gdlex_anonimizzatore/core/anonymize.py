from __future__ import annotations

from gdlex_anonimizzatore.core.models import EntityFinding


def apply_replacements(text: str, findings: list[EntityFinding]) -> str:
    """Apply replacement from right-to-left to preserve offsets."""
    selected = [f for f in findings if f.anonymize]
    selected.sort(key=lambda item: item.start, reverse=True)
    out = text
    for finding in selected:
        if finding.start < 0 or finding.end > len(out) or finding.start >= finding.end:
            continue
        out = out[: finding.start] + finding.replacement + out[finding.end :]
    return out
