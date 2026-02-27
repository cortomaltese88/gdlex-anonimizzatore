from __future__ import annotations

from pathlib import Path

import pytest

from gdlex_anonimizzatore.core.models import (
    EntityFinding,
    EntityType,
    FileJob,
    FileStatus,
    Settings,
)
from gdlex_anonimizzatore.core.report import generate_report
from gdlex_anonimizzatore.core.reporting import ProcessingResult, build_result


def _make_finding(entity_type: EntityType, anonymize: bool) -> EntityFinding:
    return EntityFinding(
        value="test",
        entity_type=entity_type,
        start=0,
        end=4,
        replacement="[MASK]",
        anonymize=anonymize,
    )


def test_txt_ok(tmp_path: Path) -> None:
    """Caso a: TXT OK — counts and status."""
    job = FileJob(
        input_path=tmp_path / "doc.txt",
        file_type="TXT",
        status=FileStatus.PROCESSED,
        output_path=tmp_path / "out.txt",
        findings=[
            _make_finding(EntityType.EMAIL, anonymize=True),
            _make_finding(EntityType.CODICE_FISCALE, anonymize=False),
        ],
    )
    result = build_result(job)
    assert result.status == "OK"
    assert result.counts_found["EMAIL"] == 1
    assert result.counts_found["CODICE_FISCALE"] == 1
    assert result.counts_replaced["EMAIL"] == 1
    assert result.counts_replaced.get("CODICE_FISCALE", 0) == 0


def test_docx_warn_cross_run(tmp_path: Path) -> None:
    """Caso b: DOCX WARN cross-run skipped."""
    job = FileJob(
        input_path=tmp_path / "doc.docx",
        file_type="DOCX",
        status=FileStatus.PROCESSED,
        output_path=tmp_path / "out.docx",
    )
    result = build_result(job, docx_skipped=2)
    assert result.status == "WARN"
    assert result.docx_cross_run_skipped == 2


def test_err_missing_file(tmp_path: Path) -> None:
    """Caso c: ERR — file inesistente."""
    job = FileJob(
        input_path=tmp_path / "missing.txt",
        file_type="TXT",
        status=FileStatus.ERROR,
        output_path=None,
        error="file non trovato",
    )
    result = build_result(job)
    assert result.status == "ERR"
    assert result.output_path is None


def test_report_with_results(tmp_path: Path) -> None:
    """Caso d: generate_report con results include la sezione RIEPILOGO PER FILE."""
    result_ok = ProcessingResult(
        input_path=str(tmp_path / "ok.txt"),
        output_path=str(tmp_path / "ok_out.txt"),
        file_type="TXT",
        status="OK",
        counts_found={"EMAIL": 1},
        counts_replaced={"EMAIL": 1},
        warnings=[],
        errors=[],
    )
    result_err = ProcessingResult(
        input_path=str(tmp_path / "err.txt"),
        output_path=None,
        file_type="TXT",
        status="ERR",
        counts_found={},
        counts_replaced={},
        warnings=[],
        errors=["file non trovato"],
    )
    settings = Settings()
    job = FileJob(input_path=tmp_path / "ok.txt")
    report_path = generate_report([job], settings, tmp_path, results=[result_ok, result_err])
    text = report_path.read_text(encoding="utf-8")
    assert "RIEPILOGO PER FILE" in text
    assert "→ OK" in text
    assert "→ ERR" in text
