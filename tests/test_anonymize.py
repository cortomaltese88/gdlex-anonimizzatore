from gdlex_anonimizzatore.core.anonymize import apply_replacements
from gdlex_anonimizzatore.core.models import EntityFinding, EntityType


def test_apply_replacements_reverse_offset_safe() -> None:
    text = "a foo@example.com b RSSMRA85M01H501U c"
    findings = [
        EntityFinding(
            value="foo@example.com",
            entity_type=EntityType.EMAIL,
            start=text.index("foo@example.com"),
            end=text.index("foo@example.com") + len("foo@example.com"),
            replacement="[EMAIL]",
        ),
        EntityFinding(
            value="RSSMRA85M01H501U",
            entity_type=EntityType.CODICE_FISCALE,
            start=text.index("RSSMRA85M01H501U"),
            end=text.index("RSSMRA85M01H501U") + len("RSSMRA85M01H501U"),
            replacement="[CF]",
        ),
    ]

    out = apply_replacements(text, findings)
    assert out == "a [EMAIL] b [CF] c"
