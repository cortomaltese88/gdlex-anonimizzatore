from gdlex_anonimizzatore.core.anonymize import apply_replacements
from gdlex_anonimizzatore.core.models import EntityType, Settings
from gdlex_anonimizzatore.core.recognizers import detect_entities


def _societa_findings(text: str, settings: Settings):
    return [f for f in detect_entities(text, settings) if f.entity_type == EntityType.SOCIETA]


def test_societa_mapping_is_session_wide_across_multiple_files() -> None:
    settings = Settings()

    f_a = _societa_findings("Accordo con Eni S.p.A.", settings)
    f_b = _societa_findings("Verbale: Eni S.p.A. e Enel S.p.A.", settings)

    assert f_a[0].replacement == "Alfa"
    assert f_b[0].replacement == "Alfa"
    assert f_b[1].replacement == "Beta"


def test_reset_clears_session_mapping_restart_from_alfa() -> None:
    settings = Settings()
    _societa_findings("Eni S.p.A. e Enel S.p.A.", settings)
    assert settings.societa_session_mapping

    settings.societa_session_mapping.clear()  # same reset effect required by app reset

    f_new = _societa_findings("Enel S.p.A.", settings)
    assert f_new[0].replacement == "Alfa"


def test_email_cf_piva_regression_still_detected_and_replaced() -> None:
    settings = Settings()
    text = "mail foo@example.com CF RSSMRA85M01H501U PIVA 12345678901"
    findings = detect_entities(text, settings)
    out = apply_replacements(text, findings)

    assert "[EMAIL]" in out
    assert "[CF]" in out
    assert "[PIVA]" in out


def test_institutional_terms_not_anonymized_as_societa() -> None:
    settings = Settings()
    findings = _societa_findings("Il Tribunale di Milano emette decreto.", settings)
    assert findings == []
