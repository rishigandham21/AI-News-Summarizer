import requests
from bs4 import BeautifulSoup

def fetch_content(url):
    """
    Scrape <p> tags from a page and join text.
    """
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    paragraphs = soup.select('p')
    text = ' '.join(p.get_text(strip=True) for p in paragraphs)
    return text[:2000]  # limit size
