# agent.py
"""
Core AI agent module integrating memory management and search functionality.
"""
import json
import ollama
from colorama import Fore, Style

from memory import HybridMemory
from search import SearchEngine
from utils import get_limited_msgs
from config import MODEL_NAME, OLLAMA_COMMON_OPTIONS, KEEP_ALIVE

class ChatAgent:
    def __init__(self):
        self.memory = HybridMemory()
        self.searcher = SearchEngine()

    def analyze_intent(self, current_query):
        """Intent analysis: use a limited window of history to analyze and rewrite search keywords"""
        full_history = self.memory.get_full_history()
        limited_history = get_limited_msgs(full_history)
        
        # exclude system prompts, keep only actual conversation
        history_for_prompt = []
        for msg in limited_history:
            if msg['role'] != 'system':
                history_for_prompt.append(f"{msg['role']}: {msg['content']}")
        history_text = "\n".join(history_for_prompt)
        
        prompt = (
            f"You are a search expert. Your task is to analyze the conversation history and extract the most suitable search keywords for the user's question.\n\n"
            f"Conversation history:\n{history_text}\n"
            f"User current input: {current_query}\n\n"
            f"Requirements:\n"
            f"1. Decide whether a live web search is needed for facts or specific references.\n"
            f"2. Extract search keywords: combine with historical context and replace vague pronouns (e.g., 'he', 'that event', 'this person') with concrete entity names.\n"
            f"3. Keywords should be concise and precise, suitable for search engines.\n"
            f"4. If no search is needed, the keywords may be an empty string \"\".\n\n"
            f"Return strictly in the following JSON format with no extra characters:\n"
            f"{{\"search\": true/false, \"keywords\": \"optimized keywords\"}}"
        )
        try:
            print(f"{Fore.BLUE}>> 🤖 Analyzing context and rewriting search keywords...{Style.RESET_ALL}")
            res = ollama.chat(
                model=MODEL_NAME, 
                messages=[{'role':'user', 'content':prompt}], 
                format='json',
                keep_alive=KEEP_ALIVE,
                options=OLLAMA_COMMON_OPTIONS
            )
            data = json.loads(res['message']['content'])
            
            # Regardless of whether the model returns search True/False, use keywords if present
            # Ensure keywords is a string; accept empty string
            keywords = data.get('keywords', current_query)
            if not isinstance(keywords, str): # prevent model returning non-string types
                keywords = current_query 
            
            return data.get('search', False), keywords
        except Exception as e:
            print(f"{Fore.RED}>> ⚠️ Intent analysis error: {e}. Falling back to original input and defaulting to no search.{Style.RESET_ALL}")
            return False, current_query

    def run(self):
        self.searcher.start()
        print(f"\n{Fore.CYAN}=== Smart Online Assistant V7.0 (Deep Historical Awareness) ==={Style.RESET_ALL}")
        print(f"Commands: {Fore.GREEN}/s <text>{Style.RESET_ALL} force-search (assistant rewrites query) | {Fore.GREEN}/n <text>{Style.RESET_ALL} no-search | {Fore.GREEN}/raw{Style.RESET_ALL} raw memory | {Fore.GREEN}/zip{Style.RESET_ALL} summarize memory | {Fore.GREEN}/clear{Style.RESET_ALL} clear memory")
        print("-" * 50)

        try:
            while True:
                mode_icon = "📝 raw" if self.memory.mode == 'raw' else "📉 zip"
                user_in = input(f"\n{Fore.GREEN}You [{mode_icon}]: {Style.RESET_ALL}").strip()
                
                if user_in.lower() in ['exit', 'quit', 'q']: 
                    print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                    break
                if not user_in: continue

                if user_in.startswith("/"):
                    if user_in == "/raw": self.memory.set_mode('raw'); continue
                    if user_in == "/zip": self.memory.set_mode('zip'); continue
                    if user_in == "/clear": self.memory.history=[]; self.memory.save(); print(f"{Fore.YELLOW}Memory cleared!{Style.RESET_ALL}"); continue
                
                need_search = False
                kw = user_in # default keywords are the user's raw input
                target_question = user_in # actual question submitted to the AI

                if user_in.startswith("/s "):
                    target_question = user_in[3:].strip()
                    if not target_question:
                        print(f"{Fore.RED}Error: /s requires content after the command.{Style.RESET_ALL}")
                        continue
                    need_search = True
                    # call analyze_intent to get history-rewritten keywords; ignore model's search decision
                    _, kw = self.analyze_intent(target_question)
                    print(f"{Fore.MAGENTA}🔧 [manual force-search] Assistant rewrote keywords -> {Fore.WHITE}{kw}{Style.RESET_ALL}")
                
                elif user_in.startswith("/n "):
                    target_question = user_in[3:].strip()
                    if not target_question:
                        print(f"{Fore.RED}Error: /n requires content after the command.{Style.RESET_ALL}")
                        continue
                    need_search = False
                    kw = "" # explicitly no search; set keywords empty
                    print(f"{Fore.MAGENTA}🔧 [manual no-search] Answering based only on known memory{Style.RESET_ALL}")
                
                else:
                    # automatic mode
                    need_search, kw = self.analyze_intent(user_in)
                    target_question = user_in # in automatic mode, the submitted question is the user input
                    if need_search:
                        if kw: # only notify if keywords are non-empty
                            print(f"{Fore.MAGENTA}💡 [auto suggestion] Web search keywords -> {Fore.WHITE}{kw}{Style.RESET_ALL}")
                        else: # if AI suggests search but provides empty keywords, skip
                            print(f"{Fore.LIGHTBLACK_EX}💡 [auto suggestion] AI recommends searching but provided no keywords; skipping search.{Style.RESET_ALL}")
                            need_search = False

                search_data = ""
                if need_search and kw: # only run search when need_search is True and kw is non-empty
                    docs = self.searcher.search(kw)
                    if docs: 
                        search_data = "\n\n[Live references]:\n" + "\n".join(docs)
                    else:
                        print(f"{Fore.LIGHTBLACK_EX}   [-] No valid search results were obtained.{Style.RESET_ALL}")

                # generate answer
                full_history = self.memory.get_full_history()
                limited_history = get_limited_msgs(full_history)
                
                # System prompt to guide assistant behavior
                system_prompt = (
                    "You are a professional and helpful AI assistant. Answer based on the following principles:\n"
                    "1. Prefer using your own knowledge and conversation history to answer.\n"
                    "2. If [Live references] are provided, prioritize extracting information from them for facts, data, or recent information.\n"
                    "3. If references conflict with internal knowledge, prefer the references and cite sources.\n"
                    "4. Keep answers concise and accurate; avoid redundancy.\n"
                    "5. If references are insufficient to answer, state that you can only answer based on known information.\n"
                    "6. Avoid mentioning you are an AI model; do not say you don't know the source—integrate and answer directly.\n"
                )
                msgs = [{'role':'system', 'content': system_prompt}]
                
                # add limited conversation history
                msgs.extend(limited_history)
                
                # add current user question and search data
                final_user_content = f"{search_data}\n----------------\nCurrent question: {target_question}"
                msgs.append({'role':'user', 'content': final_user_content})

                print(f"\n{Fore.BLUE}AI is thinking...{Style.RESET_ALL}")
                stream = ollama.chat(
                    model=MODEL_NAME, 
                    messages=msgs, 
                    stream=True, 
                    options=OLLAMA_COMMON_OPTIONS,
                    keep_alive=KEEP_ALIVE
                )
                
                print(f"{Fore.MAGENTA}AI: {Style.RESET_ALL}", end="", flush=True)
                full = ""
                for chunk in stream:
                    c = chunk['message']['content']
                    print(c, end="", flush=True)
                    full += c
                print("\n" + "-"*50)
                
                self.memory.add_turn(target_question, full) # record the actual user question (not the command)
                # To prevent memory bloat, periodically compress or clean old memory (optional)
                # if len(self.memory.history) > 100: # example: compress old turns if conversation rounds exceed 100
                #     self.memory.compress_old_turns()

        except KeyboardInterrupt: 
            print(f"\n{Fore.YELLOW}User interrupted, exiting.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}An exception occurred: {e}{Style.RESET_ALL}")
        finally: 
            self.searcher.stop()
