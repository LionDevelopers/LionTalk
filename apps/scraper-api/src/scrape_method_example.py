def scrape_N(link, department, series):
    """
    Scrape method N for [describe the website format].
    
    Args:
        link: URL of the seminar page
        department: Department name from CSV
        series: Series name from CSV
    
    Returns:
        SeminarFullyBaked object or None if scraping fails
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
            page.goto(link, wait_until="networkidle", timeout=60000)
            
            print("Waiting for content...")
            
            # Replace '#your-selector' with the selector you found
            html = page.locator('#your-selector').inner_html()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Optional: Sanitize HTML if needed
            # Remove unwanted tags that might confuse Gemini
            for strong_tag in soup.find_all('strong'):
                strong_tag.unwrap()
            # Add more sanitization as needed
            
            with open('source.html', 'wb') as f:
                f.write(soup.encode('utf-8'))
            
            print(f"HTML written to source.html...")
        
        except Exception as e:
            print(f"Scraping failed: {e}")
            page.screenshot(path="debug_error.png")
            print("Screenshot saved to debug_error.png")
            browser.close()
            return None
        
        browser.close()
        return parse_html("./source.html", department, series)