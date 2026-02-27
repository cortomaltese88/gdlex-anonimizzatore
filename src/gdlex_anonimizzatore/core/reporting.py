from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from gdlex_anonimizzatore.core.models import FileJob, FileStatus


@dataclass
class ProcessingResult:
    input_path: str
    output_path: str | None
    file_type: Literal["TXT", "DOCX"]
    status: Literal["OK", "WARN", "ERR"]
    counts_found: dict[str, int]
    counts_replaced: dict[str, int]
    warnings: list[str]
    errors: list[str]
    docx_cross_run_skipped: int = 0


def build_result(
    job: FileJob,
    docx_skipped: int = 0,
    extra_warnings: list[str] | None = None,
    extra_errors: list[str] | None = None,
) -> ProcessingResult:
    counts_found: dict[str, int] = {}
    counts_replaced: dict[str, int] = {}
    for f in job.findings:
        key = f.entity_type.value
        counts_found[key] = counts_found.get(key, 0) + 1
        if f.anonymize:
            counts_replaced[key] = counts_replaced.get(key, 0) + 1

    warnings: list[str] = list(extra_warnings or [])
    errors: list[str] = list(extra_errors or [])

    if job.status == FileStatus.ERROR:
        status: Literal["OK", "WARN", "ERR"] = "ERR"
        if job.error:
            errors.append(job.error)
    elif docx_skipped > 0 or warnings or (job.error and job.output_path is not None):
        status = "WARN"
        if job.error and job.output_path is not None:
            warnings.append(job.error)
    else:
        status = "OK"

    return ProcessingResult(
        input_path=str(job.input_path),
        output_path=str(job.output_path) if job.output_path is not None else None,
        file_type=job.file_type,  # type: ignore[arg-type]
        status=status,
        counts_found=counts_found,
        counts_replaced=counts_replaced,
        warnings=warnings,
        errors=errors,
        docx_cross_run_skipped=docx_skipped,
    )
