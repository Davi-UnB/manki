# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field

class FlashcardData(BaseModel):
    caractere: str = Field(description="A palavra em chinês (Hanzi)")
    pinyin: str = Field(description="O pinyin da palavra")
    frase_caracteres: str = Field(description="Uma frase de exemplo simples e curta usando a palavra, em chinês (Hanzi).")
    frase_pinyin: str = Field(description="O pinyin da frase de exemplo.")
    traducao: str = Field(description="A tradução da palavra para o inglês.")
