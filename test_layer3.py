"""
Test script for Layer 3: Content Generation
Demonstrates quote extraction, theme summarization, action generation, and assembly.
"""

from layer3_content import (
    QuoteExtractor,
    ThemeSummarizer,
    ActionIdeaGenerator,
    PulseDocumentAssembler,
    Layer3Pipeline
)


def test_quote_extraction():
    """Test quote extraction with source references."""
    print("\n" + "="*60)
    print("TEST 1: QUOTE EXTRACTION")
    print("="*60)
    
    sample_reviews = [
        {
            'review_id': 'r1',
            'text': 'KYC verification took 5 days and failed twice without clear explanation. Very frustrating process.',
            'theme': 'KYC Delays',
            'theme_confidence': 0.95
        },
        {
            'review_id': 'r2',
            'text': 'Identity document upload keeps failing. No guidance on acceptable formats.',
            'theme': 'KYC Delays',
            'theme_confidence': 0.88
        },
        {
            'review_id': 'r3',
            'text': 'Pan and Aadhaar verification is very slow compared to other apps.',
            'theme': 'KYC Delays',
            'theme_confidence': 0.82
        }
    ]
    
    extractor = QuoteExtractor(quotes_per_theme=2)
    quotes = extractor.extract('KYC Delays', sample_reviews)
    
    print(f"Extracted {len(quotes)} quotes:")
    for i, quote in enumerate(quotes, 1):
        print(f"\n  Quote {i}:")
        print(f"    Text: {quote['text'][:100]}...")
        print(f"    Confidence: {quote['confidence']:.2f}")
        print(f"    Source: {quote['source_id']}")
        print(f"    Theme: {quote['theme']}")
    
    print("\n✓ Quote extraction test passed")


def test_theme_summarization():
    """Test LLM-based theme summarization."""
    print("\n" + "="*60)
    print("TEST 2: THEME SUMMARIZATION")
    print("="*60)
    
    theme_name = "KYC Verification Delays"
    theme_description = "Users experiencing slow identity verification"
    
    sample_reviews = [
        {
            'text': 'KYC verification took 5 days and failed twice without clear explanation.',
            'theme_confidence': 0.95,
            'rating': 2
        },
        {
            'text': 'Identity document upload keeps failing. No guidance on acceptable formats.',
            'theme_confidence': 0.88,
            'rating': 1
        },
        {
            'text': 'Pan and Aadhaar verification is very slow compared to other apps.',
            'theme_confidence': 0.82,
            'rating': 2
        }
    ]
    
    summarizer = ThemeSummarizer()
    summary = summarizer.summarize(theme_name, theme_description, sample_reviews)
    
    print(f"Theme: {theme_name}")
    print(f"Summary: {summary}")
    print(f"Length: {len(summary.split())} words")
    
    print("\n✓ Theme summarization test passed")


def test_action_generation():
    """Test chain-of-thought action generation."""
    print("\n" + "="*60)
    print("TEST 3: ACTION IDEA GENERATION (CHAIN-OF-THOUGHT)")
    print("="*60)
    
    themes = [
        {
            'theme_name': 'KYC Verification Delays',
            'summary': 'Users frustrated with slow verification process taking 5+ days.',
            'size': 45
        },
        {
            'theme_name': 'Payment Failures',
            'summary': 'Frequent payment deductions without confirmation or refund.',
            'size': 38
        },
        {
            'theme_name': 'App Performance',
            'summary': 'Mixed feedback on app speed and reliability during peak hours.',
            'size': 32
        }
    ]
    
    quotes = [
        {'text': 'KYC took 5 days and failed twice', 'theme': 'KYC Verification Delays'},
        {'text': 'Payment deducted but not reflected', 'theme': 'Payment Failures'},
        {'text': 'App crashes during market hours', 'theme': 'App Performance'}
    ]
    
    generator = ActionIdeaGenerator()
    actions = generator.generate(themes, quotes)
    
    print(f"Generated {len(actions)} action ideas:\n")
    for i, action in enumerate(actions, 1):
        print(f"  {i}. {action}")
    
    assert len(actions) == 3, "Should generate exactly 3 actions"
    
    print("\n✓ Action generation test passed")


