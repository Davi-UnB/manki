"""Modelos do domínio.

`FlashcardData` é o contrato com o LLM (validado por Pydantic); os demais são
estruturas internas imutáveis que trafegam pelo pipeline.
"""

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class FlashcardData(BaseModel):
    """Conteúdo textual de um flashcard, produzido pelo LLM."""

    model_config = ConfigDict(extra="forbid")

    caractere: str = Field(description="A palavra em chinês (Hanzi)")
    pinyin: str = Field(description="O pinyin da palavra")
    frase_caracteres: str = Field(
        description="Uma frase de exemplo simples e curta usando a palavra, em chinês (Hanzi)."
    )
    frase_pinyin: str = Field(description="O pinyin da frase de exemplo.")
    traducao: str = Field(description="A tradução da palavra para o inglês.")


@dataclass(frozen=True, slots=True)
class WordRequest:
    """Uma linha de entrada: a palavra e, opcionalmente, a frase escolhida pelo usuário."""

    word: str
    custom_sentence: str | None = None


@dataclass(frozen=True, slots=True)
class CardAssets:
    """Mídias associadas a um cartão."""

    word_audio: Path
    sentence_audio: Path
    stroke_html: str


@dataclass(frozen=True, slots=True)
class Card:
    """Um cartão pronto para ser adicionado ao baralho."""

    request: WordRequest
    data: FlashcardData
    assets: CardAssets
