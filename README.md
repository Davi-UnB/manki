# Manki - Gerador Automático de Flashcards de Mandarim para o Anki

**Manki** é uma ferramenta modular em Python desenvolvida para automatizar a criação de flashcards de Mandarim (chinês simplificado) altamente informativos e prontos para serem importados no **Anki**.

O projeto utiliza Inteligência Artificial (LLMs locais via LM Studio ou nuvem via Google Gemini) para criar frases de exemplo contextuais (focadas no nível HSK 3) com pinyin e tradução para o inglês, além de enriquecer cada cartão com áudio falado (TTS) e imagens que ensinam a ordem dos traços de escrita de cada caractere.

---

## 🚀 Funcionalidades

1. **Geração de Conteúdo Inteligente (LLM)**:
   - Tradução da palavra de forma isolada para o inglês.
   - Criação de uma frase natural de exemplo usando a palavra estudada (adequada ao nível HSK 3).
   - Conversão da frase para Pinyin.
2. **Geração Automática de Áudios (TTS)**:
   - Gravação de áudios em formato `.mp3` para a pronúncia da palavra isolada e da frase de exemplo em chinês simplificado.
3. **Ordem de Escrita dos Traços (Stroke Order)**:
   - Extração automática de animações e imagens demonstrando como escrever cada caractere a partir do site *Stroke Order*.
4. **Empacotamento Automático para o Anki (`.apkg`)**:
   - Cria um baralho formatado e estilizado com campos dedicados para áudio, pinyin, caracteres e traços de escrita.

---

## 📂 Estrutura do Projeto

*   **`main.py`**: Ponto de entrada do script que interage com o usuário, lê as palavras e coordena o fluxo de criação.
*   **`config.py`**: Gerenciamento de chaves de API, variáveis de ambiente e parâmetros do Anki (IDs do modelo e do baralho).
*   **`models.py`**: Define o modelo de dados dos flashcards estruturado com **Pydantic**.
*   **`llm_service.py`**: Gerencia a comunicação com as APIs de LLM (Google Gemini ou LM Studio / OpenAI).
*   **`audio_service.py`**: Responsável pela geração de arquivos de áudio em mandarim usando `gTTS`.
*   **`scraper_service.py`**: Realiza o scraping no site *Stroke Order* para obter o passo a passo da escrita dos ideogramas.
*   **`anki_builder.py`**: Cria a estrutura do deck, associa mídias e exporta o pacote final no formato `.apkg`.

---

## 🛠️ Pré-requisitos

*   **Python 3.9** ou superior.
*   Conexão com a internet (para TTS, scraping e API do Gemini).
*   **Opcional**: [LM Studio](https://lmstudio.ai/) instalado e rodando com um modelo local se não for usar a API do Gemini.

---

## ⚙️ Instalação e Configuração

1.  **Clone o repositório ou navegue até a pasta do projeto**:
    ```bash
    cd manki
    ```

2.  **Crie e ative um ambiente virtual**:
    *   No macOS/Linux:
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```
    *   No Windows:
        ```cmd
        python -m venv .venv
        .venv\Scripts\activate
        ```

3.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuração de Variáveis de Ambiente**:
    Se você deseja usar o **Google Gemini**, crie um arquivo chamado `.env` na raiz do projeto e insira sua chave de API:
    ```env
    GEMINI_API_KEY="SUA_CHAVE_API_AQUI"
    ```
    
    *Nota: Se preferir usar um modelo local rodando no **LM Studio**, configure `USE_GEMINI = False` no arquivo `config.py`.*

---

## 🎯 Como Usar

Você pode usar o **Manki** de duas formas: através de um arquivo de entrada (recomendado e mais flexível) ou de forma interativa via terminal.

### Opção A: Usando arquivo de entrada (Recomendado)

Esta opção permite gerar flashcards em lote e definir **frases de exemplo customizadas** para cada caractere.

1. Crie um arquivo de texto (por padrão chamado `input.txt`) na raiz do projeto.
2. Escreva as palavras e frases no formato `palavra: frase` (uma por linha). Você também pode passar apenas a palavra e deixar a IA gerar a frase para você. Linhas em branco ou iniciadas com `#` são ignoradas.

   **Exemplo de `input.txt`**:
   ```text
   作弊: 你真的作弊了
   亮: 还真能亮
   性格: 挺有性格
   # Esta palavra não tem frase customizada; a IA criará uma focada em HSK 3
   减肥
   散会: 我说散会了吗
   ```

3. Com o ambiente virtual ativo, execute o script principal. Ele detectará automaticamente o arquivo `input.txt` na raiz:
   ```bash
   python main.py
   ```

   *Dica: Você também pode usar um arquivo com outro nome e passá-lo como argumento:*
   ```bash
   python main.py meus_cards.txt
   ```

---

### Opção B: Entrada interativa via Terminal

Se o arquivo `input.txt` (ou o especificado) não for encontrado, o script entrará automaticamente no modo interativo:

1. Execute o script:
   ```bash
   python main.py
   ```
2. Digite as palavras que deseja processar, separadas por espaços:
   ```text
   Insira as palavras (separadas por espaços): 电脑 苹果 飞机
   ```

---

### Processamento e Importação

Para qualquer uma das opções acima, o programa irá:
1. Consultar a IA para obter ou validar as frases de exemplo, pinyin correspondente e traduções.
2. Gerar os áudios `.mp3` correspondentes para a palavra e para a frase.
3. Buscar na web as animações de ordem dos traços dos caracteres.
4. Adicionar os cartões e gerar o arquivo `flashcards.apkg` na raiz do projeto.

Para utilizar no Anki:
- Abra o **Anki** no computador, vá em **Arquivo > Importar...** e escolha o arquivo `flashcards.apkg`.
