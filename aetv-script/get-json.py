from playwright.async_api import async_playwright

import config
import os
import asyncio
import json

#crawler code
async def crawl(base_url : str, browser_type : str = "chromium", max_depth : int = 2):
    visited_urls = set()
    pending_urls = asyncio.Queue()
    domain = config.get_domain(base_url)
    dir_name = f"json/{domain}"
    os.makedirs(dir_name, exist_ok=True)
    crawled_count = 0
    js_script = ""

    with open("test-xpath.js", "r") as f:
        js_script += f.read()

    await pending_urls.put((base_url, 0))
    print(f"Initiating crawl from {base_url}, Domain: {domain}")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        try:
            while not pending_urls.empty():
                crawled_count += 1
                # if crawled_count >= 2:
                #     break
                current_url, current_depth = await pending_urls.get()
                if current_url in visited_urls:
                    continue
                if current_depth > max_depth:
                    continue
                # if config.get_domain(current_url) != domain:
                #     continue

                print(f"Scraping {current_url}, Depth: {current_depth}")
                visited_urls.add(current_url)

                page = await context.new_page()
                try:
                    await page.goto(current_url, wait_until = "domcontentloaded", timeout = 60000)
                    result = await page.evaluate(js_script)
                    content = json.loads(result)
                    if len(result) > 2:
                        file_path = config.get_path(current_url)
                        with open(f"{dir_name}/{file_path}.json", "w") as f:
                            json.dump(content, f, indent=4)

                    if current_depth < max_depth:
                        links = await page.evaluate('''
                            Array.from(document.querySelectorAll('a')).map(a => a.href)
                        ''')

                        for link in links:
                            this_domain = config.get_domain(link)
                            if this_domain != domain:
                                continue
                            if link not in visited_urls:
                                await pending_urls.put((link, current_depth + 1))
                except Exception as e:
                    print(f"Error crawling {current_url} : {e}")

        except Exception as e:
            print(f"Error crawling {base_url} : {e}")
        finally:
            await page.close()

if __name__ == "__main__":
    # START_URL = "https://aetv.com/shows"
    START_URL = "https://www.aetv.com/shows/the-first-48/season-3"
    MAX_DEPTH = 3
    BROWSER_TYPE = "chromium"

    asyncio.run(crawl(START_URL, BROWSER_TYPE, MAX_DEPTH))


