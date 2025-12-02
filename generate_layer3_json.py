"""Generate sample Layer 3 JSON output."""

from layer3_content import Layer3Pipeline
import json
from datetime import datetime, timedelta

# Calculate week dates
week_end = datetime.now() - timedelta(days=7)
week_start = week_end - timedelta(days=6)

# Sample enriched reviews (output from Layer 2)
enriched_reviews = [
    {
        'reviewId': 'gp_rev_001',
        'content': 'KYC verification took 5 days and failed twice without clear explanation. Very frustrating process.',
        'text': 'KYC verification took 5 days and failed twice without clear explanation. Very frustrating process.',
        'score': 2,
        'at': week_end,
        'theme_name': 'KYC Verification Delays',
        'theme_confidence': 0.95
    },
    {
        'reviewId': 'gp_rev_002',
        'content': 'Identity document upload keeps failing. No guidance on acceptable formats.',
        'text': 'Identity document upload keeps failing. No guidance on acceptable formats.',
        'score': 1,
        'at': week_end,
        'theme_name': 'KYC Verification Delays',
        'theme_confidence': 0.88
    },
    {
        'reviewId': 'gp_rev_003',
        'content': 'Been waiting for KYC approval for 7 days now. Customer support not responsive.',
        'text': 'Been waiting for KYC approval for 7 days now. Customer support not responsive.',
        'score': 2,
        'at': week_end,
        'theme_name': 'KYC Verification Delays',
        'theme_confidence': 0.92
    },
    {
        'reviewId': 'gp_rev_004',
        'content': 'Payment deducted from bank but order not confirmed. No refund received after 3 days.',
        'text': 'Payment deducted from bank but order not confirmed. No refund received after 3 days.',
        'score': 1,
        'at': week_end,
        'theme_name': 'Payment Failures',
        'theme_confidence': 0.89
    },
    {
        'reviewId': 'gp_rev_005',
        'content': 'UPI payment failed but amount was debited. Support team says wait 7 business days.',
        'text': 'UPI payment failed but amount was debited. Support team says wait 7 business days.',
        'score': 2,
        'at': week_end,
        'theme_name': 'Payment Failures',
        'theme_confidence': 0.91
    },
    {
        'reviewId': 'gp_rev_006',
        'content': 'App crashes frequently during market hours. Very frustrating when trying to execute trades.',
        'text': 'App crashes frequently during market hours. Very frustrating when trying to execute trades.',
        'score': 2,
        'at': week_end,
        'theme_name': 'App Performance',
        'theme_confidence': 0.85
    }
]

# Sample theme metadata (output from Layer 2)
theme_metadata = {
    'themes': [
        {
            'theme_name': 'KYC Verification Delays',
            'description': 'Users experiencing slow and unclear KYC verification processes',
            'size': 45,
            'keywords': ['KYC', 'verification', 'document', 'approval']
        },
        {
            'theme_name': 'Payment Failures',
            'description': 'Payment deductions without order confirmation or refunds',
            'size': 38,
            'keywords': ['payment', 'deducted', 'refund', 'UPI']
        },
        {
            'theme_name': 'App Performance',
            'description': 'App crashes and performance issues during peak hours',
            'size': 32,
            'keywords': ['crash', 'slow', 'performance', 'market hours']
        }
    ],
    'total_reviews': 115,
    'clustered_reviews': 115
}

# Initialize Layer 3 pipeline
layer3 = Layer3Pipeline(
    product_name='Groww',
    week_start=week_start.strftime('%Y-%m-%d'),
    week_end=week_end.strftime('%Y-%m-%d')
)

# Process reviews to generate pulse document
pulse_document = layer3.process(enriched_reviews, theme_metadata)

# Pretty print JSON
print(json.dumps(pulse_document, indent=2, ensure_ascii=False))

# Save to file
with open('layer3_output.json', 'w', encoding='utf-8') as f:
    json.dump(pulse_document, f, indent=2, ensure_ascii=False)

print('\n✓ Saved to layer3_output.json', file=__import__('sys').stderr)
