## scraper-api To-Do List

*   [x] Add Playwright browser opening
*   [ ] Create CSV website input list
*   [ ] Iterate through CSV using various scraping method
*   [ ] Add additional scraping formats for different website layouts
*   [ ] Add while loop for all websites in CSV with if statements for scraping formats
*   [X] Add BeautifulSoup HTML extraction to source.html
*   [ ] Use BeautifulSoup to sanitize source.html
*   [X] Pass source.html to Gemini API
*   [X] Create JSON fields
*   [X] Produce output.json for frontend


## Setup

```bash
    docker build -t scraper-api .
    docker run -v $(pwd)/src:/app/src scraper-api
```

In the future .env should be migrated to docker-compose