from pathlib import Path

from manki.anki import GenankiDeckBuilder
from manki.domain.models import Card, CardAssets, FlashcardData, WordRequest


def make_card(tmp_path: Path, word: str) -> Card:
    audio_word = tmp_path / f"{word}_p.mp3"
    audio_sentence = tmp_path / f"{word}_f.mp3"
    for path in (audio_word, audio_sentence):
        path.write_bytes(b"fake")
    return Card(
        request=WordRequest(word),
        data=FlashcardData(
            caractere=word,
            pinyin="pīn",
            frase_caracteres=f"{word}了",
            frase_pinyin="frase",
            traducao="meaning",
        ),
        assets=CardAssets(audio_word, audio_sentence, "<img src='x'>"),
    )


def test_export_writes_package(tmp_path: Path):
    deck = GenankiDeckBuilder(deck_id=1, deck_name="Teste", model_id=2)
    deck.add(make_card(tmp_path, "电脑"))
    output = tmp_path / "deck.apkg"
    assert deck.export(output) == 1
    assert output.exists() and output.stat().st_size > 0


def test_export_without_cards_is_a_noop(tmp_path: Path):
    deck = GenankiDeckBuilder(deck_id=1, deck_name="Teste", model_id=2)
    output = tmp_path / "deck.apkg"
    assert deck.export(output) == 0
    assert not output.exists()


def test_sound_tags_reference_only_the_file_name(tmp_path: Path):
    deck = GenankiDeckBuilder(deck_id=1, deck_name="Teste", model_id=2)
    deck.add(make_card(tmp_path, "苹果"))
    fields = deck._deck.notes[0].fields
    assert fields[3] == "[sound:苹果_p.mp3]"
    assert fields[6] == "[sound:苹果_f.mp3]"
