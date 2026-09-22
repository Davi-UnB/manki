"""Síntese de voz via gTTS."""

import warnings
from pathlib import Path

from gtts import gTTS

from manki.errors import AudioError


class GTTSSynthesizer:
    """Implementa `AudioSynthesizer` usando o Google Translate TTS."""

    def __init__(self, lang: str = "zh-CN"):
        self.lang = lang

    def synthesize(self, text: str, destination: Path) -> Path:
        if not text.strip():
            raise AudioError("Não há texto para sintetizar.")
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with warnings.catch_warnings():
                # gTTS marca 'zh-CN' como depreciado e "cai" para... 'zh-CN' de
                # novo (bug da própria tabela interna da lib); o idioma segue
                # válido, então só silenciamos o ruído.
                warnings.filterwarnings("ignore", category=DeprecationWarning, module="gtts")
                gTTS(text=text, lang=self.lang).save(str(destination))
        except Exception as exc:
            raise AudioError(f"Falha ao gerar áudio para '{text}': {exc}") from exc
        return destination
