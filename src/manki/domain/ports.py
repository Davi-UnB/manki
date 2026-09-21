"""Portas (interfaces) que o pipeline consome.

O pipeline depende apenas destes protocolos; as implementações concretas
(OpenAI, Gemini, gTTS, strokeorder.com, genanki) vivem em `manki.providers` e
`manki.anki` e são injetadas na composição feita pela CLI.
"""

from pathlib import Path
from typing import Protocol, runtime_checkable

from manki.domain.models import Card, FlashcardData, WordRequest


@runtime_checkable
class LLMProvider(Protocol):
    """Gera o conteúdo textual de um flashcard."""

    name: str

    def generate(self, request: WordRequest) -> FlashcardData: ...


@runtime_checkable
class AudioSynthesizer(Protocol):
    """Sintetiza um texto em mandarim para um arquivo de áudio."""

    def synthesize(self, text: str, destination: Path) -> Path: ...


@runtime_checkable
class StrokeOrderProvider(Protocol):
    """Devolve o HTML com as animações de ordem dos traços de uma palavra."""

    def html_for(self, word: str) -> str: ...


@runtime_checkable
class DeckBuilder(Protocol):
    """Acumula cartões e exporta o pacote final."""

    def add(self, card: Card) -> None: ...

    def export(self, destination: Path) -> int: ...
