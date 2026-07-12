from openai import OpenAI
from google import genai
from google.genai.types import Schema, Type
from models import FlashcardData
import json

class LLMService:
    """Responsável pela comunicação com o LM Studio ou Google Gemini."""
    def __init__(self, config):
        self.config = config
        self.use_gemini = config.USE_GEMINI
        
        if self.use_gemini:
            self.gemini_client = genai.Client(api_key=self.config.GEMINI_API_KEY)
        else:
            self.openai_client = OpenAI(base_url=self.config.OPENAI_BASE_URL, api_key=self.config.OPENAI_API_KEY)
            
        self.system_prompt = (
            "Você é um assistente de criação de flashcards de mandarim para o Anki. "
            "Siga ESTRITAMENTE as regras e preencha os dados no formato JSON solicitado. "
            "Regras para a frase: Crie uma frase de exemplo clara, natural e útil. "
            "Utilize vocabulário e gramática focados no nível HSK 3. "
            "Não limite a frase apenas a pronomes básicos, mas também evite palavras "
            "muito avançadas ou raras (HSK 5+). A frase deve demonstrar o uso real da palavra.\n"
            "Regras para a tradução: O campo 'traducao' deve conter EXCLUSIVAMENTE o significado da palavra "
            "isolada, em INGLÊS. NÃO traduza a frase de exemplo. Retorne apenas definições curtas em inglês."
        )

    def fetch_data(self, word: str, custom_sentence: str = None) -> FlashcardData:
        if self.use_gemini:
            return self._fetch_gemini(word, custom_sentence)
        else:
            return self._fetch_openai(word, custom_sentence)

    def _fetch_gemini(self, word: str, custom_sentence: str = None) -> FlashcardData:
        if custom_sentence:
            prompt_user = (
                f"{self.system_prompt}\n\n"
                f"Gere as informações para a palavra em chinês: {word}\n"
                f"IMPORTANTE: Você deve usar OBRIGATORIAMENTE a seguinte frase de exemplo fornecida pelo usuário no campo 'frase_caracteres': {custom_sentence}\n"
                f"Preencha o campo 'frase_pinyin' com o pinyin correto dessa frase fornecida."
            )
        else:
            prompt_user = f"{self.system_prompt}\n\nGere as informações para a palavra em chinês: {word}"
        
        response_schema = Schema(
            type=Type.OBJECT,
            properties={
                "caractere": Schema(type=Type.STRING),
                "pinyin": Schema(type=Type.STRING),
                "frase_caracteres": Schema(type=Type.STRING),
                "frase_pinyin": Schema(type=Type.STRING),
                "traducao": Schema(type=Type.STRING),
            },
            required=["caractere", "pinyin", "frase_caracteres", "frase_pinyin", "traducao"]
        )

        response = self.gemini_client.models.generate_content(
            model=self.config.GEMINI_MODEL_NAME,
            contents=[{"role": "user", "parts": [{"text": prompt_user}]}],
            config={
                "response_mime_type": "application/json",
                "response_schema": response_schema
            }
        )
        return FlashcardData.model_validate_json(response.text)

    def _fetch_openai(self, word: str, custom_sentence: str = None) -> FlashcardData:
        if custom_sentence:
            prompt_user = (
                f"Gere as informações para a palavra em chinês: {word}\n"
                f"IMPORTANTE: Você deve usar OBRIGATORIAMENTE a seguinte frase de exemplo fornecida pelo usuário no campo 'frase_caracteres': {custom_sentence}\n"
                f"Preencha o campo 'frase_pinyin' com o pinyin correto dessa frase fornecida."
            )
        else:
            prompt_user = f"Gere as informações para a palavra em chinês: {word}"
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt_user}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "flashcard_data",
                        "schema": FlashcardData.model_json_schema(),
                        "strict": True
                    }
                },
                temperature=0.3
            )
            content = response.choices[0].message.content
            return FlashcardData.model_validate_json(content)
            
        except Exception as e:
            print(f"⚠️ Aviso: Tentativa de extração estrita falhou, usando modo fallback para '{word}'. Detalhes: {e}")
            return self._fetch_openai_fallback(prompt_user)

    def _fetch_openai_fallback(self, prompt_user: str) -> FlashcardData:
        prompt_fallback = (
            f"{prompt_user}\n\n"
            "Retorne APENAS um objeto JSON válido com as seguintes chaves:\n"
            "- caractere (a palavra em chinês)\n"
            "- pinyin (o pinyin da palavra)\n"
            "- frase_caracteres (frase de exemplo em nível HSK 3)\n"
            "- frase_pinyin (pinyin da frase)\n"
            "- traducao (tradução para inglês)\n"
            "Não adicione nenhuma formatação Markdown ao redor."
        )
        response = self.openai_client.chat.completions.create(
            model=self.config.MODEL_NAME,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt_fallback}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content
        if content.startswith("```json"):
            content = content.replace("```json\n", "").replace("```", "")
        return FlashcardData.model_validate_json(content)
