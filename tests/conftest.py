"""Test configuration and fixtures."""
import sys
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def isolate_env(monkeypatch):
    """
    Autouse: every test gets an env free of .env-file and cross-test
    module-cache pollution. Patches the dotenv source, not
    src.config.load_dotenv, so it doesn't matter when src modules import
    it. Tradeoff accepted: the load_dotenv() call itself can never be
    unit-tested under this fixture — only require()'s post-load behavior.
    """
    modules_to_remove = [m for m in sys.modules if m.startswith("src")]
    for module_name in modules_to_remove:
        del sys.modules[module_name]

    with patch("dotenv.load_dotenv"):
        yield
