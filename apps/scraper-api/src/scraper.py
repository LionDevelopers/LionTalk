from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import os
import csv
import pandas as pd

class Entry(BaseModel):
    seminar_title: str = Field(description="The title of the seminar.")
    date: str = Field(description="Date of the seminar.")
    location: str = Field(description="Building location.")
    time: str = Field(description="Time of the seminar.")
    speaker: str = Field(description="Name of the speaker.")
    affiliation: str = Field(description="Speaker's affiliated school or organization.")
    abstract: str = Field(description="Brief detail overview of the seminar topic.")
    bio: str = Field(description="Information about the speaker.")

class Seminar(BaseModel):
    department: str = Field(description="The department as identified in the first " \
                                        "path segment of the website URL being parsed." \
                                        "i.e. Statistics, Applied Math, Student")
    entries: List[Entry]

def parse_html(source):

    # Send scraped data to Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment!")

    client = genai.Client(api_key=api_key)

    prompt = "Extract every single occurrence of an entry found in the HTML. " \
    "Do not summarize or truncate the list. " \
    "The final JSON must contain a list of all items found, from the first to the very last one in the file."

    print(f"Retrieving response from Gemini...")
    
    # Ensure source.html exists before uploading
    if not os.path.exists(source):
        print("Error: source.html was not created.")
        return

    myfile = client.files.upload(file=source)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=[prompt, myfile],
        config={
        "response_mime_type": "application/json",
        "response_json_schema": Seminar.model_json_schema(),
        },
    )

    output_path = Path("/app/out/apps/liontalk/src/data/seminars.json")
    print(f"DEBUG: Attempting to write to {output_path.absolute()}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Writing Gemini response to {output_path}...")
    seminar = Seminar.model_validate_json(response.text)
    with open(output_path, "w") as f:
        f.write(seminar.model_dump_json(indent=2))
        f.flush()  # Ensure data is written to buffer
        os.fsync(f.fileno())  # Force write to disk and sync to host filesystem
    
    # Verify file exists and has content
    if output_path.exists():
        print(f"File exists: {output_path}, size: {output_path.stat().st_size} bytes")
    else:
        print(f"ERROR: File was not created at {output_path}")
    
    print(f"Completed!" + "\n")

def scrape_1(link):
    # Scrape HTML of specified website
    with sync_playwright() as p:

        is_headless = os.getenv("HEADLESS", "true").lower() == "true"
        browser = p.chromium.launch(headless=is_headless, slow_mo=50)

        # Use a real browser Context + User Agent to avoid bot detection
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("Navigating to URL...")
            # Wait for 'networkidle' (ensures the page is actually finished loading)
            page.goto(link, wait_until="networkidle", timeout=60000)
            
            print("Waiting for content...")
            # Wait for target selector before grabbing HTML
            page.wait_for_selector('#seminar-content', state="attached", timeout=60000)

            html = page.inner_html('#seminar-content')
            soup = BeautifulSoup(html, 'html.parser')

            # Sanitize HTML before sending to Gemini
            for strong_tag in soup.find_all('strong'):
                strong_tag.unwrap()

            with open('source.html', 'wb') as f:
                f.write(soup.encode('utf-8'))

            print(f"HTML written to source.html...")
        
        except Exception as e:
            # Add Screenshot debugging to see failure (e.g., CAPTCHA)
            print(f"Scraping failed: {e}")
            page.screenshot(path="debug_error.png")
            print("Screenshot saved to debug_error.png")
            browser.close()
            return

        browser.close()
        parse_html("./source.html")

def main():

    script_dir = os.path.dirname(__file__) # Get current filepath
    input_path = os.path.join(script_dir, 'input.csv') # Append input.csv
    df = pd.read_csv(input_path) # Read into pandas DataFrame

    for index, row in df.iterrows():
        link = row['website'] # Get website link
        scrape_method = row['scrape_method'] # Get scrape method

        print(f"Processing row {index}: link={link}, scrape_method={scrape_method}")

        if scrape_method == 1:
            scrape_1(link)
        # Add future scrape methods for different website layouts
        # else if scrape_method == 2:
        #     scrape_2(link)
        # else if scrape_method == 3:
        #     scrape_3(link)
        else:
            print(f"Unknown scrape method: {scrape_method}")
    
if __name__ == "__main__":
    main()