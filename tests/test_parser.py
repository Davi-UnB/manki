from pathlib import Path

from manki.inputs import parse_lines, parse_words, read_requests
from manki.inputs.parser import parse_line


def test_word_without_sentence():
    assert parse_line("减肥") == __import__(
        "manki.domain.models", fromlist=["WordRequest"]
    ).WordRequest("减肥", None)


def test_ascii_and_fullwidth_separators():
    assert parse_line("作弊: 你真的作弊了").custom_sentence == "你真的作弊了"
    assert parse_line("亮：还真能亮").custom_sentence == "还真能亮"


def test_sentence_may_contain_separator():
    request = parse_line("说: 他说: 好的")
    assert request.word == "说"
    assert request.custom_sentence == "他说: 好的"


def test_blank_and_comment_lines_are_ignored():
    assert parse_lines(["", "   ", "# comentário", "苹果"]) == parse_lines(["苹果"])


def test_empty_sentence_falls_back_to_none():
    assert parse_line("苹果:   ").custom_sentence is None


def test_line_without_word_is_dropped():
    assert parse_line(": só a frase") is None


def test_parse_words_splits_on_whitespace():
    assert [r.word for r in parse_words(" 电脑  苹果\n飞机 ")] == ["电脑", "苹果", "飞机"]


def test_read_requests(tmp_path: Path):
    file = tmp_path / "input.txt"
    file.write_text("# cabeçalho\n作弊: 你真的作弊了\n\n减肥\n", encoding="utf-8")
    requests = read_requests(file)
    assert [(r.word, r.custom_sentence) for r in requests] == [
        ("作弊", "你真的作弊了"),
        ("减肥", None),
    ]
