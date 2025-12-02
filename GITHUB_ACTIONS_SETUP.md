# GitHub Actions Setup Guide

## ✅ Step 1: Push to GitHub - COMPLETE

Code successfully pushed to: https://github.com/priyankakakar2020-web/Milestone-2-

**Commit**: `6dbbc35` - "Add GitHub Actions automation for weekly pulse system"

**Files Pushed**:
- ✅ `.github/workflows/weekly_pulse.yml` - GitHub Actions workflow
- ✅ All 4 layers (layer1_import.py, layer2_themes.py, layer3_content.py, layer4_distribution.py)
- ✅ Full pipeline (run_full_pipeline.py, send_weekly_pulse.py)
- ✅ Test files (test_layer1.py, test_layer2.py, test_layer3.py, test_layer4.py)
- ✅ Documentation (SETUP_GUIDE.md, LAYER2_README.md, LAYER3_TESTS.md, SCHEDULER_README.md)
- ✅ .gitignore (protects .env and sensitive files)

---

## 🔐 Step 2: Add GitHub Secrets

### Navigate to Secrets Settings

1. **Go to your repository**:
   - https://github.com/priyankakakar2020-web/Milestone-2-

2. **Click on "Settings"** (top menu bar)

3. **In left sidebar, expand "Secrets and variables"**

4. **Click "Actions"**

5. **Click "New repository secret"** (green button)

---

### Add Secret 1: GEMINI_API_KEY

1. **Name**: `GEMINI_API_KEY`
2. **Secret**: `AIzaSyCj0APLH2rm-riDu6au2Hyuinj48liYTuo`
3. Click **"Add secret"**

---

### Add Secret 2: EMAIL_SENDER

1. Click **"New repository secret"** again
2. **Name**: `EMAIL_SENDER`
3. **Secret**: `priyankakakar2020@gmail.com`
4. Click **"Add secret"**

---

### Add Secret 3: EMAIL_PASSWORD

1. Click **"New repository secret"** again
2. **Name**: `EMAIL_PASSWORD`
3. **Secret**: `ahqkwttcctloaokx`
4. Click **"Add secret"**

---

### Verify Secrets Added

You should see 3 secrets in the list:
```
✓ GEMINI_API_KEY        Updated now
✓ EMAIL_SENDER          Updated now  
✓ EMAIL_PASSWORD        Updated now
```

---

## 🚀 Step 3: Test GitHub Actions

### Option A: Manual Trigger (Recommended First)

1. **Go to "Actions" tab** in your repository

2. **Click "Weekly Product Pulse"** workflow (left sidebar)

3. **Click "Run workflow"** (right side)

4. **Optional**: Check "Dry run" for preview without sending

5. **Click green "Run workflow"** button

6. **Wait 2-5 minutes** for workflow to complete

7. **Check status**:
   - ✅ Green checkmark = Success
   - ❌ Red X = Failed (click to see logs)

### Option B: Wait for Scheduled Run

The workflow will automatically run:
- **Every Monday at 9:00 AM IST** (3:30 AM UTC)

---

## 📊 Step 4: Monitor Workflow Execution

### View Workflow Logs

1. Go to **"Actions"** tab

2. Click on the workflow run (e.g., "Add GitHub Actions automation")

3. Click on **"generate-and-send-pulse"** job

4. Expand steps to see detailed logs:
   ```
   ✓ Checkout code
   ✓ Set up Python
   ✓ Install dependencies
   ✓ Configure environment
   ✓ Run full pipeline (Layers 1-3)
   ✓ Send weekly pulse email (Layer 4)
   ✓ Upload artifacts
   ```

### Download Artifacts

After workflow completes:

1. Scroll to bottom of workflow run page

2. Click **"weekly-pulse-outputs"** artifact

3. Downloads a ZIP containing:
   - `reviews_week_*.csv` - Enriched reviews
   - `weekly_pulse_*.json` - Generated pulse document
   - `email_send_log.csv` - Delivery log
   - `preview_email.html` - Email preview (if dry run)

**Retention**: 90 days

---

## 🔍 Step 5: Verify Email Delivery

### Check Recipient Inbox

1. **Login to**: https://mail.google.com/

2. **Account**: priyanka.kakar@sattva.co.in

3. **Look for email**:
   - **Subject**: "Weekly Product Pulse – Groww"
   - **From**: priyankakakar2020@gmail.com
   - **Received**: Within 5 minutes of workflow completion

