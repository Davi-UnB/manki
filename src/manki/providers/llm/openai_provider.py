"""Adaptador para qualquer endpoint compatível com a API da OpenAI.

Cobre DeepSeek, Groq, LM Studio e a própria OpenAI: o que muda entre eles é o
modo de saída estruturada, que vem do preset em `manki.config`.
"""

import logging

from openai import OpenAI
from pydantic import ValidationError

from manki.config import LLMSettings, StructuredOutput
from manki.domain.models import FlashcardData, WordRequest
from manki.errors import LLMError
from manki.providers.llm.prompts import FIELD_GUIDE, SYSTEM_PROMPT, user_prompt

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider:
    """Implementa `LLMProvider` sobre `chat.completions`."""

    def __init__(self, settings: LLMSettings, *, timeout: float = 20.0, client: OpenAI | None = None):
        self.settings = settings
        self.name = f"{settings.provider.value}/{settings.model}"
        self._client = client or OpenAI(
            base_url=settings.base_url,
            api_key=settings.api_key,
            timeout=timeout,
        )

    def generate(self, request: WordRequest) -> FlashcardData:
        prompt = user_prompt(request)
        try:
            return self._structured_call(prompt)
        except Exception as exc:  # qualquer falha da via estrita cai no fallback textual
            logger.warning(
                "Extração estrita falhou para '%s' (%s). Tentando modo texto.", request.word, exc
            )
            return self._plain_json_call(prompt)

    def _structured_call(self, prompt: str) -> FlashcardData:
        if self.settings.structured_output is StructuredOutput.JSON_OBJECT:
            response_format = {"type": "json_object"}
            prompt = f"{prompt}\n{FIELD_GUIDE}"
        else:
            schema = FlashcardData.model_json_schema()
            schema["additionalProperties"] = False
            response_format = {
                "type": "json_schema",
                "json_schema": {"name": "flashcard_data", "schema": schema, "strict": True},
            }
        content = self._complete(prompt, response_format=response_format, temperature=self.settings.temperature)
        return _parse(content)

    def _plain_json_call(self, prompt: str) -> FlashcardData:
        content = self._complete(f"{prompt}\n\n{FIELD_GUIDE}", temperature=0.1)
        return _parse(_strip_code_fence(content))

    def _complete(self, prompt: str, *, temperature: float, response_format: dict | None = None) -> str:
        kwargs = {"response_format": response_format} if response_format else {}
        try:
            response = self._client.chat.completions.create(
                model=self.settings.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                **kwargs,
            )
        except Exception as exc:  # erros de rede/API da SDK
            raise LLMError(f"Chamada ao provedor '{self.name}' falhou: {exc}") from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise LLMError(f"Provedor '{self.name}' devolveu uma resposta vazia.")
        return content


def _strip_code_fence(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    return text.strip()


def _parse(content: str) -> FlashcardData:
    try:
        return FlashcardData.model_validate_json(content)
    except ValidationError as exc:
        raise LLMError(f"Resposta do LLM fora do formato esperado: {exc}") from exc
