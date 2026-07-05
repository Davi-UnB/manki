from gtts import gTTS

class AudioService:
    """Responsável por gerar os áudios via TTS."""
    @staticmethod
    def generate(text: str, filename: str) -> str:
        tts = gTTS(text=text, lang='zh-CN')
        tts.save(filename)
        return filename
