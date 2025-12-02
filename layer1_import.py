"""
Layer 1: Data Import & Validation
- Scraper/API Client
- Schema Validator
- PII Detector
- Deduplication
"""

import os
import json
import hashlib
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from google_play_scraper import Sort, reviews as fetch_reviews


class ScraperClient:
    """Scraper/API Client for fetching app reviews from Google Play."""
    
    def __init__(self, app_id: str, lang: str = 'en', country: str = 'in'):
        self.app_id = app_id
        self.lang = lang
        self.country = country
    
    def fetch_batch(self, count: int = 200, continuation_token=None) -> Tuple[List[Dict], Optional[str]]:
        """Fetch a batch of reviews from Google Play."""
        try:
            result, token = fetch_reviews(
                self.app_id,
                lang=self.lang,
                country=self.country,
                sort=Sort.NEWEST,
                count=count,
                continuation_token=continuation_token
            )
            return result, token
        except Exception as e:
            print(f"Error fetching reviews: {e}")
            return [], None


class SchemaValidator:
    """Validate that reviews contain required fields."""
    
    REQUIRED_FIELDS = ['reviewId', 'content', 'score', 'at']
    OPTIONAL_FIELDS = ['userName', 'userImage', 'thumbsUpCount', 'reviewCreatedVersion', 
                       'replyContent', 'repliedAt']
    
    @staticmethod
    def validate(review: Dict) -> Tuple[bool, str]:
        """
        Validate review schema.
        Returns: (is_valid, error_message)
        """
        # Check required fields
        missing = [field for field in SchemaValidator.REQUIRED_FIELDS if field not in review]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        # Check data types
        if not isinstance(review.get('reviewId'), str) or not review['reviewId']:
            return False, "reviewId must be a non-empty string"
        
        if not isinstance(review.get('content'), str):
            return False, "content must be a string"
        
        if not isinstance(review.get('score'), (int, float)) or not (1 <= review['score'] <= 5):
            return False, "score must be between 1 and 5"
        
        if not isinstance(review.get('at'), datetime):
            return False, "at must be a datetime object"
        
        return True, ""
    
    @staticmethod
    def validate_batch(reviews: List[Dict]) -> List[Dict]:
        """Filter valid reviews from a batch."""
        valid = []
        for r in reviews:
            is_valid, error = SchemaValidator.validate(r)
            if is_valid:
                valid.append(r)
            else:
                print(f"Invalid review {r.get('reviewId', 'UNKNOWN')}: {error}")
        return valid


class PIIDetector:
    """Early PII detection and filtering."""
    
    import re
    
    # Patterns for PII detection
    EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    PHONE_PATTERN = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    LONG_DIGIT_PATTERN = re.compile(r'\b\d{10,}\b')  # Potential account/ID numbers
    
    @staticmethod
    def contains_pii(text: str) -> Tuple[bool, List[str]]:
        """
        Check if text contains PII.
        Returns: (has_pii, list_of_pii_types_found)
        """
        if not text:
            return False, []
        
        pii_types = []
        
        if PIIDetector.EMAIL_PATTERN.search(text):
            pii_types.append('email')
        
        if PIIDetector.PHONE_PATTERN.search(text):
            pii_types.append('phone')
        
        if PIIDetector.LONG_DIGIT_PATTERN.search(text):
            pii_types.append('long_digits')
        
        return len(pii_types) > 0, pii_types
    
    @staticmethod
    def flag_pii_reviews(reviews: List[Dict]) -> List[Dict]:
        """Add PII flag to reviews that contain PII."""
        for review in reviews:
            text = review.get('content', '')
            has_pii, pii_types = PIIDetector.contains_pii(text)
            review['_pii_detected'] = has_pii
            review['_pii_types'] = pii_types
        return reviews


class Deduplicator:
    """Deduplication to avoid processing same review twice."""
    
    def __init__(self, state_file: str = 'dedup_state.json'):
        self.state_file = state_file
        self.seen_ids = self._load_state()
    
    def _load_state(self) -> set:
        """Load previously seen review IDs from disk."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('seen_ids', []))
            except Exception as e:
                print(f"Error loading dedup state: {e}")
        return set()
    
    def _save_state(self):
        """Persist seen review IDs to disk."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({'seen_ids': list(self.seen_ids)}, f, indent=2)
        except Exception as e:
            print(f"Error saving dedup state: {e}")
    
    @staticmethod
    def compute_hash(review: Dict) -> str:
        """Compute content hash for duplicate detection."""
        # Use reviewId as primary key, fallback to content hash
        review_id = review.get('reviewId', '')
        if review_id:
            return review_id
        
        # Fallback: hash content + timestamp
        content = review.get('content', '')
        timestamp = review.get('at', datetime.now()).isoformat()
        combined = f"{content}|{timestamp}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    def filter_duplicates(self, reviews: List[Dict]) -> List[Dict]:
        """Remove reviews that have been seen before."""
        unique = []
        new_ids = []
        
        for review in reviews:
            rid = self.compute_hash(review)
            if rid not in self.seen_ids:
                unique.append(review)
                new_ids.append(rid)
                self.seen_ids.add(rid)
        
        if new_ids:
            self._save_state()
        
        return unique
    
    def mark_as_seen(self, reviews: List[Dict]):
        """Mark reviews as seen without filtering."""
        for review in reviews:
            rid = self.compute_hash(review)
            self.seen_ids.add(rid)
        self._save_state()


class Layer1Pipeline:
    """Orchestrates Layer 1: Data Import & Validation."""
    
    def __init__(self, app_id: str, lang: str = 'en', country: str = 'in', 
                 dedup_state_file: str = 'dedup_state.json'):
        self.scraper = ScraperClient(app_id, lang, country)
        self.validator = SchemaValidator()
        self.pii_detector = PIIDetector()
        self.deduplicator = Deduplicator(dedup_state_file)
    
    def process_batch(self, count: int = 200, continuation_token=None) -> Tuple[List[Dict], Optional[str]]:
        """
        Process a batch through Layer 1 pipeline.
        Returns: (validated_reviews, continuation_token)
        """
        # Step 1: Scraper - fetch reviews
        raw_reviews, token = self.scraper.fetch_batch(count, continuation_token)
        if not raw_reviews:
            return [], token
        
        print(f"Fetched {len(raw_reviews)} raw reviews")
        
        # Step 2: Schema Validator - ensure required fields
        valid_reviews = self.validator.validate_batch(raw_reviews)
        print(f"Valid reviews after schema validation: {len(valid_reviews)}")
        
        # Step 3: PII Detector - flag reviews with PII
        flagged_reviews = self.pii_detector.flag_pii_reviews(valid_reviews)
        pii_count = sum(1 for r in flagged_reviews if r.get('_pii_detected'))
        print(f"Reviews flagged with PII: {pii_count}")
        
        # Step 4: Deduplication - remove previously seen reviews
        unique_reviews = self.deduplicator.filter_duplicates(flagged_reviews)
        print(f"Unique reviews after deduplication: {len(unique_reviews)}")
        
        return unique_reviews, token
    
    def get_stats(self) -> Dict:
        """Get pipeline statistics."""
        return {
            'total_seen_reviews': len(self.deduplicator.seen_ids),
            'dedup_state_file': self.deduplicator.state_file
        }
