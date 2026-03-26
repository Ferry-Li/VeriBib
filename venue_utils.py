"""Venue (conference/journal) abbreviation utilities."""

import re
import requests
from config import VENUE_ABBR_MAP, USE_LLM_FOR_VENUE_ABBR, LLM_API_URL, LLM_API_HEADERS, LLM_MODEL, LLM_PROVIDER


def abbr_venue(venue_name):
    """Abbreviate venue name using rules or LLM."""
    if not venue_name:
        return ""

    # 1. Match using rule dictionary (case-insensitive, simple punctuation removal)
    v_clean = re.sub(r'[^\w\s]', '', venue_name).strip().lower()
    for long_full, short_name in VENUE_ABBR_MAP.items():
        l_clean = re.sub(r'[^\w\s]', '', long_full).strip().lower()
        # Match if one contains the other (loose matching)
        if l_clean in v_clean or v_clean in l_clean:
            return short_name

    # 2. Rule didn't match, use LLM abbreviation if enabled
    if USE_LLM_FOR_VENUE_ABBR:
        return llm_abbreviate_venue(venue_name)

    return venue_name


def llm_abbreviate_venue(venue):
    """Use LLM to generate venue abbreviation."""
    # Build known abbreviations reference
    abbr_list = "\n".join([f"- {full}: {abbr}" for full, abbr in VENUE_ABBR_MAP.items()])

    prompt = f"""
You are an academic paper formatting expert.
Please abbreviate the following conference or journal name to its standard abbreviation in the field.
Only output the abbreviation itself, no additional explanation.
If it is already an abbreviation, output it as is.

Known venue abbreviations:
{abbr_list}

Name: {venue}
"""
    try:
        # Handle different provider APIs
        if LLM_PROVIDER == "claude":
            resp = requests.post(
                LLM_API_URL,
                headers=LLM_API_HEADERS,
                json={
                    "model": LLM_MODEL,
                    "max_tokens": 20,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=10
            )
            content = resp.json()["content"][0]["text"]
        elif LLM_PROVIDER == "gemini":
            resp = requests.post(
                LLM_API_URL,
                headers=LLM_API_HEADERS,
                json={
                    "contents": [{"parts": [{"text": prompt}]}]
                },
                timeout=10
            )
            content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # OpenAI-compatible API
            resp = requests.post(
                LLM_API_URL,
                headers=LLM_API_HEADERS,
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                },
                timeout=10
            )
            content = resp.json()["choices"][0]["message"]["content"]

        return content.strip()
    except Exception as e:
        return venue
