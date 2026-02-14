from __future__ import annotations

from datetime import datetime
from pathlib import Path

from gdlex_anonimizzatore.core.models import FileJob, Settings


def generate_report(jobs: list[FileJob], settings: Settings, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination / f"gdlex_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    lines: list[str] = [
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
