import os
import genanki
from models import FlashcardData

class AnkiDeckBuilder:
    """Responsável por orquestrar a criação do modelo, deck e notas no Anki."""
    def __init__(self, deck_id: int, deck_name: str, model_id: int):
        self.deck = genanki.Deck(deck_id, deck_name)
        self.media_files = []
        self.model = genanki.Model(
            model_id,
            'Mandarim Auto',
            fields=[
                {'name': 'Ordem Traços'},
                {'name': 'Caractere'},
                {'name': 'Pinyin'},
                {'name': 'Áudio Caractere'},
                {'name': 'Frase Caracteres'},
                {'name': 'Frase Pinyin'},
                {'name': 'Áudio Frase'},
                {'name': 'Tradução'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Ordem Traços}}<br><br>{{Caractere}}<br><br>{{Frase Caracteres}}',
                    'afmt': '{{FrontSide}}<hr id=answer>{{Pinyin}}<br>{{Áudio Caractere}}<br>{{Frase Pinyin}}<br>{{Áudio Frase}}<br><br>{{Tradução}}',
                },
            ],
            css='.card { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 22px; text-align: center; color: black; background-color: white; }'
        )

    def add_card(self, data: FlashcardData, stroke_links: str, audio_char: str, audio_frase: str):
        self.media_files.extend([audio_char, audio_frase])
        
        note = genanki.Note(
            model=self.model,
            fields=[
                stroke_links,                               
                data.caractere,                             
                data.pinyin,                                
                f"[sound:{audio_char}]",               
                data.frase_caracteres,                      
                data.frase_pinyin,                          
                f"[sound:{audio_frase}]",              
                data.traducao                               
            ]
        )
        self.deck.add_note(note)

    def export(self, filename: str):
        if not self.deck.notes:
            print("Nenhum cartão foi gerado para empacotar.")
            return

        print(f"\nEmpacotando {len(self.deck.notes)} cartões...")
        package = genanki.Package(self.deck)
        package.media_files = self.media_files
        package.write_to_file(filename)
        print(f"🎉 Pronto! Arquivo '{filename}' gerado com sucesso na pasta atual.")
        self._cleanup_media()

    def _cleanup_media(self):
        for media_file in self.media_files:
            if os.path.exists(media_file):
                os.remove(media_file)
