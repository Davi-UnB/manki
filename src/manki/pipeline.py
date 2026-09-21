"""Orquestração: de palavras para cartões.

O pipeline conhece apenas as portas do domínio. As etapas de rede de cada
palavra (LLM, TTS e scraping) são independentes entre palavras, então rodam em
paralelo; a inserção no baralho acontece na ordem da entrada para manter o
resultado determinístico.
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from manki.domain.models import Card, CardAssets, WordRequest
from manki.domain.ports import AudioSynthesizer, DeckBuilder, LLMProvider, StrokeOrderProvider

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Failure:
    word: str
    error: str


@dataclass
class PipelineResult:
    created: int = 0
    failures: list[Failure] = field(default_factory=list)
    output_file: Path | None = None

    @property
    def ok(self) -> bool:
        return self.created > 0 and not self.failures


class FlashcardPipeline:
    def __init__(
        self,
        *,
        llm: LLMProvider,
        audio: AudioSynthesizer,
        strokes: StrokeOrderProvider,
        deck: DeckBuilder,
        media_dir: Path,
        workers: int = 4,
    ):
        self._llm = llm
        self._audio = audio
        self._strokes = strokes
        self._deck = deck
        self._media_dir = media_dir
        self._workers = max(1, workers)

    def run(self, requests: list[WordRequest], destination: Path) -> PipelineResult:
        result = PipelineResult(output_file=destination)
        if not requests:
            return result

        total = len(requests)
        with ThreadPoolExecutor(max_workers=self._workers) as pool:
            outcomes = pool.map(
                lambda item: self._build_card(item[0], item[1]), enumerate(requests)
            )

            for position, (request, outcome) in enumerate(zip(requests, outcomes), start=1):
                card, error = outcome
                if card is None:
                    logger.error("[%d/%d] ⚠️  '%s': %s", position, total, request.word, error)
                    result.failures.append(Failure(request.word, str(error)))
                    continue
                self._deck.add(card)
                result.created += 1
                logger.info("[%d/%d] ✅ Cartão para '%s' criado.", position, total, request.word)

        exported = self._deck.export(destination)
        result.created = exported
        return result

    def _build_card(self, index: int, request: WordRequest) -> tuple[Card | None, Exception | None]:
        """Executa as etapas de uma palavra. Nunca levanta: o erro volta no par."""
        try:
            data = self._llm.generate(request)
            word_audio = self._audio.synthesize(
                data.caractere, self._media_dir / f"manki_{index}_palavra.mp3"
            )
            sentence_audio = self._audio.synthesize(
                data.frase_caracteres, self._media_dir / f"manki_{index}_frase.mp3"
            )
            stroke_html = self._strokes.html_for(data.caractere)
            assets = CardAssets(
                word_audio=word_audio, sentence_audio=sentence_audio, stroke_html=stroke_html
            )
            return Card(request=request, data=data, assets=assets), None
        except Exception as exc:  # falha de uma palavra não derruba o lote
            logger.debug("Falha ao montar cartão de '%s'", request.word, exc_info=exc)
            return None, exc
