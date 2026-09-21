import pytest

from manki.config import Provider, Settings, StructuredOutput
from manki.errors import ConfigurationError


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in list(__import__("os").environ):
        if name.startswith("MANKI_") or name.endswith("_API_KEY"):
            monkeypatch.delenv(name, raising=False)


def test_provider_preset_defines_model_and_output_mode(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "k")
    settings = Settings.load(provider="groq")
    assert settings.llm.provider is Provider.GROQ
    assert settings.llm.base_url == "https://api.groq.com/openai/v1"
    assert settings.llm.structured_output is StructuredOutput.JSON_SCHEMA


def test_deepseek_uses_json_object_mode(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    assert Settings.load(provider="deepseek").llm.structured_output is StructuredOutput.JSON_OBJECT


def test_local_provider_needs_no_api_key():
    assert Settings.load(provider="lmstudio").llm.provider is Provider.LMSTUDIO


def test_missing_api_key_is_a_configuration_error():
    with pytest.raises(ConfigurationError, match="GEMINI_API_KEY"):
        Settings.load(provider="gemini")


def test_unknown_provider_lists_the_options():
    with pytest.raises(ConfigurationError, match="Opções"):
        Settings.load(provider="inexistente")


def test_cli_overrides_win_over_environment(monkeypatch):
    monkeypatch.setenv("MANKI_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    monkeypatch.setenv("MANKI_MODEL", "do-env")
    settings = Settings.load(model="da-cli", deck_name="HSK3", workers=8)
    assert settings.llm.model == "da-cli"
    assert settings.anki.deck_name == "HSK3"
    assert settings.workers == 8


def test_invalid_numeric_env_is_rejected(monkeypatch):
    monkeypatch.setenv("LMSTUDIO_API_KEY", "k")
    monkeypatch.setenv("MANKI_WORKERS", "muitos")
    with pytest.raises(ConfigurationError, match="MANKI_WORKERS"):
        Settings.load(provider="lmstudio")
