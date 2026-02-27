from __future__ import annotations

from datetime import datetime
from pathlib import Path

from gdlex_anonimizzatore.core.models import FileJob, Settings
from gdlex_anonimizzatore.core.reporting import ProcessingResult

_ENTITY_ORDER = ["EMAIL", "CODICE_FISCALE", "PARTITA_IVA", "SOCIETA", "PERSONA"]


def _format_counts(counts: dict[str, int]) -> str:
    return "  ".join(f"{e}={counts.get(e, 0)}" for e in _ENTITY_ORDER)


def _summary_lines(results: list[ProcessingResult]) -> list[str]:
    sep_double = "═══════════════════════════════"
    sep_single = "───────────────────────────────"
    lines: list[str] = [sep_double, "RIEPILOGO PER FILE", sep_double]
    for r in results:
        basename = Path(r.input_path).name
        lines.append(f"{basename} [{r.file_type}] → {r.status}")
        lines.append(f"  trovate:    {_format_counts(r.counts_found)}")
        lines.append(f"  sostituite: {_format_counts(r.counts_replaced)}")
        if r.file_type == "DOCX" and r.docx_cross_run_skipped > 0:
            lines.append(f"  docx cross-run skipped: {r.docx_cross_run_skipped}")
        for w in r.warnings[:3]:
            lines.append(f"  warning: {w}")
        for e in r.errors[:3]:
            lines.append(f"  errore:  {e}")
        lines.append(sep_single)
    lines.append(sep_double)
    return lines


def generate_report(
    jobs: list[FileJob],
    settings: Settings,
    destination: Path,
    results: list[ProcessingResult] | None = None,
) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination / f"gdlex_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    lines: list[str] = []
    if results:
        lines.extend(_summary_lines(results))
        lines.append("")
    lines += [
        f"GDLEX Anonimizzatore v{settings.version}",
        f"Timestamp: {datetime.now().isoformat()}",
        f"Output folder: {destination}",
        f"Whitelist sessione: {sorted(settings.session_whitelist)}",
        "Mapping SOCIETA sessione:",
    ]
    if settings.societa_session_mapping:
        for company_key, placeholder in settings.societa_session_mapping.items():
            lines.append(f"- {company_key} -> {placeholder}")
    else:
        lines.append("- Nessun mapping SOCIETA")
    lines.append("Mapping PERSONA sessione:")
    if settings.persona_session_mapping:
        for person_key, placeholder in settings.persona_session_mapping.items():
            lines.append(f"- {person_key} -> {placeholder}")
    else:
        lines.append("- Nessun mapping PERSONA")
    lines.append("")
    for job in jobs:
        lines.extend(
            [
                f"File: {job.input_path}",
                f"Stato: {job.status.value}",
                f"Entita trovate: {len(job.findings)}",
                f"Output: {job.output_path or '-'}",
                f"Errore: {job.error or '-'}",
                "Mapping:",
            ]
        )
        if job.findings:
            for f in job.findings:
                lines.append(f"- {f.value} ({f.entity_type.value}) -> {f.replacement} | anonymize={f.anonymize}")
        else:
            lines.append("- Nessuna entita")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
