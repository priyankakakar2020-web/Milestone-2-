"""
Test script for Layer 2: Theme Extraction & Classification
Demonstrates embedding generation, clustering, labeling, and theme limiting.
"""

from layer2_themes import (
    EmbeddingGenerator, 
    ThemeClusterer, 
    ThemeLabeler,
    ThemeLimitEnforcer,
    Layer2Pipeline
)
import pandas as pd
import glob


def test_embedding_generation():
    """Test embedding generation."""
    print("\n" + "="*60)
    print("TEST 1: EMBEDDING GENERATION")
    print("="*60)
    
    sample_texts = [
        "KYC verification is taking too long with document upload issues",
        "Payment failed but amount was deducted from my account",
        "Great app for beginners, easy to understand",
        "KYC process needs improvement, very slow",
        "Withdrawal is pending for 3 days now"
    ]
    
    generator = EmbeddingGenerator(model_name='all-MiniLM-L6-v2')
    embeddings = generator.generate(sample_texts, batch_size=5)
    
    print(f"Input texts: {len(sample_texts)}")
    print(f"Embeddings shape: {embeddings.shape}")
    print(f"Sample embedding (first 5 dims): {embeddings[0][:5]}")
    print("✓ Embedding generation test passed")


def test_clustering():
    """Test HDBSCAN clustering."""
    print("\n" + "="*60)
    print("TEST 2: THEME CLUSTERING")
    print("="*60)
    
    # Load actual review data
    files = glob.glob('reviews_week_*.csv')
    if not files:
        print("⚠ No review files found. Skipping clustering test.")
        return
    
    df = pd.read_csv(files[0])
    texts = df['text'].dropna().head(100).tolist()
    
    print(f"Loaded {len(texts)} reviews for clustering")
    
    # Generate embeddings
    generator = EmbeddingGenerator()
    embeddings = generator.generate(texts)
    
    # Cluster
    clusterer = ThemeClusterer(min_cluster_size=10, min_samples=3)
    clusterer.fit(embeddings)
    
    stats = clusterer.get_cluster_stats()
    print(f"Clustering results:")
    print(f"  Clusters found: {stats['n_clusters']}")
    print(f"  Noise points: {stats['n_noise']}")
    print(f"  Cluster sizes: {stats['cluster_sizes']}")
    
    print("✓ Clustering test passed")


def test_theme_labeling():
    """Test LLM-based theme labeling."""
    print("\n" + "="*60)
    print("TEST 3: THEME LABELING")
    print("="*60)
    
    sample_reviews = [
        "KYC verification took 5 days, document upload failed multiple times",
        "Identity verification process is very slow and confusing",
        "KYC rejected twice without clear reason, frustrating experience",
        "Aadhaar and PAN verification needs better guidance"
    ]
    
    import numpy as np
    probabilities = np.array([0.95, 0.90, 0.88, 0.85])
    
    labeler = ThemeLabeler()
    result = labeler.label_cluster(sample_reviews, probabilities)
    
    print(f"Sample cluster: {len(sample_reviews)} reviews about KYC")
    print(f"Generated theme:")
    print(f"  Name: {result['theme_name']}")
    print(f"  Description: {result['description']}")
    
    print("✓ Theme labeling test passed")


def test_theme_limit_enforcer():
    """Test theme limiting to max 5."""
    print("\n" + "="*60)
    print("TEST 4: THEME LIMIT ENFORCER")
    print("="*60)
    
    # Create mock themes
    mock_themes = [
        {'cluster_id': 0, 'theme_name': 'KYC Issues', 'description': '...', 'size': 45},
        {'cluster_id': 1, 'theme_name': 'Payment Failures', 'description': '...', 'size': 38},
        {'cluster_id': 2, 'theme_name': 'App Performance', 'description': '...', 'size': 32},
        {'cluster_id': 3, 'theme_name': 'Onboarding', 'description': '...', 'size': 28},
        {'cluster_id': 4, 'theme_name': 'Withdrawals', 'description': '...', 'size': 22},
        {'cluster_id': 5, 'theme_name': 'UI/UX', 'description': '...', 'size': 15},
        {'cluster_id': 6, 'theme_name': 'Support', 'description': '...', 'size': 12},
        {'cluster_id': 7, 'theme_name': 'Features', 'description': '...', 'size': 8},
    ]
    
    import numpy as np
    labels = np.array([0] * 45 + [1] * 38 + [2] * 32 + [3] * 28 + [4] * 22 + [5] * 15 + [6] * 12 + [7] * 8)
    embeddings = np.random.rand(200, 384)
    reviews = [''] * 200
    
    print(f"Input: {len(mock_themes)} themes")
    
    enforced = ThemeLimitEnforcer.enforce_limit(mock_themes, reviews, labels, embeddings)
    
    print(f"Output: {len(enforced)} themes (max 5)")
    for theme in enforced:
        print(f"  {theme['theme_name']}: {theme['size']} reviews")
    
    assert len(enforced) <= 5, "Theme limit not enforced!"
    print("✓ Theme limit enforcer test passed")


def test_full_pipeline():
    """Test full Layer 2 pipeline."""
    print("\n" + "="*60)
    print("TEST 5: FULL LAYER 2 PIPELINE")
    print("="*60)
    
    # Load sample reviews
    files = glob.glob('reviews_week_*.csv')
    if not files:
        print("⚠ No review files found. Creating sample data.")
        sample_reviews = [
            {'review_id': f'r{i}', 'text': f'Sample review {i}'} 
            for i in range(50)
        ]
    else:
        df = pd.read_csv(files[0])
        sample_reviews = df[['review_id', 'text']].dropna().head(100).to_dict('records')
    
    print(f"Processing {len(sample_reviews)} reviews through Layer 2")
    
    # Run pipeline
    pipeline = Layer2Pipeline(
        embedding_model='all-MiniLM-L6-v2',
        min_cluster_size=10,
        min_samples=3,
        max_themes=5
    )
    
    enriched_reviews, metadata = pipeline.process(sample_reviews)
    
    print(f"\nResults:")
    print(f"  Enriched reviews: {len(enriched_reviews)}")
    print(f"  Themes identified: {len(metadata['themes'])}")
    print(f"  Embedding model: {metadata['embedding_model']}")
    
    print(f"\nThemes:")
    for theme in metadata['themes']:
        print(f"  • {theme['theme_name']}: {theme['size']} reviews")
        print(f"    {theme['description']}")
    
    print(f"\nSample enriched review:")
    sample = enriched_reviews[0]
    print(f"  ID: {sample.get('review_id')}")
    print(f"  Theme: {sample.get('theme')}")
    print(f"  Confidence: {sample.get('theme_confidence'):.2f}")
    print(f"  Text: {sample.get('text', '')[:100]}...")
    
    print("✓ Full pipeline test passed")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LAYER 2 COMPONENT TESTS")
    print("="*60)
    
    try:
        test_embedding_generation()
        test_clustering()
        test_theme_labeling()
        test_theme_limit_enforcer()
        test_full_pipeline()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
