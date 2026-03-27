"""Paper matching logic."""

import requests
import re
from config import LLM_API_URL, LLM_API_HEADERS, LLM_MODEL, LLM_PROVIDER, VENUE_ABBR_MAP


def count_word_diff(title1, title2):
    """Count the number of different words between two titles.

    Returns:
        int: Number of words that differ (word-level symmetric difference)
    """
    # Extract words (alphanumeric, longer than 2 chars)
    words1 = set(re.findall(r'\w+', title1.lower()))
    words2 = set(re.findall(r'\w+', title2.lower()))

    # Common words to ignore
    stop_words = {'a', 'an', 'the', 'of', 'for', 'in', 'on', 'with', 'and', 'to', 'via', 'using', 'based', 'from', 'by'}
    words1 = set(w for w in words1 if w not in stop_words and len(w) > 2)
    words2 = set(w for w in words2 if w not in stop_words and len(w) > 2)

    # Word difference = words in one but not the other
    return len(words1.symmetric_difference(words2))


def check_match(user, paper, max_word_diff=3):
    """Check if user entry matches the paper from Semantic Scholar.

    Args:
        user: User's bib entry
        paper: Paper from Semantic Scholar
        max_word_diff: Maximum word difference allowed for title match

    Returns:
        dict with:
            - match: bool - whether it's the same paper
            - title_match: bool
            - word_diff: int - number of different words in title
            - author_match: bool
            - year_match: bool
            - venue_match: bool
    """
    u_title = user.get("title", "").lower().strip()
    u_author = user.get("author", "").lower()
    u_year = str(user.get("year", "")).strip()
    u_venue = user.get("booktitle", user.get("journal", "")).lower()

    r_title = paper.get("title", "").lower().strip()
    r_author = " & ".join([a["name"] for a in paper.get("authors", [])]).lower()
    r_year = str(paper.get("year", "")).strip()
    r_venue = paper.get("venue", "").lower()

    # Title match based on word difference
    word_diff = count_word_diff(u_title, r_title)
    title_match = word_diff <= max_word_diff

    # Check year
    year_match = (u_year == r_year) or (not u_year) or (not r_year)

    # Check venue (abbreviation allowed)
    from venue_utils import abbr_venue
    u_venue_abbr = abbr_venue(u_venue).lower() if u_venue else ""
    r_venue_abbr = abbr_venue(r_venue).lower() if r_venue else ""

    venue_match = (u_venue == r_venue) or (u_venue_abbr == r_venue_abbr) or (not u_venue)

    # Check author (partial match allowed)
    author_match = False
    if u_author and r_author:
        # Get last names
        u_lastnames = [name.split()[-1] for name in u_author.replace(",", " ").split(" and ")]
        r_lastnames = [name.split()[-1] for name in r_author.replace(" & ", " ").replace(",", " ").split()]

        # Check if at least half of authors match
        matches = sum(1 for ul in u_lastnames if any(rl.startswith(ul[:3]) for rl in r_lastnames))
        author_match = matches > 0 and matches >= len(u_lastnames) / 2
    else:
        author_match = True  # No author info to compare

    # Overall match requires title match and venue match (when user provides venue)
    match = title_match and (year_match or not u_year or not r_year) and (venue_match or not u_venue)

    return {
        "match": match,
        "title_match": title_match,
        "word_diff": word_diff,
        "author_match": author_match,
        "year_match": year_match,
        "venue_match": venue_match
    }


def is_same(user, paper):
    """Check if user entry matches the paper from Semantic Scholar (simple bool)."""
    result = check_match(user, paper)
    return result["match"]
