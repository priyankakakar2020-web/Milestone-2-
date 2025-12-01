import re
import html

def clean_text(text):
    """
    Cleans the review text by stripping HTML, removing emojis,
    normalizing whitespace, and removing PII.
    """
    if not text:
        return ""

    # 1. Strip HTML tags
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)

    # 2. Remove emojis (simple range-based approach, can be expanded)
    # This regex covers many common emoji ranges
    text = re.sub(r'[^\w\s,.\'\"?!@#%&()\-:;]', '', text)

    # 3. Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # 4. Remove PII
    # Email
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL_REMOVED]', text)
    # Phone numbers (simple patterns, can be more strict)
    # Matches patterns like +91-1234567890, 1234567890, 123-456-7890
    text = re.sub(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[PHONE_REMOVED]', text)
    
    return text
