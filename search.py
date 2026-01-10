# search.py
"""
Web search module
"""
import time
from playwright.sync_api import sync_playwright
import trafilatura
# from bs4 import BeautifulSoup # If trafilatura is sufficient, bs4 may not be needed
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
                "--headless=new",  # Playwright's recommended new headless mode
                "--no-sandbox",
                "--window-position=-2000,-2000",
            ])  # Position the window off-screen
        else:
            args.extend(["--window-position=0, 0"])

        self.browser = self.playwright.chromium.launch(
            headless=HEADLESS,
            args=args,
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0 Safari/537.36",
            locale="zh-CN",
        )
        print(f"{Fore.GREEN}>> 🌐 Browser started successfully.{Style.RESET_ALL}")

    def stop(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print(f"{Fore.GREEN}>> 🌐 Browser closed.{Style.RESET_ALL}")

    def search(self, query):
        """
        Optimized pagination search based on screenshot feedback:
        1. Simulate scrolling to the bottom to trigger the 'More Results' button.
        2. Precisely click the 'More Results' button.
        3. Add buffer wait time after clicking to ensure dynamic content loads.
        """

        page = self.context.new_page()
        docs = []
        unique_links = []
        seen_urls = set()

        max_scan_pages = MAX_PAGES_TO_SCAN  # Maximum pages to scan for pagination, read from config

        try:
            print(f"{Fore.YELLOW}>> 🌐 Performing online search and simulating pagination: {query}{Style.RESET_ALL}")
            page.goto(f"https://duckduckgo.com/?q={query}&ia=web", timeout=20000)

            pages_clicked = 0
            while len(unique_links) < MAX_SEARCH_RESULTS and pages_clicked < max_scan_pages:
                # 1. Wait for initial results to load
                try:
                    page.wait_for_selector('[data-testid="result"]', timeout=8000)
                except:
                    print(f"{Fore.LIGHTBLACK_EX}   [-] No search results found or load timed out, stopping pagination.{Style.RESET_ALL}")
                    break

                # 2. Extract all currently loaded links
                # Prefer using the data-testid attribute, fallback to article h2 a
                locs = page.locator('a[data-testid="result-title-a"]').all()
                if not locs:
                    locs = page.locator('article h2 a').all()

                for l in locs:
                    try:
                        url = l.get_attribute('href')
                        title = l.inner_text().strip()
                        if url and "http" in url and url not in seen_urls:
                            # Filter out DuckDuckGo's own links
                            if "duckduckgo.com" not in url and "start.duckduckgo.com" not in url:
                                unique_links.append({'title': title, 'url': url})
                                seen_urls.add(url)
                    except Exception:
                        # Ignore elements whose attributes cannot be retrieved
                        # print(f"{Fore.RED}   [!] Error extracting link attributes: {e}{Style.RESET_ALL}")
                        pass

                # If current count meets the target, exit early
                if len(unique_links) >= MAX_SEARCH_RESULTS:
                    break

                # 3. Simulate the actions from the screenshot: scroll to the bottom and click
                print(f"{Fore.CYAN}   [Paginate] Retrieved {len(unique_links)} items, scrolling down to find button...{Style.RESET_ALL}")

                # Remember current count before attempting to load more
                count_before = len(unique_links)

                # Scroll to the bottom
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)  # wait for button to render

                # Try clicking the 'More Results' button (text selector based on screenshot)
                btn_selectors = [
                    "button#more-results",
                    "text='More Results'",
                    "a.result--more__btn",
                ]

                clicked = False
                for selector in btn_selectors:
                    btn = page.locator(selector).first
                    if btn.count() > 0 and btn.is_visible() and btn.is_enabled():
                        try:
                            btn.scroll_into_view_if_needed()  # ensure visible
                            btn.click()
                            pages_clicked += 1
                            print(f"{Fore.CYAN}   [√] Successfully clicked 'More Results' (#{pages_clicked}){Style.RESET_ALL}")
                            clicked = True
                            # Important: wait after clicking to let new results load
                            time.sleep(2.5)
                            break
                        except Exception:
                            # print(f"{Fore.RED}   [!] Click failed for {selector}: {click_err}{Style.RESET_ALL}")
                            continue

                # If button not found, or clicking doesn't increase links, we've likely reached the end
                if not clicked:
                    print(f"{Fore.LIGHTBLACK_EX}   [-] No more results button found or cannot be clicked; search finished.{Style.RESET_ALL}")
                    break

                # Extra check: if clicked but results didn't change, it may be blocked or ended
                new_links_after_click = len(unique_links)
                if new_links_after_click <= count_before:  # no new links after click
                    # Try scrolling again to trigger lazy-loading
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1.0)
                    # Re-extract links to see if any new ones appeared
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
                        except Exception:
                            pass

                    if temp_new_count == 0:
                        print(f"{Fore.LIGHTBLACK_EX}   [-] No new content loaded after click or second scroll; may have reached results limit.{Style.RESET_ALL}")
                        break

            # 4. Deep-read stage (take a limited number)
            final_links = unique_links[:MAX_SEARCH_RESULTS]
            print(f"{Fore.YELLOW}>> 🔍 Decided to deep-read {len(final_links)} web pages...{Style.RESET_ALL}")

            for i, link in enumerate(final_links, 1):
                try:
                    print(f"[{i}/{len(final_links)}] Reading: {link['title'][:30].strip()}...", end="", flush=True)
                    page.goto(link['url'], timeout=15000, wait_until="domcontentloaded")

                    # Simulate reading scroll
                    page.mouse.wheel(0, 2000)
                    time.sleep(1)

                    # Use trafilatura to extract main content
                    text = trafilatura.extract(page.content()) or page.inner_text("body")

                    # Simple cleaning and truncation
                    clean = "\n".join([t.strip() for t in text.split('\n') if len(t.strip()) > 10])
                    clean = clean[:2500]  # truncate to avoid too long

                    if len(clean) > 50:
                        docs.append(f"Source: \"{link['title']}\"\nURL: {link['url']}\nContent: {clean}\n")
                        print(f"{Fore.GREEN} √{Style.RESET_ALL}")
                        print(f"{Fore.LIGHTBLACK_EX}   📝 Summary: {clean[:80].replace(chr(10), ' ')}...{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED} x (content too short or empty){Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED} x (load or extract failed: {e}){Style.RESET_ALL}")
                    continue

        except Exception as e:
            print(f"{Fore.RED}Search exception: {e}{Style.RESET_ALL}")
        finally:
            page.close()
        return docs
