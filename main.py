"""Main entry point for Bib Checker."""

import argparse
import re
import time
from config import BIB_FILE, OUTPUT_BIB, SLEEP_TIME, VENUE_ABBR_MAP, TITLE_MAX_WORD_DIFF
from bib_parser import parse_bib_file
from semantic_scholar import search_ss, search_by_author_title
from matcher import check_match
from exporter import export_updated_bib, export_md


def extract_author_lastname(author_str):
    """Extract first author's last name from author string."""
    if not author_str:
        return None

    # Split by " and " to get first author
    first_author = author_str.split(" and ")[0].strip()

    # Get last name (first word before comma, or last word)
    if "," in first_author:
        # Format: "LastName, FirstName"
        return first_author.split(",")[0].strip()
    else:
        # Format: "FirstName LastName"
        parts = first_author.split()
        return parts[-1] if parts else None


def get_venue_priority(paper):
    """Get priority for a paper based on venue.

    Priority (lower is better):
    1. Known venues in VENUE_ABBR_MAP (priority 1)
    2. Other journals/conferences (priority 2)
    3. ArXiv (priority 3)
    4. Empty venue (priority 4)
    """
    venue = paper.get("venue", "").lower()
    if not venue:
        return 4  # Empty venue has lowest priority

    # Check if venue is in VENUE_ABBR_MAP (case-insensitive)
    for known_venue in VENUE_ABBR_MAP.keys():
        if known_venue.lower() in venue or venue in known_venue.lower():
            return 1

    # Check for arxiv
    if "arxiv" in venue:
        return 3

    # Other journals/conferences
    return 2


def process(bib):
    """Process a single BibTeX entry."""
    title = bib.get("title", "").strip()
    author = bib.get("author", "")
    year = bib.get("year", "")

    if not title:
        return {"status": "❌ Title is empty", "orig": bib, "ss": None, "match_details": {}}

    # First attempt: search by title
    data = search_ss(title)

    best = None
    match_details = {}
    if data and "data" in data and len(data["data"]) > 0:
        # Try matching with progressively more word differences: 0, 1, 2, ...
        for max_diff in range(TITLE_MAX_WORD_DIFF + 1):
            # Get papers that match title within this word diff
            title_matches = []
            for p in data["data"]:
                result = check_match(bib, p, max_word_diff=max_diff)
                if result["title_match"]:
                    title_matches.append((p, result))

            if title_matches:
                # Among title matches, rank by: 1) author match, 2) venue priority, 3) word_diff
                # author_match is True/False, convert to 0/1 for sorting (True=1 is better)
                best, match_details = min(title_matches, key=lambda x: (
                    -int(x[1].get("author_match", False)),  # Higher is better (invert)
                    get_venue_priority(x[0]),                 # Lower is better
                    x[1].get("word_diff", 0)                 # Lower is better
                ))

                # Now check if it's a full match (including venue)
                if best and match_details.get("match"):
                    break
                else:
                    # Keep looking for better match with more word differences
                    pass

    # Fallback: try search with author + title keywords
    if not best and author:
        lastname = extract_author_lastname(author)
        title_words = re.findall(r'\w+', title)
        fallback_data = search_by_author_title(lastname, title_words, year)

        if fallback_data and "data" in fallback_data and len(fallback_data["data"]) > 0:
            # Try matching with progressively more word differences
            for max_diff in range(TITLE_MAX_WORD_DIFF + 1):
                title_matches = []
                for p in fallback_data["data"]:
                    result = check_match(bib, p, max_word_diff=max_diff)
                    if result["title_match"]:
                        title_matches.append((p, result))

                if title_matches:
                    # Among title matches, rank by author match, then venue priority, then word_diff
                    best, match_details = min(title_matches, key=lambda x: (
                        -int(x[1].get("author_match", False)),
                        get_venue_priority(x[0]),
                        x[1].get("word_diff", 0)
                    ))
                    break

    if not data or "data" not in data or len(data["data"]) == 0:
        return {"status": "❌ Not found in Semantic Scholar", "orig": bib, "ss": None, "match_details": {}}

    # Check if we have a full match (including venue)
    if not best or not match_details.get("match"):
        # Even if not a full match, return the best candidate from SS
        # Rank by: title match > author match > venue priority > word_diff
        if data and "data" in data:
            ranked = []
            for p in data["data"]:
                result = check_match(bib, p, max_word_diff=TITLE_MAX_WORD_DIFF)
                ranked.append((p, result))

            if ranked:
                best, match_details = min(ranked, key=lambda x: (
                    -int(x[1].get("title_match", False)),   # Higher is better
                    -int(x[1].get("author_match", False)),  # Higher is better
                    get_venue_priority(x[0]),                # Lower is better
                    x[1].get("word_diff", 0)                # Lower is better
                ))

        return {"status": "⚠️ Mismatch", "orig": bib, "ss": best, "match_details": match_details}

    return {
        "status": "✅ Up-to-date",
        "orig": bib,
        "ss": best,
        "url": f"https://www.semanticscholar.org/paper/{best['paperId']}",
        "match_details": match_details
    }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="BibTeX Checker - Verify and fix BibTeX entries using Semantic Scholar")
    parser.add_argument("input", nargs="?", default=BIB_FILE, help="Input BibTeX file (default: test.bib)")
    parser.add_argument("-o", "--output", metavar="FILE", help="Output optimized BibTeX file (default: output_updated.bib)")
    parser.add_argument("--no-output", action="store_true", help="Do not output optimized BibTeX file")
    parser.add_argument("-r", "--report", metavar="FILE", help="Output report file (default: bib_report.md)")
    parser.add_argument("--no-report", action="store_true", help="Do not output report file")

    args = parser.parse_args()

    input_file = args.input
    output_file = None if args.no_output else (args.output if args.output else OUTPUT_BIB)
    report_file = None if args.no_report else (args.report if args.report else "bib_report.md")

    entries = parse_bib_file(input_file)
    print(f"Reading {len(entries)} items from {input_file}")

    results = []
    for i, e in enumerate(entries, 1):
        print(f"{i}/{len(entries)}")
        res = process(e)
        results.append(res)
        time.sleep(SLEEP_TIME)

    if report_file:
        export_md(results, report_file)
        print(f"Report: {report_file}")

    if output_file:
        export_updated_bib(results, output_file)
        print(f"Optimized BibTeX: {output_file}")

    print("✅ Done!")


if __name__ == "__main__":
    main()
