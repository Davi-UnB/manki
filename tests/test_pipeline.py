from pathlib import Path

from manki.domain.models import WordRequest
from manki.pipeline import FlashcardPipeline

from tests.fakes import FakeAudio, FakeDeck, FakeLLM, FakeStrokes


def build(tmp_path: Path, llm: FakeLLM, deck: FakeDeck, workers: int = 2) -> FlashcardPipeline:
    return FlashcardPipeline(
        llm=llm,
        audio=FakeAudio(),
        strokes=FakeStrokes(),
        deck=deck,
        media_dir=tmp_path,
        workers=workers,
    )


def test_builds_one_card_per_word_in_input_order(tmp_path: Path):
    deck = FakeDeck()
    requests = [WordRequest(w) for w in ("电脑", "苹果", "飞机")]
    result = build(tmp_path, FakeLLM(), deck).run(requests, tmp_path / "out.apkg")

    assert result.created == 3
    assert result.failures == []
    assert [card.data.caractere for card in deck.cards] == ["电脑", "苹果", "飞机"]
    assert deck.exported_to == tmp_path / "out.apkg"


def test_custom_sentence_reaches_the_card(tmp_path: Path):
    deck = FakeDeck()
    build(tmp_path, FakeLLM(), deck).run([WordRequest("作弊", "你真的作弊了")], tmp_path / "o.apkg")
    assert deck.cards[0].data.frase_caracteres == "你真的作弊了"


def test_failed_word_is_reported_without_stopping_the_batch(tmp_path: Path):
    deck = FakeDeck()
    requests = [WordRequest("电脑"), WordRequest("苹果"), WordRequest("飞机")]
    result = build(tmp_path, FakeLLM(failing_words={"苹果"}), deck).run(requests, tmp_path / "o.apkg")

    assert result.created == 2
    assert [f.word for f in result.failures] == ["苹果"]
    assert [card.data.caractere for card in deck.cards] == ["电脑", "飞机"]


def test_media_files_are_written_with_unique_names(tmp_path: Path):
    deck = FakeDeck()
    build(tmp_path, FakeLLM(), deck).run([WordRequest("电脑"), WordRequest("苹果")], tmp_path / "o.apkg")
    names = {path.name for card in deck.cards for path in (card.assets.word_audio, card.assets.sentence_audio)}
    assert len(names) == 4


def test_empty_input_does_not_touch_the_deck(tmp_path: Path):
    deck = FakeDeck()
    result = build(tmp_path, FakeLLM(), deck).run([], tmp_path / "o.apkg")
    assert result.created == 0 and deck.exported_to is None
