#!/usr/bin/env python3
"""
Bib Checker - Verify BibTeX entries via Google Scholar
Uses ScraperAPI to collect all versions of papers and outputs verification results
"""
import re
import requests
from typing import List, Dict, Optional

import config

BASE_URL = "http://api.scraperapi.com"


def clean_html(text: str) -> str:
    """Clean HTML tags from text"""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def retry_request(func, max_retries: int = 3, delay: int = 2):
    """Retry a request with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1}/{max_retries} after error: {e}")
                time.sleep(delay * (attempt + 1))
            else:
                raise e


def search_google_scholar(query: str) -> Optional[str]:
    """Search Google Scholar via ScraperAPI"""
    if not config.SCRAPER_API_KEY:
        print("Error: SCRAPER_API_KEY not set in config.py")
        return None

    url = f"https://scholar.google.com/scholar?q={requests.utils.quote(query)}&hl=en"
    params = {'api_key': config.SCRAPER_API_KEY, 'url': url}

    def _request():
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.text

    try:
        return retry_request(_request, config.MAX_RETRIES, config.RETRY_DELAY)
    except Exception as e:
        print(f"Error searching: {e}")
        return None


def get_all_versions(cluster_id: str) -> List[Dict]:
    """Get all versions of a paper from Google Scholar"""
    if not config.SCRAPER_API_KEY:
        return []

    all_versions_url = f"https://scholar.google.com/scholar?cluster={cluster_id}&hl=en&as_sdt=0,5"
    params = {'api_key': config.SCRAPER_API_KEY, 'url': all_versions_url}

    def _request():
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.text

    try:
        html = retry_request(_request, config.MAX_RETRIES, config.RETRY_DELAY)
    except Exception as e:
        print(f"Error fetching all versions: {e}")
        return []

    results = []

    # Find all version titles and URLs
    version_pattern = r'<h3[^>]*class=["\']gs_rt["\'][^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
    version_matches = list(re.finditer(version_pattern, html, re.DOTALL))

    # Find all pub info
    pub_pattern = r'<div class="gs_a">(.*?)</div>'
    pub_matches = list(re.finditer(pub_pattern, html, re.DOTALL))

    for i, (v_match, pub_match) in enumerate(zip(version_matches, pub_matches)):
        v_url = v_match.group(1)
        if v_url.startswith('/'):
            v_url = "https://scholar.google.com" + v_url

        v_title = clean_html(v_match.group(2))
        pub_info = clean_html(pub_match.group(1))

        # Extract year
        year_match = re.search(r'(19|20)\d{2}', pub_info)
        year = year_match.group(0) if year_match else ''

        # Fallback: extract year from URL
        if not year:
            url_year_match = re.search(r'/([12]\d{3})/', v_url)
            if url_year_match:
                year = url_year_match.group(1)

        # Extract authors (everything before first dash)
        authors = pub_info.split('-')[0].strip() if '-' in pub_info else pub_info

        # Extract journal (everything after last dash)
        journal = ''
        if '-' in pub_info:
            parts = pub_info.split('-')
            for part in reversed(parts):
                part = part.strip()
                if re.match(r'^\d{4}$', part):
                    continue
                if part:
                    journal = part
                    break

        # Special handling for known sources
        if 'proceedings.mlr.press' in v_url.lower():
            journal = 'Proceedings of Machine Learning Research (PMLR)'
        elif 'arxiv.org' in v_url.lower():
            arxiv_match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+)', v_url)
            if arxiv_match:
                journal = f'arXiv:{arxiv_match.group(1)}'

        is_arxiv = 'arxiv.org' in v_url.lower()

        results.append({
            'version_num': i + 1,
            'title': v_title,
            'authors': authors,
            'year': year,
            'journal': journal,
            'url': v_url,
            'is_arxiv': is_arxiv
        })

    return results


def analyze_with_llm(versions: List[Dict], bib_entry: Dict = None) -> Dict:
    """Use LLM to determine the most likely correct metadata from all versions"""
    if not config.LLM_API_KEY:
        # Return the first published version if no LLM
        published = [v for v in versions if not v.get('is_arxiv')]
        if published:
            return published[0]
        return versions[0] if versions else {}

    # Prepare the versions info for the LLM
    versions_text = ""
    for v in versions:
        versions_text += f"""
Version {v['version_num']}:
  Title: {v['title']}
  Authors: {v['authors']}
  Year: {v['year']}
  Journal/Source: {v['journal']}
  URL: {v['url']}
  is_arxiv: {v['is_arxiv']}
"""

    # Add bib entry for comparison if provided
    bib_info = ""
    if bib_entry:
        bib_info = f"""
