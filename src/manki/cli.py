"""Interface de linha de comando e composição das dependências.

Este é o único módulo que conhece todas as implementações concretas: ele lê os
argumentos, monta os adaptadores e entrega tudo pronto ao `FlashcardPipeline`.

Códigos de saída: 0 sucesso, 1 erro fatal (configuração/entrada/exportação),
2 baralho gerado com falhas parciais.
"""

import argparse
import logging
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from manki import __version__
from manki.anki import GenankiDeckBuilder
from manki.config import Provider, Settings
from manki.domain.models import WordRequest
from manki.errors import MankiError
from manki.inputs import parse_words, read_requests
from manki.logging_setup import setup_logging
from manki.pipeline import FlashcardPipeline, PipelineResult
from manki.providers.audio import GTTSSynthesizer
from manki.providers.llm import build_llm_provider
from manki.providers.strokes import StrokeOrderScraper

logger = logging.getLogger(__name__)

DEFAULT_INPUT = Path("input.txt")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manki",
        description="Gera um baralho .apkg de mandarim a partir de uma lista de palavras.",
        epilog="Formato do arquivo de entrada: uma palavra por linha, opcionalmente "
        "'palavra: frase customizada'. Linhas vazias e iniciadas por '#' são ignoradas.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"arquivo de entrada (padrão: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "-w", "--words", nargs="+", metavar="PALAVRA",
        help="palavras informadas direto na linha de comando (ignora o arquivo)",
    )
    parser.add_argument(
        "-p", "--provider", choices=[p.value for p in Provider],
        help="provedor de LLM (padrão: MANKI_PROVIDER ou deepseek)",
    )
    parser.add_argument("-m", "--model", help="modelo a usar (sobrescreve o padrão do provedor)")
    parser.add_argument("-o", "--output", type=Path, help="arquivo .apkg de saída")
    parser.add_argument("-d", "--deck", help="nome do baralho no Anki")
    parser.add_argument("-j", "--workers", type=int, help="palavras processadas em paralelo")
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="verbosidade (padrão: INFO)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="apenas mostra as palavras interpretadas, sem chamar nenhuma API",
    )
    parser.add_argument("--version", action="version", version=f"manki {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    setup_logging(args.log_level or "INFO")
    load_dotenv()  # o `.env` entra no ambiente antes de qualquer leitura de config

    try:
        requests = collect_requests(args)
        if not requests:
            logger.error("Nenhuma palavra para processar.")
            return 1

        if args.dry_run:
            for request in requests:
                suffix = f" → {request.custom_sentence}" if request.custom_sentence else ""
                logger.info("%s%s", request.word, suffix)
            logger.info("%d palavra(s) prontas para processamento.", len(requests))
            return 0

        settings = Settings.load(
            provider=args.provider,
            model=args.model,
            output=args.output,
            deck_name=args.deck,
            workers=args.workers,
            log_level=args.log_level,
        )
        setup_logging(settings.log_level)
        result = run(settings, requests)
    except MankiError as exc:
        logger.error("❌ %s", exc)
        return 1
    except KeyboardInterrupt:
        logger.warning("Interrompido pelo usuário.")
        return 1

    if result.created == 0:
        logger.error("Nenhum cartão foi gerado.")
        return 1

    logger.info("🎉 %d cartão(ões) em '%s'.", result.created, result.output_file)
    if result.failures:
        logger.warning(
            "%d palavra(s) falharam: %s",
            len(result.failures),
            ", ".join(failure.word for failure in result.failures),
        )
        return 2
    return 0


def collect_requests(args: argparse.Namespace) -> list[WordRequest]:
    """Resolve a origem da entrada: flag `--words`, arquivo ou modo interativo."""
    if args.words:
        return parse_words(" ".join(args.words))

    if args.input.exists():
        logger.info("Lendo palavras de '%s'.", args.input)
        return read_requests(args.input)

    if args.input != DEFAULT_INPUT:
        raise MankiError(f"O arquivo '{args.input}' não foi encontrado.")

    if not sys.stdin.isatty():
        return parse_words(sys.stdin.read())

    return parse_words(input("Insira as palavras (separadas por espaços): "))


def run(settings: Settings, requests: list[WordRequest]) -> PipelineResult:
    """Compõe os adaptadores e executa o pipeline."""
    llm = build_llm_provider(settings)
    logger.info("Provedor: %s | baralho: %s", llm.name, settings.anki.deck_name)

    deck = GenankiDeckBuilder(
        deck_id=settings.anki.deck_id,
        deck_name=settings.anki.deck_name,
        model_id=settings.anki.model_id,
    )
    # As mídias vivem em um diretório temporário: nada de .mp3 soltos no projeto.
    with tempfile.TemporaryDirectory(prefix="manki-media-") as tmp:
        pipeline = FlashcardPipeline(
            llm=llm,
            audio=GTTSSynthesizer(),
            strokes=StrokeOrderScraper(timeout=settings.request_timeout),
            deck=deck,
            media_dir=Path(tmp),
            workers=settings.workers,
        )
        return pipeline.run(requests, settings.anki.output_file)


if __name__ == "__main__":
    raise SystemExit(main())
