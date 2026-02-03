## scraper-api To-Do List

*   [X] Add Playwright browser opening
*   [X] Create CSV website input list
*   [X] Iterate through CSV using scraping method 1
*   [ ] Add additional scraping formats for different website layouts
*   [X] Set up open source while maintaining API key privacy
*   [X] Turn Gemini API call into a function
*   [X] Add while loop for all websites in CSV with if statements for scraping formats
*   [X] Add BeautifulSoup HTML extraction to source.html
*   [ ] Use BeautifulSoup to sanitize source.html
*   [X] Pass source.html to Gemini API
*   [X] Create JSON fields
*   [X] Produce output.json for frontend
*   [X] Fix incorrect department identification in output.json

```bash
    # Build Image
    docker build -t scraper-api .

    # Run Container with src as volume
        # --name is scraper-instance
        # --env-file for having env var in container (GEMINI_API_KEY)
        # -v Volume so it gets live code so we don't always have to rebuild
    docker run --name scraper-instance --env-file .env -v $(pwd)/src:/app/src scraper-api
    
    # Copy out output.json from container
    docker cp scraper-instance:/app/out/apps/liontalk/src/data/seminars.json ./seminars.json
```
