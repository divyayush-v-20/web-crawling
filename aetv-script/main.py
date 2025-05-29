from playwright.async_api import async_playwright

import config
import os
import asyncio

#crawler code
async def crawl(base_url : str, browser_type : str = "chromium", max_depth : int = 2):
    visited_urls = set()
    pending_urls = asyncio.Queue()
    domain = config.get_domain(base_url)
    # dir_name = f"html/{domain}"
    dir_name = "html/aetv_tmp"
    os.makedirs(dir_name, exist_ok=True)
    crawled_count = 0

    await pending_urls.put((base_url, 0))
    print(f"Initiating crawl from {base_url}, Domain: {domain}")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        try:
            while not pending_urls.empty():
                crawled_count += 1
                if crawled_count >= 10:
                    break
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

                    # body_content = page.locator('body')
                    # html_content = await body_content.inner_html()
                    html_content = await page.content()

                    file_path = config.get_path(current_url)
                    with open(f"{dir_name}/{file_path}", "w") as f:
                        f.write(html_content)

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
    START_URL = "https://aetv.com/shows"
    MAX_DEPTH = 2
    BROWSER_TYPE = "chromium"

    asyncio.run(crawl(START_URL, BROWSER_TYPE, MAX_DEPTH))


    #aetv - 360 urls
    #showname xpath selector for aetv.com -> /html/body/div/div/div/div/div/div/ul/li/a/div/div/text()
    #seasons xpath selector for aetv.com -> /html/body/section/div/div/div/section/div/div/div/div/strong/span[1]/text()
    #episode xpath selector for aetv.com -> /html/body/section/div/div/div/section/div/div/div/div/strong/span[2]/text()
    #airdate xpath selector for aetv.com -> /html/body/section/div/div/div/section/div/div/div/div/strong[2]/text()
    #episode description xpath selector for aetv.com -> /html/body/section/div/div/div/section/div/div/div/div/div[1]/p/text()