# Complete 4-Layer Integration & Automation Guide

## 🎯 Overview

The **Integrated Pulse Pipeline** automates the entire weekly product pulse generation and distribution workflow through 4 sequential layers.

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATED PULSE PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   LAYER 1        │  Data Import & Validation
│   Import         │  • Google Play scraper
│   & Validate     │  • Schema validation
│                  │  • PII detection
│                  │  • Deduplication
└────────┬─────────┘
         │ 100+ valid reviews
         ▼
┌──────────────────┐
│   LAYER 2        │  Theme Extraction & Classification
│   Extract        │  • Sentence embeddings
│   Themes         │  • HDBSCAN clustering
│                  │  • LLM theme labeling
│                  │  • Max 5 themes
└────────┬─────────┘
         │ Enriched reviews + themes
         ▼
┌──────────────────┐
│   LAYER 3        │  Content Generation
│   Generate       │  • Quote extraction
│   Content        │  • Theme summarization
│                  │  • Action generation (CoT)
│                  │  • 250-word pulse assembly
└────────┬─────────┘
         │ Pulse document (JSON)
         ▼
┌──────────────────┐
│   LAYER 4        │  Distribution & Feedback
│   Distribute     │  • HTML + plain text rendering
│   & Track        │  • PII final check
│                  │  • Gmail SMTP delivery
│                  │  • Logging & tracking
└──────────────────┘
         │ Email sent
         ▼
   📧 priyanka.kakar@sattva.co.in
```

---

## 🚀 Quick Start

### Local Execution

```bash
# Dry run (preview without sending)
python integrated_pipeline.py --dry-run

# Full pipeline with email delivery
python integrated_pipeline.py