BIB ENTRY TO COMPARE:
  Authors: {bib_entry.get('author', '')}
  Year: {bib_entry.get('year', '')}
  Journal: {bib_entry.get('journal', '')}"""

    prompt = f"""Given the following multiple versions of the same paper from Google Scholar, determine the most likely CORRECT metadata.
Consider:
- Published versions (not arXiv) are preferred over arXiv preprints
- Conference proceedings (like PMLR/ICML) are preferred over preprints
- More complete author lists are more reliable
- Author names may have format differences (e.g., "Li, hua" vs "Hua Li") - compare by surname matching

{bib_info}

{versions_text}

Output ONLY in this exact format (no other text):
Title: <correct title>
Authors: <comma-separated full author names>
Year: <4-digit year>
Journal: <full journal or conference name>
Match_Authors: YES if bib authors match found authors (surname match), NO if different
Match_Year: YES if bib year matches found year, NO if different
Match_Journal: YES if bib journal matches found journal (keyword match), NO if different"""

    try:
        # Use LLM adapter
        import llm_adapter
        content = llm_adapter.call_llm(prompt)

        if content:
            # Parse the LLM response
            llm_result = {}
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith("Title:"):
                    llm_result['title'] = line.replace("Title:", "").strip()
                elif line.startswith("Authors:"):
                    llm_result['authors'] = line.replace("Authors:", "").strip()
                elif line.startswith("Year:"):
                    llm_result['year'] = line.replace("Year:", "").strip()
                elif line.startswith("Journal:"):
                    llm_result['journal'] = line.replace("Journal:", "").strip()
                elif line.startswith("Match_Authors:"):
                    llm_result['match_authors'] = line.replace("Match_Authors:", "").strip().upper()
                elif line.startswith("Match_Year:"):
                    llm_result['match_year'] = line.replace("Match_Year:", "").strip().upper()
                elif line.startswith("Match_Journal:"):
                    llm_result['match_journal'] = line.replace("Match_Journal:", "").strip().upper()

            if llm_result:
                return llm_result

    except Exception as e:
        print(f"  LLM error: {e}")

    # Fallback: return first published version
    published = [v for v in versions if not v.get('is_arxiv')]
    if published:
        return published[0]
    return versions[0] if versions else {}


def parse_bib_file(filepath: str) -> List[Dict]:
    """Parse a BibTeX file and return list of entries"""
    entries = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []

    # Parse BibTeX entries
    entry_pattern = r'@(\w+)\s*\{\s*([^,\s]+),([^@]+)\}'
    matches = re.finditer(entry_pattern, content, re.DOTALL)

    for match in matches:
        entry_type = match.group(1)
        cite_key = match.group(2)
        fields_str = match.group(3)

        # Extract fields
        title = ''
        author = ''
        year = ''
        journal = ''
        booktitle = ''

        title_match = re.search(r'title\s*=\s*[{"]([^}"]+)[}"]', fields_str, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()

        author_match = re.search(r'author\s*=\s*\{([^}]+)\}', fields_str, re.IGNORECASE)
        if author_match:
            author = author_match.group(1).strip()

        year_match = re.search(r'year\s*=\s*[{"]([^}"]+)[}"]', fields_str, re.IGNORECASE)
        if year_match:
            year = year_match.group(1).strip()

        journal_match = re.search(r'journal\s*=\s*\{([^}]+)\}', fields_str, re.IGNORECASE)
        if journal_match:
            journal = journal_match.group(1).strip()

        booktitle_match = re.search(r'booktitle\s*=\s*\{([^}]+)\}', fields_str, re.IGNORECASE)
        if booktitle_match:
            booktitle = booktitle_match.group(1).strip()

        entries.append({
            'cite_key': cite_key,
            'entry_type': entry_type,
            'title': title,
            'author': author,
            'year': year,
            'journal': journal or booktitle,
            'original_title': title
        })

    return entries


def verify_entry(entry: Dict) -> Dict:
    """Verify a single entry against Google Scholar"""
    title = entry.get('original_title', entry.get('title', ''))
    if not title:
        return {'error': 'No title to search'}

    print(f"Searching: {title[:60]}...")

    # Search
    html = search_google_scholar(title)
    if not html:
        return {'error': 'Search failed'}

    # Find cluster ID
    cluster_match = re.search(r'cluster=(\d+)', html)
    if not cluster_match:
        return {'error': 'No cluster ID found'}

    cluster_id = cluster_match.group(1)

    # Get all versions
    versions = get_all_versions(cluster_id)

    if not versions:
        return {'error': 'No versions found'}

    # Use LLM to determine the best metadata
    print(f"  Analyzing {len(versions)} versions with LLM...")
    best = analyze_with_llm(versions, entry)

    return {
        'versions': versions,
        'num_versions': len(versions),
        'best': best  # LLM-determined best metadata
    }


def format_markdown_table(results: List[Dict], entries: List[Dict]) -> str:
    """Format results as markdown table"""
    lines = [
        "# BibTeX Verification Report",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\nSource: Google Scholar (via ScraperAPI)",
        "\n---\n",
        f"\n## Summary: {len(entries)} entries checked\n"
    ]

    # Main table
    lines.append("| # | Cite Key | Title | Found | Year | Journal/Conf | Authors |")
    lines.append("|---|----------|-------|-------|------|-------------|--------|")

    for i, (entry, result) in enumerate(zip(entries, results), 1):
        cite_key = entry.get('cite_key', '')
        title = entry.get('title', '')[:config.TITLE_MAX_LEN] if config.TITLE_MAX_LEN else entry.get('title', '')
        bib_year = entry.get('year', '')
        bib_journal = entry.get('journal', '')
        bib_author = entry.get('author', '')

        if 'error' in result:
            status = f"[ERROR] {result['error']}"
            year_match = "-"
            journal_match = "-"
            author_match = "-"
            num_versions = 0
        else:
            versions = result.get('versions', [])
            num_versions = len(versions)
            status = f"Found {num_versions} versions"

            # Use LLM-determined best metadata and match status
            best = result.get('best', {})
            found_year = best.get('year', '')
            found_journal = best.get('journal', '')
            found_authors = best.get('authors', '')
            match_year = best.get('match_year', '')
            match_journal = best.get('match_journal', '')
            match_authors = best.get('match_authors', '')

            # Year comparison (use LLM result if available, otherwise manual)
            if match_year:
                year_match = f"[{match_year}] {bib_year}" if match_year == "YES" else f"[{match_year}] {bib_year} -> {found_year}"
            elif bib_year and found_year:
                if bib_year == found_year:
                    year_match = f"[OK] {bib_year}"
                else:
                    year_match = f"[WARN] {bib_year} -> {found_year}"
            else:
                year_match = f"{bib_year or '-'} -> {found_year or '-'}"

            # Journal comparison (use LLM result if available)
            if match_journal:
                j_short = bib_journal[:config.JOURNAL_MAX_LEN] if config.JOURNAL_MAX_LEN and bib_journal else bib_journal
                if match_journal == "YES":
                    journal_match = f"[OK] {j_short}"
                else:
                    j_found = found_journal[:config.JOURNAL_MAX_LEN] if config.JOURNAL_MAX_LEN and found_journal else found_journal
                    journal_match = f"[WARN] {j_short} -> {j_found}"
            else:
                j_short = bib_journal[:config.JOURNAL_MAX_LEN] if config.JOURNAL_MAX_LEN and bib_journal else bib_journal
                j_found = found_journal[:config.JOURNAL_MAX_LEN] if config.JOURNAL_MAX_LEN and found_journal else found_journal
                if bib_journal and found_journal and bib_journal.lower() in found_journal.lower():
                    journal_match = f"[OK] {j_short}"
                else:
                    journal_match = f"[WARN] {j_short} -> {j_found}"

            # Author comparison (use LLM result)
            if match_authors:
                a_short = bib_author[:config.AUTHOR_MAX_LEN] if config.AUTHOR_MAX_LEN and bib_author else bib_author
                if match_authors == "YES":
                    author_match = f"[OK] {a_short}"
                else:
                    a_found = found_authors[:config.AUTHOR_MAX_LEN] if config.AUTHOR_MAX_LEN and found_authors else found_authors
                    author_match = f"[WARN] {a_short} -> {a_found}"
            else:
                a_short = bib_author[:config.AUTHOR_MAX_LEN] if config.AUTHOR_MAX_LEN and bib_author else bib_author
                a_found = found_authors[:config.AUTHOR_MAX_LEN] if config.AUTHOR_MAX_LEN and found_authors else found_authors
                author_match = f"{a_short} -> {a_found}"

        lines.append(f"| {i} | {cite_key} | {title}... | {status} | {year_match} | {journal_match} | {author_match} |")

    lines.append("\n---\n")

    # Detailed versions for each entry
    lines.append("## Detailed Versions\n")

    for i, (entry, result) in enumerate(zip(entries, results), 1):
        if 'error' in result:
            continue

        versions = result.get('versions', [])
        if not versions:
            continue

        cite_key = entry.get('cite_key', '')
        title = entry.get('title', '')

        lines.append(f"\n### {i}. [{cite_key}]")
        lines.append(f"\n**Title**: {title}\n")

        for v in versions:
            vtype = "[arXiv]" if v.get('is_arxiv') else "[Published]"
            vtitle = v.get('title', '')[:config.TITLE_MAX_LEN] if config.TITLE_MAX_LEN else v.get('title', '')
            vyear = v.get('year', '-')
            vjournal = v.get('journal', '-')
            vauthors = v.get('authors', '')[:config.AUTHOR_MAX_LEN] if config.AUTHOR_MAX_LEN else v.get('authors', '')
            vurl = v.get('url', '')

            lines.append(f"\n- **{vtype}** {vyear} - {vjournal}")
            lines.append(f"  - Title: {vtitle}")
            lines.append(f"  - Authors: {vauthors}")
            lines.append(f"  - URL: {vurl}")

    return "\n".join(lines)


def format_text_table(results: List[Dict], entries: List[Dict]) -> str:
    """Format results as plain text"""
    lines = [
        "BibTeX Verification Report",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Source: Google Scholar (via ScraperAPI)",
        "",
        f"Summary: {len(entries)} entries checked",
        "=" * 60,
    ]

    for i, (entry, result) in enumerate(zip(entries, results), 1):
        cite_key = entry.get('cite_key', '')
        title = entry.get('title', '')
        bib_year = entry.get('year', '')
        bib_journal = entry.get('journal', '')

        lines.append(f"\n[{i}] {cite_key}")
        lines.append(f"    Title: {title}")
        bib_journal_trunc = bib_journal[:config.JOURNAL_MAX_LEN] if config.JOURNAL_MAX_LEN else bib_journal
        lines.append(f"    Bib: {bib_year} | {bib_journal_trunc}")

        if 'error' in result:
            lines.append(f"    Status: ERROR - {result['error']}")
        else:
            versions = result.get('versions', [])
            num_versions = len(versions)
            lines.append(f"    Status: Found {num_versions} versions")

            # Show LLM-determined best
            best = result.get('best', {})
            if best:
                best_journal = best.get('journal', '-')[:config.JOURNAL_MAX_LEN] if config.JOURNAL_MAX_LEN else best.get('journal', '-')
                best_authors = best.get('authors', '-')[:config.AUTHOR_MAX_LEN] if config.AUTHOR_MAX_LEN else best.get('authors', '-')
                lines.append(f"    LLM Best: {best.get('year', '-')} | {best_journal}")
                lines.append(f"    Authors: {best_authors}")

            # Show first 3 versions
            for v in versions[:3]:
                vtype = "arXiv" if v.get('is_arxiv') else "Pub"
                vyear = v.get('year', '-')
                vjournal = v.get('journal', '-')
                lines.append(f"      - [{vtype}] {vyear} | {vjournal[:40]}")

    return "\n".join(lines)


def format_json_output(results: List[Dict], entries: List[Dict]) -> str:
    """Format results as JSON"""
    output = {
        'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': 'Google Scholar (via ScraperAPI)',
        'entries': []
    }

    for entry, result in zip(entries, results):
        output['entries'].append({
            'cite_key': entry.get('cite_key'),
            'title': entry.get('title'),
            'bib_year': entry.get('year'),
            'bib_journal': entry.get('journal'),
            'result': result
        })

    return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="BibTeX Verification via Google Scholar")
    parser.add_argument("files", nargs="+", help="BibTeX files to verify")
    parser.add_argument("--output", "-o", help="Output file (default: verification_report.md)")
    parser.add_argument("--format", "-f", choices=["markdown", "txt", "json"], help="Output format")
    parser.add_argument("--llm", "-l", help="LLM provider (deepseek, openai/gpt, gemini/google, claude/anthropic, qwen/alibaba, kimi/moonshot, minimax, glm/zhipu)")

    args = parser.parse_args()

    # Override config LLM provider if specified
    if args.llm:
        config.LLM_PROVIDER = args.llm.lower()

    # Check config
    if not config.SCRAPER_API_KEY:
        print("Error: Please set SCRAPER_API_KEY in config.py")
        sys.exit(1)

    # Parse all entries
    all_entries = []
    for filepath in args.files:
        entries = parse_bib_file(filepath)
        print(f"Loaded {len(entries)} entries from {filepath}")
        all_entries.extend(entries)

    if not all_entries:
        print("No entries found")
        sys.exit(1)

    print(f"\nVerifying {len(all_entries)} entries...\n")

    # Verify each entry
    results = []
    for i, entry in enumerate(all_entries, 1):
        print(f"[{i}/{len(all_entries)}] ", end="", flush=True)
        result = verify_entry(entry)
        results.append(result)

        if 'error' not in result:
            print(f"Found {result.get('num_versions', 0)} versions")
        else:
            print(f"Error: {result.get('error')}")

    # Format output
    output_format = args.format or config.OUTPUT_FORMAT
    output_file = args.output or config.OUTPUT_FILE

    if output_format == "markdown":
        content = format_markdown_table(results, all_entries)
    elif output_format == "txt":
        content = format_text_table(results, all_entries)
    elif output_format == "json":
        content = format_json_output(results, all_entries)
    else:
        content = format_markdown_table(results, all_entries)

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n[OK] Results saved to {output_file}")


if __name__ == "__main__":
    import requests
    main()
