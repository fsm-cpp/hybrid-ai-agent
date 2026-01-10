# main.py
"""
Entry point: initialize and run the ChatAgent.
"""
from colorama import init, Fore, Style
from agent import ChatAgent

if __name__ == "__main__":
    # initialize colorama so colors reset after each print
    init(autoreset=True)
    
    try:
        agent = ChatAgent()
        agent.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
