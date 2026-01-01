from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from typing import List, Optional

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
    entries: List[Entry]

def main():
    # Scrape HTML of specified website
    with sync_playwright() as p:

        is_headless = os.getenv("HEADLESS", "true").lower() == "true"
        browser = p.chromium.launch(headless=is_headless, slow_mo=50)
        page = browser.new_page()
        page.goto('https://stat.columbia.edu/seminars/statistics-seminar-series/')
        html = page.inner_html('#seminar-content')
        soup = BeautifulSoup(html, 'html.parser')

        with open('source.html', 'wb') as f:
            f.write(soup.encode('utf-8'))

        print(f"HTML written to source.html")

    # Send scraped data to Gemini
    load_dotenv() # This loads the .env file if it exists
    api_key_value = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key_value)

    prompt = "Extract every single occurrence of an entry found in the HTML. " \
    "Do not summarize or truncate the list. " \
    "The final JSON must contain a list of all items found, from the first to the very last one in the file."

    print(f"Retrieving response from Gemini")
    myfile = client.files.upload(file="./source.html")
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=[prompt, myfile],
        config={
        "response_mime_type": "application/json",
        "response_json_schema": Seminar.model_json_schema(),
        },
    )

    print(f"Writing Gemini response to output.json")
    seminar = Seminar.model_validate_json(response.text)
    with open("output.json", "w") as f:
        f.write(seminar.model_dump_json(indent=2))
    
    print(f"Completed")

if __name__ == "__main__":
    main()