# With custom config
python integrated_pipeline.py --config config.json
```

### GitHub Actions (Automated)

**Schedule**: Every Monday at 9:00 AM IST  
**Manual Trigger**: https://github.com/priyankakakar2020-web/Milestone-2-/actions

---

## 📋 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| **Product** | | |
| `APP_ID` | `com.nextbillion.groww` | Google Play app ID |
| `PRODUCT_NAME` | `Groww` | Product name for reports |
| `LANG` | `en` | Review language |
| `COUNTRY` | `in` | Review country |
| **Data Collection** | | |
| `TIME_WINDOW_WEEKS` | `12` | Weeks of data to fetch |
| `TARGET_COUNT` | `100` | Target review count |
| `MIN_REVIEW_LENGTH` | `100` | Minimum review chars |
| **Layer 2: Themes** | | |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `MIN_CLUSTER_SIZE` | `15` | HDBSCAN min cluster size |
| `MIN_SAMPLES` | `5` | HDBSCAN min samples |
| `MAX_THEMES` | `5` | Maximum themes to extract |
| **Layer 3: Content** | | |
| `MAX_WORD_COUNT` | `250` | Pulse word limit |
| `QUOTES_PER_THEME` | `3` | Quotes per theme |
| **Layer 4: Email** | | |
| `EMAIL_SENDER` | - | Sender email (required) |
| `EMAIL_PASSWORD` | - | Gmail app password (required) |
| `EMAIL_TO` | `priyanka.kakar@sattva.co.in` | Recipient email |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | `587` | SMTP port |
| **API Keys** | | |
| `GEMINI_API_KEY` | - | Gemini API key (required) |

### Custom Configuration File

Create `config.json`:

```json
{
  "app_id": "com.nextbillion.groww",
  "product_name": "Groww",
  "time_window_weeks": 12,
  "target_review_count": 100,
  "max_themes": 5,
  "email_to": "priyanka.kakar@sattva.co.in"
}
```

Run with custom config:
```bash
python integrated_pipeline.py --config config.json
```

---

## 📊 Pipeline Execution Flow

### Step 1: Initialization

```python
pipeline = IntegratedPulsePipeline(config=config)
```

**Actions**:
- Load configuration from environment or config file
- Initialize statistics tracking
- Validate required credentials (API keys, SMTP)

### Step 2: Layer 1 - Data Import

```python
valid_reviews = pipeline._run_layer1(data_start, week_end)
```

**Process**:
1. Fetch reviews from Google Play (batch of 200)
2. Validate schema (reviewId, content, score, at)
3. Detect PII (flag, don't block)
4. Deduplicate using reviewId/content hash
5. Filter by date range and minimum length

**Output**: `List[Dict]` - 100+ valid reviews

**Stats Tracked**:
- Valid reviews collected
- Total reviews seen
- Duplicates filtered
- PII flagged

### Step 3: Layer 2 - Theme Extraction

```python
enriched_reviews, theme_metadata = pipeline._run_layer2(valid_reviews)
```

**Process**:
1. Generate embeddings (all-MiniLM-L6-v2, 384 dims)
2. Cluster with HDBSCAN (min_cluster_size=15)
3. Label clusters with Gemini LLM
4. Enforce max 5 themes (merge rest into "Other")
5. Add `theme_name` and `theme_confidence` to each review

**Output**: 
- Enriched reviews with theme assignments
- Theme metadata (names, descriptions, sizes)

**Stats Tracked**:
- Number of themes found
- Reviews per theme
- Theme names and sizes

### Step 4: Layer 3 - Content Generation

```python
pulse_document = pipeline._run_layer3(enriched_reviews, theme_metadata, week_start, week_end)
```

**Process**:
1. **Quote Extraction**: Top 3 quotes per theme (by confidence)
2. **Theme Summarization**: 1-2 sentence summaries (LLM)
3. **Action Generation**: 3 specific actions (chain-of-thought)
4. **Document Assembly**: Combine into 250-word pulse

**Output**: Pulse document (JSON)

```json
{
  "title": "Weekly Product Pulse – Groww",
  "overview": "This week's 115 reviews highlight...",
  "themes": [...],
  "quotes": [...],
  "actions": [...],
  "metadata": {
    "word_count": 238,
    "total_reviews": 115
  }
}
```

**Stats Tracked**:
- Word count
- Themes included
- Quotes extracted
- Actions generated
- Output filename

### Step 5: Layer 4 - Distribution

```python
delivery_result = pipeline._run_layer4(pulse_document, dry_run)
```

**Process**:
1. **Render Email**: HTML + plain text templates
2. **PII Check**: Double-verify both versions
3. **Scrub PII**: Auto-mask if detected
4. **Send Email**: Gmail SMTP with retry (max 3)
5. **Log Status**: Save to `email_send_log.csv`

**Output**: Delivery result

```python
{
  'status': 'SENT',
  'metadata': {
    'sent_at': '2025-12-02T21:45:12',
    'attempts': 1
  },
  'pii_clean': True
}
```

**Stats Tracked**:
- Delivery status
- Recipient email
- PII check result
- Attempts made
- Send timestamp

### Step 6: Final Report

```python
result = pipeline.run(dry_run=False)
```

**Output**: Complete execution report

```json
{
  "status": "SUCCESS",
  "stats": {
    "layer1": {...},
    "layer2": {...},
    "layer3": {...},
    "layer4": {...},
    "execution_time": {
      "layer1": 45.2,
      "layer2": 12.8,
      "layer3": 8.5,
      "layer4": 3.1,
      "total": 69.6
    }
  },
  "pulse_document": {...},
  "delivery_result": {...}
}
```

---

## 📈 Performance Metrics

### Typical Execution Times

| Layer | Task | Average Time |
|-------|------|--------------|
| **Layer 1** | Fetch & validate 100 reviews | 30-60s |
| **Layer 2** | Generate embeddings + cluster | 10-20s |
| **Layer 3** | Generate content with LLM | 5-15s |
| **Layer 4** | Render + send email | 2-5s |
| **Total** | End-to-end pipeline | **47-100s** |

### Resource Usage

- **Memory**: ~500MB (embeddings + models)
- **API Calls**: 
  - Google Play: 1-5 requests
  - Gemini LLM: 5-10 requests
  - SMTP: 1 request
- **Storage**: 
  - Reviews CSV: ~50KB
  - Pulse JSON: ~5KB
  - Logs: ~2KB per run

---

## 🧪 Testing

### Dry Run (No Email)

```bash
python integrated_pipeline.py --dry-run
```

**Output**:
- ✓ All layers execute
- ✓ Email rendered (saved as preview)
- ✗ Email NOT sent
- ✓ Statistics logged

### Full Test

```bash
python integrated_pipeline.py
```

**Output**:
- ✓ All layers execute
- ✓ Email rendered
- ✓ Email sent to recipient
- ✓ Logged to `email_send_log.csv`

### Unit Tests

```bash
# Test individual layers
python test_layer1.py
python test_layer2.py
python test_layer3.py
python test_layer4.py
```

---

## 📁 Files Generated

### During Execution

| File | Description | Size | Retention |
|------|-------------|------|-----------|
| `weekly_pulse_YYYY_MM_DD.json` | Generated pulse document | ~5KB | Permanent |
| `reviews_week_YYYY_MM_DD.csv` | Enriched reviews | ~50KB | Permanent |
| `email_send_log.csv` | Delivery log | ~2KB/run | Permanent |
| `dedup_state.json` | Deduplication state | ~10KB | Permanent |
| `preview_email.html` | Email preview (dry run) | ~4KB | Overwritten |
| `preview_email.txt` | Plain text preview | ~2KB | Overwritten |

### GitHub Actions Artifacts

Downloaded from: https://github.com/priyankakakar2020-web/Milestone-2-/actions

- `weekly-pulse-outputs.zip` (90-day retention)
  - All CSV, JSON, HTML files
  - Delivery logs

---

## 🛠️ Troubleshooting

### Issue: Layer 1 - No Reviews Fetched

**Symptoms**: "No valid reviews collected. Cannot proceed."

**Solutions**:
1. Check `APP_ID` is correct
2. Reduce `MIN_REVIEW_LENGTH` (try 50)
3. Increase `TIME_WINDOW_WEEKS` (try 24)
4. Check Google Play app has reviews

### Issue: Layer 2 - No Themes Found

**Symptoms**: "Themes identified: 0"

**Solutions**:
1. Reduce `MIN_CLUSTER_SIZE` (try 10)
2. Reduce `MIN_SAMPLES` (try 3)
3. Increase `TARGET_COUNT` (try 200)
4. Check reviews have sufficient variety

### Issue: Layer 3 - Word Count Exceeded

**Symptoms**: Word count > 250

**Solutions**:
1. System auto-compresses to 250 words
2. Summaries shortened to first sentence
3. Check `pulse_document['metadata']['word_count']`

### Issue: Layer 4 - Email Not Sent

**Symptoms**: Status = "ERROR" or "BLOCKED"

**Solutions**:

**If ERROR**:
1. Check `EMAIL_PASSWORD` is correct (Gmail App Password)
2. Verify SMTP settings (host: smtp.gmail.com, port: 587)
3. Check network allows port 587
4. Review `email_send_log.csv` for error details

**If BLOCKED**:
1. PII detected in email content
2. Check logs for PII patterns found
3. System attempts auto-scrubbing
4. If scrubbing fails, email is blocked for safety

### Issue: Gemini API Rate Limit

**Symptoms**: "429 Too Many Requests"

**Solutions**:
1. Wait 60 seconds and retry
2. Reduce `TARGET_COUNT`
3. Check Gemini API quota
4. Use fallback (keyword-based summaries)

---

## 🔄 Automation

### GitHub Actions Workflow

**File**: `.github/workflows/weekly_pulse.yml`

**Schedule**:
```yaml
schedule:
  - cron: '30 3 * * 1'  # Monday 9:00 AM IST (3:30 AM UTC)
