<img width="1617" height="901" alt="image" src="https://github.com/user-attachments/assets/f3e53be0-9c59-41ab-979a-cbae5a47c04c" />

# Adding New Scrape Methods

This guide explains how to add support for new website formats to the scraper.

## Overview

The scraper uses Playwright to extract HTML content from seminar pages, then uses Google's Gemini API to parse the structured data. Each website format requires its own scrape method function.

## Step 1: Inspect the Target Website

Before writing code, you need to identify the HTML element that contains the seminar content.

### Using Browser Developer Tools

1. Open the website in your browser (Chrome, Firefox, or Edge)
2. Right-click on the main content area containing the seminars
3. Select "Inspect" or "Inspect Element"
4. The browser's Developer Tools will open showing the HTML structure

### Finding the Right Selector

Look for a container element that wraps all the seminar entries. Common patterns:

- ID selector: Look for `id="seminar-content"` or similar
  - Use: `#seminar-content`
- Class selector: Look for `class="seminars"` or `class="events-list"`
  - Use: `.seminars` or `.events-list`
- Semantic HTML: Look for `<main>`, `<article>`, or `<section>` tags
  - Use: `main`, `article.content`, or `section.seminars`

### Testing Your Selector

1. In the browser console (F12), try:script
   document.querySelector('#your-selector')
2. Verify that it contains all the seminar data

### Creating a Scrape Function
1. A boilerplate template following the pattern of scrape_1 is located in /apps/scraper-api/src/scraper_method_example.py
2. Replace `#your-selector` with the selector you found
3. The locator auto-waits for the element. If the page loads dynamically, you may have to add additional waits:
    `page.wait_for_selector('#your-selector', state="visible", timeout=60000)`
4. Sanitize the HTML using BeautifulSoup

### Add to Main
```
if scrape_method == 1:
    seminar_data = scrape_1(link, department, series)
    if seminar_data:
        all_seminars.append(seminar_data)
# Existing code

# INSERT YOUR CODE HERE:
elif scrape_method == N:  # Replace N with your method number
    seminar_data = scrape_N(link, department, series)
    if seminar_data:
        all_seminars.append(seminar_data)

# Existing code
else:
    print(f"Unknown scrape method: {scrape_method}")
```

### Update input.csv
Add a new row to src/input.csv with your link:
`department,series,website,scrape_method`
Make sure the scrape_method matches your scrape_method in main.

### Test your method

Before testing, you'll need to set up your own Gemini API key. The scraper uses Google's Gemini API to extract structured data from HTML.

### Get Your Gemini API Key

1. Go to Google AI Studio: Visit [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. *reate a new API key:
   - Click "Create API Key"
   - Select or create a Google Cloud project
   - Copy the generated API key (you'll only see it once!)

### Set Up Environment Variables

1. Create a `.env` file in the `apps/scraper-api/` directory:
   cd apps/scraper-api
   cp .env.example .env
2. Add your key as follows: `GEMINI_API_KEY=your_actual_api_key_here`
Make sure your `cd` is /apps/scraper-api/ because that is where the uv files are located
3. Temporarily modify the code to use the env variable. In src/scraper.py, modify the parse_html() function:
```
def parse_html(source, department, series):
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment! Please set it in .env file.")
    
    client = genai.Client(api_key=api_key)
    # ... rest of the function
```
MAKE SURE TO REMOVE ANY HARDCODED API KEYS!
The .env file is included in the .gitignore to avoid committing your API key to the repo.

### Test your method
Run the following command:
`uv run python src/scraper.py`
Check source.html and seminars.json
   
## To-Do

*   [ ] Create how-to use document for making new scrapers
*   [ ] Store scraped html in variable versus file (check if feasible)
*   [ ] Create list of additional tags for ENTRIES


