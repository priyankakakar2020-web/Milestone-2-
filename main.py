import sys
from google_play_scraper import Sort, reviews
from datetime import datetime, timedelta
import os
import pandas as pd
from cleaner import clean_text
from storage import save_reviews, save_theme_counts
from classifier import classify_week_reviews_llm
from emailer import draft_weekly_email, generate_subject, scrub_pii, send_email, log_email_send

# Configuration
APP_ID = 'com.nextbillion.groww'
LANG = 'en'
COUNTRY = 'in'
PRODUCT_NAME = 'Groww'
TARGET_COUNT = 100
MIN_WEEKS = 8
MAX_WEEKS = 12

def fetch_and_process_reviews():
    print(f"Starting review import for {APP_ID}...")
    
    today = datetime.now()
    # We want reviews from [today - MAX_WEEKS weeks] to [today - 1 week]
    # Actually user said "last 8-12 weeks" and "up to last week".
    # Let's define the window:
    # End date: today - 7 days (last week)
    # Start date: today - (MAX_WEEKS * 7) days
    
    end_date = today - timedelta(days=7)
    start_date = today - timedelta(days=MAX_WEEKS * 7)
    
    print(f"Target date range: {start_date.date()} to {end_date.date()}")

    all_reviews = []
    continuation_token = None
    
    # Fetch in batches until we cover the time range and have enough reviews
    # google-play-scraper 'reviews' function returns a batch.
    
    # We might need to fetch more if we don't hit 100 valid reviews.
    # Strategy: Fetch, Filter, Check count. If < 100, extend range?
    # The user said: "if the limit is not reached you can extend the time frame."
    # So we can keep fetching older reviews.
    
    fetched_count = 0
    
    while True:
        result, continuation_token = reviews(
            APP_ID,
            lang=LANG,
            country=COUNTRY,
            sort=Sort.NEWEST,
            count=200, # Fetch a batch
            continuation_token=continuation_token
        )
        
        if not result:
            break
            
        for r in result:
            review_date = r['at']
            
            # If review is newer than end_date, skip it (too recent)
            # But since we sort by NEWEST, we just continue until we hit the range
            if review_date > end_date:
                continue
                
            # If review is older than start_date, we might stop...
            # UNLESS we haven't reached 100 reviews yet.
            if review_date < start_date:
                if len(all_reviews) >= TARGET_COUNT:
                    # We have enough reviews and we passed the start date.
                    # We can stop.
                    break
                else:
                    # We need more reviews, so we extend the timeframe implicitly by continuing to accept older reviews.
                    pass
            
            # Process review
            cleaned_text = clean_text(r['content'])
            cleaned_title = clean_text(r.get('userName', '')) # Title is often not explicitly separate in scraper result, using userName or just content?
            # Wait, google-play-scraper result has: reviewId, userName, userImage, content, score, thumbsUpCount, reviewCreatedVersion, at, replyContent, repliedAt
            # It doesn't strictly have a "Title". The user request said "Title (review heading)".
            # Play store reviews often don't have a title anymore, just the star rating and text.
            # We will use an empty string or the first few words for title if needed, or just map what we have.
            # Let's check if there is a title field I missed. The library docs say: content, score, etc. No title.
            # I will leave title empty or use a placeholder.
            
            # Filter by length > 100 chars
            if len(cleaned_text) < 100:
                continue
                
            review_data = {
                'week_start_date': (review_date - timedelta(days=review_date.weekday())).strftime('%Y-%m-%d'), # Start of the week for this review
                'week_end_date': (review_date + timedelta(days=6-review_date.weekday())).strftime('%Y-%m-%d'),
                'review_id': r['reviewId'],
                'rating': r['score'],
                'title': '', # No title in standard Play Store response
                'text': cleaned_text,
                'date': review_date.strftime('%Y-%m-%d %H:%M:%S'),
                'program_tag': APP_ID # Using App ID as tag
            }
            
            all_reviews.append(review_data)
            
        fetched_count += len(result)
        print(f"Fetched {fetched_count} raw reviews, {len(all_reviews)} qualified reviews so far...")

        # Check exit condition
        # If we have enough reviews AND we have covered the minimum date range (which we check inside the loop logic sort of)
        # Actually, if we are past start_date and have enough reviews, we stop.
        # The loop break above handles "past start_date AND >= TARGET_COUNT".
        
        # What if we run out of reviews?
        if not continuation_token:
            break
            
        # Check if we should stop fetching because we went way too far back?
        # For now, let's trust the ">= TARGET_COUNT" logic.
        
        # Optimization: If the last review in this batch is older than start_date AND we have enough reviews, stop.
        last_review_date = result[-1]['at']
        if last_review_date < start_date and len(all_reviews) >= TARGET_COUNT:
            break

    print(f"Total qualified reviews collected: {len(all_reviews)}")
    
    # Save reviews
    # The user wants "Store weekly buckets".
    # So we should group by week and save.
    
    df = pd.DataFrame(all_reviews)
    if not df.empty:
        # Group by week_start_date
        for week_start, group in df.groupby('week_start_date'):
            # We need a datetime object for the saver
            ws_date = datetime.strptime(week_start, '%Y-%m-%d')
            records = group.to_dict('records')
            # LLM-based classification in batches
            id_to_theme = classify_week_reviews_llm(records)
            for rec in records:
                rid = rec.get('review_id')
                if rid in id_to_theme:
                    rec['theme'] = id_to_theme[rid]['theme']
                    rec['theme_reason'] = id_to_theme[rid]['reason']
                else:
                    # Fallback: heuristic classification
                    from classifier import assign_theme
                    rec['theme'] = assign_theme(rec.get('text', ''))
                    rec['theme_reason'] = 'Assigned by keyword heuristic (no LLM result).'
            # Aggregate counts per theme
            counts = {}
            for rec in records:
                t = rec.get('theme') or 'Onboarding'
                counts[t] = counts.get(t, 0) + 1
            # Save weekly outputs
            save_reviews(records, ws_date)
            save_theme_counts(counts, ws_date)
            # Keep top themes by count for later selection
            top_themes_by_count = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
            print(f"Top themes for week {week_start}: {top_themes_by_count}")
            # Weekly one-page note generation
            top3 = [name for name, _ in top_themes_by_count[:3]]
            # Collect summaries per top theme (map stage)
            from summarizer import summarize_theme, synthesize_weekly_pulse, compress_note_if_needed
            theme_summaries = []
            for name in top3:
                texts = [rec['text'] for rec in records if rec.get('theme') == name]
                if texts:
                    theme_summaries.append(summarize_theme(name, texts))
            # Determine week_end from group
            week_end = group['week_end_date'].iloc[0] if 'week_end_date' in group.columns else week_start
            # Reduce stage: synthesize weekly pulse
            note = synthesize_weekly_pulse(week_start, week_end, theme_summaries, top3)
            # Enforce word limit and structure
            note_final = compress_note_if_needed(note, max_words=250)
            # Save weekly note artifact
            from storage import save_weekly_pulse
            save_weekly_pulse(note_final, ws_date)
            # Draft and send weekly email
            subject = generate_subject(PRODUCT_NAME, week_start, week_end)
            body = draft_weekly_email(note_final, week_start, week_end, PRODUCT_NAME)
            body = scrub_pii(body)
            to_addr = os.getenv('EMAIL_TO', 'priyanka.kakar@sattva.co.in')
            status, err = send_email(subject, body, to_addr)
            log_email_send(week_start, week_end, subject, to_addr, status, err)
    else:
        print("No reviews found matching criteria.")

if __name__ == "__main__":
    fetch_and_process_reviews()
