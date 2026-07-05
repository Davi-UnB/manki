from config import Config
from llm_service import LLMService
from audio_service import AudioService
from scraper_service import StrokeScraperService
from anki_builder import AnkiDeckBuilder

class FlashcardGeneratorApp:
    """Aplicação principal que integra todos os serviços."""
    def __init__(self):
        self.config = Config()
        self.llm = LLMService(self.config)
        self.audio = AudioService()
        self.scraper = StrokeScraperService()
        self.anki = AnkiDeckBuilder(
            deck_id=self.config.DECK_ID, 
            deck_name=self.config.DECK_NAME,
            model_id=self.config.MODEL_ID
        )

    def process_words(self, words: list[str]):
        for i, word in enumerate(words):
            print(f"[{i+1}/{len(words)}] Processando '{word}'...")
            try:
                # 1. Obtém dados do LLM
                data = self.llm.fetch_data(word)
                
                # 2. Gera os áudios
                audio_char_file = f"audio_char_{i}.mp3"
                audio_frase_file = f"audio_frase_{i}.mp3"
                self.audio.generate(data.caractere, audio_char_file)
                self.audio.generate(data.frase_caracteres, audio_frase_file)
                
                # 3. Gera links de ordem dos traços
                stroke_links = self.scraper.get_images_html(data.caractere)
                
                # 4. Adiciona a Nota ao Deck
                self.anki.add_card(data, stroke_links, audio_char_file, audio_frase_file)
                
                print(f"✅ Cartão para '{word}' criado com sucesso.")
            except Exception as e:
                print(f"⚠️ Erro ao processar '{word}': {e}")
                
        # Empacota no final
        self.anki.export(self.config.OUTPUT_FILE)


if __name__ == "__main__":
    print(f"Iniciando gerador de flashcards (LM Studio / {Config.MODEL_NAME}) - Modo Modular")
    user_input = input("Insira as palavras (separadas por espaços): ").strip()
    
    if user_input:
        words_to_process = [w for w in user_input.split(" ") if w]
        app = FlashcardGeneratorApp()
        app.process_words(words_to_process)
    else:
        print("Nenhuma palavra inserida.")