import requests
from bs4 import BeautifulSoup

def main():
    url = "https://utexas.edu/"

    # Header to mimic a human browser request
    headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "DNT": "1", # Do Not Track
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
    }

    try:
        response = requests.get(url, headers=headers)
        # Raise an error if the request failed (e.g., 404 or 500)
        response.raise_for_status()

        # Save the content to a file
        with open("source.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print("HTML saved successfully to source.txt")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()