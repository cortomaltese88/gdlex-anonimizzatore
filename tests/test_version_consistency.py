import importlib.metadata as m
from pathlib import Path
import re

import pytest


def _pyproject_version() -> str:
    content = Path("pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, flags=re.MULTILINE)
    assert match is not None
    return match.group(1)


def test_installed_metadata_version_matches_pyproject() -> None:
    try:
        installed = m.version("gdlex-anonimizzatore")
    except m.PackageNotFoundError:
        pytest.skip("Package metadata not available in local test env; validated in CI after editable install")
    assert installed == _pyproject_version()
