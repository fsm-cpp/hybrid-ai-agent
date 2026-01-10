# Smart Online Assistant (Deep Historical Awareness)

This project is a local AI assistant using Ollama and Playwright, featuring web search and hybrid memory. It understands conversational context, rewrites search queries, and answers using both live search results and conversation history.

## Project Structure

```
hybrid_agent_project/
├── config.py             # Global configuration and constants (model names, context window, search limits, etc.)
├── utils.py              # Utility helper functions (e.g., trimming history length).
├── memory.py             # Memory management: load, save, and summarize conversation history.
├── search.py             # Web search functions using Playwright for scraping and pagination.
├── agent.py              # Core AI agent combining memory, search, and LLM interactions.
├── main.py               # Entry point to initialize and run the assistant.
├── requirements.txt      # Project dependencies.
├── README.md             # Project documentation.
└── hybrid_memory.json    # Memory file storing conversation history; created/updated at runtime.
```

## Features

*   **Hybrid Memory Modes**: Supports `raw` (full-text) and `zip` (summarized) memory modes. In `zip` mode the assistant compresses past content to save context tokens.
*   **Deep Historical Awareness**: `analyze_intent` rewrites search queries using a small window of recent history to improve relevance.
*   **Smart Web Search**: Uses DuckDuckGo for queries and Playwright to simulate browsing, pagination, and content extraction.
*   **Commands**:
    *   `/s <text>`: Force an online search; the assistant will rewrite the query using history and `<text>`.
    *   `/n <text>`: Force no-online-search; answer only from known knowledge and memory.
    *   `/raw`: Switch memory mode to `raw`.
    *   `/zip`: Switch memory mode to `zip` (summarized).
    *   `/clear`: Clear all stored memory.
    *   `exit`, `quit`, `q`: Exit the program.
*   **Configurable**: All key parameters are editable in `config.py`.

## Setup

1.  **Python environment**: Ensure Python 3.9+ is installed.

2.  **Ollama**:
    *   Install Ollama following instructions at [ollama.com](https://ollama.com/).
    *   Pull required model(s) (e.g., `qwen3:30b-instruct`). Run:
        ```bash
        ollama run qwen3:30b-instruct
        # wait for the model to download
        ```
        Make sure `MODEL_NAME` and `SUMMARY_MODEL` in `config.py` match an available local model.

3.  **Install dependencies**:
    ```bash
    cd hybrid_agent_project
    pip install -r requirements.txt
    ```

4.  **Install Playwright browser**:
    ```bash
    playwright install chromium
    ```

## Running the Assistant

From the `hybrid_agent_project` directory run:

```bash
python main.py
```

Or run as a module:

```bash
python -m hybrid_agent_project.main
```

## Usage

On startup you should see a prompt like:

```
=== Smart Online Assistant V7.0 (Deep Historical Awareness) ===
Commands: /s <text> (force-search, assistant rewrites query) | /n <text> (no-search) | /raw (raw memory) | /zip (summarize memory) | /clear (clear memory)
--------------------------------------------------

You [📉 compressed]:
```

Type questions or use commands to interact with the assistant.

Example conversation:

```
You [📉 compressed]: Any recent developments in AI models?
AI is thinking...
AI: ... (performs online search and responds)

You [📉 compressed]: /s Bill Gates net worth
🔧 [manual force-search] Assistant rewrites query -> Bill Gates net worth
>> 🌐 Performing web search and simulated pagination: Bill Gates net worth
... (search process)
AI is thinking...
AI: ... (responds based on search results)

You [📉 compressed]: /raw
>> Mode switched to: raw
You [📝 raw]: Has he launched any new philanthropy projects recently?
AI is thinking...
AI: ... (answers using history or additional search; 'he' is resolved to Bill Gates)

You [📝 raw]: /clear
Memory cleared!
You [📝 raw]:
```
Real chat examples are in `real_chat.txt`.

## Configuration

Edit `config.py` to adjust assistant behavior:

*   `MODEL_NAME`, `SUMMARY_MODEL`: change the Ollama models used.
*   `HEADLESS`, `HIDE_WINDOW`: control Playwright browser visibility.
*   `CONTEXT_WINDOW`: set the model context window size.
*   `MAX_SEARCH_RESULTS`, `MAX_PAGES_TO_SCAN`: tune search behavior.
*   `HISTORY_LIMIT`: how many recent turns are considered for intent analysis.
*   `MEMORY_FILE`: change the memory filename.

## Notes

*   Web search success depends on network conditions and target sites' anti-scraping measures.
*   Ollama model performance and response quality depend on the model chosen.
*   To completely hide the browser set `HIDE_WINDOW = True`.
*   To show the browser set `HIDE_WINDOW = False`.


## ⚠️ License / Copyright

**Copyright (c) 2026 Feng Simo. All rights reserved.**

This code is for demonstration purposes only. You may not use, modify, distribute, or sublicense this code.
