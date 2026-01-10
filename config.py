# config.py
"""
Global configuration and constants
"""
import os

# === ⚙️ Global configuration ===
MODEL_NAME = "qwen3:30b-instruct"      # primary conversational model
SUMMARY_MODEL = "qwen3:30b-instruct"   # memory summarization model
HEADLESS = False                    # False = show browser
CONTEXT_WINDOW = 32768              # context window size

# === ⚙️ Tunable configuration parameters ===
MAX_SEARCH_RESULTS = 15      # max number of pages to fetch and extract content from
MAX_PAGES_TO_SCAN = 2        # how many search result pages to scan (each page adds ~10-15 links)
HISTORY_LIMIT = 5                   
MEMORY_FILE = "hybrid_memory.json" # path to memory file
HIDE_WINDOW = True # hide the browser window off-screen (Playwright arg: --window-position)

# Common Ollama model options
OLLAMA_COMMON_OPTIONS = {
    'num_ctx': CONTEXT_WINDOW,
    'temperature': 0.6,
}
KEEP_ALIVE = "60m" 
# ===================================

# Ensure the memory file path is absolute or relative to the script directory
MEMORY_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), MEMORY_FILE)
