"""Leitura da entrada do usuário (arquivo ou linha de comando).

Isolado de qualquer I/O de rede para poder ser testado diretamente.
"""

from pathlib import Path

from manki.domain.models import WordRequest

#: Delimitadores aceitos entre palavra e frase customizada (ASCII e fullwidth).
SEPARATORS = (":", "：")
COMMENT_PREFIX = "#"


def parse_line(line: str) -> WordRequest | None:
    """Converte uma linha `palavra` ou `palavra: frase` em `WordRequest`."""
    text = line.strip()
    if not text or text.startswith(COMMENT_PREFIX):
        return None

    for separator in SEPARATORS:
        if separator in text:
            word, sentence = text.split(separator, 1)
            word, sentence = word.strip(), sentence.strip()
            return WordRequest(word, sentence or None) if word else None

    return WordRequest(text)


def parse_lines(lines) -> list[WordRequest]:
    return [request for line in lines if (request := parse_line(line)) is not None]


def parse_words(raw: str) -> list[WordRequest]:
    """Modo interativo: palavras separadas por espaço, sem frase customizada."""
    return [WordRequest(word) for word in raw.split() if word]


def read_requests(path: Path) -> list[WordRequest]:
    with path.open("r", encoding="utf-8") as handle:
        return parse_lines(handle)