def test_pulse_assembly():
    """Test pulse document assembly with word limit."""
    print("\n" + "="*60)
    print("TEST 4: PULSE DOCUMENT ASSEMBLY")
    print("="*60)
    
    themes = [
        {
            'theme_name': 'KYC Verification Delays',
            'description': 'Slow verification process',
            'summary': 'Users frustrated with slow KYC verification taking 5+ days with unclear rejection reasons.',
            'size': 45
        },
        {
            'theme_name': 'Payment Failures',
            'description': 'Payment issues',
            'summary': 'Frequent payment deductions without confirmation causing user distrust.',
            'size': 38
        },
        {
            'theme_name': 'App Performance',
            'description': 'Performance concerns',
            'summary': 'Mixed feedback on app reliability during peak trading hours.',
            'size': 32
        }
    ]
    
    quotes = [
        {'text': 'KYC verification took 5 days and failed twice without explanation.', 'theme': 'KYC Verification Delays'},
        {'text': 'Payment deducted but order not confirmed. No refund received.', 'theme': 'Payment Failures'},
        {'text': 'App crashes frequently during market hours. Very frustrating.', 'theme': 'App Performance'}
    ]
    
    actions = [
        'Add real-time status updates and progress indicators to KYC verification flow',
        'Implement automatic refund system for failed payment transactions within 24 hours',
        'Increase server capacity and add performance monitoring during peak hours'
    ]
    
    assembler = PulseDocumentAssembler(
        product_name='Groww',
        week_start='2025-11-25',
        week_end='2025-12-01'
    )
    
    document = assembler.assemble(themes, quotes, actions)
    
    print(f"\nAssembled Pulse Document:")
    print(f"\nTitle: {document['title']}")
    print(f"\nOverview: {document['overview']}")
    
    print(f"\nThemes ({len(document['themes'])}):")
    for theme in document['themes']:
        print(f"  • {theme['name']} ({theme['size']} reviews)")
        print(f"    {theme['summary']}")
    
    print(f"\nQuotes ({len(document['quotes'])}):")
    for i, quote in enumerate(document['quotes'], 1):
        print(f"  {i}. \"{quote}\"")
    
    print(f"\nActions ({len(document['actions'])}):")
    for i, action in enumerate(document['actions'], 1):
        print(f"  {i}. {action}")
    
    print(f"\nMetadata:")
    print(f"  Product: {document['metadata']['product']}")
    print(f"  Period: {document['metadata']['week_start']} to {document['metadata']['week_end']}")
    print(f"  Total Reviews: {document['metadata']['total_reviews']}")
    print(f"  Word Count: {document['metadata']['word_count']}/250")
    
    assert document['metadata']['word_count'] <= 250, "Document exceeds 250-word limit!"
    
    print("\n✓ Pulse assembly test passed")


def test_full_pipeline():
    """Test full Layer 3 pipeline."""
    print("\n" + "="*60)
    print("TEST 5: FULL LAYER 3 PIPELINE")
    print("="*60)
    
    # Mock enriched reviews from Layer 2
    enriched_reviews = [
        {
            'review_id': f'r{i}',
            'text': f'KYC verification is slow and frustrating. Takes {i} days to complete.',
            'theme': 'KYC Verification Delays',
            'theme_confidence': 0.9 - (i * 0.01),
            'rating': 2
        }
        for i in range(20)
    ] + [
        {
            'review_id': f'p{i}',
            'text': f'Payment failed but amount deducted. Issue number {i}.',
            'theme': 'Payment Failures',
            'theme_confidence': 0.85 - (i * 0.01),
            'rating': 1
        }
        for i in range(15)
    ]
    
    # Mock theme metadata
    theme_metadata = {
        'themes': [
            {
                'cluster_id': 0,
                'theme_name': 'KYC Verification Delays',
                'description': 'Slow identity verification process',
                'size': 20
            },
            {
                'cluster_id': 1,
                'theme_name': 'Payment Failures',
                'description': 'Payment deduction issues',
                'size': 15
            }
        ]
    }
    
    # Run pipeline
    pipeline = Layer3Pipeline(
        product_name='Groww',
        week_start='2025-11-25',
        week_end='2025-12-01'
    )
    
    pulse_document = pipeline.process(enriched_reviews, theme_metadata)
    
    print(f"\n{'='*60}")
    print("FINAL PULSE DOCUMENT")
    print(f"{'='*60}")
    print(f"\n{pulse_document['title']}")
    print(f"\n{pulse_document['overview']}")
    
    print(f"\n--- Top Themes ---")
    for theme in pulse_document['themes']:
        print(f"\n{theme['name']} ({theme['size']} reviews)")
        print(f"{theme['summary']}")
    
    print(f"\n--- User Quotes ---")
    for quote in pulse_document['quotes']:
        print(f"• \"{quote}\"")
    
    print(f"\n--- Action Ideas ---")
    for i, action in enumerate(pulse_document['actions'], 1):
        print(f"{i}. {action}")
    
    print(f"\n--- Metadata ---")
    print(f"Word Count: {pulse_document['metadata']['word_count']}/250")
    
    print("\n✓ Full pipeline test passed")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LAYER 3 COMPONENT TESTS")
    print("="*60)
    
    try:
        test_quote_extraction()
        test_theme_summarization()
        test_action_generation()
        test_pulse_assembly()
        test_full_pipeline()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
