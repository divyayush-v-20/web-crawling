import asyncio
from playwright.async_api import async_playwright
import html2text
import random
import time # Import time for measuring execution time
from playwright_stealth import stealth_async # Import the stealth plugin

async def scrape_html(url: str) -> str:
    async with async_playwright() as p:
        proxy_server = None # Set to None if you're not using a proxy

        browser = await p.chromium.launch(
            headless=False, 
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            args=[
                '--disable-blink-features=AutomationControlled', # Helps bypass basic bot detection
                '--no-sandbox', # Recommended for robust execution environments
                '--disable-setuid-sandbox',
                '--auto-open-devtools-for-tabs' # Opens DevTools automatically for debugging
            ],
            proxy={"server": proxy_server} if proxy_server else None # Apply proxy if defined
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080} # Standard desktop resolution
        )
        page = await context.new_page()

        # --- Apply Playwright Stealth (Crucial for strong bot detection sites) ---
        await stealth_async(page) 

        # Optional: Selective resource blocking (re-enabled image/media blocking, others kept for now)
        # Be cautious with blocking, as essential JS/CSS can break the page.
        # await page.route(
        #     "**/*",
        #     lambda route: route.abort()
        #     if route.request.resource_type in ["image", "media"]
        #     else route.continue()
        # )

        try:
            print(f"Navigating to {url}...")
            # Use 'networkidle' for dynamic sites like Crunchyroll, and extended timeout.
            await page.goto(url, wait_until='networkidle', timeout=90000) # Increased to 90 seconds

            # --- Attempt to dismiss cookie consent banners/overlays ---
            # Added Crunchyroll-specific cookie consent selectors for "Accept All Cookies" and "Reject All"
            cookie_consent_selectors = [
                'button:has-text("Accept All Cookies")', # Specific to Crunchyroll output
                'button:has-text("Accept all")',
                'button:has-text("Accept")',
                'button:has-text("Continue")',
                'button:has-text("Got it")',
                '#onetrust-accept-btn-handler', # Common for OneTrust
                '#didomi-notice-agree-button',  # Common for Didomi
                '.cc-btn.cc-allow',             # Common for CookieConsent
                '.fc-button.fc-cta-consent',    # Common for Funding Choices
                '[aria-label*="cookie consent"] button', # More generic
                '[data-testid*="cookie-consent"] button',
                'div[role="dialog"] button:has-text("Accept")',
                'button:has-text("Reject All Cookies")', # Added specific Crunchyroll selector
                'button:has-text("Reject All")', # Generic reject
            ]

            print("Attempting to dismiss cookie consent banner (if present)...")
            found_cookie_button = False
            for selector in cookie_consent_selectors:
                try:
                    consent_button = page.locator(selector)
                    await consent_button.wait_for(state='visible', timeout=5000)
                    
                    # Simulate human-like mouse movement before clicking
                    box = await consent_button.bounding_box()
                    if box:
                        # Move mouse to the center of the button
                        await page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                        await asyncio.sleep(random.uniform(0.2, 0.5)) # Small delay before click
                    
                    await consent_button.click()
                    print(f"Clicked cookie consent button with selector: {selector}")
                    await asyncio.sleep(random.uniform(3, 6)) # Longer variable delay after clicking
                    found_cookie_button = True
                    break 
                except Exception:
                    # print(f"No button for '{selector}' found or clickable.") # Uncomment for more verbose debugging
                    pass
            
            if not found_cookie_button:
                print("No cookie consent button found or clicked.")
                # Also try to close any "Update Browser" banners if they appear, though stealth should reduce these.
                try:
                    # Look for a common close button or "No, thanks"
                    update_banner_close_selectors = [
                        'button:has-text("No, thanks")',
                        'button[aria-label="Close"]', # Common for dialogs
                        'button.close-button'
                    ]
                    for sel in update_banner_close_selectors:
                        close_button = page.locator(sel)
                        await close_button.wait_for(state='visible', timeout=3000)
                        await close_button.click()
                        print(f"Closed update/info banner with selector: {sel}")
                        await asyncio.sleep(random.uniform(1, 2))
                        break
                except Exception:
                    pass


            # Scroll down to load dynamic content (simulating human scroll)
            print("Simulating scroll to load dynamic content...")
            for _ in range(5): # Scroll more times to ensure content loads
                await page.evaluate("window.scrollBy(0, window.innerHeight / 2)")
                await asyncio.sleep(random.uniform(1.5, 3.5))
            await asyncio.sleep(random.uniform(3, 7)) # Final delay after scrolls

            # --- Wait for actual content to load ---
            # Wait for a prominent element that should be present when the main content loads.
            # For Crunchyroll's alphabetical page, this could be a link to an anime series.
            try:
                # This selector is an example; you might need to inspect the page manually
                # if this specific one doesn't work after the page renders.
                await page.wait_for_selector('a[href*="/series/"]', timeout=20000) 
                print("Primary content element found (e.g., an anime series link).")
            except Exception as e:
                print(f"Timed out waiting for primary content element: {e}. Page might not have loaded correctly or is still blocked.")
                # If content isn't there, the HTML capture will be sparse.

            raw_body_html = await page.inner_html('body')

            return raw_body_html

        except Exception as e:
            return f"Error scraping {url}: {e}"
        # finally:
        #     await browser.close()

# --- Main execution block (UNCHANGED AS PER YOUR REQUEST) ---
async def main():
    # === IMPORTANT: Replace this with the URL you want to scrape ===
    # target_url = "https://fm99.lt/top-10"
    # target_url = "https://www.example.com"
    # target_url = "https://en.wikipedia.org/wiki/Web_scraping"
    # target_url = "https://www.crunchyroll.com/videos/alphabetical"
    # target_url = "https://www.aetv.com/shows"
    target_url = "https://www.crunchyroll.com/videos/alphabetical#L"
    # target_url = "https://www.hotstar.com/in/home"
    # target_url = "https://www.powerapp.com.tr/yayin-akisi/powerturktv/"
    # target_url = "https://ktena.co.kr/skyUHD/?d=20250510"
    # target_url = "https://abc.com/browse/comedy"
    # target_url = "https://www.radiofreccia.it/palinsesto/giovedi/"
    # target_url = "https://programtv.onet.pl/program-tv/tvn-style-hd-141?dzien=0"

    # file_name = "abc_com_browse_comedy"
    file_name = "crunchyroll"
    # file_name = "powerapp"
    # file_name = "hotstar"
    # file_name = "skyuhd"
    # file_name = "fm99"
    # file_name = "aetv"
    # file_name = "radiofreccia"
    # file_name = "programtv_onet"

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
    with open(f"results/{file_name}.md", "w") as f:
        f.write(markdown_content)

if __name__ == "__main__":
    # Run the main asynchronous function
    asyncio.run(main())