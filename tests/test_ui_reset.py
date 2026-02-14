from gdlex_anonimizzatore.ui.state_helpers import file_actions_enabled, has_resettable_state


def test_file_actions_enabled() -> None:
    assert file_actions_enabled(1, False)
    assert not file_actions_enabled(0, False)
    assert not file_actions_enabled(2, True)


def test_has_resettable_state() -> None:
    assert has_resettable_state(1, False, 0, "Pronto")
    assert has_resettable_state(0, True, 0, "Pronto")
    assert has_resettable_state(0, False, 1, "Pronto")
    assert has_resettable_state(0, False, 0, "Elaborato")
    assert not has_resettable_state(0, False, 0, "Pronto")