### Email Should Contain

- 📊 **Top Themes** (max 5 themes with sizes)
- 💬 **User Feedback** (representative quotes)
- 🎯 **Recommended Actions** (3 specific actions)
- **Metadata** (week dates, review count)
- **Professional HTML design** (green accents, mobile-friendly)

---

## 🛠️ Troubleshooting

### Issue: Workflow Fails on "Install dependencies"

**Cause**: Missing dependencies in requirements.txt

**Solution**: Check requirements.txt includes:
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

### Issue: Workflow Fails on "Configure environment"

**Cause**: GitHub Secrets not set correctly

**Solution**:
1. Go to Settings → Secrets and variables → Actions
2. Verify all 3 secrets exist: `GEMINI_API_KEY`, `EMAIL_SENDER`, `EMAIL_PASSWORD`
3. Re-create any missing secrets

---

### Issue: Email Not Sent (PII Blocked)

**Cause**: PII detected in email content

**Solution**: Check workflow logs for:
```
⚠ PII detected! Attempting to scrub...
✗ PII still present after scrubbing. Blocking send.
```

Email is blocked for safety. Review quotes and summaries for:
- Email addresses
- Phone numbers
- Long digit sequences
- Names with titles (Mr./Mrs./Ms./Dr.)

---

### Issue: Email Sent but Not Received

**Cause**: SMTP authentication failed or email in spam

**Solution**:
1. Check workflow logs for "Email sent successfully"
2. Check spam/junk folder in recipient inbox
3. Verify App Password is correct in GitHub Secrets
4. Check `email_send_log.csv` artifact for status

---

### Issue: Workflow Times Out

**Cause**: Too many reviews to process or LLM API slow

**Solution**:
1. Reduce `TARGET_COUNT` in workflow (default: 100)
2. Reduce `TIME_WINDOW_WEEKS` (default: 12)
3. Check Gemini API quota

---

## 📅 Workflow Schedule

### Current Schedule
```yaml
schedule:
  - cron: '30 3 * * 1'  # Every Monday at 3:30 AM UTC (9:00 AM IST)
```

### Modify Schedule

Edit `.github/workflows/weekly_pulse.yml`:

```yaml
# Daily at 9 AM IST
- cron: '30 3 * * *'

# Every Friday at 6 PM IST
- cron: '30 12 * * 5'

# First day of month at 9 AM IST
- cron: '30 3 1 * *'
```

**Cron Format**: `minute hour day month weekday`

**Note**: GitHub uses UTC timezone (IST = UTC + 5:30)

---

## 🎯 Success Checklist

- ✅ Code pushed to GitHub
- ✅ GitHub Secrets added (3 secrets)
- ✅ Workflow triggered manually
- ✅ All steps completed successfully
- ✅ Email received in inbox
- ✅ Artifacts downloaded and verified
- ✅ `email_send_log.csv` shows SENT status
- ✅ Scheduled runs configured

---

## 📈 Next Steps

### 1. Monitor First Scheduled Run

Wait until next Monday at 9:00 AM IST to verify automatic execution.

### 2. Customize Workflow

Edit `.github/workflows/weekly_pulse.yml` to:
- Change schedule
- Add more recipients
- Adjust review count/time window
- Enable/disable dry run

### 3. Set Up Notifications

Enable email notifications for workflow failures:
1. Settings → Notifications
2. Check "Send notifications for failed workflows"

### 4. Add More Features

- Multiple recipients (CC/BCC)
- Slack/Teams integration
- Custom email templates
- A/B testing for themes
- Sentiment analysis trends

---

## 🔗 Quick Links

- **Repository**: https://github.com/priyankakakar2020-web/Milestone-2-
- **Actions**: https://github.com/priyankakakar2020-web/Milestone-2-/actions
- **Secrets**: https://github.com/priyankakakar2020-web/Milestone-2-/settings/secrets/actions
- **Workflow File**: `.github/workflows/weekly_pulse.yml`

---

## 📞 Support

If you encounter issues:
1. Check workflow logs in Actions tab
2. Review troubleshooting section above
3. Check `email_send_log.csv` artifact
4. Verify GitHub Secrets are correct

---

**Status**: ✅ Ready for Production  
**Next Run**: Monday, 9:00 AM IST (Automatic)
