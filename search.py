# search.py
"""
网络搜索模块
"""
import time
from playwright.sync_api import sync_playwright
import trafilatura
# from bs4 import BeautifulSoup # 如果trafilatura足够，可以不需要bs4
from colorama import Fore, Style

from config import HEADLESS, HIDE_WINDOW, MAX_SEARCH_RESULTS, MAX_PAGES_TO_SCAN

class SearchEngine:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    def start(self):
        self.playwright = sync_playwright().start()
        args = [
                   "--disable-blink-features=AutomationControlled", 
                   "--start-maximized",
                ]  
        if HIDE_WINDOW:
            args.extend([
                    "--headless=new", # Playwright推荐的新headless模式
                   "--no-sandbox",
                   "--window-position=-2000,-2000"]) # 将窗口定位在屏幕外
        else:
            args.extend([
                   "--window-position=0, 0"])
        self.browser = self.playwright.chromium.launch(
            headless=HEADLESS, 
            args=args 
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0 Safari/537.36",
            locale="zh-CN"
        )
        print(f"{Fore.GREEN}>> 🌐 浏览器启动成功.{Style.RESET_ALL}")

    def stop(self):
        if self.context: self.context.close()
        if self.browser: self.browser.close()
        if self.playwright: self.playwright.stop()
        print(f"{Fore.GREEN}>> 🌐 浏览器已关闭.{Style.RESET_ALL}")

    def search(self, query):
        """
        根据截图反馈优化的翻页搜索：
        1. 模拟滚动到底部触发"更多结果"按钮。
        2. 精确点击"更多结果"按钮。
        3. 增加点击后的缓冲等待时间，确保动态内容加载。
        """
        page = self.context.new_page()
        docs = []
        unique_links = []
        seen_urls = set()

        max_scan_pages = MAX_PAGES_TO_SCAN # 允许翻页的上限，从配置中读取

        try:
            print(f"{Fore.YELLOW}>> 🌐 正在联网检索并模拟翻页: {query}{Style.RESET_ALL}")
            page.goto(f"https://duckduckgo.com/?q={query}&ia=web", timeout=20000)
            
            pages_clicked = 0
            while len(unique_links) < MAX_SEARCH_RESULTS and pages_clicked < max_scan_pages:
                # 1. 等待初始结果加载
                try:
                    page.wait_for_selector('[data-testid="result"]', timeout=8000)
                except:
                    print(f"{Fore.LIGHTBLACK_EX}   [-] 未找到搜索结果或加载超时，停止翻页。{Style.RESET_ALL}")
                    break

                # 2. 提取当前已加载的所有链接
                # 优先使用data-testid属性，如果没有则回退到h2 a
                locs = page.locator('a[data-testid="result-title-a"]').all()
                if not locs:
                    locs = page.locator('article h2 a').all()

                for l in locs:
                    try:
                        url = l.get_attribute('href')
                        title = l.inner_text().strip()
                        if url and "http" in url and url not in seen_urls:
                            # 过滤掉DuckDuckGo自身的链接
                            if "duckduckgo.com" not in url and "start.duckduckgo.com" not in url:
                                unique_links.append({'title': title, 'url': url})
                                seen_urls.add(url)
                    except Exception as e:
                        # 忽略无法获取属性的元素
                        # print(f"{Fore.RED}   [!] 提取链接时出错: {e}{Style.RESET_ALL}")
                        pass
                
                # 如果当前数量已经达标，提前退出
                if len(unique_links) >= MAX_SEARCH_RESULTS:
                    break

                # 3. 模拟你在截图中的操作：滑到底部点击
                print(f"{Fore.CYAN}   [翻页] 已获取 {len(unique_links)} 条，正在向下滑动寻找按钮...{Style.RESET_ALL}")
                
                # 滚动到底部
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5) # 等待按钮渲染

                # 尝试点击"更多结果"按钮 (根据截图文本匹配)
                btn_selectors = [
                    "button#more-results",
                    "text='更多结果'",
                    "text='More Results'",
                    "a.result--more__btn"
                ]
                
                clicked = False
                for selector in btn_selectors:
                    btn = page.locator(selector).first
                    if btn.count() > 0 and btn.is_visible() and btn.is_enabled():
                        try:
                            btn.scroll_into_view_if_needed() # 确保可见
                            btn.click()
                            pages_clicked += 1
                            print(f"{Fore.CYAN}   [√] 成功点击“更多结果” (第 {pages_clicked} 次){Style.RESET_ALL}")
                            clicked = True
                            # 关键：点击后必须等一会儿，让新结果刷出来
                            time.sleep(2.5) 
                            break
                        except Exception as click_err:
                            # print(f"{Fore.RED}   [!] 点击 {selector} 失败: {click_err}{Style.RESET_ALL}")
                            continue
                
                # 如果没找到按钮，或者点击后链接数没增加，说明已经到底了
                if not clicked:
                    print(f"{Fore.LIGHTBLACK_EX}   [-] 未发现更多结果按钮或无法点击，搜索结束。{Style.RESET_ALL}")
                    break
                
                # 额外检查：如果点击了但结果没变，可能是被拦截或真的没了
                # 简单比较本次循环开始和结束时 unique_links 的数量
                new_links_after_click = len(unique_links)
                if len(unique_links) <= new_links_after_click: # 严格来说，应该比对新抓取的 locs 数量，但为了简化，这样也可
                     # 再次尝试滚动一次看是否触发 (应对懒加载)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1.0)
                    # 重新抓取一次链接，看是否有新增
                    locs_after_scroll = page.locator('a[data-testid="result-title-a"]').all()
                    if not locs_after_scroll:
                        locs_after_scroll = page.locator('article h2 a').all()
                    
                    temp_new_count = 0
                    for l in locs_after_scroll:
                        try:
                            url = l.get_attribute('href')
                            title = l.inner_text().strip()
                            if url and "http" in url and url not in seen_urls:
                                if "duckduckgo.com" not in url and "start.duckduckgo.com" not in url:
                                    unique_links.append({'title': title, 'url': url})
                                    seen_urls.add(url)
                                    temp_new_count += 1
                        except:
                            pass
                    
                    if temp_new_count == 0:
                        print(f"{Fore.LIGHTBLACK_EX}   [-] 点击后或二次滚动后未发现新内容加载，可能已达结果上限。{Style.RESET_ALL}")
                        break


            # 4. 深度阅读环节 (截取指定数量)
            final_links = unique_links[:MAX_SEARCH_RESULTS]
            print(f"{Fore.YELLOW}>> 🔍 最终决定深度阅读 {len(final_links)} 篇网页原文...{Style.RESET_ALL}")

            for i, link in enumerate(final_links, 1):
                try:
                    print(f"[{i}/{len(final_links)}] 正在读取: {link['title'][:30].strip()}...", end="", flush=True)
                    page.goto(link['url'], timeout=15000, wait_until="domcontentloaded")
                    
                    # 模拟阅读滚动
                    page.mouse.wheel(0, 2000)
                    time.sleep(1)
                    
                    # 使用trafilatura提取主要内容
                    text = trafilatura.extract(page.content()) or page.inner_text("body")
                    
                    # 简单清洗并截断
                    clean = "\n".join([t.strip() for t in text.split('\n') if len(t.strip()) > 10])
                    clean = clean[:2500] # 截断，避免过长
                    
                    if len(clean) > 50:
                        docs.append(f"来源:《{link['title']}》\nURL: {link['url']}\n内容:{clean}\n")
                        print(f"{Fore.GREEN} √{Style.RESET_ALL}")
                        print(f"{Fore.LIGHTBLACK_EX}   📝 摘要: {clean[:80].replace(chr(10), ' ')}...{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED} x (内容过短或为空){Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED} x (加载或提取失败: {e}){Style.RESET_ALL}")
                    continue

        except Exception as e:
            print(f"{Fore.RED}搜索异常: {e}{Style.RESET_ALL}")
        finally: 
            page.close()
        return docs
