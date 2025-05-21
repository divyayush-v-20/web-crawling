import asyncio
from playwright.async_api import async_playwright
import html2text 

async def scrape_html(url: str) -> str:
    async with async_playwright() as p:
        # Launch a Chromium browser instance
        browser = await p.chromium.launch()
        # Create a new page in the browser
        page = await browser.new_page()

        try:
            # Navigate to the specified URL.
            # 'domcontentloaded' waits until the initial HTML document has been completely loaded and parsed.
            await page.goto(url, wait_until='domcontentloaded')

            # --- Attempt to dismiss cookie consent banners/overlays ---
            # This section tries to find and click common "Accept" or "Continue" buttons
            # within cookie consent pop-ups or overlays.
            # It uses a list of common selectors for these buttons.
            cookie_consent_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Accept all")',
                'button:has-text("Continue")',
                'button:has-text("Got it")',
                'button[id*="cookie"][class*="accept"]',
                'button[class*="cookie"][class*="accept"]',
                'a[id*="cookie"][class*="accept"]',
                'a[class*="cookie"][class*="accept"]',
                '.cookie-consent-button',
                '.consent-button',
                '#onetrust-accept-btn-handler', # Common for OneTrust
                '#didomi-notice-agree-button',  # Common for Didomi
                '.cc-btn.cc-allow',             # Common for CookieConsent
                '.fc-button.fc-cta-consent'     # Common for Funding Choices
            ]

            print("Attempting to dismiss cookie consent banner (if present)...")
            for selector in cookie_consent_selectors:
                try:
                    await page.locator(selector).wait_for(state='visible', timeout=5000)
                    await page.click(selector)
                    print(f"Clicked cookie consent button with selector: {selector}")
                    await asyncio.sleep(2)
                    break 
                except Exception:
                    pass
            print("Finished attempting to dismiss cookie consent.")

            raw_body_html = await page.inner_html('body')

            return raw_body_html

        except Exception as e:
            return f"Error scraping {url}: {e}"
        finally:
            await browser.close()

# --- Main execution block ---
async def main():
    # === IMPORTANT: Replace this with the URL you want to scrape ===
    # target_url = "https://fm99.lt/top-10"
    # target_url = "https://www.example.com"
    # target_url = "https://en.wikipedia.org/wiki/Web_scraping"
    # target_url = "https://www.crunchyroll.com/videos/alphabetical"
    target_url = "https://www.aetv.com/shows"

    print(f"Attempting to scrape raw HTML from: {target_url}\n")
    raw_html_output = await scrape_html(target_url)

    # Check if scraping was successful
    if raw_html_output.startswith("Error scraping"):
        print(raw_html_output)
        return

    print("Raw HTML scraped. Now converting to Markdown...\n")

    # --- Convert raw HTML to Markdown using html2text ---
    # Initialize the HTML2Text converter
    h = html2text.HTML2Text()

    # Configure html2text for desired Markdown output
    # These settings aim for a clean, readable Markdown representation.
    h.ignore_links = False       # Keep links in the Markdown output
    h.ignore_images = True       # Ignore images (useful for text-focused markdown)
    h.body_width = 0             # Disable line wrapping (output will be one long line if no natural breaks)
    h.single_line_break = True   # Treat single line breaks as spaces, not new paragraphs
    h.unicode_snob = True        # Convert unicode characters to their closest ASCII equivalent
    h.skip_internal_links = True # Do not convert internal page links (e.g., #section-id)
    h.use_automatic_links = True # Use automatic links for URLs where possible

    # Perform the conversion
    markdown_content = h.handle(raw_html_output)

    # Print the generated Markdown content
    with open("aetv.md", "w") as f:
        f.write(markdown_content)

if __name__ == "__main__":
    # Run the main asynchronous function
    asyncio.run(main())