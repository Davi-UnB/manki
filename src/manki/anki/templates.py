"""Definição do modelo de nota (campos, templates e CSS).

Separado do builder porque é conteúdo de apresentação: mudar o visual do cartão
não deve exigir tocar na lógica de empacotamento.
"""

NOTE_TYPE_NAME = "Mandarim Auto"

FIELDS = [
    {"name": "Ordem Traços"},
    {"name": "Caractere"},
    {"name": "Pinyin"},
    {"name": "Áudio Caractere"},
    {"name": "Frase Caracteres"},
    {"name": "Frase Pinyin"},
    {"name": "Áudio Frase"},
    {"name": "Tradução"},
]

TEMPLATES = [
    {
        "name": "Card 1",
        "qfmt": "{{Ordem Traços}}<br><br>{{Caractere}}<br><br>{{Frase Caracteres}}",
        "afmt": (
            "{{FrontSide}}<hr id=answer>"
            "{{Pinyin}}<br>{{Áudio Caractere}}<br>"
            "{{Frase Pinyin}}<br>{{Áudio Frase}}<br><br>{{Tradução}}"
        ),
    }
]

CSS = (
    ".card { font-family: \"Helvetica Neue\", Helvetica, Arial, sans-serif; "
    "font-size: 22px; text-align: center; color: black; background-color: white; }"
)
