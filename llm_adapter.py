#!/usr/bin/env python3
"""
LLM Adapter - Support for multiple LLM providers
"""
import requests
from typing import Dict, List, Optional
import config


def call_deepseek(prompt: str, model: str = "deepseek-chat") -> Optional[str]:
    """Call DeepSeek API"""
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You extract paper metadata from search results. Output only the final result in the exact format requested."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"DeepSeek API error: {e}")
    return None


def call_openai(prompt: str, model: str = "gpt-4o") -> Optional[str]:
    """Call OpenAI API (GPT)"""
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You extract paper metadata from search results. Output only the final result in the exact format requested."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"OpenAI API error: {e}")
    return None


def call_gemini(prompt: str, model: str = "gemini-2.0-flash") -> Optional[str]:
    """Call Google Gemini API"""
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={config.LLM_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [
                    {"parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "systemInstruction": {
                        "parts": [{"text": "You extract paper metadata from search results. Output only the final result in the exact format requested."}]
                    }
                }
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    except Exception as e:
        print(f"Gemini API error: {e}")
    return None


def call_anthropic(prompt: str, model: str = "claude-sonnet-4-6") -> Optional[str]:
    """Call Anthropic Claude API"""
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": config.LLM_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "max_tokens": 1024,
                "system": "You extract paper metadata from search results. Output only the final result in the exact format requested.",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("content", [{}])[0].get("text", "")
    except Exception as e:
        print(f"Anthropic API error: {e}")
    return None


def call_qwen(prompt: str, model: str = "qwen-plus") -> Optional[str]:
    """Call Alibaba Qwen API"""
    try:
        response = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers={
                "Authorization": f"Bearer {config.LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "input": {
                    "system": "You extract paper metadata from search results. Output only the final result in the exact format requested.",
                    "messages": [{"role": "user", "content": prompt}]
                },
                "parameters": {"temperature": 0.3}
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"Qwen API error: {e}")
    return None


def call_kimi(prompt: str, model: str = "moonshot-v1-8k") -> Optional[str]:
    """Call Kimi (Moonshot) API"""
    try:
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You extract paper metadata from search results. Output only the final result in the exact format requested."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"Kimi API error: {e}")
    return None


def call_minimax(prompt: str, model: str = "MiniMax-Text-01") -> Optional[str]:
    """Call MiniMax API"""
    try:
        response = requests.post(
            "https://api.minimax.chat/v1/text/chatcompletion_v2",
            headers={
                "Authorization": f"Bearer {config.LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You extract paper metadata from search results. Output only the final result in the exact format requested."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"MiniMax API error: {e}")
    return None


def call_glm(prompt: str, model: str = "glm-4-flash") -> Optional[str]:
    """Call Zhipu GLM API"""
    try:
        response = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={
                "Authorization": f"Bearer {config.LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You extract paper metadata from search results. Output only the final result in the exact format requested."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"GLM API error: {e}")
    return None


# LLM provider mapping
LLM_PROVIDERS = {
    "deepseek": call_deepseek,
    "openai": call_openai,
    "gpt": call_openai,
    "gemini": call_gemini,
    "google": call_gemini,
    "claude": call_anthropic,
    "anthropic": call_anthropic,
    "qwen": call_qwen,
    "alibaba": call_qwen,
    "kimi": call_kimi,
    "moonshot": call_kimi,
    "minimax": call_minimax,
    "glm": call_glm,
    "zhipu": call_glm,
}

# Default models for each provider
DEFAULT_MODELS = {
    "deepseek": "deepseek-chat",
    "openai": "gpt-4o",
    "gpt": "gpt-4o",
    "gemini": "gemini-2.0-flash",
    "google": "gemini-2.0-flash",
    "claude": "claude-sonnet-4-6",
    "anthropic": "claude-sonnet-4-6",
    "qwen": "qwen-plus",
    "alibaba": "qwen-plus",
    "kimi": "moonshot-v1-8k",
    "moonshot": "moonshot-v1-8k",
    "minimax": "MiniMax-Text-01",
    "glm": "glm-4-flash",
    "zhipu": "glm-4-flash",
}


def call_llm(prompt: str, provider: str = None, model: str = None) -> Optional[str]:
    """Call LLM with specified provider"""
    if provider is None:
        provider = config.LLM_PROVIDER

    provider = provider.lower()

    if provider not in LLM_PROVIDERS:
        print(f"Unknown LLM provider: {provider}")
        return None

    if model is None:
        model = config.LLM_MODEL or DEFAULT_MODELS.get(provider)

    return LLM_PROVIDERS[provider](prompt, model)
