"""Atalho de compatibilidade: `python main.py [arquivo]`.

O ponto de entrada oficial é `manki` (console script) ou `python -m manki`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from manki.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
