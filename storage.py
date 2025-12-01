import pandas as pd
import os
import json
from datetime import datetime

def save_reviews(reviews, week_start_date):
    """
    Saves the list of reviews to a CSV file bucketed by week.
    
    reviews: List of dictionaries containing review data.
    week_start_date: datetime object representing the start of the week.
    """
    if not reviews:
        print("No reviews to save.")
        return

    # Format filename: reviews_week_YYYY_MM_DD.csv
    filename = f"reviews_week_{week_start_date.strftime('%Y_%m_%d')}.csv"
    filepath = os.path.join(os.getcwd(), filename)

    df = pd.DataFrame(reviews)
    
    # Ensure columns are in the desired order
    columns = ['week_start_date', 'week_end_date', 'review_id', 'title', 'text', 'theme', 'theme_reason', 'date', 'program_tag']
    # Add missing columns with None if they don't exist
    for col in columns:
        if col not in df.columns:
            df[col] = None
            
    df = df[columns]

    # Save to CSV
    # If file exists, we might want to append or overwrite. 
    # For this milestone, let's overwrite to keep it simple and idempotent for the week run.
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"Saved {len(reviews)} reviews to {filepath}")


def save_weekly_pulse(note_json, week_start_date: datetime):
    """
    Save the weekly pulse note JSON artifact.
    note_json: dict with keys title, overview, themes[], quotes[], actions[]
    """
    filename = f"weekly_pulse_{week_start_date.strftime('%Y_%m_%d')}.json"
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(note_json, f, ensure_ascii=False, indent=2)


def save_theme_counts(counts, week_start_date: datetime):
    """
    Save per-week theme counts to a CSV file.
    counts: dict mapping theme -> count
    week_start_date: datetime representing start of week
    """
    filename = f"reviews_week_{week_start_date.strftime('%Y_%m_%d')}_theme_counts.csv"
    filepath = os.path.join(os.getcwd(), filename)
    rows = [{"theme": k, "count": v} for k, v in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)]
    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"Saved theme counts to {filepath}")
