# agent.py
"""
核心AI代理模块，整合记忆管理和搜索功能。
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
        """意图分析：结合受限的全历史进行分析并重构搜索关键词"""
        full_history = self.memory.get_full_history()
        limited_history = get_limited_msgs(full_history)
        
        # 排除系统提示，只保留实际对话
        history_for_prompt = []
        for msg in limited_history:
            if msg['role'] != 'system':
                history_for_prompt.append(f"{msg['role']}: {msg['content']}")
        history_text = "\n".join(history_for_prompt)
        
        prompt = (
            f"你是一个搜索专家。你的任务是分析对话历史，为用户的问题提取最适合搜索引擎的关键词。\n\n"
            f"【对话历史】:\n{history_text}\n"
            f"【用户当前输入】: {current_query}\n\n"
            f"【任务要求】:\n"
            f"1. 判断是否需要联网搜索实时事实或具体资料。\n"
            f"2. 提取搜索关键词：必须结合历史背景，将模糊的代词（如'他'、'那个事件'、'此人'）替换为具体的实体名词。\n"
            f"3. 关键词应简洁、精准，适合搜索引擎检索。\n"
            f"4. 如果不需要搜索，关键词可以为空字符串 \"\"。\n\n"
            f"请严格按照以下 JSON 格式返回，不要有任何多余字符：\n"
            f"{{\"search\": true/false, \"keywords\": \"优化后的关键词内容\"}}"
        )
        try:
            print(f"{Fore.BLUE}>> 🤖 正在分析背景并重构搜索词...{Style.RESET_ALL}")
            res = ollama.chat(
                model=MODEL_NAME, 
                messages=[{'role':'user', 'content':prompt}], 
                format='json',
                keep_alive=KEEP_ALIVE,
                options=OLLAMA_COMMON_OPTIONS
            )
            data = json.loads(res['message']['content'])
            
            # 无论模型返回 search 是 True 还是 False，只要 keywords 存在，我们就拿来用
            # 确保keywords是一个字符串，如果为空也接受
            keywords = data.get('keywords', current_query)
            if not isinstance(keywords, str): # 预防模型返回非字符串类型
                keywords = current_query 
            
            return data.get('search', False), keywords
        except Exception as e:
            print(f"{Fore.RED}>> ⚠️ 意图分析出错: {e}。回退至原始输入，并默认不搜索。{Style.RESET_ALL}")
            return False, current_query

    def run(self):
        self.searcher.start()
        print(f"\n{Fore.CYAN}=== 智能联网助手 V7.0 (深度历史感知) ==={Style.RESET_ALL}")
        print(f"指令: {Fore.GREEN}/s <内容>{Style.RESET_ALL} 强搜(AI改写词) | {Fore.GREEN}/n <内容>{Style.RESET_ALL} 禁搜 | {Fore.GREEN}/raw{Style.RESET_ALL} 原文 | {Fore.GREEN}/zip{Style.RESET_ALL} 压缩 | {Fore.GREEN}/clear{Style.RESET_ALL} 清空记忆")
        print("-" * 50)

        try:
            while True:
                mode_icon = "📝原文" if self.memory.mode == 'raw' else "📉压缩"
                user_in = input(f"\n{Fore.GREEN}你 [{mode_icon}]: {Style.RESET_ALL}").strip()
                
                if user_in.lower() in ['exit', 'quit', '退出', 'q']: 
                    print(f"{Fore.YELLOW}再见！{Style.RESET_ALL}")
                    break
                if not user_in: continue

                if user_in.startswith("/"):
                    if user_in == "/raw": self.memory.set_mode('raw'); continue
                    if user_in == "/zip": self.memory.set_mode('zip'); continue
                    if user_in == "/clear": self.memory.history=[]; self.memory.save(); print(f"{Fore.YELLOW}记忆已清空！{Style.RESET_ALL}"); continue
                
                need_search = False
                kw = user_in # 默认关键词为用户原始输入
                target_question = user_in # 实际提交给AI的问题

                if user_in.startswith("/s "):
                    target_question = user_in[3:].strip()
                    if not target_question:
                        print(f"{Fore.RED}错误: /s 指令后需要内容。{Style.RESET_ALL}")
                        continue
                    need_search = True
                    # 调用 analyze_intent 获取基于历史重构的关键词，忽略模型对"是否该搜"的判断
                    _, kw = self.analyze_intent(target_question)
                    print(f"{Fore.MAGENTA}🔧 [手动强搜] AI 基于背景重构关键词 -> {Fore.WHITE}{kw}{Style.RESET_ALL}")
                
                elif user_in.startswith("/n "):
                    target_question = user_in[3:].strip()
                    if not target_question:
                        print(f"{Fore.RED}错误: /n 指令后需要内容。{Style.RESET_ALL}")
                        continue
                    need_search = False
                    kw = "" # 明确不搜索，关键词设为空
                    print(f"{Fore.MAGENTA}🔧 [手动禁搜] 仅基于已知记忆回答{Style.RESET_ALL}")
                
                else:
                    # 自动模式
                    need_search, kw = self.analyze_intent(user_in)
                    target_question = user_in # 自动模式下，提交给AI的问题就是用户输入
                    if need_search:
                        if kw: # 只有关键词不为空才提示
                            print(f"{Fore.MAGENTA}💡 [自动建议] 联网搜索关键词 -> {Fore.WHITE}{kw}{Style.RESET_ALL}")
                        else: # 如果AI建议搜索但关键词为空，则不进行搜索
                            print(f"{Fore.LIGHTBLACK_EX}💡 [自动建议] AI认为需要搜索但未给出关键词，跳过搜索。{Style.RESET_ALL}")
                            need_search = False

                search_data = ""
                if need_search and kw: # 只有need_search为True且kw不为空时才执行搜索
                    docs = self.searcher.search(kw)
                    if docs: 
                        search_data = "\n\n【实时参考资料】:\n" + "\n".join(docs)
                    else:
                        print(f"{Fore.LIGHTBLACK_EX}   [-] 未获取到有效搜索结果。{Style.RESET_ALL}")

                # 生成回答
                full_history = self.memory.get_full_history()
                limited_history = get_limited_msgs(full_history)
                
                # 系统提示可以更详细一些，指导AI的行为
                system_prompt = (
                    "你是一个专业且乐于助人的AI助手。请基于以下原则回答问题：\n"
                    "1. 优先使用你自己的知识和对话历史来回答。\n"
                    "2. 如果提供了【实时参考资料】，请优先从中提取信息来回答当前问题，尤其是涉及到事实、数据、最新信息等。\n"
                    "3. 如果参考资料与你的内部知识有冲突，请以参考资料为准并注明来源。\n"
                    "4. 回答要简洁、准确，避免冗余和重复。\n"
                    "5. 如果参考资料不足以回答问题，说明你只能根据已知信息回答。\n"
                    "6. 避免提及自己是AI模型，也不要说自己不知道信息来源，直接整合信息回答即可。\n"
                )
                msgs = [{'role':'system', 'content': system_prompt}]
                
                # 添加受限历史对话
                msgs.extend(limited_history)
                
                # 添加当前用户问题和搜索资料
                final_user_content = f"{search_data}\n----------------\n当前问题: {target_question}"
                msgs.append({'role':'user', 'content': final_user_content})

                print(f"\n{Fore.BLUE}AI 正在思考...{Style.RESET_ALL}")
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
                
                self.memory.add_turn(target_question, full) # 记录的是用户实际提问的内容，而不是指令
                # 为了防止内存膨胀，定期清理老旧内存文件（可选）
                # if len(self.memory.history) > 100: # 示例：如果对话轮数超过100，可以考虑压缩旧的
                #     self.memory.compress_old_turns()

        except KeyboardInterrupt: 
            print(f"\n{Fore.YELLOW}用户中断，程序退出。{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}程序发生异常: {e}{Style.RESET_ALL}")
        finally: 
            self.searcher.stop()
