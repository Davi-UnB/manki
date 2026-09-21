"""Caminho completo sem rede: pipeline real + genanki real, provedores dublês."""

import zipfile
from pathlib import Path

from manki.anki import GenankiDeckBuilder
from manki.domain.models import WordRequest
from manki.pipeline import FlashcardPipeline

from tests.fakes import FakeAudio, FakeLLM, FakeStrokes


def test_generates_a_valid_apkg_with_media(tmp_path: Path):
    deck = GenankiDeckBuilder(deck_id=1, deck_name="Mandarim", model_id=2)
    pipeline = FlashcardPipeline(
        llm=FakeLLM(failing_words={"飞机"}),
        audio=FakeAudio(),
        strokes=FakeStrokes(),
        deck=deck,
        media_dir=tmp_path / "media",
        workers=3,
    )
    output = tmp_path / "flashcards.apkg"
    result = pipeline.run(
        [WordRequest("电脑"), WordRequest("飞机"), WordRequest("苹果", "我有苹果")], output
    )

    assert result.created == 2
    assert [failure.word for failure in result.failures] == ["飞机"]
    assert output.exists()

    with zipfile.ZipFile(output) as package:
        names = set(package.namelist())
    assert "collection.anki2" in names
    # Duas mídias por cartão gerado, numeradas no manifesto do pacote.
    assert {"0", "1", "2", "3"} <= names
