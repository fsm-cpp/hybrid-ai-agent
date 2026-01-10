# memory.py
"""
Memory management module
"""
import json
import os
import ollama
from colorama import Fore, Style

from config import MEMORY_FILE_PATH, SUMMARY_MODEL, OLLAMA_COMMON_OPTIONS, KEEP_ALIVE

class HybridMemory:
    """Hybrid memory manager"""
    def __init__(self, mode="zip"):
        self.mode = mode
        self.history = []
        self.load()

    def load(self):
        if os.path.exists(MEMORY_FILE_PATH):
            try:
                with open(MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.mode = data.get('mode', self.mode)
                print(f"{Fore.GREEN}>> 📂 Loaded history memory ({len(self.history)} items){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}>> ⚠️ Failed to load memory file: {e}. A new memory file will be created.{Style.RESET_ALL}")
                self.history = [] # ensure the program can continue even if loading fails

    def save(self):
        with open(MEMORY_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({'mode': self.mode, 'history': self.history}, f, ensure_ascii=False, indent=2)

    def set_mode(self, new_mode):
        self.mode = new_mode
        self.save()
        print(f"{Fore.BLUE}>> Mode switched to: {new_mode}{Style.RESET_ALL}")

    def add_turn(self, user_text, ai_text):
        if self.mode == 'raw':
            print(f"{Fore.BLUE}>> 📝 [raw mode] Recorded this conversation turn{Style.RESET_ALL}")
            self.history.append({'role': 'user', 'content': user_text})
            self.history.append({'role': 'assistant', 'content': ai_text})
        else:
            print(f"{Fore.BLUE}>> 📉 [zip mode] Condensing AI response into a brief summary (keeping user text)...{Style.RESET_ALL}")
            prompt = f"Please condense the following AI response into a factual summary within 100 characters, preserving key conclusions:\nContent: {ai_text}\nSummary:"
            try:
                resp = ollama.generate(
                    model=SUMMARY_MODEL, 
                    prompt=prompt, 
                    keep_alive=KEEP_ALIVE,
                    options=OLLAMA_COMMON_OPTIONS
                )
                summary_ai = resp['response'].strip().split("</think>")[-1].strip()
                print(f"{Fore.CYAN}   + Response condensed: {summary_ai[:30]}...{Style.RESET_ALL}")
                
                self.history.append({'role': 'user', 'content': user_text})
                self.history.append({'role': 'assistant', 'content': summary_ai})
            except Exception as e:
                print(f"{Fore.RED}>> Failed to summarize response: {e}. Saving AI response as original text.{Style.RESET_ALL}")
                self.history.append({'role': 'user', 'content': user_text})
                self.history.append({'role': 'assistant', 'content': ai_text})
        self.save()

    def get_full_history(self):
        return self.history
