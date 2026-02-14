from gdlex_anonimizzatore.core.anonymize import apply_replacements
from gdlex_anonimizzatore.core.models import EntityType, Settings
from gdlex_anonimizzatore.core.recognizers import detect_entities


def _persona_findings(text: str, settings: Settings):
    return [f for f in detect_entities(text, settings) if f.entity_type == EntityType.PERSONA]


def test_persona_detect_and_replace_supported_patterns() -> None:
    settings = Settings()
    text = "ROSSI Mario incontra Mario ROSSI"
    findings = _persona_findings(text, settings)

    assert len(findings) == 2
    out = apply_replacements(text, findings)
    assert "Tizio" in out
    assert "ROSSI Mario" not in out
    assert "Mario ROSSI" not in out


def test_persona_session_coherence_across_files() -> None:
    settings = Settings()
    f1 = _persona_findings("File A: ROSSI Mario", settings)
    f2 = _persona_findings("File B: Mario ROSSI", settings)

    assert f1[0].replacement == "Tizio"
    assert f2[0].replacement == "Tizio"


def test_persona_exclusion_for_institutional_terms() -> None:
    settings = Settings()
    text = "Tribunale di Milano e Corte di Appello"
    assert _persona_findings(text, settings) == []


def test_persona_reset_mapping_restarts_from_first_placeholder() -> None:
    settings = Settings()
    _persona_findings("ROSSI Mario", settings)
    assert settings.persona_session_mapping

    settings.persona_session_mapping.clear()

    findings = _persona_findings("BIANCHI Luca", settings)
    assert findings[0].replacement == "Tizio"


def test_persona_title_case_with_explicit_title_uses_gender() -> None:
    settings = Settings()
    findings_f = _persona_findings("Sig.ra Maria Rossi", settings)
    findings_m = _persona_findings("Dott. Paolo Verdi", settings)

    assert findings_f[0].replacement == "Tizia"
    assert findings_m[0].replacement == "Tizio"
