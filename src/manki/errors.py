"""Hierarquia de erros da aplicação.

Cada adaptador externo traduz suas falhas (HTTP, API, parsing) para uma dessas
exceções, de modo que o pipeline lide apenas com erros do domínio.
"""


class MankiError(Exception):
    """Erro base de todos os erros previstos da aplicação."""


class ConfigurationError(MankiError):
    """Configuração ausente ou inválida (chave de API, provedor desconhecido...)."""


class LLMError(MankiError):
    """Falha ao obter dados estruturados do provedor de LLM."""


class AudioError(MankiError):
    """Falha ao sintetizar áudio."""


class StrokeOrderError(MankiError):
    """Falha ao obter a ordem dos traços de um caractere."""


class DeckExportError(MankiError):
    """Falha ao empacotar o baralho."""
