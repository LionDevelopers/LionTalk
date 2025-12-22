from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo = 50)
    page = browser.new_page()
    page.goto('https://stat.columbia.edu/seminars/statistics-seminar-series/')
    html = page.inner_html('#seminar-content')
    soup = BeautifulSoup(html, 'html.parser')

    with open('source.txt', 'wb') as f:
        f.write(soup.encode('utf-8'))

    print(f"HTML written to source.txt")