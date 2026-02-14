import json
from types import SimpleNamespace

from gdlex_anonimizzatore.core.models import EntityFinding, EntityType, Settings
from gdlex_anonimizzatore.core.session_store import export_session, import_session


def _state_with_data() -> SimpleNamespace:
    settings = Settings()
    settings.societa_session_mapping = {"eni spa": "Alfa"}
    settings.persona_session_mapping = {"mario|rossi": "Tizio"}
    settings.session_whitelist = {"foo@example.com", "Tribunale"}
    jobs = [
        SimpleNamespace(
            findings=[
                EntityFinding(
                    value="ROSSI Mario",
                    entity_type=EntityType.PERSONA,
                    start=0,
                    end=11,
                    replacement="Tizio",
                    anonymize=True,
                )
            ]
        )
    ]
    return SimpleNamespace(settings=settings, jobs=jobs)


def test_session_store_roundtrip() -> None:
    state = _state_with_data()
    exported = export_session(state)
    payload = json.loads(json.dumps(exported))

    target = SimpleNamespace(settings=Settings(), jobs=[])
    import_session(payload, target)

    assert target.settings.societa_session_mapping == {"eni spa": "Alfa"}
    assert target.settings.persona_session_mapping == {"mario|rossi": "Tizio"}
    assert target.settings.session_whitelist == {"foo@example.com", "Tribunale"}


def test_session_store_backward_compat_missing_fields() -> None:
    target = SimpleNamespace(settings=Settings(), jobs=[])

    import_session({"app_version": "0.1"}, target)
    assert target.settings.session_whitelist == set()

    import_session({"mapping": []}, target)
    assert target.settings.societa_session_mapping == {}
    assert target.settings.persona_session_mapping == {}


def test_session_store_ignores_extra_fields() -> None:
    target = SimpleNamespace(settings=Settings(), jobs=[])
    data = {
        "mapping": [{"original": "eni spa", "entity_type": "SOCIETA", "replacement": "Alfa", "anonymize": True}],
        "whitelist_session": ["x"],
        "unexpected": {"nested": True},
    }

    import_session(data, target)
    assert target.settings.societa_session_mapping == {"eni spa": "Alfa"}
    assert target.settings.session_whitelist == {"x"}
