# classifier.py

"""
Simple keyword-based classifier to assign a review to one of the predefined themes.
"""

from themes import THEMES

def assign_theme(text: str) -> str:
    """Assign a theme based on keyword matching.
    Returns the theme name if a keyword matches, otherwise "Other".
    """
    lowered = text.lower()
    for theme, data in THEMES.items():
        for kw in data.get("keywords", []):
            if kw.lower() in lowered:
                return theme
    return "Other"

# LLM-based classification
import os
import json
from typing import List, Dict

try:
    from openai import OpenAI
    _openai_client = OpenAI()
except Exception:
    _openai_client = None


def get_allowed_themes() -> List[str]:
    return list(THEMES.keys())


def _build_classification_prompt(batch: List[Dict]) -> str:
    allowed = get_allowed_themes()
    lines = [
        "You are tagging reviews into at most 5 fixed themes.",
        "Allowed themes:",
    ]
    for i, t in enumerate(allowed, start=1):
        desc = THEMES.get(t, {}).get("description", "")
        lines.append(f"{i}. {t} – {desc}")
    lines.append("For each review, output JSON with: review_id, chosen_theme (exactly one from the list), short_reason (1 sentence, no PII).")
    lines.append("Reviews:")
    lines.append(json.dumps([{ "review_id": r["review_id"], "title": r.get("title", ""), "text": r.get("text", "") } for r in batch], ensure_ascii=False))
    lines.append("Return only a JSON array of objects.")
    return "\n".join(lines)


def _valid_theme(theme: str) -> bool:
    return theme in THEMES


def _reprompt_single(review: Dict) -> str:
    if _openai_client is None or not os.getenv("OPENAI_API_KEY"):
        return assign_theme(review.get("text", ""))
    allowed = ", ".join(get_allowed_themes())
    prompt = (
        "Choose the single best theme from this list: " + allowed + "\n" +
        "Return just the theme name.\n" +
        json.dumps({ "review_id": review.get("review_id"), "text": review.get("text", "") }, ensure_ascii=False)
    )
    try:
        resp = _openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[{ "role": "user", "content": prompt }],
            temperature=0
        )
        theme = resp.choices[0].message.content.strip()
        return theme
    except Exception:
        return assign_theme(review.get("text", ""))


def classify_reviews_llm(batch: List[Dict]) -> List[Dict]:
    """Classify a batch of reviews using LLM. Returns list of {review_id, chosen_theme, short_reason}."""
    # Fallback to keyword heuristic if no API key
    if _openai_client is None or not os.getenv("OPENAI_API_KEY"):
        out = []
        for r in batch:
            theme = assign_theme(r.get("text", ""))
            out.append({
                "review_id": r.get("review_id"),
                "chosen_theme": theme,
                "short_reason": "Assigned by keyword heuristic."
            })
        return out
    prompt = _build_classification_prompt(batch)
    try:
        resp = _openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[{ "role": "user", "content": prompt }],
            temperature=0
        )
        content = resp.choices[0].message.content
        data = json.loads(content)
    except Exception:
        # Fallback to heuristic
        data = []
        for r in batch:
            theme = assign_theme(r.get("text", ""))
            data.append({
                "review_id": r.get("review_id"),
                "chosen_theme": theme,
                "short_reason": "Assigned by keyword heuristic (LLM error)."
            })
    # Guardrails: ensure valid themes; re-prompt or fallback
    fixed = []
    for item in data:
        rid = item.get("review_id")
        theme = item.get("chosen_theme") or ""
        reason = item.get("short_reason") or ""
        if not _valid_theme(theme):
            # Try re-prompt single
            # Note: Keep to 5 fixed themes; if still invalid, fallback to Onboarding
            candidate = _reprompt_single(next((r for r in batch if r.get("review_id") == rid), {"text": ""}))
            theme = candidate if _valid_theme(candidate) else "Onboarding"
            reason = reason or "Adjusted to allowed theme after validation."
        fixed.append({ "review_id": rid, "chosen_theme": theme, "short_reason": reason })
    return fixed


def classify_week_reviews_llm(reviews: List[Dict]) -> Dict[str, Dict]:
    """Classify all reviews in a week. Returns map: review_id -> {theme, reason}."""
    results: Dict[str, Dict] = {}
    # batch in chunks of up to 10
    batch_size = 10
    current = []
    for r in reviews:
        current.append({ "review_id": r.get("review_id"), "title": r.get("title", ""), "text": r.get("text", "") })
        if len(current) >= batch_size:
            for item in classify_reviews_llm(current):
                results[item["review_id"]] = { "theme": item["chosen_theme"], "reason": item["short_reason"] }
            current = []
    if current:
        for item in classify_reviews_llm(current):
            results[item["review_id"]] = { "theme": item["chosen_theme"], "reason": item["short_reason"] }
    return results
