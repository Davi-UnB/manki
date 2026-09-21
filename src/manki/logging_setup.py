"""Configuração única de logging para a CLI."""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # Bibliotecas de rede são verbosas demais em DEBUG.
    for noisy in ("httpx", "httpcore", "urllib3", "google_genai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
