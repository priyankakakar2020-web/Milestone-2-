# Complete Setup Guide: Weekly Product Pulse System

## Overview
This system automatically generates weekly product pulse reports from Google Play reviews using a 4-layer architecture, then sends them via Gmail.

## Architecture

```
Layer 1: Data Import & Validation
├─ Scraper/API Client
├─ Schema Validator
├─ PII Detector
├─ Deduplicator
└─ Scheduler (weekly trigger)

Layer 2: Theme Extraction & Classification
├─ Embedding Generation (sentence-transformers)
├─ Theme Clustering (HDBSCAN)
├─ Theme Labeling (Gemini LLM)
└─ Theme Limit Enforcer (max 5)

Layer 3: Content Generation
├─ Quote Extraction (with source refs)
├─ Theme Summarization (per theme)
├─ Action Idea Generator (chain-of-thought)
└─ Pulse Document Assembler (250-word limit)

Layer 4: Distribution & Feedback
├─ Email Template Renderer (HTML + plain text)
├─ PII Final Check (double-verification)
├─ Delivery System (with retry logic)
└─ Read Receipt Tracker (optional)
```

## Prerequisites

1. **Python 3.11+**
2. **Gmail account** with App Password
3. **Gemini API key**
4. **GitHub account** (for automation)

## Step 1: Local Setup

### Install Dependencies
```bash
cd c:\Users\Admin\milestone_2
pip install -r requirements.txt
```

**Dependencies include**:
- `google-play-scraper`: Fetch reviews
- `pandas`: Data manipulation
- `google-generativeai`: Gemini LLM
- `sentence-transformers`: Embeddings
- `hdbscan`: Clustering
- `scikit-learn`: ML utilities
- `schedule`: Cron-like scheduling

### Configure Environment Variables

**PowerShell (Windows)**:
```powershell
# Gemini API
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY","AIzaSyCj0APLH2rm-riDu6au2Hyuinj48liYTuo","User")

# Gmail SMTP
[Environment]::SetEnvironmentVariable("EMAIL_SENDER","priyankakakar2020@gmail.com","User")
[Environment]::SetEnvironmentVariable("EMAIL_PASSWORD","Desigirl!@#2025","User")
[Environment]::SetEnvironmentVariable("EMAIL_TO","priyanka.kakar@sattva.co.in","User")
[Environment]::SetEnvironmentVariable("EMAIL_FROM","priyankakakar2020@gmail.com","User")

# SMTP Configuration
[Environment]::SetEnvironmentVariable("SMTP_HOST","smtp.gmail.com","User")
[Environment]::SetEnvironmentVariable("SMTP_PORT","587","User")
[Environment]::SetEnvironmentVariable("SMTP_USER","priyankakakar2020@gmail.com","User")
[Environment]::SetEnvironmentVariable("SMTP_PASS","Desigirl!@#2025","User")

# Product Configuration
[Environment]::SetEnvironmentVariable("APP_ID","com.nextbillion.groww","User")
[Environment]::SetEnvironmentVariable("PRODUCT_NAME","Groww","User")
[Environment]::SetEnvironmentVariable("TIME_WINDOW_WEEKS","12","User")
[Environment]::SetEnvironmentVariable("TARGET_COUNT","100","User")
```

## Step 2: Test Locally

### Run Full Pipeline
```bash
# Layers 1-3: Generate pulse document
python run_full_pipeline.py

# Layer 4: Send email (dry run first)
python send_weekly_pulse.py --dry-run

# Layer 4: Actually send
python send_weekly_pulse.py
```

### Expected Output
```
============================================================
FULL 4-LAYER PIPELINE EXECUTION
============================================================

Layer 1: DATA IMPORT & VALIDATION
  Fetched 200 raw reviews
  Valid reviews after schema validation: 198
  Reviews flagged with PII: 12
  Unique reviews after deduplication: 195

Layer 2: THEME EXTRACTION & CLASSIFICATION
  Generating embeddings for 195 texts
  Clustering themes with HDBSCAN
  Found 5 themes identified
    • KYC Verification Delays: 45 reviews
    • Payment Failures: 38 reviews
    • App Performance: 32 reviews
    • Onboarding Issues: 25 reviews
    • Other: 55 reviews

Layer 3: CONTENT GENERATION
  Extracting quotes per theme
  Generating theme summaries
  Generating action ideas (chain-of-thought)
  Assembling pulse document
  Final document: 238 words

✓ Pulse document saved: weekly_pulse_2025_11_25.json
✓ Reviews saved: reviews_week_2025_11_25.csv

Layer 4: DISTRIBUTION & FEEDBACK
  Rendering email templates
  PII final check: ✓ Passed
  Sending to priyanka.kakar@sattva.co.in
  ✓ EMAIL SENT SUCCESSFULLY
```

