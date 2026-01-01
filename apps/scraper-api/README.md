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
    # Build Image
    docker build -t scraper-api .

    # Run Container with src as volume
        # --name is scraper-instance
        # --env-file for having env var in container (GEMINI_API_KEY)
        # -v Volume so it gets live code so we don't always have to rebuild
    docker run --name scraper-instance --env-file .env -v $(pwd)/src:/app/src scraper-api
    
    # Copy out output.json from container
    docker cp romantic_dijkstra:/app/output.json ./output.json
```

In the future .env should be migrated to docker-compose