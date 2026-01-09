# main.py
"""
程序入口文件，初始化并运行ChatAgent。
"""
from colorama import init, Fore, Style
from agent import ChatAgent

if __name__ == "__main__":
    # 初始化 colorama，使其在每次print后自动重置颜色
    init(autoreset=True)
    
    try:
        agent = ChatAgent()
        agent.run()
    except Exception as e:
        print(f"{Fore.RED}致命错误: {e}{Style.RESET_ALL}")
