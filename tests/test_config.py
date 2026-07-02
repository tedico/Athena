import pytest


def test_missing_env_var_raises(monkeypatch):
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    from src import config
    with pytest.raises(config.ConfigError, match="NOTION_API_KEY"):
        config.require("NOTION_API_KEY")


def test_present_env_var_returned(monkeypatch):
    monkeypatch.setenv("NOTION_API_KEY", "secret_x")
    from src import config
    assert config.require("NOTION_API_KEY") == "secret_x"
