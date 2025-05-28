import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig # Import BrowserConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from playwright.async_api import Page

async def custom_interaction_and_scrape():
    url = "https://aetv.com" # Replace with your target URL
    # IMPORTANT: Replace with a real URL that has a "Show More" button and dynamic content
    # For testing, you might need to create a simple local HTML file or find a public site.
    
    # Define a simple extraction schema for initial data
    initial_schema = {
        "name": "InitialData",
        "baseSelector": "div.main-content", # Adjust if necessary for your target site
        "fields": [
            {"name": "title", "selector": "h1", "type": "text"},
            {"name": "description", "selector": "p.intro", "type": "text"}
        ]
    }

    all_extracted_data = {}

    async def interact_and_extract_hook(page: Page, context):
        """
        This hook is executed after the page has been navigated to and loaded by Crawl4AI.
        We can now use Playwright's 'page' object for direct interaction.
        """
        print(f"Hook: Interacting with page: {page.url}")
        
        # 1. Use Playwright to find and click the "Show More" button
        try:
            # Adjust the selector for your actual "Show More" button
            show_more_button = await page.wait_for_selector(
                "button.show-more", timeout=5000 
            )
            await show_more_button.click()
            print("Hook: Clicked 'Show More' button.")
            
            # Wait for the dynamic content to load after the click
            # Adjust the selector for the container of your dynamic content
            await page.wait_for_selector("div.additional-details", timeout=10000)
            print("Hook: Dynamic content loaded.")

            # 2. Use Playwright to scrape the newly revealed content
            dynamic_elements = await page.locator("div.additional-details .detail-item").all_text_contents()
            contact_email_href = await page.locator("a.email-link").get_attribute("href")

            all_extracted_data['dynamic_content'] = {
                "extra_info": dynamic_elements,
                "contact_email": contact_email_href
            }
            print(f"Hook: Scraped dynamic content: {all_extracted_data['dynamic_content']}")

        except Exception as e:
            print(f"Hook: Error during interaction or dynamic scraping: {e}")
            all_extracted_data['dynamic_content'] = "Failed to load dynamic content."

    # --- NEW HOOK REGISTRATION METHOD ---
    # Create a BrowserConfig object and pass hooks to its 'hooks' dictionary
    browser_config = BrowserConfig(
        headless=True,  # Set to False during development to see the browser
        verbose=True,
        hooks={
            "after_goto": [interact_and_extract_hook] # Register the hook here
        }
    )

    # Configure Crawl4AI's run settings
    crawler_run_config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(initial_schema),
        cache_mode="bypass" # Ensure fresh content
    )

    # Pass the browser_config to the AsyncWebCrawler constructor
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print(f"Starting crawl for: {url}")
        result = await crawler.arun(url=url, config=crawler_run_config)

        if result.success:
            print("\n--- Initial Crawl Result ---")
            print(f"URL: {result.url}")
            print(f"Status Code: {result.status_code}")
            print("Extracted Initial Content:")
            print(result.extracted_content)

            print("\n--- Dynamic Content (from Playwright interaction) ---")
            print(all_extracted_data.get('dynamic_content', 'No dynamic content extracted.'))

            # You can combine results or process them further
            final_data = {
                "initial_scrape": result.extracted_content,
                "dynamic_scrape": all_extracted_data.get('dynamic_content')
            }
            print("\n--- Combined Final Data ---")
            print(final_data)

        else:
            print(f"Crawl Failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(custom_interaction_and_scrape())