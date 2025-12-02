import pandas as pd
import glob
from classifier import assign_theme

# Load all weekly review files
files = glob.glob('reviews_week_*.csv')
all_reviews = []

for f in files:
    df = pd.read_csv(f)
    all_reviews.append(df)

df_all = pd.concat(all_reviews, ignore_index=True)

# Apply theme classification to existing reviews (using keyword heuristic)
df_all['theme'] = df_all['text'].apply(lambda x: assign_theme(str(x)) if pd.notna(x) else 'Other')

# Count themes
theme_counts = df_all['theme'].value_counts()

print("=" * 60)
print("THEME DISTRIBUTION ACROSS ALL WEEKS")
print("=" * 60)
print(theme_counts)
print()

# Top 3 themes
top3 = theme_counts.head(3)
print("=" * 60)
print("TOP 3 THEMES")
print("=" * 60)
for i, (theme, count) in enumerate(top3.items(), 1):
    print(f"{i}. {theme}: {count} reviews")
print()

# Show sample reviews for each top theme
print("=" * 60)
print("SAMPLE REVIEWS BY TOP 3 THEMES")
print("=" * 60)

for theme in top3.index:
    theme_reviews = df_all[df_all['theme'] == theme]
    print(f"\n{'='*60}")
    print(f"THEME: {theme.upper()} ({len(theme_reviews)} reviews)")
    print(f"{'='*60}")
    
    # Show up to 3 sample reviews
    for idx, row in theme_reviews.head(3).iterrows():
        print(f"\nReview ID: {row.get('review_id', 'N/A')}")
        print(f"Date: {row.get('date', 'N/A')}")
        text = row.get('text', '')
        # Truncate long reviews for readability
        display_text = text[:300] + '...' if len(str(text)) > 300 else text
        print(f"Text: {display_text}")
        print("-" * 60)
