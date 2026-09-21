"""Dublês das portas do domínio, usados pelos testes do pipeline."""

from pathlib import Path

from manki.domain.models import Card, FlashcardData, WordRequest


class FakeLLM:
    name = "fake/model"

    def __init__(self, failing_words: set[str] | None = None):
        self.failing_words = failing_words or set()
        self.calls: list[WordRequest] = []

    def generate(self, request: WordRequest) -> FlashcardData:
        self.calls.append(request)
        if request.word in self.failing_words:
            raise RuntimeError("provedor indisponível")
        return FlashcardData(
            caractere=request.word,
            pinyin="pīn",
            frase_caracteres=request.custom_sentence or f"{request.word}了",
            frase_pinyin="frase pīn",
            traducao="meaning",
        )


class FakeAudio:
    def synthesize(self, text: str, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"fake-mp3")
        return destination


class FakeStrokes:
    def html_for(self, word: str) -> str:
        return f'<img src="https://example.test/{word}.gif">'


class FakeDeck:
    def __init__(self):
        self.cards: list[Card] = []
        self.exported_to: Path | None = None

    def add(self, card: Card) -> None:
        self.cards.append(card)

    def export(self, destination: Path) -> int:
        self.exported_to = destination
        return len(self.cards)