```

**Manual Trigger**:
1. Go to Actions tab
2. Click "Weekly Product Pulse"
3. Click "Run workflow"
4. Optional: Check "dry run"
5. Click green "Run workflow"

**Environment**:
- Python 3.11
- Ubuntu latest
- All dependencies auto-installed
- Secrets loaded from GitHub

**Artifacts**:
- Stored for 90 days
- Available for download
- Includes all CSVs, JSONs, logs

---

## 📧 Email Output

### HTML Email

**Features**:
- Professional design
- Green accent color (#4CAF50)
- Mobile-responsive (max 600px)
- Inline CSS (email client compatible)
- Emojis: 📊 💬 🎯

**Sections**:
1. Title + metadata
2. Overview box
3. Top themes (3-5)
4. User quotes (3-9)
5. Recommended actions (3)
6. Footer with contact

### Plain Text Email

**Features**:
- ASCII box drawing
- Clean structure
- Works in all clients
- Fallback for HTML

---

## 🎯 Success Metrics

### Pipeline Health

| Metric | Target | Threshold |
|--------|--------|-----------|
| Execution time | <2 min | <5 min |
| Valid reviews | 100+ | 50+ |
| Themes found | 3-5 | 2+ |
| Word count | 200-250 | <250 |
| Email delivery | SENT | Not BLOCKED |

### Quality Indicators

- ✅ No PII in email
- ✅ Diverse themes (not all "Other")
- ✅ Specific actions (not generic)
- ✅ Representative quotes
- ✅ Concise summaries

---

## 🔗 Related Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Local development setup
- **[GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)** - GitHub automation
- **[LAYER3_TESTS.md](LAYER3_TESTS.md)** - Unit test documentation
- **[LAYER2_README.md](LAYER2_README.md)** - Theme extraction details
- **[SCHEDULER_README.md](SCHEDULER_README.md)** - Scheduler configuration

---

## 📞 Support

**Check logs first**:
```bash
# View execution logs
cat email_send_log.csv

# View GitHub Actions logs
# Go to: https://github.com/priyankakakar2020-web/Milestone-2-/actions
```

**Common issues**:
1. Missing environment variables
2. Invalid API keys
3. Network/firewall issues
4. Insufficient reviews
5. PII detection false positives

---

**System Status**: ✅ Production Ready  
**Last Updated**: 2025-12-02  
**Version**: 1.0
