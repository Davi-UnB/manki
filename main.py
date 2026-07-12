try:
    import readline
except ImportError:
    pass

import os
import sys
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

    def process_words(self, word_pairs: list[tuple[str, str | None]]):
        for i, (word, custom_sentence) in enumerate(word_pairs):
            if custom_sentence:
                print(f"[{i+1}/{len(word_pairs)}] Processando '{word}' com frase customizada...")
            else:
                print(f"[{i+1}/{len(word_pairs)}] Processando '{word}'...")
            try:
                # 1. Obtém dados do LLM
                data = self.llm.fetch_data(word, custom_sentence)
                
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
    
    file_path = "input.txt"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
    word_pairs = []
    
    # Se o arquivo de entrada existir, processa a partir dele
    if os.path.exists(file_path):
        print(f"Lendo palavras e frases do arquivo: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Aceita ':' (inglês) ou '：' (chinês) como delimitadores
                if ":" in line:
                    parts = line.split(":", 1)
                elif "：" in line:
                    parts = line.split("：", 1)
                else:
                    parts = [line]
                
                word = parts[0].strip()
                sentence = parts[1].strip() if len(parts) > 1 else None
                if word:
                    word_pairs.append((word, sentence))
    else:
        # Se um argumento foi passado e o arquivo não foi encontrado, encerra com erro
        if len(sys.argv) > 1:
            print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
            sys.exit(1)
            
        # Fallback interativo caso não haja arquivo de entrada
        user_input = input("Insira as palavras (separadas por espaços): ").strip()
        if user_input:
            words_to_process = [w for w in user_input.split(" ") if w]
            word_pairs = [(w, None) for w in words_to_process]

    if word_pairs:
        app = FlashcardGeneratorApp()
        app.process_words(word_pairs)
    else:
        print("Nenhuma palavra inserida para processamento.")