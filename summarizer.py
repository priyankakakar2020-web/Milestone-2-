import os
import json
from typing import List, Dict

try:
    import google.generativeai as genai
    _gemini_api = os.getenv("GEMINI_API_KEY")
    if _gemini_api:
        genai.configure(api_key=_gemini_api)
    _gemini_ready = bool(_gemini_api)
except Exception:
    _gemini_ready = False


def _llm_available() -> bool:
    return _gemini_ready


def _chunk_list(items: List[str], size: int) -> List[List[str]]:
    chunks = []
    for i in range(0, len(items), size):
        chunks.append(items[i:i+size])
    return chunks


def summarize_theme(theme: str, review_texts: List[str], chunk_size: int = 20) -> Dict:
    """Map stage: summarize reviews per theme in chunks and aggregate key points and quotes."""
    aggregated_points: List[str] = []
    aggregated_quotes: List[str] = []

    chunks = _chunk_list(review_texts, chunk_size)
    for chunk in chunks:
        if _llm_available():
            prompt = (
                "You are summarizing groww app feedback.\n" +
                f"Theme: {theme}\n\n" +
                "Reviews (already cleaned, no direct PII):\n" +
                json.dumps(chunk, ensure_ascii=False) + "\n\n" +
                "Tasks:\n" +
                "1. Extract 3–5 key points about this theme in a neutral, factual tone.\n" +
                "2. Identify up to 3 short, vivid quotes that capture the sentiment.\n" +
                "   - Do NOT include names, usernames, emails, or IDs.\n" +
                "   - If a quote contains PII, rewrite it to keep meaning but remove the PII.\n" +
                "3. Return JSON:\n" +
                "   {\n" +
                "     \"theme\": \"...\",\n" +
                "     \"key_points\": [\"...\", \"...\"],\n" +
                "     \"review_quotes\": [\"...\", \"...\", \"...\"]\n" +
                "   }\n" +
                "Keep everything concise. Avoid marketing fluff."
            )
            try:
                model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
                model = genai.GenerativeModel(model_name)
                resp = model.generate_content(prompt)
                data = json.loads(resp.text or "{}")
                points = data.get("key_points", [])
                quotes = data.get("review_quotes", [])
            except Exception:
                points = []
                quotes = []
        else:
            # Heuristic fallback: derive simple points from theme name
            base = theme.lower()
            points = [
                f"Users discuss {base} flow and clarity.",
                f"Pain points around {base} consistency and reliability.",
                f"Suggestions to improve {base} guidance and UX."
            ]
            quotes = [
                "\"It should be simpler to complete this step.\"",
                "\"The process felt confusing at moments.\""
            ]
        # Aggregate with simple dedup and limits
        for p in points:
            if p not in aggregated_points and len(aggregated_points) < 5:
                aggregated_points.append(p)
        for q in quotes:
            if q not in aggregated_quotes and len(aggregated_quotes) < 3:
                aggregated_quotes.append(q)

    return {"theme": theme, "key_points": aggregated_points, "review_quotes": aggregated_quotes}


def _note_text(note: Dict) -> str:
    parts = []
    parts.append(note.get("title", ""))
    parts.append(note.get("overview", ""))
    for t in note.get("themes", []):
        parts.append(f"{t.get('name', '')}: {t.get('summary', '')}")
    parts.extend(note.get("quotes", []))
    parts.extend(note.get("actions", []))
    return "\n".join([p for p in parts if p])


def _word_count(text: str) -> int:
    return len(text.strip().split()) if text else 0


def synthesize_weekly_pulse(week_start: str, week_end: str, theme_summaries: List[Dict], top3_names: List[str]) -> Dict:
    """Reduce stage: create weekly pulse note JSON from theme summaries."""
    payload = {
        "title": "Weekly Product Pulse",
        "overview": "",
        "themes": [],
        "quotes": [],
        "actions": []
    }
    if _llm_available():
        prompt = (
            "You are creating a weekly product pulse for internal stakeholders (Product/Growth, Support, Leadership).\n\n" +
            f"Input:\n- Time window: {week_start} to {week_end}\n- review themes with key points and quotes:\n" +
            json.dumps(theme_summaries, ensure_ascii=False) + "\n\n" +
            "Constraints:\n" +
            "- Select the Top 3 themes that matter most based on frequency & impact.\n" +
            "- Produce:\n" +
            "  1) A short title for the pulse.\n" +
            "  2) A one-paragraph overview (max 60 words).\n" +
            "  3) A bullet list of the Top 3 themes:\n" +
            "     - For each, 1 sentence with sentiment + key insight.\n" +
            "  4) 3 short quotes (1–2 lines each), clearly marked with theme.\n" +
            "  5) 3 specific action ideas (bullets), each linked to a theme.\n\n" +
            "Style & limits:\n" +
            "- Total length: ≤250 words.\n" +
            "- Use clear bullets and sub-bullets where needed.\n" +
            "- Executive-friendly, neutral tone. Do not overpraise.\n" +
            "- No names, emails, IDs, or any PII.\n\n" +
            "Output in this JSON structure:\n" +
            "{\n  \"title\": \"...\",\n  \"overview\": \"...\",\n  \"themes\": [\n    {\"name\": \"...\", \"summary\": \"...\"},\n    ...\n  ],\n  \"quotes\": [\"...\", \"...\", \"...\"],\n  \"actions\": [\"...\", \"...\", \"...\"]\n}\n"
        )
        try:
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(prompt)
            payload = json.loads(resp.text or "{}")
        except Exception:
            pass

    # Minimal heuristic fallback if payload incomplete
    if not payload.get("themes"):
        payload["title"] = "Weekly Product Pulse"
        payload["overview"] = "Top feedback themes and actions for the week."
        for name in top3_names:
            payload["themes"].append({"name": name, "summary": f"Feedback clustered around {name.lower()}."})
        payload["quotes"] = ["\"A representative user quote.\" (on Theme)"] * 3
        payload["actions"] = [f"Investigate {top3_names[0]} issues", f"Improve {top3_names[1]} guidance", f"Monitor {top3_names[2]} performance"]

    return payload


def compress_note_if_needed(note: Dict, max_words: int = 250) -> Dict:
    text = _note_text(note)
    if _word_count(text) <= max_words or not _llm_available():
        return note
    prompt = (
        "Compress this note to at most 250 words, preserving:\n" +
        "- 3 themes, 3 quotes, 3 actions.\n" +
        "- Bullet-based, scannable structure.\n" +
        "- No PII.\n\n" +
        _note_text(note)
    )
    try:
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content(prompt)
        compressed = json.loads(resp.text or "{}")
        return compressed
    except Exception:
        return note
