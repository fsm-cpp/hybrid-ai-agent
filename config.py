# config.py
"""
全局配置和常量
"""
import os

# === ⚙️ 全局配置区域 ===
MODEL_NAME = "qwen3:30b-instruct"      # 主对话模型
SUMMARY_MODEL = "qwen3:30b-instruct"   # 记忆压缩模型
HEADLESS = False                    # False=显示浏览器
CONTEXT_WINDOW = 32768              # 上下文窗口大小

# === ⚙️ 修改后的配置参数 ===
MAX_SEARCH_RESULTS = 30      # 最终决定阅读并抓取正文的网页总数
MAX_PAGES_TO_SCAN = 4        # 搜索结果翻页次数（每翻一页约增加10-15条链接）
HISTORY_LIMIT = 5                   
MEMORY_FILE = "hybrid_memory.json" # 记忆文件路径
HIDE_WINDOW = True # 是否将浏览器窗口隐藏到屏幕外 (Playwright args中的 --window-position)

# 统一Ollama模型参数
OLLAMA_COMMON_OPTIONS = {
    'num_ctx': CONTEXT_WINDOW,
    'temperature': 0.6,
}
KEEP_ALIVE = "60m" 
# ===================================

# 确保memory文件路径是绝对路径，或相对于脚本运行目录
MEMORY_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), MEMORY_FILE)
