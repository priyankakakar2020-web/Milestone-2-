# Complete Testing Guide

## 🧪 How to Test the Weekly Pulse System

This guide covers all testing methods from individual components to full end-to-end pipeline.

---

## 📋 Quick Test Options

| Test Type | Command | Time | Safe? |
|-----------|---------|------|-------|
| **Dry Run (Recommended First)** | `py integrated_pipeline.py --dry-run` | 2-3 min | ✅ No email sent |
| **Full Local Test** | `py integrated_pipeline.py` | 2-3 min | ⚠️ Sends email |
| **Individual Layer Tests** | `py test_layer3.py` | 10 sec | ✅ No email |
| **GitHub Actions Dry Run** | Manual trigger + check dry run | 3-5 min | ✅ No email sent |
| **GitHub Actions Full Test** | Manual trigger | 3-5 min | ⚠️ Sends email |

---

## 🎯 Recommended Testing Sequence

### **Step 1: Test Individual Layers (5 minutes)**

Test each layer independently to verify components work:

```bash
# Test Layer 1: Data Import & Validation
py test_layer1.py

# Test Layer 2: Theme Extraction & Classification  
py test_layer2.py

# Test Layer 3: Content Generation
py test_layer3.py

# Test Layer 4: Distribution & Feedback
py test_layer4.py
```

**Expected Output**: All tests should pass with ✓ marks

**What it validates**:
- Layer 1: Scraping, validation, deduplication
- Layer 2: Embeddings, clustering, theme labeling
- Layer 3: Quote extraction, summarization, action generation
- Layer 4: Email rendering, PII detection, delivery system

---

### **Step 2: Dry Run - Integrated Pipeline (2-3 minutes)**

Run the full pipeline WITHOUT sending email:

```bash
cd c:\Users\Admin\milestone_2
py integrated_pipeline.py --dry-run
```

**Expected Output**:
```
======================================================================
STARTING 4-LAYER INTEGRATED PULSE PIPELINE
======================================================================
Product: Groww (com.nextbillion.groww)
Time Window: 12 weeks
Target Reviews: 100
Dry Run: True
======================================================================

======================================================================
LAYER 1: DATA IMPORT & VALIDATION
======================================================================
Fetching reviews from 2025-09-09 to 2025-11-25
Progress: 106/100 valid reviews
✓ Layer 1 completed in 45.2s
✓ Valid reviews: 106

======================================================================
LAYER 2: THEME EXTRACTION & CLASSIFICATION
======================================================================
Generating embeddings for 106 reviews
Clustering with HDBSCAN
✓ Layer 2 completed in 12.8s
✓ Themes identified: 5

======================================================================
LAYER 3: CONTENT GENERATION
======================================================================
Extracting quotes per theme
Generating theme summaries
Generating action ideas
✓ Layer 3 completed in 8.5s
✓ Word count: 238/250

======================================================================
LAYER 4: DISTRIBUTION & FEEDBACK
======================================================================
Rendering email templates
PII check: ✓ Passed
✓ Dry run complete. Skipping actual send.
✓ Layer 4 completed in 3.1s

======================================================================
PIPELINE EXECUTION COMPLETE
======================================================================
Total execution time: 69.6s
  Layer 1: 45.2s
  Layer 2: 12.8s
  Layer 3: 8.5s
  Layer 4: 3.1s
======================================================================

✓ Pipeline executed successfully!
```

**What it validates**:
- ✅ All 4 layers execute without errors
- ✅ Reviews are fetched and validated
- ✅ Themes are discovered
- ✅ Pulse document is generated
- ✅ Email is rendered (saved as preview)
- ✅ NO email is sent

**Files Generated**:
- `weekly_pulse_YYYY_MM_DD.json` - Pulse document
- `preview_email.html` - HTML email preview
- `preview_email.txt` - Plain text preview

**Inspect Preview**:
```bash
# Open HTML preview in browser
start preview_email.html

# View plain text
type preview_email.txt
```

---

### **Step 3: Full Local Test (2-3 minutes)**

Run the complete pipeline WITH email delivery:

```bash
cd c:\Users\Admin\milestone_2
py integrated_pipeline.py
```

