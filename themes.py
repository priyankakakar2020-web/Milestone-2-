# themes.py

"""
Configuration for review theme classification.
"""

THEMES = {
    "Onboarding": {
        "description": "Onboarding – onboarding Grow experience, install access reviews, understanding of the product experience.",
        "keywords": ["install", "setup", "first", "onboard", "experience", "getting started", "new user"]
    },
    "KYC": {
        "description": "KYC – KYC related reviews.",
        "keywords": ["kyc", "verification", "identity", "document", "aadhar", "pan", "id verification"]
    },
    "Payments": {
        "description": "Payments – Regarding payments and linking bank accounts and knowing details.",
        "keywords": ["payment", "bank account", "link", "card", "deposit", "funds", "transfer"]
    },
    "Statement": {
        "description": "Statement – statement related to products purchased via app experiences.",
        "keywords": ["statement", "report", "summary", "history", "balance", "portfolio", "account statement"]
    },
    "Withdrawals": {
        "description": "Withdrawals – withdrawals related to products purchased via app experiences.",
        "keywords": ["withdraw", "withdrawal", "cash out", "payout", "redeem", "transfer out"]
    }
}
