"""Semantic Scholar API client."""

import requests
import time
from config import SS_API_KEY


def search_ss(title):
    """Search Semantic Scholar for a paper by title."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {}
    if SS_API_KEY:
        headers["x-api-key"] = SS_API_KEY

    params = {
        "query": title,
        "limit": 10,
        "fields": "title,year,venue,externalIds,authors,paperId"
    }

    # Retry up to 5 times to avoid hanging
    max_retries = 5
    for attempt in range(max_retries):
        try:
            res = requests.get(
                url,
                headers=headers,
                params=params,
                verify=False,
                timeout=20
            )

            # Success - return immediately
            if res.status_code == 200:
                return res.json()

            # Rate limit / server error - retry
            if res.status_code in (429, 500, 502, 503, 504):
                print(f"Server busy, retrying {attempt+1}/{max_retries}")
                time.sleep(3)
                continue

            # Other errors (404, 403, 401, etc.) - no retry
            print(f"API error: {res.status_code}")
            return None

        except Exception as e:
            print(f"Network error, retry {attempt+1}/{max_retries}")
            time.sleep(2)

    # Max retries exceeded - return None
    print("Multiple retries failed, skipping")
    return None


def search_by_author_title(author_lastname, title_words, year=None):
    """Fallback search using author and title keywords."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    headers = {}
    if SS_API_KEY:
        headers["x-api-key"] = SS_API_KEY

    # Build query from title words and author
    query_parts = [author_lastname] + title_words[:5]  # Limit keywords
    query = " ".join(query_parts)
    if year:
        query += f" {year}"

    params = {
        "query": query,
        "limit": 10,
        "fields": "title,year,venue,externalIds,authors,paperId"
    }

    try:
        res = requests.get(
            url,
            headers=headers,
            params=params,
            verify=False,
            timeout=20
        )
        if res.status_code == 200:
            return res.json()
    except:
        pass

    return None
