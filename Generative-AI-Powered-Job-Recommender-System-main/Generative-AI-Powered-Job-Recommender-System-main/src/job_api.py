import feedparser


RSS_FEEDS = [
    ("WeWorkRemotely", "https://weworkremotely.com/categories/remote-programming-jobs.rss"),
    ("Remotive", "https://remotive.io/remote-jobs.rss"),
]


def fetch_rss_jobs(search_query: str, rows: int = 60):
    search_terms = [s.lower() for s in search_query.split(',') if s.strip()] or [search_query.lower()]
    results = []

    for source, url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            blob = f"{title} {summary}".lower()
            if any(term.strip() and term.strip() in blob for term in search_terms):
                link = entry.get('link')
                company = entry.get('author') or (title.split('-')[-1].strip() if '-' in title else "")
                results.append({
                    "title": title,
                    "companyName": company or source,
                    "url": link,
                    "source": source,
                })
            if len(results) >= rows:
                break
        if len(results) >= rows:
            break

    return results
