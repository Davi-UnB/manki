import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (se existir)
load_dotenv()

class Config:
    """Configurações globais da aplicação."""
    # ==========================
    # ESCOLHA DO PROVEDOR DE IA
    # ==========================
    USE_GEMINI = True  # Mude para True para usar a API do Google Gemini
    
    # Configurações LM Studio (Local)
    OPENAI_BASE_URL = "http://localhost:1234/v1"
    OPENAI_API_KEY = "lm-studio"
    MODEL_NAME = "qwen3.5/9b"
    
    # Configurações Gemini (Nuvem)
    # Agora a chave será lida automaticamente do arquivo .env
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_NAME = "gemini-3.5-flash"

    # ==========================
    # ANKI
    # ==========================
    DECK_NAME = "Mandarim"
    OUTPUT_FILE = "flashcards.apkg"

    # Configurações do Anki (genanki)
    MODEL_ID = 1607392319
    DECK_ID = 2059400110
