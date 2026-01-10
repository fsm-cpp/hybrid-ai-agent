# Smart Online Assistant (Deep Historical Awareness)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/AI-Ollama-000000?logo=ollama&logoColor=white)](https://ollama.com/)
[![Playwright](https://img.shields.io/badge/Web-Playwright-45ba4b?logo=playwright&logoColor=white)](https://playwright.dev/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

> **An intelligent local AI agent featuring autonomous web search, hybrid memory management, and context-aware query rewriting.**

## 📖 Overview

**Smart Online Assistant** is a privacy-first, local AI agent powered by **Ollama** (LLMs) and **Playwright**. Unlike standard chatbots, it bridges the gap between offline privacy and real-time information.

It implements a **RAG (Retrieval-Augmented Generation)** workflow that autonomously browses the web when necessary, rewrites search queries based on conversation history, and manages context using a unique **Hybrid Memory (Raw/Zip)** system.

## ✨ Key Features

*   **🌐 Autonomous Web Search**: Uses Playwright to simulate human browsing (DuckDuckGo), handling pagination and anti-scraping to fetch real-time data without API costs.
*   **🧠 Hybrid Memory Architecture**:
    *   **Raw Mode**: Retains full-text conversation history.
    *   **Zip Mode**: Automatically summarizes past interactions to save context window tokens while retaining key facts.
*   **🔄 Context-Aware Intent Analysis**: The agent analyzes your intent (`analyze_intent`) and rewrites search keywords using recent history to ensure search results are relevant.
*   **⚡ Local & Private**: Powered entirely by local models (e.g., `qwen3:30b-instruct`). Your data stays on your machine.
*   **🛠️ Full Control**: Force search (`/s`), force offline (`/n`), or switch memory modes instantly via commands.

## 🚀 Quick Start

### Prerequisites
1.  **Python 3.9+** installed.
2.  **[Ollama](https://ollama.com/)** installed and running.

### Installation

1.  **Clone the repository** (if applicable) or download the source.

2.  **Install Python dependencies**:
    ```bash
    cd hybrid_agent_project
    pip install -r requirements.txt
    ```

3.  **Install Playwright Browser**:
    ```bash
    playwright install chromium
    ```

4.  **Prepare the Model**:
    Pull the required model (ensure it matches `MODEL_NAME` in `config.py`):
    ```bash
    ollama run qwen3:30b-instruct
    # Wait for the model to download
    ```

### Running the Assistant

Run the main script:
```bash
python main.py
```

Or run as a module:

```bash
python -m hybrid_agent_project.main
```

## 💡 Usage

Once started, interact with the agent naturally or use the following commands:

| Command | Description |
| :--- | :--- |
| `/s <text>` | **Force Search**: Rewrites query based on history + `<text>` and searches the web. |
| `/n <text>` | **No Search**: Forces the LLM to answer from internal knowledge/memory only. |
| `/raw` | Switch memory to **Full-text** mode. |
| `/zip` | Switch memory to **Summarized** mode (saves tokens). |
| `/clear` | Clear all conversation history. |
| `exit` / `q` | Quit the application. |

### 📄 Real-World Examples
> **Check [`real_chat.txt`](real_chat.txt) for a full log of actual conversations, search processes, and memory compression in action.**

### Example Output
```text
You [📉 compressed]: /s Bill Gates net worth
🔧 [manual force-search] Assistant rewrites query -> Bill Gates net worth 2026
>> 🌐 Performing web search and simulated pagination...
AI is thinking...
AI: ... (Responds based on live search results)
```

## ⚙️ Configuration

Edit `config.py` to customize the agent's behavior:

*   `MODEL_NAME`: The Ollama model to use (default: `qwen3:30b-instruct`).
*   `SUMMARY_MODEL`: The model used for compressing memory.
*   `HIDE_WINDOW`: Set to `False` to watch the browser scrape in real-time.
*   `HISTORY_LIMIT`: Number of turns used for intent analysis.
*   `MEMORY_FILE`: Path to the JSON memory file.

## 📂 Project Structure

```text
hybrid_agent_project/
├── agent.py              # Core Logic: Combines LLM, Memory, and Search
├── search.py             # Web Scraping: Playwright & DuckDuckGo integration
├── memory.py             # Memory System: JSON handling & Summarization
├── config.py             # Settings: Models, timeouts, search limits
├── main.py               # Entry Point: CLI Loop
├── utils.py              # Helpers: Text processing
├── real_chat.txt         # Log of real usage examples
└── requirements.txt      # Dependencies
```

## ⚠️ License / Copyright

**Copyright (c) 2026 Feng Simo. All rights reserved.**

This code is for **demonstration purposes only**. You may not use, modify, distribute, or sublicense this code without explicit permission.