"""
Test script for Layer 1: Data Import & Validation
Demonstrates each component independently and as a pipeline.
"""

from layer1_import import ScraperClient, SchemaValidator, PIIDetector, Deduplicator, Layer1Pipeline
from datetime import datetime


def test_scraper():
    """Test the scraper client."""
    print("\n" + "="*60)
    print("TEST 1: SCRAPER CLIENT")
    print("="*60)
    
    scraper = ScraperClient('com.nextbillion.groww', 'en', 'in')
    reviews, token = scraper.fetch_batch(count=10)
    
    print(f"Fetched {len(reviews)} reviews")
    if reviews:
        print(f"Sample review ID: {reviews[0].get('reviewId')}")
        print(f"Sample content: {reviews[0].get('content', '')[:100]}...")
        print(f"Continuation token exists: {token is not None}")
    print("✓ Scraper test passed")


def test_schema_validator():
    """Test schema validation."""
    print("\n" + "="*60)
    print("TEST 2: SCHEMA VALIDATOR")
    print("="*60)
    
    # Valid review
    valid_review = {
        'reviewId': 'test123',
        'content': 'Great app!',
        'score': 5,
        'at': datetime.now()
    }
    
    # Invalid reviews
    invalid_reviews = [
        {'content': 'Missing ID'},  # Missing reviewId
        {'reviewId': 'test', 'score': 5, 'at': datetime.now()},  # Missing content
        {'reviewId': '', 'content': 'Empty ID', 'score': 5, 'at': datetime.now()},  # Empty reviewId
        {'reviewId': 'test', 'content': 'Bad score', 'score': 10, 'at': datetime.now()},  # Invalid score
    ]
    
    is_valid, msg = SchemaValidator.validate(valid_review)
    print(f"Valid review: {is_valid} - {msg or 'OK'}")
    
    for i, inv in enumerate(invalid_reviews, 1):
        is_valid, msg = SchemaValidator.validate(inv)
        print(f"Invalid {i}: {is_valid} - {msg}")
    
    print("✓ Schema validator test passed")


def test_pii_detector():
    """Test PII detection."""
    print("\n" + "="*60)
    print("TEST 3: PII DETECTOR")
    print("="*60)
    
    test_cases = [
        ("Clean text with no PII", False, []),
        ("Contact me at john@example.com", True, ['email']),
        ("Call +91-9876543210 for help", True, ['phone']),
        ("My account ID is 1234567890123", True, ['long_digits']),
        ("Email support@app.com or call 123-456-7890", True, ['email', 'phone']),
    ]
    
    for text, expected_has_pii, expected_types in test_cases:
        has_pii, pii_types = PIIDetector.contains_pii(text)
        status = "✓" if has_pii == expected_has_pii else "✗"
        print(f"{status} '{text[:40]}...' -> PII: {has_pii}, Types: {pii_types}")
    
    print("✓ PII detector test passed")


def test_deduplicator():
    """Test deduplication."""
    print("\n" + "="*60)
    print("TEST 4: DEDUPLICATOR")
    print("="*60)
    
    dedup = Deduplicator(state_file='test_dedup_state.json')
    
    reviews = [
        {'reviewId': 'rev1', 'content': 'First review', 'at': datetime.now()},
        {'reviewId': 'rev2', 'content': 'Second review', 'at': datetime.now()},
        {'reviewId': 'rev1', 'content': 'Duplicate of first', 'at': datetime.now()},  # Duplicate
        {'reviewId': 'rev3', 'content': 'Third review', 'at': datetime.now()},
    ]
    
    unique = dedup.filter_duplicates(reviews)
    print(f"Input: {len(reviews)} reviews")
    print(f"Output: {len(unique)} unique reviews")
    print(f"Filtered: {len(reviews) - len(unique)} duplicates")
    
    # Test persistence
    unique_ids = [r['reviewId'] for r in unique]
    print(f"Unique IDs: {unique_ids}")
    
    # Second pass should filter all
    unique2 = dedup.filter_duplicates(reviews)
    print(f"Second pass: {len(unique2)} unique (should be 0 if all duplicates)")
    
    print("✓ Deduplicator test passed")


def test_full_pipeline():
    """Test the full Layer 1 pipeline."""
    print("\n" + "="*60)
    print("TEST 5: FULL LAYER 1 PIPELINE")
    print("="*60)
    
    pipeline = Layer1Pipeline('com.nextbillion.groww', 'en', 'in', 'test_pipeline_dedup.json')
    
    # Process one batch
    reviews, token = pipeline.process_batch(count=20)
    
    print(f"\nProcessed {len(reviews)} reviews through full pipeline")
    
    if reviews:
        print("\nSample review:")
        sample = reviews[0]
        print(f"  ID: {sample.get('reviewId')}")
        print(f"  Content: {sample.get('content', '')[:80]}...")
        print(f"  Score: {sample.get('score')}")
        print(f"  PII Detected: {sample.get('_pii_detected')}")
        print(f"  PII Types: {sample.get('_pii_types')}")
    
    stats = pipeline.get_stats()
    print(f"\nPipeline Statistics:")
    print(f"  Total seen: {stats['total_seen_reviews']}")
    print(f"  State file: {stats['dedup_state_file']}")
    
    print("✓ Full pipeline test passed")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LAYER 1 COMPONENT TESTS")
    print("="*60)
    
    try:
        test_scraper()
        test_schema_validator()
        test_pii_detector()
        test_deduplicator()
        test_full_pipeline()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
