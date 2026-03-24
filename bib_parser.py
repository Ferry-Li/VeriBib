#!/usr/bin/env python3
"""BibTeX Parser"""
import re
from typing import List, Dict


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
        title = _extract_field(fields_str, 'title')
        author = _extract_field(fields_str, 'author')
        year = _extract_field(fields_str, 'year')
        journal = _extract_field(fields_str, 'journal')
        booktitle = _extract_field(fields_str, 'booktitle')

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


def _extract_field(content: str, field_name: str) -> str:
    """Extract a field from BibTeX content"""
    match = re.search(
        rf'{field_name}\s*=\s*[{{"]([^}}"]+)[}}"]',
        content,
        re.IGNORECASE
    )
    return match.group(1).strip() if match else ''
