from __future__ import annotations


def file_actions_enabled(job_count: int, busy: bool) -> bool:
    return job_count > 0 and not busy


def has_resettable_state(job_count: int, log_has_text: bool, progress_value: int, status_text: str) -> bool:
    return job_count > 0 or log_has_text or progress_value > 0 or status_text != "Pronto"
