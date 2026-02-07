from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from pathlib import Path
from urllib.parse import urlparse
import os, csv, pandas as pd, json, re, time

class Entry(BaseModel):
    seminar_title: str = Field(description="The title of the seminar.")
    date: str = Field(description="Date of the seminar in dd-MMM-yy format.")
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

def parse_html(source: Union[str, list], department: str, series: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment!")

    client = genai.Client(api_key=api_key)

    if isinstance(source, list):
        # Pass events as JSON in the prompt (no file upload)
        prompt = (
            "Extract every single occurrence of an entry from the following JSON event list. "
            "Do not summarize or truncate. Map each event into the schema (seminar_title, date, location, time, speaker, affiliation, abstract, bio). "
            "Use empty string for any missing field. The final JSON must contain a list of all items found, from the first to the very last one.\n"
            # "Each event has from_timestamp and to_timestamp as Unix timestamps (seconds since 1970-01-01 UTC). "
            # "Convert from_timestamp into a short date for the date field (e.g. ‘dd-MMM-yy’). Use both timestamps to form a time range for the time field (e.g. ‘5:45 pm - 6:30 pm’). "
            # "Use the event’s item_tz_offset if present for local time.\n\n"
            + json.dumps(source, indent=2)
        )
        contents = [prompt]
    else:
        # File path: upload HTML and use existing prompt
        prompt = (
            "Extract every single occurrence of an entry found in the HTML. "
            "Do not summarize or truncate the list. "
            "The final JSON must contain a list of all items found, from the first to the very last one in the file."
        )
        if not os.path.exists(source):
            print("Error: source file was not created.")
            return None
        myfile = client.files.upload(file=source)
        contents = [prompt, myfile]

    print("Retrieving response from Gemini...")

    # --- RETRY LOGIC for Gemini API 503 Error ---
    response = None
    max_retries = 5
    base_delay = 2  # Start with 2 seconds wait

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite", 
                contents=contents,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": SeminarHalfBaked.model_json_schema(),
                },
            )
            break # Success! Exit the loop.
            
        except Exception as e:
            error_msg = str(e)
            # Check for specific error codes: 503 (Unavailable) or 429 (Resource Exhausted)
            if "503" in error_msg or "429" in error_msg:
                if attempt == max_retries - 1:
                    print(f"Max retries reached. Failing with error: {e}")
                    raise e # Give up if we hit the limit
                
                # Exponential backoff: 2s, 4s, 8s... + random jitter
                sleep_time = (base_delay * (2 ** attempt)) + random.uniform(0.1, 1.0)
                print(f"Gemini overloaded (Attempt {attempt+1}/{max_retries}). Sleeping {sleep_time:.2f}s...")
                time.sleep(sleep_time)
            else:
                # If it's a different error (e.g., Invalid API Key), crash immediately
                raise e
    # --- RETRY LOGIC ENDS HERE ---

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
            page.goto(link, wait_until="domcontentloaded")
            
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
            page.goto(link, wait_until="domcontentloaded")
            
            print("Waiting for content...")

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            script_tag = soup.find("script", string=re.compile("var events_data"))
            events = None

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
                    
                    # LIMIT TO TOP 5
                    events = events[:5]
                    print(f"Found {len(events)} upcoming events (limited to top 5).")
                else:
                    print("Found the script, but could not extract the events_data array.")
            else:
                print("Could not find the script tag containing event data.")

            browser.close()
            if events is not None:
                return parse_html(events, department, series)
            # Fallback: write full HTML and let Gemini extract from it
            with open("source.html", "wb") as f:
                f.write(soup.encode("utf-8"))
            print("HTML written to source.html (fallback).")
            return parse_html("./source.html", department, series)

        except Exception as e:
            # Add Screenshot debugging to see failure (e.g., CAPTCHA)
            print(f"Scraping failed: {e}")
            page.screenshot(path="debug_error.png")
            print("Screenshot saved to debug_error.png")
            browser.close()
            return None

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
            page.goto(link, wait_until="domcontentloaded")
            
            print("Waiting for content...")

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            script_tag = soup.find("script", string=re.compile("var events_data"))
            events = None

            if script_tag:
                script_text = script_tag.string
                match = re.search(r"var events_data = (\[.*?\]);", script_text, re.DOTALL)
                
                if match:
                    events_json = match.group(1)
                    events = json.loads(events_json)

                    # Keep only events that start after the current time
                    now = int(time.time())
                    events = [e for e in events if int(e.get("from_timestamp", 0)) > now]
                    
                    # LIMIT TO TOP 5
                    events = events[:5]
                    print(f"Found {len(events)} upcoming events (limited to top 5).")
                else:
                    print("Found the script, but could not extract the events_data array.")
            else:
                print("Could not find the script tag containing event data.")

            browser.close()
            if events is not None:
                return parse_html(events, department, series)
            with open("source.html", "wb") as f:
                f.write(soup.encode("utf-8"))
            print("HTML written to source.html (fallback).")
            return parse_html("./source.html", department, series)

        except Exception as e:
            # Add Screenshot debugging to see failure (e.g., CAPTCHA)
            print(f"Scraping failed: {e}")
            page.screenshot(path="debug_error.png")
            print("Screenshot saved to debug_error.png")
            browser.close()
            return None
        
def scrape_4(link, department, series):
    """
    Scrape method for columbia.seminars.app style pages.
    Targets <section id="events"> and waits for <article class="seminar-event">.
    """
    with sync_playwright() as p:

        is_headless = os.getenv("HEADLESS", "true").lower() == "true"
        browser = p.chromium.launch(headless=is_headless, slow_mo=50)

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("Navigating to URL...")
            # increased timeout for SPA loading
            page.goto(link, wait_until="networkidle", timeout=60000)
            
            print("Waiting for seminar events to render...")
            # Wait specifically for the event cards to appear
            page.wait_for_selector('article.seminar-event', timeout=30000)

            # Extract specific section to reduce noise for the LLM (removes navbars/modals)
            html = page.locator('section#events').inner_html()
            
            if not html:
                print("Warning: section#events was empty or not found.")
                html = page.content() # Fallback to full page

            soup = BeautifulSoup(html, 'html.parser')

            # Find all event articles and limit to top 5
            articles = soup.find_all('article', class_='seminar-event')
            top_articles = articles[:5]

            # Rebuild a minimal HTML structure with only the top 5 events
            new_soup = BeautifulSoup("<html><body><section id='events'></section></body></html>", "html.parser")
            section = new_soup.find("section")

            for article in top_articles:
                section.append(article)
            
            print(f"Truncated HTML to top {len(top_articles)} events.")

            with open('source.html', 'wb') as f:
                f.write(new_soup.encode('utf-8'))

            print(f"HTML written to source.html...")
        
        except Exception as e:
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
            seminar_data = scrape_3(link, department, series)
            if seminar_data:
                all_seminars.append(seminar_data)
        elif scrape_method == 4:
            seminar_data = scrape_4(link, department, series)
            if seminar_data:
                all_seminars.append(seminar_data)
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