# Manki - Gerador Automático de Flashcards de Mandarim para o Anki

**Manki** é uma ferramenta em Python que automatiza a criação de flashcards de Mandarim (chinês simplificado) prontos para importar no **Anki**.

Cada palavra vira um cartão com frase de exemplo contextual (nível HSK 3), pinyin, tradução para o inglês, áudio da palavra e da frase (TTS) e a animação da ordem dos traços de cada caractere.

---

## 🚀 Funcionalidades

1. **Geração de conteúdo por LLM**: tradução da palavra isolada, frase de exemplo natural (HSK 3) e o pinyin correspondente. Provedores suportados: DeepSeek, Groq, OpenAI, LM Studio (local) e Google Gemini.
2. **Áudio automático (TTS)**: `.mp3` para a palavra e para a frase, via `gTTS`.
3. **Ordem dos traços**: animações extraídas de *strokeorder.com*, com cache por caractere e novas tentativas automáticas.
4. **Empacotamento `.apkg`**: baralho formatado com campos dedicados para áudio, pinyin, caracteres e traços.
5. **Processamento paralelo**: as palavras do lote são processadas simultaneamente; uma falha isolada não interrompe as demais.

---

## 📂 Arquitetura

O projeto segue *ports & adapters*: o pipeline depende apenas de interfaces (`manki.domain.ports`), e as implementações concretas são injetadas pela CLI. Trocar de provedor de LLM, de TTS ou da fonte de traços não exige tocar na lógica de orquestração.

```
src/manki/
├── cli.py              # Argumentos, composição das dependências e códigos de saída
├── config.py           # Settings a partir de .env/ambiente + presets por provedor
├── pipeline.py         # Orquestração: palavras → cartões (paralelo, tolerante a falhas)
├── errors.py           # Hierarquia de exceções do domínio
├── logging_setup.py    # Configuração de logging
├── domain/
│   ├── models.py       # WordRequest, FlashcardData (Pydantic), CardAssets, Card
│   └── ports.py        # Protocolos: LLMProvider, AudioSynthesizer, StrokeOrderProvider, DeckBuilder
├── inputs/parser.py    # Leitura e interpretação do arquivo de entrada
├── providers/
│   ├── llm/            # prompts.py + adaptadores OpenAI-compatível e Gemini + factory
│   ├── audio/          # gTTS
│   └── strokes/        # scraping de strokeorder.com (sessão com retry e timeout)
└── anki/
    ├── deck.py         # Montagem e exportação com genanki
    └── templates.py    # Campos, templates e CSS do tipo de nota
tests/                  # Testes com dublês das portas — nenhuma chamada de rede
```

Decisões relevantes:

- **Provedor por configuração, não por código**: cada provedor tem um preset (URL base, modelo padrão, variável da chave e o modo de saída estruturada que suporta) em `config.py`.
- **Mídias em diretório temporário**: os `.mp3` não são mais escritos na raiz do projeto e somem sozinhos ao final.
- **Rede com limites**: toda requisição tem timeout e retry — antes um servidor lento podia travar a execução indefinidamente.
- **Falhas isoladas**: um erro em uma palavra é registrado e reportado no fim; o baralho é gerado com o restante.

---

## 🛠️ Pré-requisitos

- **Python 3.10** ou superior.
- Conexão com a internet (TTS, scraping e API do LLM).
- **Opcional**: [LM Studio](https://lmstudio.ai/) rodando localmente, para usar um modelo sem nuvem.

---

## ⚙️ Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .                 # ou: pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha a chave do provedor que for usar:

```bash
cp .env.example .env
```

```env
MANKI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sua_chave_aqui
```

Para usar o LM Studio não é preciso chave: `MANKI_PROVIDER=lmstudio`.

---

## 🎯 Como Usar

### Arquivo de entrada (recomendado)

Crie um `input.txt` com uma palavra por linha, opcionalmente com uma frase customizada após `:` ou `：`. Linhas vazias e iniciadas por `#` são ignoradas:

```text
作弊: 你真的作弊了
亮: 还真能亮
性格: 挺有性格
# sem frase customizada: a IA cria uma focada em HSK 3
减肥
```

```bash
manki                    # lê input.txt
manki meus_cards.txt     # outro arquivo
python -m manki          # equivalente, sem instalar o console script
python main.py           # atalho compatível com a versão anterior
```

### Palavras direto no terminal

```bash
manki --words 电脑 苹果 飞机
```

Sem arquivo e sem `--words`, o programa pergunta as palavras interativamente.

### Opções

| Opção | Descrição |
| --- | --- |
| `-p, --provider` | `deepseek`, `groq`, `lmstudio`, `openai` ou `gemini` |
| `-m, --model` | Modelo específico (sobrescreve o padrão do provedor) |
| `-o, --output` | Caminho do `.apkg` gerado (padrão: `flashcards.apkg`) |
| `-d, --deck` | Nome do baralho no Anki (padrão: `Mandarim`) |
| `-j, --workers` | Palavras processadas em paralelo (padrão: 4) |
| `--dry-run` | Mostra as palavras interpretadas sem chamar nenhuma API |
| `--log-level` | `DEBUG`, `INFO`, `WARNING` ou `ERROR` |

Tudo também pode vir do ambiente: `MANKI_PROVIDER`, `MANKI_MODEL`, `MANKI_BASE_URL`, `MANKI_DECK_NAME`, `MANKI_OUTPUT`, `MANKI_WORKERS`, `MANKI_TIMEOUT`, `MANKI_LOG_LEVEL`.

**Códigos de saída**: `0` sucesso · `1` erro fatal (configuração, entrada ou exportação) · `2` baralho gerado com falhas parciais.

---

## 🧪 Testes

```bash
pip install -e ".[dev]"
pytest
```

Os testes usam dublês das portas do domínio — não fazem chamadas de rede nem consomem créditos de API.

---

## 📥 Importando no Anki

Abra o **Anki**, vá em **Arquivo > Importar...** e escolha o `flashcards.apkg` gerado.
