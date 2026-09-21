"""Ordem dos traços a partir de strokeorder.com.

Melhorias sobre o scraping original: sessão HTTP reutilizada com retry e
timeout (antes um request sem timeout podia travar a execução inteira), cache
por caractere entre palavras e falha isolada por caractere.
"""

import logging
import threading

import requests
from lxml import html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.strokeorder.com/chinese/{char}"
_GIF_XPATH = "//img[contains(@src, '/assets/bishun/animation/')]/@src"
_USER_AGENT = "manki/0.2 (+https://github.com/; gerador de flashcards)"


class StrokeOrderScraper:
    """Implementa `StrokeOrderProvider`."""

    def __init__(self, *, timeout: float = 20.0, session: requests.Session | None = None):
        self.timeout = timeout
        self._session = session or _build_session()
        self._cache: dict[str, str | None] = {}
        self._lock = threading.Lock()

    def html_for(self, word: str) -> str:
        fragments = []
        for char in _unique_chars(word):
            url = self._image_url(char)
            if url:
                fragments.append(f'<img src="{url}">')
        return " ".join(fragments)

    def _image_url(self, char: str) -> str | None:
        with self._lock:
            if char in self._cache:
                return self._cache[char]

        url = _BASE_URL.format(char=char)
        result: str | None = None
        try:
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()
            tree = html.fromstring(response.content)
            matches = tree.xpath(_GIF_XPATH)
            if matches:
                result = requests.compat.urljoin(url, matches[0])
            else:
                logger.debug("Sem animação de traços para '%s'.", char)
        except Exception as exc:
            logger.warning("Não foi possível obter a ordem dos traços de '%s': %s", char, exc)

        with self._lock:
            self._cache[char] = result
        return result


def _unique_chars(word: str) -> list[str]:
    seen: set[str] = set()
    ordered = []
    for char in word:
        if char.strip() and char not in seen:
            seen.add(char)
            ordered.append(char)
    return ordered


def _build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": _USER_AGENT})
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session
