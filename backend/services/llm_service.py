"""LLM service for ResQ-AI using Google's Gemini API through OpenAI compatibility."""

from __future__ import annotations

import json
import os
import re
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip()
FORCE_DEMO_MODE = os.getenv("FORCE_DEMO_MODE", "false").strip().lower() == "true"

_client = None

if GEMINI_API_KEY and not FORCE_DEMO_MODE:
    try:
        _client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    except Exception:
        _client = None


def is_live_mode() -> bool:
    return _client is not None


def _extract_json(text: str) -> Optional[dict]:
    """Best-effort extraction of a JSON object from an LLM response."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return None

    return None


def call_llm_json(system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> dict:
    """
    Calls Gemini through the OpenAI-compatible API and expects a JSON object.

    Returns:
      {
        "data": parsed JSON or None,
        "raw": raw model output or None,
        "mode": "live" or "demo",
        "error": error string or None
      }
    """
    if _client is None:
        return {
            "data": None,
            "raw": None,
            "mode": "demo",
            "error": "no_api_key_or_forced_demo",
        }

    try:
        response = _client.chat.completions.create(
            model=GEMINI_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw_text = response.choices[0].message.content or ""
        parsed = _extract_json(raw_text)

        if parsed is None:
            return {
                "data": None,
                "raw": raw_text,
                "mode": "live",
                "error": "unparseable_json",
            }

        return {
            "data": parsed,
            "raw": raw_text,
            "mode": "live",
            "error": None,
        }

    except Exception as exc:
        # Keep the existing ResQ-AI demo fallback if the API is unavailable,
        # the key is invalid, or the free-tier quota is exhausted.
        return {
            "data": None,
            "raw": None,
            "mode": "demo",
            "error": str(exc),
        }
