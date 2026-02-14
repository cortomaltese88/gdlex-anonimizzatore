from gdlex_anonimizzatore.core.models import EntityType, Settings
from gdlex_anonimizzatore.core.recognizers import detect_entities


def test_detect_entities_txt_patterns() -> None:
    text = "Contatti: foo.bar+1@example.com CF RSSMRA85M01H501U PIVA 12345678901"
    findings = detect_entities(text, Settings())
    types = {f.entity_type for f in findings}
    assert EntityType.EMAIL in types
    assert EntityType.CODICE_FISCALE in types
    assert EntityType.PARTITA_IVA in types


def test_session_whitelist_skips_value() -> None:
    settings = Settings(session_whitelist={"foo@example.com"})
    findings = detect_entities("foo@example.com", settings)
    assert findings == []


def test_societa_mapping_is_coherent_per_document() -> None:
    text = "Eni S.p.A. e ENI S.P.A. hanno un accordo con Acme Srl."
    findings = [f for f in detect_entities(text, Settings()) if f.entity_type == EntityType.SOCIETA]

    assert len(findings) == 3
    assert findings[0].replacement == "Alfa"
    assert findings[1].replacement == "Alfa"
    assert findings[2].replacement == "Beta"


def test_societa_ignores_institutional_entities() -> None:
    text = "Agenzia delle Entrate S.p.A. e Comune Energia Srl"
    findings = [f for f in detect_entities(text, Settings()) if f.entity_type == EntityType.SOCIETA]
    assert findings == []


def test_societa_placeholder_avoids_double_societa() -> None:
    text = "La società Eni S.p.A. ha deliberato."
    findings = [f for f in detect_entities(text, Settings()) if f.entity_type == EntityType.SOCIETA]
    assert findings
    replaced = text.replace(findings[0].value, findings[0].replacement)
    assert "società società" not in replaced
    assert "La società Alfa" in replaced


def test_societa_mapping_persists_across_files_in_session() -> None:
    settings = Settings()
    f1 = [f for f in detect_entities("Eni S.p.A.", settings) if f.entity_type == EntityType.SOCIETA]
    f2 = [f for f in detect_entities("Acme Srl", settings) if f.entity_type == EntityType.SOCIETA]
    f3 = [f for f in detect_entities("ENI S.P.A.", settings) if f.entity_type == EntityType.SOCIETA]

    assert f1[0].replacement == "Alfa"
    assert f2[0].replacement == "Beta"
    assert f3[0].replacement == "Alfa"
