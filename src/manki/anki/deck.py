"""Montagem e exportação do baralho com genanki."""

import logging
from pathlib import Path

import genanki

from manki.anki import templates
from manki.domain.models import Card
from manki.errors import DeckExportError

logger = logging.getLogger(__name__)


class GenankiDeckBuilder:
    """Implementa `DeckBuilder`.

    Guarda apenas os caminhos das mídias; a limpeza dos arquivos temporários é
    responsabilidade de quem os criou (o pipeline, via diretório temporário).
    """

    def __init__(self, *, deck_id: int, deck_name: str, model_id: int):
        self._deck = genanki.Deck(deck_id, deck_name)
        self._model = genanki.Model(
            model_id,
            templates.NOTE_TYPE_NAME,
            fields=templates.FIELDS,
            templates=templates.TEMPLATES,
            css=templates.CSS,
        )
        self._media_files: list[str] = []

    @property
    def card_count(self) -> int:
        return len(self._deck.notes)

    def add(self, card: Card) -> None:
        assets = card.assets
        self._media_files.extend([str(assets.word_audio), str(assets.sentence_audio)])
        note = genanki.Note(
            model=self._model,
            fields=[
                assets.stroke_html,
                card.data.caractere,
                card.data.pinyin,
                f"[sound:{assets.word_audio.name}]",
                card.data.frase_caracteres,
                card.data.frase_pinyin,
                f"[sound:{assets.sentence_audio.name}]",
                card.data.traducao,
            ],
        )
        self._deck.add_note(note)

    def export(self, destination: Path) -> int:
        if not self._deck.notes:
            logger.warning("Nenhum cartão foi gerado para empacotar.")
            return 0

        package = genanki.Package(self._deck)
        package.media_files = self._media_files
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            package.write_to_file(str(destination))
        except Exception as exc:
            raise DeckExportError(f"Falha ao escrever '{destination}': {exc}") from exc
        return self.card_count
