"""Paper matching logic."""

import requests
from config import LLM_API_URL, LLM_API_HEADERS, LLM_MODEL, LLM_PROVIDER, VENUE_ABBR_MAP


def is_same(user, paper):
    """Check if user entry matches the paper from Semantic Scholar."""
    u_title = user.get("title", "")
    r_title = paper.get("title", "")

    # Build venue abbreviation reference for the LLM
    abbr_list = "\n".join([f"- {full}: {abbr}" for full, abbr in VENUE_ABBR_MAP.items()])
    venue_ref = f"\n\nKnown venue abbreviations:\n{abbr_list}"

    prompt = f"Determine if these are the same paper, reply YES/NO only:{venue_ref}\n\nUser title: {u_title}\nActual title: {r_title}"

    try:
        # Handle different provider APIs
        if LLM_PROVIDER == "claude":
            # Claude uses different message format
            resp = requests.post(
                LLM_API_URL,
                headers=LLM_API_HEADERS,
                json={
                    "model": LLM_MODEL,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=10
            )
            content = resp.json()["content"][0]["text"]
        elif LLM_PROVIDER == "gemini":
            # Gemini uses different format
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
            # OpenAI-compatible API (deepseek, qwen, kimi, gpt, openai)
            resp = requests.post(
                LLM_API_URL,
                headers=LLM_API_HEADERS,
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0
                },
                timeout=10
            )
            content = resp.json()["choices"][0]["message"]["content"]

        return "YES" in content.upper()
    except:
        return True
