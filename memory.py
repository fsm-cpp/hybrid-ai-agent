# memory.py
"""
记忆管理模块
"""
import json
import os
import ollama
from colorama import Fore, Style

from config import MEMORY_FILE_PATH, SUMMARY_MODEL, OLLAMA_COMMON_OPTIONS, KEEP_ALIVE

class HybridMemory:
    """混合记忆管理器"""
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
                print(f"{Fore.GREEN}>> 📂 已加载历史记忆 ({len(self.history)} 条){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}>> ⚠️ 记忆文件加载失败: {e}. 将创建新的记忆文件.{Style.RESET_ALL}")
                self.history = [] # 确保即使加载失败，也能继续运行

    def save(self):
        with open(MEMORY_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({'mode': self.mode, 'history': self.history}, f, ensure_ascii=False, indent=2)

    def set_mode(self, new_mode):
        self.mode = new_mode
        self.save()
        print(f"{Fore.BLUE}>> 模式已切换到: {new_mode}{Style.RESET_ALL}")

    def add_turn(self, user_text, ai_text):
        if self.mode == 'raw':
            print(f"{Fore.BLUE}>> 📝 [原文模式] 已记录本轮对话{Style.RESET_ALL}")
            self.history.append({'role': 'user', 'content': user_text})
            self.history.append({'role': 'assistant', 'content': ai_text})
        else:
            print(f"{Fore.BLUE}>> 📉 [压缩模式] 正在提炼回答摘要(保留User原文)...{Style.RESET_ALL}")
            prompt = f"请将以下AI的回答提炼为100字内的核心事实摘要，保留关键结论：\n内容：{ai_text}\n摘要:"
            try:
                resp = ollama.generate(
                    model=SUMMARY_MODEL, 
                    prompt=prompt, 
                    keep_alive=KEEP_ALIVE,
                    options=OLLAMA_COMMON_OPTIONS
                )
                summary_ai = resp['response'].strip().split("</think>")[-1].strip()
                print(f"{Fore.CYAN}   + 回答已浓缩: {summary_ai[:30]}...{Style.RESET_ALL}")
                
                self.history.append({'role': 'user', 'content': user_text})
                self.history.append({'role': 'assistant', 'content': summary_ai})
            except Exception as e:
                print(f"{Fore.RED}>> 压缩摘要失败: {e}。将以原文形式记录AI回答。{Style.RESET_ALL}")
                self.history.append({'role': 'user', 'content': user_text})
                self.history.append({'role': 'assistant', 'content': ai_text})
        self.save()

    def get_full_history(self):
        return self.history
