"""Adaptador para a API do Google Gemini (saída estruturada nativa)."""

from google import genai
from google.genai.types import Schema, Type
from pydantic import ValidationError

from manki.config import LLMSettings
from manki.domain.models import FlashcardData, WordRequest
from manki.errors import LLMError
from manki.providers.llm.prompts import SYSTEM_PROMPT, user_prompt

_RESPONSE_SCHEMA = Schema(
    type=Type.OBJECT,
    properties={
        "caractere": Schema(type=Type.STRING),
        "pinyin": Schema(type=Type.STRING),
        "frase_caracteres": Schema(type=Type.STRING),
        "frase_pinyin": Schema(type=Type.STRING),
        "traducao": Schema(type=Type.STRING),
    },
    required=["caractere", "pinyin", "frase_caracteres", "frase_pinyin", "traducao"],
)


class GeminiProvider:
    """Implementa `LLMProvider` sobre `google-genai`."""

    def __init__(self, settings: LLMSettings, client=None):
        self.settings = settings
        self.name = f"gemini/{settings.model}"
        self._client = client or genai.Client(api_key=settings.api_key)

    def generate(self, request: WordRequest) -> FlashcardData:
        prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt(request)}"
        try:
            response = self._client.models.generate_content(
                model=self.settings.model,
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": _RESPONSE_SCHEMA,
                },
            )
        except Exception as exc:
            raise LLMError(f"Chamada ao Gemini falhou: {exc}") from exc

        if not response.text:
            raise LLMError("Gemini devolveu uma resposta vazia.")
        try:
            return FlashcardData.model_validate_json(response.text)
        except ValidationError as exc:
            raise LLMError(f"Resposta do Gemini fora do formato esperado: {exc}") from exc
