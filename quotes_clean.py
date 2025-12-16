import pandas as pd
from playwright.sync_api import sync_playwright

all_quotes = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://quotes.toscrape.com/js/")
    
    # Screenshot of first page for portfolio
    page.screenshot(path="quotes_page_screenshot.png", full_page=True)
    
    while True:
        # Scrape all quotes on current page
        quote_elements = page.query_selector_all("div.quote")
        for quote in quote_elements:
            text = quote.query_selector("span.text").inner_text().strip()
            author = quote.query_selector("small.author").inner_text().strip()
            tags_elements = quote.query_selector_all("div.tags a")
            tags = ", ".join([tag.inner_text().strip() for tag in tags_elements])
            all_quotes.append({"Quote": text, "Author": author, "Tags": tags})
        
        # Check if 'Next' button exists
        next_button = page.query_selector("li.next a")
        if next_button:
            next_button.click()
            page.wait_for_timeout(1000)  # wait 1 sec for JS to load
        else:
            break
    
    browser.close()

# -------------------------------
# ETL: Clean & Structure Data
# -------------------------------
for item in all_quotes:
    item["Quote"] = item["Quote"].strip()
    item["Author"] = item["Author"].strip()
    item["Tags"] = item["Tags"].strip()

df = pd.DataFrame(all_quotes)
df.drop_duplicates(inplace=True)

# -------------------------------
# Load: Export CSV & Excel
# -------------------------------
df.to_csv("quotes_all_pages_clean.csv", index=False)
df.to_excel("quotes_all_pages_clean.xlsx", index=False)

print(f"✅ Scraped {len(df)} quotes from all pages")
print("✅ CSV, Excel, and screenshot ready for portfolio")
