"""
Full 4-Layer Pipeline Runner
Executes all layers in sequence: Import → Theme Extraction → Content Generation → Distribution
"""

import os
import json
from datetime import datetime, timedelta

# Layer imports
from layer1_import import Layer1Pipeline
from layer2_themes import Layer2Pipeline
from layer3_content import Layer3Pipeline


def run_full_pipeline(app_id: str = None,
                     product_name: str = None,
                     time_window_weeks: int = None,
                     target_count: int = None):
    """
    Execute complete 4-layer pipeline.
    
    Args:
        app_id: Google Play app ID
        product_name: Product name for reports
        time_window_weeks: Number of weeks to fetch
        target_count: Target review count
    """
    # Load from environment or use defaults
    app_id = app_id or os.getenv('APP_ID', 'com.nextbillion.groww')
    product_name = product_name or os.getenv('PRODUCT_NAME', 'Groww')
    time_window_weeks = time_window_weeks or int(os.getenv('TIME_WINDOW_WEEKS', '12'))
    target_count = target_count or int(os.getenv('TARGET_COUNT', '100'))
    
    # Calculate week dates
    today = datetime.now()
    week_end = today - timedelta(days=7)  # Last week
    week_start = week_end - timedelta(days=6)  # Start of last week
    
    week_start_str = week_start.strftime('%Y-%m-%d')
    week_end_str = week_end.strftime('%Y-%m-%d')
    
    print("\n" + "="*60)
    print("FULL 4-LAYER PIPELINE EXECUTION")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Product: {product_name} ({app_id})")
    print(f"  Time Window: {time_window_weeks} weeks")
    print(f"  Target Reviews: {target_count}")
    print(f"  Week: {week_start_str} to {week_end_str}")
    print("\n" + "="*60)
    
    # =========================================================================
    # LAYER 1: DATA IMPORT & VALIDATION
    # =========================================================================
    print("\n" + "="*60)
    print("LAYER 1: DATA IMPORT & VALIDATION")
    print("="*60)
    
    layer1 = Layer1Pipeline(
        app_id=app_id,
        lang=os.getenv('LANG', 'en'),
        country=os.getenv('COUNTRY', 'in')
    )
    
    # Fetch reviews
    all_reviews = []
    continuation_token = None
    
    while len(all_reviews) < target_count:
        batch, continuation_token = layer1.process_batch(
            count=200,
            continuation_token=continuation_token
        )
        
        if not batch:
            break
        
        # Filter by date range
        for review in batch:
            review_date = review['at']
            data_start = today - timedelta(weeks=time_window_weeks)
            
            if data_start <= review_date <= week_end:
                # Add cleaned text
                from cleaner import clean_text
                review['text'] = clean_text(review.get('content', ''))
                
                # Skip short reviews
                if len(review['text']) >= 100:
                    all_reviews.append(review)
        
        if len(all_reviews) >= target_count:
            break
        
        if not continuation_token:
            break
    
    print(f"\n✓ Layer 1 complete: {len(all_reviews)} valid reviews")
    
    if len(all_reviews) == 0:
        print("Error: No reviews collected. Exiting.")
        return
    
    # =========================================================================
    # LAYER 2: THEME EXTRACTION & CLASSIFICATION
    # =========================================================================
    print("\n" + "="*60)
    print("LAYER 2: THEME EXTRACTION & CLASSIFICATION")
    print("="*60)
    
    layer2 = Layer2Pipeline(
        embedding_model='all-MiniLM-L6-v2',
        min_cluster_size=15,
        min_samples=5,
        max_themes=5
    )
    
    enriched_reviews, theme_metadata = layer2.process(all_reviews)
    
    print(f"\n✓ Layer 2 complete: {len(theme_metadata['themes'])} themes identified")
    for theme in theme_metadata['themes']:
        print(f"  • {theme['theme_name']}: {theme['size']} reviews")
    
    # =========================================================================
    # LAYER 3: CONTENT GENERATION
    # =========================================================================
    print("\n" + "="*60)
    print("LAYER 3: CONTENT GENERATION")
    print("="*60)
    
    layer3 = Layer3Pipeline(
        product_name=product_name,
        week_start=week_start_str,
        week_end=week_end_str
    )
    
    pulse_document = layer3.process(enriched_reviews, theme_metadata)
    
    print(f"\n✓ Layer 3 complete: Pulse document generated")
    print(f"  Title: {pulse_document['title']}")
    print(f"  Word count: {pulse_document['metadata']['word_count']}/250")
    print(f"  Themes: {len(pulse_document['themes'])}")
    print(f"  Quotes: {len(pulse_document['quotes'])}")
    print(f"  Actions: {len(pulse_document['actions'])}")
    
    # Save pulse document
    pulse_filename = f"weekly_pulse_{week_start_str.replace('-', '_')}.json"
    with open(pulse_filename, 'w', encoding='utf-8') as f:
        json.dump(pulse_document, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Pulse document saved: {pulse_filename}")
    
    # Save enriched reviews
    import pandas as pd
    df = pd.DataFrame(enriched_reviews)
    reviews_filename = f"reviews_week_{week_start_str.replace('-', '_')}.csv"
    df.to_csv(reviews_filename, index=False, encoding='utf-8')
    
    print(f"✓ Reviews saved: {reviews_filename}")
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETE (Layers 1-3)")
    print("="*60)
    print("\nNext step: Run send_weekly_pulse.py to deliver (Layer 4)")
    print("  python send_weekly_pulse.py")
    print("  python send_weekly_pulse.py --dry-run  (preview without sending)")


if __name__ == "__main__":
    run_full_pipeline()
