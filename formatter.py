#!/usr/bin/env python3
"""Output Formatter - Format verification results"""
import json
from typing import List, Dict
from datetime import datetime
import config


def format_markdown(results: List[Dict], entries: List[Dict], detailed: bool = False) -> str:
    """Format results as markdown"""
    lines = [
        "# BibTeX Verification Report",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\nSource: Google Scholar (via ScraperAPI)",
        "\n---",
        f"\n## Summary: {len(entries)} entries checked\n"
    ]

    # Header
    lines.append("| # | Cite Key | Title | Found | Year | Journal/Conf | Authors |")
    lines.append("|---|----------|-------|-------|------|-------------|--------|")

    for i, (entry, result) in enumerate(zip(entries, results), 1):
        row = _format_row(i, entry, result)
        lines.append(row)

    # Detailed versions (optional)
    if detailed:
        lines.append("\n---\n")
        lines.append("## Detailed Versions\n")

        for i, (entry, result) in enumerate(zip(entries, results), 1):
            if 'error' in result or not result.get('versions'):
                continue

            lines.append(f"\n### {i}. [{entry.get('cite_key', '')}]")
            lines.append(f"\n**Title**: {entry.get('title', '')}\n")

            for v in result.get('versions', []):
                vtype = "[arXiv]" if v.get('is_arxiv') else "[Published]"
                lines.append(f"\n- **{vtype}** {v.get('year', '-')} - {v.get('journal', '-')}")
                lines.append(f"  - Title: {v.get('title', '')[:60]}")
                lines.append(f"  - Authors: {v.get('authors', '')[:50]}")
                lines.append(f"  - URL: {v.get('url', '')}")

    return "\n".join(lines)


def _format_row(idx: int, entry: Dict, result: Dict) -> str:
    """Format a single table row"""
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
    else:
        num_versions = len(result.get('versions', []))
        status = f"Found {num_versions} versions"

        best = result.get('best', {})
        found_year = best.get('year', '')
        found_journal = best.get('journal', '')
        found_authors = best.get('authors', '')
        match_year = best.get('match_year', '')
        match_journal = best.get('match_journal', '')
        match_authors = best.get('match_authors', '')

        # Year
        if match_year:
            year_match = f"[{match_year}] {bib_year}" if match_year == "YES" else f"[{match_year}] {bib_year} -> {found_year}"
        else:
            year_match = f"[OK] {bib_year}" if bib_year == found_year else f"[WARN] {bib_year} -> {found_year}"

        # Journal
        j_short = bib_journal[:config.JOURNAL_MAX_LEN] if config.JOURNAL_MAX_LEN and bib_journal else bib_journal
        if match_journal:
            journal_match = f"[{match_journal}] {j_short}" if match_journal == "YES" else f"[{match_journal}] {j_short} -> {found_journal[:config.JOURNAL_MAX_LEN] if config.JOURNAL_MAX_LEN else found_journal}"
        else:
            journal_match = f"[WARN] {j_short} -> {found_journal[:config.JOURNAL_MAX_LEN] if config.JOURNAL_MAX_LEN else found_journal}"

        # Authors
        a_short = bib_author[:config.AUTHOR_MAX_LEN] if config.AUTHOR_MAX_LEN and bib_author else bib_author
        if match_authors:
            author_match = f"[{match_authors}] {a_short}" if match_authors == "YES" else f"[{match_authors}] {a_short} -> {found_authors[:config.AUTHOR_MAX_LEN] if config.AUTHOR_MAX_LEN else found_authors}"
        else:
            author_match = f"{a_short} -> {found_authors[:config.AUTHOR_MAX_LEN] if config.AUTHOR_MAX_LEN else found_authors}"

    return f"| {idx} | {cite_key} | {title}... | {status} | {year_match} | {journal_match} | {author_match} |"


def format_text(results: List[Dict], entries: List[Dict], detailed: bool = False) -> str:
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
        lines.append(f"    Bib: {bib_year} | {bib_journal[:30] if bib_journal else '-'}")

        if 'error' in result:
            lines.append(f"    Status: ERROR - {result['error']}")
        else:
            lines.append(f"    Status: Found {len(result.get('versions', []))} versions")
            best = result.get('best', {})
            if best:
                lines.append(f"    LLM Best: {best.get('year', '-')} | {best.get('journal', '-')[:40]}")
                lines.append(f"    Authors: {best.get('authors', '-')[:50]}")

            # Detailed versions (optional)
            if detailed and result.get('versions'):
                for v in result.get('versions', [])[:3]:
                    vtype = "arXiv" if v.get('is_arxiv') else "Pub"
                    lines.append(f"      - [{vtype}] {v.get('year', '-')} | {v.get('journal', '-')[:40]}")

    return "\n".join(lines)


def format_json(results: List[Dict], entries: List[Dict], detailed: bool = False) -> str:
    """Format results as JSON"""
    output = {
        'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': 'Google Scholar (via ScraperAPI)',
        'entries': []
    }

    for entry, result in zip(entries, results):
        entry_data = {
            'cite_key': entry.get('cite_key'),
            'title': entry.get('title'),
            'bib_year': entry.get('year'),
            'bib_journal': entry.get('journal'),
        }

        # Always include basic result
        if 'error' not in result:
            entry_data['num_versions'] = len(result.get('versions', []))
            entry_data['best'] = result.get('best', {})

        # Detailed versions (optional)
        if detailed and 'versions' in result:
            entry_data['versions'] = result['versions']

        output['entries'].append(entry_data)

    return json.dumps(output, ensure_ascii=False, indent=2)
