from pathlib import Path

from gdlex_anonimizzatore.core.models import FileJob, Settings
from gdlex_anonimizzatore.core.report import generate_report


def test_report_includes_session_societa_mapping(tmp_path: Path) -> None:
    settings = Settings()
    settings.societa_session_mapping = {"eni spa": "Alfa", "acme srl": "Beta"}
    job = FileJob(input_path=tmp_path / "a.txt")
    report_path = generate_report([job], settings, tmp_path)
    text = report_path.read_text(encoding="utf-8")
    assert "Mapping SOCIETA sessione:" in text
    assert "- eni spa -> Alfa" in text
    assert "- acme srl -> Beta" in text
