"""Configuração da aplicação.

Regra: nada de editar código para trocar de provedor. Cada provedor tem um
preset (URL base, modelo padrão, variável de ambiente da chave e o modo de
saída estruturada que a API suporta); a escolha vem da CLI ou do ambiente.
"""

from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path

import os

from manki.errors import ConfigurationError


class Provider(str, Enum):
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    LMSTUDIO = "lmstudio"
    OPENAI = "openai"
    GEMINI = "gemini"


class StructuredOutput(str, Enum):
    """Como pedir JSON ao endpoint compatível com OpenAI."""

    JSON_SCHEMA = "json_schema"  # schema estrito (OpenAI, Groq, LM Studio)
    JSON_OBJECT = "json_object"  # apenas "responda em JSON" (DeepSeek)


@dataclass(frozen=True, slots=True)
class ProviderPreset:
    base_url: str | None
    default_model: str
    api_key_env: str
    structured_output: StructuredOutput
    api_key_required: bool = True


PRESETS: dict[Provider, ProviderPreset] = {
    Provider.DEEPSEEK: ProviderPreset(
        base_url="https://api.deepseek.com",
        default_model="deepseek-flash",
        api_key_env="DEEPSEEK_API_KEY",
        structured_output=StructuredOutput.JSON_OBJECT,
    ),
    Provider.GROQ: ProviderPreset(
        base_url="https://api.groq.com/openai/v1",
        default_model="openai/gpt-oss-120b",
        api_key_env="GROQ_API_KEY",
        structured_output=StructuredOutput.JSON_SCHEMA,
    ),
    Provider.LMSTUDIO: ProviderPreset(
        base_url="http://localhost:1234/v1",
        default_model="google/gemma-4-12b-qat",
        api_key_env="LMSTUDIO_API_KEY",
        structured_output=StructuredOutput.JSON_SCHEMA,
        api_key_required=False,
    ),
    Provider.OPENAI: ProviderPreset(
        base_url="https://api.openai.com/v1",
        default_model="gpt-4.1-mini",
        api_key_env="OPENAI_API_KEY",
        structured_output=StructuredOutput.JSON_SCHEMA,
    ),
    Provider.GEMINI: ProviderPreset(
        base_url=None,
        default_model="gemini-3.8-flash",
        api_key_env="GEMINI_API_KEY",
        structured_output=StructuredOutput.JSON_SCHEMA,
    ),
}


@dataclass(frozen=True, slots=True)
class LLMSettings:
    provider: Provider
    model: str
    api_key: str
    base_url: str | None
    structured_output: StructuredOutput
    temperature: float = 0.3


@dataclass(frozen=True, slots=True)
class AnkiSettings:
    deck_name: str = "Mandarim"
    deck_id: int = 2059400110
    model_id: int = 1607392319
    output_file: Path = Path("flashcards.apkg")


@dataclass(frozen=True, slots=True)
class Settings:
    llm: LLMSettings
    anki: AnkiSettings
    workers: int = 4
    request_timeout: float = 20.0
    log_level: str = "INFO"

    @classmethod
    def load(
        cls,
        *,
        provider: str | None = None,
        model: str | None = None,
        output: Path | None = None,
        deck_name: str | None = None,
        workers: int | None = None,
        log_level: str | None = None,
    ) -> "Settings":
        """Monta as configurações a partir do ambiente, com overrides da CLI.

        Não lê o `.env` por conta própria: carregá-lo é papel do ponto de
        entrada, o que mantém esta função pura e testável.
        """
        provider_name = (provider or _env("MANKI_PROVIDER") or Provider.DEEPSEEK.value).lower()
        try:
            chosen = Provider(provider_name)
        except ValueError as exc:
            known = ", ".join(p.value for p in Provider)
            raise ConfigurationError(
                f"Provedor desconhecido: '{provider_name}'. Opções: {known}."
            ) from exc

        preset = PRESETS[chosen]
        api_key = _env("MANKI_API_KEY") or _env(preset.api_key_env) or ""
        if preset.api_key_required and not api_key:
            raise ConfigurationError(
                f"Chave de API ausente para o provedor '{chosen.value}'. "
                f"Defina {preset.api_key_env} no arquivo .env."
            )

        llm = LLMSettings(
            provider=chosen,
            model=model or _env("MANKI_MODEL") or preset.default_model,
            api_key=api_key or "not-needed",
            base_url=_env("MANKI_BASE_URL") or preset.base_url,
            structured_output=preset.structured_output,
            temperature=_env_float("MANKI_TEMPERATURE", 0.3),
        )
        anki = AnkiSettings(
            deck_name=deck_name or _env("MANKI_DECK_NAME") or "Mandarim",
            deck_id=_env_int("MANKI_DECK_ID", 2059400110),
            model_id=_env_int("MANKI_MODEL_ID", 1607392319),
            output_file=output or Path(_env("MANKI_OUTPUT") or "flashcards.apkg"),
        )
        settings = cls(
            llm=llm,
            anki=anki,
            workers=workers or _env_int("MANKI_WORKERS", 4),
            request_timeout=_env_float("MANKI_TIMEOUT", 20.0),
            log_level=(log_level or _env("MANKI_LOG_LEVEL") or "INFO").upper(),
        )
        if settings.workers < 1:
            raise ConfigurationError("O número de workers precisa ser >= 1.")
        return settings

    def with_workers(self, workers: int) -> "Settings":
        return replace(self, workers=workers)


def _env(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} deve ser um número inteiro (recebido: '{raw}').") from exc


def _env_float(name: str, default: float) -> float:
    raw = _env(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} deve ser um número (recebido: '{raw}').") from exc