## Step 3: GitHub Actions Setup

### Add Repository Secrets

1. Go to: **Settings → Secrets and variables → Actions**
2. Click **"New repository secret"**
3. Add these 3 secrets:

| Secret Name | Value |
|------------|-------|
| `GEMINI_API_KEY` | `AIzaSyCj0APLH2rm-riDu6au2Hyuinj48liYTuo` |
| `EMAIL_SENDER` | `priyankakakar2020@gmail.com` |
| `EMAIL_PASSWORD` | `Desigirl!@#2025` |

### Push to GitHub
```bash
git add .
git commit -m "Complete 4-layer weekly pulse system"
git push origin main
```

### Workflow Schedule
The workflow runs automatically:
- **Schedule**: Every Monday at 9:00 AM IST (3:30 AM UTC)
- **Manual**: Click "Run workflow" in Actions tab
- **Dry Run**: Check "dry run" option for preview

### Check Workflow Status
1. Go to **Actions** tab in GitHub
2. Click on latest "Weekly Product Pulse" workflow
3. View logs for each layer
4. Download artifacts (CSV, JSON, HTML preview)

## Step 4: Verify Email Delivery

### Check Email
- **To**: priyanka.kakar@sattva.co.in
- **From**: priyankakakar2020@gmail.com
- **Subject**: "Weekly Product Pulse – Groww"

### Email Content
- Professional HTML formatting
- Top 3 themes with summaries
- 3 user quotes (anonymized)
- 3 actionable recommendations
- Plain text fallback

### Check Logs
Review `email_send_log.csv`:
```csv
timestamp,week_start,week_end,subject,recipient,status,attempts,error_message,pii_clean
2025-12-01T09:00:15,2025-11-25,2025-12-01,Weekly Product Pulse – Groww,priyanka.kakar@sattva.co.in,SENT,1,,True
```

## Troubleshooting

### Issue: Gmail Authentication Failed
**Solution**: Use Gmail App Password instead of account password
1. Enable 2-Step Verification in Google Account
2. Go to Security → App passwords
3. Generate password for "Mail"
4. Update `EMAIL_PASSWORD` secret

### Issue: PII Detected and Blocked
**Solution**: Email blocked automatically if PII found
- Check `email_send_log.csv` for `pii_clean=False`
- PII is auto-scrubbed with `***` masking
- If scrubbing fails, email is blocked for safety

### Issue: No Themes Found
**Solution**: Lower clustering thresholds
- Edit `run_full_pipeline.py`:
  ```python
  layer2 = Layer2Pipeline(
      min_cluster_size=10,  # Lower from 15
      min_samples=3         # Lower from 5
  )
  ```

### Issue: SMTP Connection Timeout
**Solution**: Check firewall and SMTP settings
- Verify `SMTP_HOST=smtp.gmail.com`
- Verify `SMTP_PORT=587`
- Check network allows outbound port 587
- Retry logic will attempt 3 times automatically

### Issue: Word Count Exceeds 250
**Solution**: Automatic compression applied
- System automatically shortens summaries
- Keeps first sentence of each theme
- Logged in metadata: `word_count: 238/250`

## Files Generated

| File | Description |
|------|-------------|
| `reviews_week_YYYY_MM_DD.csv` | Enriched reviews with themes |
| `weekly_pulse_YYYY_MM_DD.json` | Generated pulse document |
| `email_send_log.csv` | Send status log with traceability |
| `dedup_state.json` | Deduplication tracking |
| `scheduler_state.json` | Scheduler run history |
| `email_tracking.json` | Read receipt tracking (optional) |

## Architecture Benefits

✓ **Modular**: Each layer can be tested independently  
✓ **Resumable**: Deduplication prevents re-processing  
✓ **Observable**: Detailed logging at each stage  
✓ **Safe**: Double PII verification before sending  
✓ **Robust**: Retry logic with automatic recovery  
✓ **Scalable**: Layer 2 handles 100s-1000s of reviews  
✓ **Intelligent**: ML-based theme discovery (not keywords)  
✓ **Actionable**: Chain-of-thought reasoning for recommendations  

## Support

For issues or questions:
1. Check layer-specific README files
2. Review GitHub Actions workflow logs
3. Inspect `email_send_log.csv` for delivery status
4. Test components individually with test scripts

## Next Steps

1. **Monitor first automated run** (next Monday 9 AM IST)
2. **Review email delivery** in inbox
3. **Adjust parameters** if needed:
   - Theme count (Layer 2: `max_themes`)
   - Word limit (Layer 3: `MAX_WORDS`)
   - Retry attempts (Layer 4: `max_retries`)
4. **Add more recipients** in workflow YAML
5. **Customize email template** in `layer4_distribution.py`

---

**System Status**: ✅ Ready for Production
