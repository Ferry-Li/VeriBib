#!/usr/bin/env python3
"""LLM Analysis - Analyze paper versions and compare with BibTeX"""
from typing import Dict, List
import llm_adapter


def analyze_with_llm(versions: List[Dict], bib_entry: Dict = None) -> Dict:
    """Use LLM to determine the most likely correct metadata from all versions"""
    if not bib_entry:
        bib_entry = {}

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

    # Add bib entry for comparison
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
        content = llm_adapter.call_llm(prompt)

        if content:
            return _parse_llm_response(content)

    except Exception as e:
        print(f"  LLM error: {e}")

    # Fallback: return first published version
    published = [v for v in versions if not v.get('is_arxiv')]
    if published:
        return published[0]
    return versions[0] if versions else {}


def _parse_llm_response(content: str) -> Dict:
    """Parse LLM response"""
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

    return llm_result