**Expected Output**: Same as dry run, but with actual email sending:
```
======================================================================
LAYER 4: DISTRIBUTION & FEEDBACK
======================================================================
Rendering email templates
  ✓ HTML: 4732 chars
  ✓ Plain: 1802 chars

PII check: ✓ Passed

Sending email via Gmail SMTP...
  Sending email (attempt 1/3)...
  ✓ Email sent successfully on attempt 1

Logging send status...
  ✓ Logged send status to email_send_log.csv

======================================================================
✓ EMAIL SENT SUCCESSFULLY
======================================================================
  Subject: Weekly Product Pulse – Groww
  To: priyanka.kakar@sattva.co.in
  Sent at: 2025-12-02T22:15:30
  Attempts: 1
======================================================================
```

**What it validates**:
- ✅ Complete pipeline execution
- ✅ Email successfully sent via Gmail SMTP
- ✅ Delivery logged

**Verify Email Received**:
1. Check inbox: priyanka.kakar@sattva.co.in
2. Subject: "Weekly Product Pulse – Groww"
3. Verify HTML email renders correctly
4. Check themes, quotes, actions are present

**Check Logs**:
```bash
# View delivery log
type email_send_log.csv
```

---

### **Step 4: GitHub Actions Dry Run Test (3-5 minutes)**

Test the automated workflow WITHOUT sending email:

#### **A. Navigate to GitHub Actions**
1. Go to: https://github.com/priyankakakar2020-web/Milestone-2-/actions
2. Click **"Weekly Product Pulse"** (left sidebar)
3. Click **"Run workflow"** button (right side)

#### **B. Configure Test Run**
1. Branch: `main` ✓
2. Check ☑️ **"Dry run (preview without sending)"**
3. Click green **"Run workflow"** button

#### **C. Monitor Execution**
1. Wait 5-10 seconds for run to appear
2. Click on the workflow run (e.g., "Manual workflow trigger")
3. Click **"generate-and-send-pulse"** job
4. Watch real-time logs

**Expected Steps**:
```
✓ Checkout code
✓ Set up Python
✓ Install dependencies
✓ Configure environment
✓ Run integrated 4-layer pipeline
  - Dry run mode: Preview without sending
  - Layer 1: Data import
  - Layer 2: Theme extraction
  - Layer 3: Content generation
  - Layer 4: Email rendering (not sent)
✓ Upload artifacts
```

#### **D. Download Artifacts**
1. Scroll to bottom of workflow run page
2. Click **"weekly-pulse-outputs"** ZIP file
3. Extract and inspect:
   - `weekly_pulse_*.json` - Generated pulse
   - `preview_email.html` - Email preview
   - `preview_email.txt` - Plain text version

**What it validates**:
- ✅ GitHub Actions workflow executes
- ✅ Secrets are loaded correctly
- ✅ All dependencies install
- ✅ Pipeline runs in cloud environment
- ✅ Artifacts are saved
- ✅ NO email is sent

---

### **Step 5: GitHub Actions Full Test (3-5 minutes)**

Test the automated workflow WITH email delivery:

#### **A. Trigger Workflow**
1. Go to: https://github.com/priyankakakar2020-web/Milestone-2-/actions
2. Click **"Weekly Product Pulse"**
3. Click **"Run workflow"**
4. **DO NOT** check "Dry run" (leave unchecked)
5. Click green **"Run workflow"**

#### **B. Verify Execution**
Watch logs for successful email delivery:
```
✓ Run integrated 4-layer pipeline
  - Production mode: Full pipeline with email delivery
  - Layer 1: Fetched 106 reviews
  - Layer 2: Identified 5 themes
  - Layer 3: Generated 238-word pulse
  - Layer 4: Email sent successfully
  - Status: SENT
  - Attempts: 1
```

#### **C. Verify Email Delivery**
1. Check inbox: priyanka.kakar@sattva.co.in
2. Email should arrive within 1-2 minutes
3. Subject: "Weekly Product Pulse – Groww"
4. Verify content looks correct

#### **D. Check Logs in Artifacts**
1. Download **"weekly-pulse-outputs"** artifact
2. Open `email_send_log.csv`
3. Verify last entry shows `status=SENT`

**What it validates**:
- ✅ Complete end-to-end automation
- ✅ GitHub Secrets work correctly
- ✅ Email delivery from cloud
- ✅ Weekly schedule is configured

---

## 🔍 Detailed Component Testing

### **Test Email Rendering Only**

```bash
# Generate sample email without full pipeline
py -c "from layer4_distribution import EmailTemplateRenderer; from generate_layer3_json import *; renderer = EmailTemplateRenderer(); import json; pulse = json.load(open('layer3_output.json')); html = renderer.render_html(pulse); open('test_email.html', 'w', encoding='utf-8').write(html); print('✓ Email rendered: test_email.html')"

# View rendered email
start test_email.html
```

