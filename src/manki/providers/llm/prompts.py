"""Prompts compartilhados pelos provedores de LLM.

Ficam isolados aqui porque são a parte do sistema que mais muda e a que mais
afeta a qualidade dos cartões — nenhum adaptador deve reescrevê-los por conta.
"""

from manki.domain.models import WordRequest

SYSTEM_PROMPT = (
    "Você é um assistente de criação de flashcards de mandarim para o Anki. "
    "Siga ESTRITAMENTE as regras e preencha os dados no formato JSON solicitado. "
    "Regras para a frase: Crie uma frase de exemplo clara, natural e útil. "
    "Utilize vocabulário e gramática focados no nível HSK 3. "
    "Não limite a frase apenas a pronomes básicos, mas também evite palavras "
    "muito avançadas ou raras (HSK 5+). A frase deve demonstrar o uso real da palavra.\n"
    "Regras para a tradução: O campo 'traducao' deve conter EXCLUSIVAMENTE o significado da palavra "
    "isolada, em INGLÊS. NÃO traduza a frase de exemplo. Retorne apenas definições curtas em inglês."
)

FIELD_GUIDE = (
    "Retorne EXCLUSIVAMENTE um objeto JSON contendo exatamente os seguintes campos:\n"
    "- caractere: palavra em chinês\n"
    "- pinyin: pinyin da palavra com tons corretos\n"
    "- frase_caracteres: frase de exemplo útil nível HSK 3\n"
    "- frase_pinyin: pinyin da frase de exemplo com tons corretos\n"
    "- traducao: tradução curta da palavra para o inglês\n"
    "Não adicione nenhuma formatação Markdown ao redor."
)


def user_prompt(request: WordRequest) -> str:
    """Instrução específica da palavra, respeitando a frase customizada quando houver."""
    base = f"Gere as informações para a palavra em chinês: {request.word}"
    if not request.custom_sentence:
        return base
    return (
        f"{base}\n"
        "IMPORTANTE: Você deve usar OBRIGATORIAMENTE a seguinte frase de exemplo fornecida "
        f"pelo usuário no campo 'frase_caracteres': {request.custom_sentence}\n"
        "Preencha o campo 'frase_pinyin' com o pinyin correto dessa frase fornecida."
    )
