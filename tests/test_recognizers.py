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
