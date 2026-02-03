from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
from urllib.parse import urlparse
import os, csv, pandas as pd, json, re, time

class Entry(BaseModel):
    seminar_title: str = Field(description="The title of the seminar.")
    date: str = Field(description="Date of the seminar.")
    location: str = Field(description="Building location.")
    time: str = Field(description="Time of the seminar.")
    speaker: str = Field(description="Name of the speaker.")
    affiliation: str = Field(description="Speaker's affiliated school or organization.")
    abstract: str = Field(description="Brief detail overview of the seminar topic.")
    bio: str = Field(description="Information about the speaker.")

class SeminarHalfBaked(BaseModel):
    """
    Intermediate schema for Gemini processing.
    'HalfBaked' implies this data is raw from the LLM and missing external metadata (department, series).
    """
    entries: List[Entry]

class SeminarFullyBaked(BaseModel):
    """
    Final schema for output.
    'FullyBaked' implies the data is complete, combining LLM extraction with CSV metadata.
    """
    department: str
    series: str
    entries: List[Entry]

def parse_html(source, department, series):

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
        return None

    myfile = client.files.upload(file=source)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=[prompt, myfile],
        config={
        "response_mime_type": "application/json",
        "response_json_schema": SeminarHalfBaked.model_json_schema(),  # Use the HalfBaked schema for extraction
        },
    )

    print(f"Parsing Gemini response...")
    # Validate the raw response using the HalfBaked model
    half_baked_data = SeminarHalfBaked.model_validate_json(response.text)
    
    # Create the FullyBaked object by injecting department and series
    fully_baked_data = SeminarFullyBaked(
        department=department, 
        series=series, 
        entries=half_baked_data.entries
    )
    print(f"Set department to: {department}, series to: {series}")
    
    return fully_baked_data

def scrape_1(link, department, series):
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

            html = page.locator('#seminar-content').inner_html()
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
            return None

        browser.close()
        return parse_html("./source.html", department, series)

def scrape_2(link, department, series):
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

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            script_tag = soup.find("script", string=re.compile("var events_data"))

            if script_tag:
                script_text = script_tag.string
                match = re.search(r"var events_data = (\[.*?\]);", script_text, re.DOTALL)
                
                if match:
                    events_json = match.group(1)
                    events = json.loads(events_json)

                    # Keep only events that start after the current time
                    now = int(time.time())
                    events = [e for e in events if int(e.get("from_timestamp", 0)) > now]

                    # Keep only events with "Seminar" in the title
                    events = [e for e in events if "Seminar" in e.get("title", "")]

                    print(f"Found {len(events)} upcoming events:\n")
                    
                else:
                    print("Found the script, but could not extract the events_data array.")
            else:
                print("Could not find the script tag containing event data.")

            with open('source.html', 'wb') as f:
                f.write(soup.encode('utf-8'))

            print(f"HTML written to source.html...")
                    
        except Exception as e:
            # Add Screenshot debugging to see failure (e.g., CAPTCHA)
            print(f"Scraping failed: {e}")
            page.screenshot(path="debug_error.png")
            print("Screenshot saved to debug_error.png")
            browser.close()
            return None

        browser.close()
        return parse_html("./source.html", department, series)

def scrape_3(link, department, series):
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

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            script_tag = soup.find("script", string=re.compile("var events_data"))

            if script_tag:
                script_text = script_tag.string
                match = re.search(r"var events_data = (\[.*?\]);", script_text, re.DOTALL)
                
                if match:
                    events_json = match.group(1)
                    events = json.loads(events_json)

                    # Keep only events that start after the current time
                    now = int(time.time())
                    events = [e for e in events if int(e.get("from_timestamp", 0)) > now]

                    # Keep only events with "Seminar" in the title
                    events = [e for e in events]

                    print(f"Found {len(events)} upcoming events:\n")
                    
                else:
                    print("Found the script, but could not extract the events_data array.")
            else:
                print("Could not find the script tag containing event data.")

            with open('source.html', 'wb') as f:
                f.write(soup.encode('utf-8'))

            print(f"HTML written to source.html...")
                    
        except Exception as e:
            # Add Screenshot debugging to see failure (e.g., CAPTCHA)
            print(f"Scraping failed: {e}")
            page.screenshot(path="debug_error.png")
            print("Screenshot saved to debug_error.png")
            browser.close()
            return None

        browser.close()
        return parse_html("./source.html", department, series)

def main():

    script_dir = os.path.dirname(__file__) # Get current filepath
    input_path = os.path.join(script_dir, 'input.csv') # Append input.csv
    df = pd.read_csv(input_path) # Read into pandas DataFrame

    output_path = Path("/app/out/apps/liontalk/src/data/seminars.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Accumulate all fully baked seminars
    all_seminars = []

    for index, row in df.iterrows():
        link = row['website'] # Get website link
        department = row['department'] # Get department from CSV
        series = row['series'] # Get series from CSV
        scrape_method = row['scrape_method'] # Get scrape method

        print(f"Processing row {index}: link={link}, department={department}, series={series}, scrape_method={scrape_method}")

        if scrape_method == 1:
            seminar_data = scrape_1(link, department, series)
            if seminar_data:
                all_seminars.append(seminar_data)
        elif scrape_method == 2:
            seminar_data = scrape_2(link, department, series)
            if seminar_data:
                all_seminars.append(seminar_data)
        elif scrape_method == 3:
            seminar_data = scrape_2(link, department, series)
            if seminar_data:
                all_seminars.append(seminar_data)
        # Add future scrape methods for different website layouts
        # elif scrape_method == n:
        #     seminar_data = scrape_n(link, department, series)
        #     if seminar_data:
        #         all_seminars.append(seminar_data)
        else:
            print(f"Unknown scrape method: {scrape_method}")
    
    # Write all seminars as a single JSON array
    print(f"Writing {len(all_seminars)} seminars to {output_path}...")
    with open(output_path, "w") as f:
        # Convert to list of dicts and write as formatted JSON array
        seminars_dict = [seminar.model_dump() for seminar in all_seminars]
        json.dump(seminars_dict, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    
    # Verify file exists and has content
    if output_path.exists():
        print(f"File exists: {output_path}, size: {output_path.stat().st_size} bytes")
    else:
        print(f"ERROR: File was not created at {output_path}")
    
    print(f"Completed! Wrote {len(all_seminars)} seminars.")
    
if __name__ == "__main__":
    main()