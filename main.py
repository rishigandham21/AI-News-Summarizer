import argparse
import time
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from transformers import pipeline

# Load summarizer model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def fetch_links(query, keywords, max_results=10):
    """
    Uses DDGS to get only links whose title or snippet mention keywords
    """
    links = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, region="in-en", safesearch="off"):
            title = r.get('title', '').lower()
            snippet = r.get('body', '').lower()
            url = r.get('href')
            if url and any(k in title or k in snippet for k in keywords):
                links.append(url)
            if len(links) >= max_results:
                break
    return links

def scrape_article(url, keywords):
    """
    Scrape paragraphs and only accept content that mentions prompt keywords sufficiently
    """
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        paragraphs = [p.get_text(strip=True) for p in soup.select('p')]
        if len(paragraphs) < 5:
            return ""
        unique_lines = set(paragraphs)
        if len(unique_lines) < 4:
            return ""
        text = ' '.join(paragraphs)
        if len(text) < 200:
            return ""
        # must have keywords appearing more than once total
        important_words = [k for k in keywords if len(k) > 3]
        if sum(text.lower().count(k) for k in important_words) < 2:
            return ""
        return text[:3000]
    except Exception:
        return ""

def summarize_text(text):
    """
    Safely summarize long text into short bullet
    """
    try:
        summary = summarizer(text, max_length=80, min_length=30, do_sample=False)
        if summary and 'summary_text' in summary[0]:
            return summary[0]['summary_text']
        else:
            return ""
    except Exception:
        return ""

def run(query):
    keywords = [w.lower() for w in query.split() if len(w) > 2]
    print(f"\n🔍 Searching for live news on: '{query}'...")
    urls = fetch_links(query, keywords)

    valid_summaries = []
    for url in urls:
        text = scrape_article(url, keywords)
        if text:
            summary = summarize_text(text)
            if summary:
                valid_summaries.append((summary, url))
        # silently skip invalid pages
        if len(valid_summaries) >= 7:
            break
        time.sleep(1)

    if valid_summaries:
        print("\n📢 Top News Highlights:\n")
        for idx, (summary, url) in enumerate(valid_summaries[:7], 1):
            print(f"{idx}. {summary}\n   ↳ {url}\n")
    else:
        print("❌ No strongly relevant live articles found. Try rephrasing your query.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-Powered Live News Summarizer on Any Topic")
    parser.add_argument("query", type=str, help="Example: 'latest sports news' or 'us elections 2024'")
    args = parser.parse_args()
    run(args.query)
