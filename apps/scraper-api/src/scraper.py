from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from pathlib import Path
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta, timezone
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
            "Use empty string for any missing field. The final JSON must contain a list of all items found, from the first to the very last one. "
            "For date and time use the event's date_display and time_display when present; otherwise use empty string.\n\n"
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
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=contents,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": SeminarHalfBaked.model_json_schema(),
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
    # 1. Define the Date Window (Now to +14 days)
    now_ts = time.time()
    end_ts = now_ts + (14 * 24 * 60 * 60)
    
    print(f"Filter Window: {datetime.fromtimestamp(now_ts).date()} to {datetime.fromtimestamp(end_ts).date()}")

    events_data = []

    with sync_playwright() as p:
        # Launch Browser (Headless for speed)
        is_headless = os.getenv("HEADLESS", "true").lower() == "true"
        browser = p.chromium.launch(headless=is_headless)
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # --- STEP 1: Scrape Main List & Filter ---
            print(f"Navigating to main list: {link}")
            page.goto(link, wait_until="domcontentloaded")
            
            soup_main = BeautifulSoup(page.content(), 'html.parser')
            view_content = soup_main.find('div', class_='view-content')
            
            if not view_content:
                print("Could not find event list container.")
                return None

            articles = view_content.find_all('article', class_='cu-event')
            events_to_visit = []

            for article in articles:
                # A. Get Timestamp (Fast & Reliable attribute)
                time_div = article.find('div', class_='event-time')
                if not time_div or not time_div.has_attr('data-start-time'):
                    continue

                try:
                    event_ts = int(time_div['data-start-time'])
                except ValueError:
                    continue

                # B. Date Filter
                if now_ts <= event_ts <= end_ts:
                    
                    # Get URL
                    link_tag = article.find('a', href=True)
                    if not link_tag: continue
                    url = link_tag['href']
                    if url.startswith("/"):
                        url = urljoin(link, url)
                    
                    # Get Title
                    title_tag = article.find('span', class_='field--name-title')
                    title = title_tag.get_text(strip=True) if title_tag else "No Title"

                    events_to_visit.append({
                        "title": title,
                        "url": url,
                        "start_timestamp": event_ts,
                        "department": department,
                        "series": series
                    })

            print(f"Found {len(events_to_visit)} events in window. Starting deep scrape...")

            # --- STEP 2: Deep Scrape Each Event ---
            for event in events_to_visit:
                print(f"Processing: {event['title']}")
                
                try:
                    page.goto(event['url'], wait_until="domcontentloaded")
                    # Optional: wait for body text to ensure load
                    # page.wait_for_selector('.field--name-body, .region-content', timeout=3000)

                    sub_soup = BeautifulSoup(page.content(), 'html.parser')
                    
                    # --- PARSING LOGIC (Based on Drupal Structure) ---

                    # 1. Location
                    # Look for explicit field OR generic class with 'location'
                    loc_div = sub_soup.find('div', class_=lambda c: c and 'field--name-field-event-location' in c)
                    if not loc_div:
                        loc_div = sub_soup.find('div', class_=lambda c: c and 'location' in c.lower())
                    event['location'] = loc_div.get_text(strip=True) if loc_div else "Location not specified"

                    # 2. Speaker Name
                    # Look for explicit field OR generic class with 'speaker'
                    speaker_div = sub_soup.find('div', class_=lambda c: c and 'field--name-field-speaker' in c)
                    if not speaker_div:
                        speaker_div = sub_soup.find('div', class_=lambda c: c and 'speaker' in c.lower())
                    event['speaker'] = speaker_div.get_text(strip=True) if speaker_div else "See Abstract"

                    # 3. Body Text (Abstract + Bio + Affiliation)
                    # Drupal puts main content in 'field--name-body'
                    body_div = sub_soup.find('div', class_='field--name-body')
                    
                    # Fallback: If no specific body field, grab the main content region
                    if not body_div:
                        body_div = sub_soup.find('div', class_='region-content')

                    full_text = body_div.get_text("\n", strip=True) if body_div else ""
                    
                    # --- INTELLIGENT SPLITTING ---
                    # Separate Abstract from Bio using regex patterns
                    
                    # Pattern 1: "About the speaker"
                    if re.search(r'about\s+the\s+speaker', full_text, re.IGNORECASE):
                        parts = re.split(r'about\s+the\s+speaker', full_text, flags=re.IGNORECASE, maxsplit=1)
                        event['abstract'] = parts[0].strip()
                        event['speaker_bio'] = parts[1].strip()
                    
                    # Pattern 2: "Bio:"
                    elif re.search(r'\bbio:', full_text, re.IGNORECASE):
                        parts = re.split(r'\bbio:', full_text, flags=re.IGNORECASE, maxsplit=1)
                        event['abstract'] = parts[0].strip()
                        event['speaker_bio'] = parts[1].strip()
                    
                    # Pattern 3: "Biography"
                    elif re.search(r'\bbiography', full_text, re.IGNORECASE):
                        parts = re.split(r'\bbiography', full_text, flags=re.IGNORECASE, maxsplit=1)
                        event['abstract'] = parts[0].strip()
                        event['speaker_bio'] = parts[1].strip()
                        
                    else:
                        # Fallback: Everything is abstract
                        event['abstract'] = full_text
                        event['speaker_bio'] = "Not detected in text"

                    # Add date_display and time_display for Gemini (Columbia = Eastern)
                    try:
                        ts = event["start_timestamp"]
                        eastern = timezone(timedelta(hours=-5))
                        dt = datetime.fromtimestamp(ts, tz=eastern)
                        event["date_display"] = dt.strftime("%d-%b-%y")
                        h, m = dt.hour, dt.minute
                        event["time_display"] = f"{h % 12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"
                    except (ValueError, OSError, KeyError):
                        event["date_display"] = ""
                        event["time_display"] = ""

                    events_data.append(event)

                except Exception as e:
                    print(f"Error parsing {event['url']}: {e}")

        except Exception as e:
            print(f"Critical Scraper Error: {e}")
            
        finally:
            browser.close()

    if not events_data:
        return None
    return parse_html(events_data, department, series)
        
def scrape_3(link, department, series):
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