---

### **Test PII Detection**

```bash
# Test PII patterns
py -c "from layer4_distribution import PIIFinalCheck; text = 'Contact me at john@example.com or +91-9876543210'; has_pii, found = PIIFinalCheck.check(text); print(f'PII detected: {has_pii}'); print(f'Found: {found}')"
```

**Expected Output**:
```
PII detected: True
Found: ['EMAIL: john@example.com', 'PHONE: +91-9876543210']
```

---

### **Test Theme Clustering**

```bash
# Run Layer 2 test to see themes
py test_layer2.py
```

---

### **Test Quote Extraction**

```bash
# Run Layer 3 test to see quotes
py test_layer3.py
```

---

## 🛠️ Troubleshooting Tests

### **Issue: "No reviews collected"**

**Cause**: Date range or filters too restrictive

**Fix**:
```bash
# Temporarily reduce filters
$env:MIN_REVIEW_LENGTH = "50"
$env:TIME_WINDOW_WEEKS = "24"
py integrated_pipeline.py --dry-run
```

---

### **Issue: "Email not sent"**

**Cause**: SMTP credentials incorrect

**Fix**:
```bash
# Verify environment variables
py -c "import os; print('EMAIL_SENDER:', os.getenv('EMAIL_SENDER')); print('EMAIL_PASSWORD:', '***' if os.getenv('EMAIL_PASSWORD') else 'NOT SET')"

# Re-set if needed
$env:EMAIL_SENDER = "priyankakakar2020@gmail.com"
$env:EMAIL_PASSWORD = "ahqkwttcctloaokx"
```

---

### **Issue: "Gemini API error"**

**Cause**: API key invalid or quota exceeded

**Fix**:
```bash
# Verify API key
py -c "import os; print('GEMINI_API_KEY:', os.getenv('GEMINI_API_KEY')[:10] + '...' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"

# Re-set if needed
$env:GEMINI_API_KEY = "AIzaSyCj0APLH2rm-riDu6au2Hyuinj48liYTuo"
```

---

### **Issue: GitHub Actions fails on dependencies**

**Cause**: Missing or conflicting dependencies

**Fix**: Check `requirements.txt` includes:
```
google-play-scraper
pandas
google-generativeai
sentence-transformers
hdbscan
scikit-learn
schedule
```

---

## ✅ Testing Checklist

Use this checklist to ensure complete testing:

### Local Testing
- [ ] Layer 1 test passed (`py test_layer1.py`)
- [ ] Layer 2 test passed (`py test_layer2.py`)
- [ ] Layer 3 test passed (`py test_layer3.py`)
- [ ] Layer 4 test passed (`py test_layer4.py`)
- [ ] Dry run successful (`py integrated_pipeline.py --dry-run`)
- [ ] HTML preview looks correct (`preview_email.html`)
- [ ] Full test sent email (`py integrated_pipeline.py`)
- [ ] Email received in inbox

### GitHub Actions Testing
- [ ] GitHub Secrets added (3 secrets)
- [ ] Workflow dry run successful
- [ ] Artifacts downloaded and verified
- [ ] Workflow full test successful
- [ ] Email received from automated run
- [ ] Delivery log shows SENT status

### Production Readiness
- [ ] All tests passing
- [ ] Email template looks professional
- [ ] No PII in emails
- [ ] Themes are relevant
- [ ] Actions are specific
- [ ] Word count under 250
- [ ] Scheduled run configured (Monday 9 AM IST)

---

## 🎯 Quick Test Commands Reference

```bash
# Individual layer tests (safe)
py test_layer1.py
py test_layer2.py
py test_layer3.py
py test_layer4.py

# Integrated pipeline tests
py integrated_pipeline.py --dry-run    # Safe: No email
py integrated_pipeline.py              # Sends email

# Check environment
py -c "import os; print('EMAIL_SENDER:', os.getenv('EMAIL_SENDER')); print('GEMINI_API_KEY:', os.getenv('GEMINI_API_KEY')[:10] + '...' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"

# View logs
type email_send_log.csv

# Open email preview
start preview_email.html
```

---

## 📞 Support

If tests fail:
1. Check error messages in console
2. Review troubleshooting section above
3. Verify environment variables are set
4. Check `email_send_log.csv` for details
5. Review GitHub Actions logs

---

**Remember**: Always start with **dry run** testing before sending actual emails!
