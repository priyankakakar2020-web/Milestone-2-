"""
Layer 3: Content Generation
- Quote Extraction (per theme, with source references)
- Theme Summarization (per theme, not per chunk)
- Action Idea Generator (chain-of-thought prompting)
- Pulse Document Assembler (template-based, 250-word limit)
"""

import os
import json
import re
from typing import List, Dict, Tuple
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    _gemini_api = os.getenv("GEMINI_API_KEY")
    if _gemini_api:
        genai.configure(api_key=_gemini_api)
    LLM_AVAILABLE = bool(_gemini_api)
except Exception:
    LLM_AVAILABLE = False


class QuoteExtractor:
    """Extract representative quotes per theme with source references."""
    
    def __init__(self, quotes_per_theme: int = 3, max_quote_length: int = 150):
        """
        Initialize quote extractor.
        
        Args:
            quotes_per_theme: Number of quotes to extract per theme
            max_quote_length: Maximum characters per quote
        """
        self.quotes_per_theme = quotes_per_theme
        self.max_quote_length = max_quote_length
    
    def extract(self, theme_name: str, reviews: List[Dict]) -> List[Dict]:
        """
        Extract top quotes for a theme.
        
        Args:
            theme_name: Theme name
            reviews: Reviews belonging to this theme (with 'text', 'theme_confidence', 'review_id')
            
        Returns:
            List of quote dicts with 'text', 'confidence', 'source_id'
        """
        if not reviews:
            return []
        
        # Sort by theme confidence (most representative first)
        sorted_reviews = sorted(
            reviews, 
            key=lambda r: r.get('theme_confidence', 0),
            reverse=True
        )
        
        quotes = []
        for review in sorted_reviews[:self.quotes_per_theme * 2]:  # Get extra for filtering
            text = review.get('text', '').strip()
            if not text or len(text) < 50:  # Skip very short reviews
                continue
            
            # Truncate if needed
            if len(text) > self.max_quote_length:
                text = text[:self.max_quote_length].rsplit(' ', 1)[0] + '...'
            
            # Anonymize any PII
            text = self._anonymize_quote(text)
            
            quotes.append({
                'text': text,
                'confidence': review.get('theme_confidence', 0),
                'source_id': review.get('review_id', 'unknown'),
                'theme': theme_name
            })
            
            if len(quotes) >= self.quotes_per_theme:
                break
        
        return quotes
    
    def _anonymize_quote(self, text: str) -> str:
        """Remove PII from quotes."""
        # Remove emails
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[email]', text)
        # Remove phone numbers
        text = re.sub(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[phone]', text)
        # Remove long digit sequences (account IDs)
        text = re.sub(r'\b\d{10,}\b', '[ID]', text)
        return text


class ThemeSummarizer:
    """Generate concise summaries per theme using LLM."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize theme summarizer.
        
        Args:
            model_name: Gemini model name
        """
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    def summarize(self, theme_name: str, theme_description: str, reviews: List[Dict]) -> str:
        """
        Summarize a theme based on all its reviews.
        
        Args:
            theme_name: Theme name
            theme_description: Theme description from Layer 2
            reviews: All reviews in this theme
            
        Returns:
            1-2 sentence summary with sentiment + key insight
        """
        if not LLM_AVAILABLE:
            return self._fallback_summary(theme_name, reviews)
        
        # Sample reviews (max 20 for context window)
        sample_reviews = self._sample_reviews(reviews, max_count=20)
        
        prompt = self._build_summary_prompt(theme_name, theme_description, sample_reviews, len(reviews))
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            summary = (response.text or "").strip()
            
            # Ensure concise (1-2 sentences)
            sentences = summary.split('. ')
            if len(sentences) > 2:
                summary = '. '.join(sentences[:2]) + '.'
            
            return summary
            
        except Exception as e:
            logger.error(f"Theme summarization failed: {e}")
            return self._fallback_summary(theme_name, reviews)
    
    def _sample_reviews(self, reviews: List[Dict], max_count: int) -> List[str]:
        """Sample representative reviews."""
        # Sort by confidence, take top reviews
        sorted_reviews = sorted(
            reviews,
            key=lambda r: r.get('theme_confidence', 0),
            reverse=True
        )
        
        return [r.get('text', '')[:300] for r in sorted_reviews[:max_count]]
    
    def _build_summary_prompt(self, theme_name: str, description: str, 
                             sample_reviews: List[str], total_count: int) -> str:
        """Build LLM prompt for theme summarization."""
        reviews_text = "\n".join([f"- {r}" for r in sample_reviews])
        
        prompt = f"""Summarize this review theme in 1-2 sentences.

Theme: {theme_name}
Description: {description}
Total Reviews: {total_count}

Sample Reviews:
{reviews_text}

Requirements:
- 1-2 sentences maximum
- Include overall sentiment (positive/negative/mixed)
- Highlight key insight or pain point
- Be specific and actionable
- No marketing language

Example: "Users express frustration with KYC verification delays, citing unclear rejection reasons and slow document processing times (avg 5+ days)."

Summary:"""
        return prompt
    
    def _fallback_summary(self, theme_name: str, reviews: List[Dict]) -> str:
        """Fallback summary when LLM unavailable."""
        count = len(reviews)
        avg_rating = sum(r.get('rating', 3) for r in reviews) / count if count > 0 else 3
        
        sentiment = "positive" if avg_rating >= 4 else "negative" if avg_rating < 3 else "mixed"
        
        return f"{count} users share {sentiment} feedback about {theme_name.lower()}, indicating this is a notable concern."


class ActionIdeaGenerator:
    """Generate actionable ideas using chain-of-thought prompting."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize action idea generator.
        
        Args:
            model_name: Gemini model name
        """
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    def generate(self, themes: List[Dict], quotes: List[Dict]) -> List[str]:
        """
        Generate 3 specific action ideas using chain-of-thought.
        
        Args:
            themes: List of theme dicts with 'theme_name', 'summary', 'size'
            quotes: List of extracted quotes
            
        Returns:
            List of 3 action ideas (1 sentence each)
        """
        if not LLM_AVAILABLE:
            return self._fallback_actions(themes)
        
        prompt = self._build_cot_prompt(themes, quotes)
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            # Parse actions from response
            actions = self._parse_actions(response.text or "")
            
            # Ensure exactly 3 actions
            if len(actions) < 3:
                actions.extend(self._fallback_actions(themes)[:3 - len(actions)])
            
            return actions[:3]
            
        except Exception as e:
            logger.error(f"Action generation failed: {e}")
            return self._fallback_actions(themes)
    
    def _build_cot_prompt(self, themes: List[Dict], quotes: List[Dict]) -> str:
        """Build chain-of-thought prompt for action generation."""
        themes_text = "\n".join([
            f"- {t['theme_name']} ({t['size']} reviews): {t.get('summary', '')}"
            for t in themes[:3]  # Top 3 themes
        ])
        
        quotes_text = "\n".join([
            f"- \"{q['text']}\" (on {q['theme']})"
            for q in quotes[:5]  # Sample quotes
        ])
        
        prompt = f"""You are a product manager analyzing user feedback to generate actionable improvements.

Top Themes:
{themes_text}

Key Quotes:
{quotes_text}

Use chain-of-thought reasoning to generate 3 specific action ideas:

Step 1: Identify the biggest pain points
<Think about which themes have the most reviews and strongest negative sentiment>

Step 2: Consider root causes
<Why are users experiencing these issues? What's the underlying problem?>

Step 3: Propose targeted solutions
<What specific changes would address the root causes?>

Output exactly 3 actions in this format:
ACTION 1: [Specific, actionable idea in 1 sentence]
ACTION 2: [Specific, actionable idea in 1 sentence]
ACTION 3: [Specific, actionable idea in 1 sentence]

Requirements:
- Be specific (not "improve UX" but "add progress indicators to KYC upload flow")
- Link to a theme
- Be implementable by product/engineering teams
- Prioritize based on impact (review count + severity)
"""
        return prompt
    
    def _parse_actions(self, response: str) -> List[str]:
        """Parse actions from LLM response."""
        actions = []
        
        # Try structured format first
        for match in re.finditer(r'ACTION \d+:\s*(.+?)(?=\n|ACTION \d+:|$)', response, re.DOTALL):
            action = match.group(1).strip()
            if action:
                actions.append(action)
        
        # Fallback: split by newlines and filter
        if not actions:
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            actions = [line for line in lines if len(line) > 20 and not line.startswith('Step')][:3]
        
        return actions
    
    def _fallback_actions(self, themes: List[Dict]) -> List[str]:
        """Fallback actions when LLM unavailable."""
        actions = []
        for theme in themes[:3]:
            name = theme['theme_name']
            actions.append(f"Investigate and address issues in {name} based on user feedback patterns.")
        return actions


class PulseDocumentAssembler:
    """Assemble final pulse document with 250-word limit."""
    
    MAX_WORDS = 250
    
    def __init__(self, product_name: str, week_start: str, week_end: str):
        """
        Initialize assembler.
        
        Args:
            product_name: Product name (e.g., "Groww")
            week_start: Week start date (YYYY-MM-DD)
            week_end: Week end date (YYYY-MM-DD)
        """
        self.product_name = product_name
        self.week_start = week_start
        self.week_end = week_end
    
    def assemble(self, themes: List[Dict], quotes: List[Dict], actions: List[str]) -> Dict:
        """
        Assemble final pulse document.
        
        Args:
            themes: Top themes with summaries
            quotes: Extracted quotes
            actions: Generated action ideas
            
        Returns:
            Pulse document dict with title, overview, themes, quotes, actions
        """
        logger.info("Assembling pulse document...")
        
        # Generate title
        title = self._generate_title()
        
        # Generate overview (max 60 words)
        overview = self._generate_overview(themes)
        
        # Select top 3 themes
        top_themes = themes[:3]
        
        # Select 3 quotes (1 per theme ideally)
        selected_quotes = self._select_quotes(quotes, top_themes)
        
        # Build document
        document = {
            'title': title,
            'overview': overview,
            'themes': [
                {
                    'name': t['theme_name'],
                    'summary': t.get('summary', ''),
                    'size': t['size']
                }
                for t in top_themes
            ],
            'quotes': [q['text'] for q in selected_quotes],
            'actions': actions[:3],
            'metadata': {
                'product': self.product_name,
                'week_start': self.week_start,
                'week_end': self.week_end,
                'total_reviews': sum(t['size'] for t in themes),
                'word_count': 0  # Will be calculated
            }
        }
        
        # Check word count and compress if needed
        document = self._enforce_word_limit(document)
        
        return document
    
    def _generate_title(self) -> str:
        """Generate pulse document title."""
        return f"Weekly Product Pulse – {self.product_name}"
    
    def _generate_overview(self, themes: List[Dict]) -> str:
        """Generate overview paragraph (max 60 words)."""
        total_reviews = sum(t['size'] for t in themes)
        top_theme = themes[0]['theme_name'] if themes else "user feedback"
        
        overview = (
            f"This week's {total_reviews} user reviews highlight key areas for improvement. "
            f"Top concern: {top_theme}. "
            f"Analysis covers {len(themes)} themes with actionable recommendations."
        )
        
        # Ensure under 60 words
        words = overview.split()
        if len(words) > 60:
            overview = ' '.join(words[:60]) + '...'
        
        return overview
    
    def _select_quotes(self, all_quotes: List[Dict], top_themes: List[Dict]) -> List[Dict]:
        """Select 3 diverse quotes (ideally 1 per theme)."""
        selected = []
        theme_names = [t['theme_name'] for t in top_themes]
        
        # Try to get 1 quote per top theme
        for theme_name in theme_names:
            theme_quotes = [q for q in all_quotes if q['theme'] == theme_name]
            if theme_quotes and len(selected) < 3:
                selected.append(theme_quotes[0])
        
        # Fill remaining slots
        for quote in all_quotes:
            if quote not in selected and len(selected) < 3:
                selected.append(quote)
        
        return selected[:3]
    
    def _count_words(self, document: Dict) -> int:
        """Count total words in pulse document."""
        text_parts = [
            document['title'],
            document['overview']
        ]
        
        for theme in document['themes']:
            text_parts.append(f"{theme['name']}: {theme['summary']}")
        
        text_parts.extend(document['quotes'])
        text_parts.extend(document['actions'])
        
        full_text = ' '.join(text_parts)
        return len(full_text.split())
    
    def _enforce_word_limit(self, document: Dict) -> Dict:
        """Compress document if over 250 words."""
        word_count = self._count_words(document)
        document['metadata']['word_count'] = word_count
        
        if word_count <= self.MAX_WORDS:
            logger.info(f"Document word count: {word_count}/{self.MAX_WORDS} ✓")
            return document
        
        logger.warning(f"Document exceeds limit: {word_count}/{self.MAX_WORDS}. Compressing...")
        
        # Compression strategy: shorten summaries
        for theme in document['themes']:
            summary = theme['summary']
            # Keep only first sentence
            theme['summary'] = summary.split('. ')[0] + '.' if '. ' in summary else summary
        
        # Recount
        new_count = self._count_words(document)
        document['metadata']['word_count'] = new_count
        
        logger.info(f"Compressed to {new_count} words")
        
        return document


class Layer3Pipeline:
    """Orchestrates Layer 3: Content Generation."""
    
    def __init__(self, product_name: str, week_start: str, week_end: str):
        """
        Initialize Layer 3 pipeline.
        
        Args:
            product_name: Product name
            week_start: Week start date
            week_end: Week end date
        """
        self.quote_extractor = QuoteExtractor(quotes_per_theme=3)
        self.summarizer = ThemeSummarizer()
        self.action_generator = ActionIdeaGenerator()
        self.assembler = PulseDocumentAssembler(product_name, week_start, week_end)
    
    def process(self, enriched_reviews: List[Dict], theme_metadata: Dict) -> Dict:
        """
        Process enriched reviews to generate pulse document.
        
        Args:
            enriched_reviews: Reviews with theme assignments (from Layer 2)
            theme_metadata: Theme metadata from Layer 2
            
        Returns:
            Final pulse document dict
        """
        logger.info("="*60)
        logger.info("LAYER 3: CONTENT GENERATION")
        logger.info("="*60)
        
        themes = theme_metadata.get('themes', [])
        
        # Step 1: Extract quotes per theme
        logger.info("Step 1: Extracting quotes per theme...")
        all_quotes = []
        for theme in themes:
            theme_name = theme['theme_name']
            theme_reviews = [r for r in enriched_reviews if r.get('theme') == theme_name]
            
            quotes = self.quote_extractor.extract(theme_name, theme_reviews)
            all_quotes.extend(quotes)
            
            logger.info(f"  {theme_name}: {len(quotes)} quotes extracted")
        
        # Step 2: Summarize each theme
        logger.info("Step 2: Generating theme summaries...")
        enriched_themes = []
        for theme in themes:
            theme_name = theme['theme_name']
            theme_desc = theme.get('description', '')
            theme_reviews = [r for r in enriched_reviews if r.get('theme') == theme_name]
            
            summary = self.summarizer.summarize(theme_name, theme_desc, theme_reviews)
            
            enriched_theme = theme.copy()
            enriched_theme['summary'] = summary
            enriched_themes.append(enriched_theme)
            
            logger.info(f"  {theme_name}: {summary[:80]}...")
        
        # Step 3: Generate action ideas
        logger.info("Step 3: Generating action ideas (chain-of-thought)...")
        actions = self.action_generator.generate(enriched_themes, all_quotes)
        for i, action in enumerate(actions, 1):
            logger.info(f"  Action {i}: {action[:80]}...")
        
        # Step 4: Assemble pulse document
        logger.info("Step 4: Assembling pulse document...")
        pulse_document = self.assembler.assemble(enriched_themes, all_quotes, actions)
        
        logger.info("="*60)
        logger.info("LAYER 3 COMPLETE")
        logger.info(f"Final document: {pulse_document['metadata']['word_count']} words")
        logger.info("="*60)
        
        return pulse_document
