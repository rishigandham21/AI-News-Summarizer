from ddgs import DDGS

def fetch_toi_links():
    """
    Hardcoded Times of India India section (most active)
    """
    return ["https://timesofindia.indiatimes.com/india"]

def search_news(query, max_results=7):
    """
    Use DuckDuckGo to search for news on the topic
    """
    links = []
    with DDGS() as ddgs:
        for r in ddgs.text(query , region="in-en", safesearch="off"):
            url = r.get('href')
            if url:
                links.append(url)
            if len(links) >= max_results:
                break
    return links

def get_links(query):
    if "times of india" in query.lower() or "toi" in query.lower():
        return fetch_toi_links()
    else:
        return search_news(query)
