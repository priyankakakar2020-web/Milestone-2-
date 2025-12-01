import os
import json
import re
import csv
from datetime import datetime
from typing import Dict

try:
    from openai import OpenAI
    _openai_client = OpenAI()
except Exception:
    _openai_client = None


def _llm_available() -> bool:
    return _openai_client is not None and bool(os.getenv("OPENAI_API_KEY"))


def generate_subject(product_name: str, week_start: str, week_end: str) -> str:
    return f"Weekly Product Pulse – {product_name} ({week_start}–{week_end})"


def draft_weekly_email(note_json: Dict, week_start: str, week_end: str, product_name: str) -> str:
    """Create the weekly email body text from the final weekly note JSON and metadata."""
    if _llm_available():
        prompt = (
            "You are drafting an internal weekly email sharing the latest product pulse.\n\n" +
            "Audience:\n" +
            "- Product & Growth: want to see what to fix or double down on.\n" +
            "- Support: wants to know what to acknowledge and celebrate.\n" +
            "- Leadership: wants a quick pulse, key risks, and wins.\n\n" +
            "Input (weekly note JSON):\n" +
            json.dumps(note_json, ensure_ascii=False) + "\n\n" +
            "Tasks:\n" +
            "- Write an email body only (no subject line).\n" +
            "- Structure:\n" +
            "  1) 2–3 line intro explaining the time window and the product/program.\n" +
            "  2) Embed the weekly pulse note in a clean, scannable format:\n" +
            "     - Title\n" +
            "     - Overview\n" +
            "     - Bulleted Top 3 themes\n" +
            "     - Bulleted 3 quotes\n" +
            "     - Bulleted 3 action ideas\n" +
            "  3) End with a short closing line and invite replies.\n\n" +
            "Constraints:\n" +
            "- Professional, neutral tone with a hint of warmth.\n" +
            "- No names, emails, or IDs. If present in quotes, anonymize generically (e.g., \"a learner\", \"one participant\").\n" +
            "- Keep the whole email under 350 words.\n\n" +
            "Output plain text only (no HTML).\n"
        )
        try:
            resp = _openai_client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            body = resp.choices[0].message.content
            return body
        except Exception:
            pass
    # Fallback plain-text formatter
    title = note_json.get("title", "Weekly Product Pulse")
    overview = note_json.get("overview", "")
    themes = note_json.get("themes", [])
    quotes = note_json.get("quotes", [])
    actions = note_json.get("actions", [])
    lines = []
    lines.append(f"Product: {product_name}\nWindow: {week_start}–{week_end}")
    lines.append("")
    lines.append(title)
    if overview:
        lines.append(overview)
    if themes:
        lines.append("Top 3 themes:")
        for t in themes[:3]:
            lines.append(f"- {t.get('name', '')}: {t.get('summary', '')}")
    if quotes:
        lines.append("Quotes:")
        for q in quotes[:3]:
            lines.append(f"- {q}")
    if actions:
        lines.append("Actions:")
        for a in actions[:3]:
            lines.append(f"- {a}")
    lines.append("")
    lines.append("Thanks for reading—happy to discuss or take inputs.")
    return "\n".join(lines)


def scrub_pii(text: str) -> str:
    """Remove emails and simple phone patterns from text."""
    if not text:
        return text
    # Remove email addresses
    text = re.sub(r"[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}", "[REDACTED]", text)
    # Remove phone numbers (including +91 and common formats)
    text = re.sub(r"(?:\+?\d{1,3}[-\.\s]?)?\(?\d{3}\)?[-\.\s]?\d{3}[-\.\s]?\d{4}", "[REDACTED]", text)
    # Generic 10+ digit sequences
    text = re.sub(r"\b\d{10,}\b", "[REDACTED]", text)
    return text


def send_email(subject: str, body_text: str, to_addr: str, from_addr: str = None,
               smtp_host: str = None, smtp_port: int = None, smtp_user: str = None, smtp_pass: str = None) -> (str, str):
    """Send email via SMTP. Returns (status, error_message)."""
    import smtplib
    from email.message import EmailMessage
    smtp_host = smtp_host or os.getenv("SMTP_HOST")
    smtp_port = int(smtp_port or os.getenv("SMTP_PORT", "587"))
    smtp_user = smtp_user or os.getenv("SMTP_USER")
    smtp_pass = smtp_pass or os.getenv("SMTP_PASS")
    from_addr = from_addr or os.getenv("EMAIL_FROM")
    if not (smtp_host and smtp_port and from_addr and to_addr):
        return ("ERROR", "Missing SMTP configuration or addresses")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body_text)
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            try:
                server.starttls()
            except Exception:
                pass
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return ("SENT", "")
    except Exception as e:
        return ("ERROR", str(e))


def log_email_send(week_start: str, week_end: str, subject: str, recipient: str, status: str, error_message: str = ""):
    """Append a row to email_log.csv with send status."""
    log_path = os.path.join(os.getcwd(), "email_log.csv")
    exists = os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "week_start", "week_end", "subject", "recipient", "status", "error_message"])
        writer.writerow([datetime.now().isoformat(), week_start, week_end, subject, recipient, status, error_message])
