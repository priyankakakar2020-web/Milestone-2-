# Weekly Review Scheduler

## Overview
The scheduler runs the review processing pipeline automatically every week (e.g., Monday 9 AM IST).

## Installation
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables
Set these in PowerShell or your `.env` file:

```powershell
# Product Configuration
[Environment]::SetEnvironmentVariable("APP_ID","com.nextbillion.groww","User")
[Environment]::SetEnvironmentVariable("PRODUCT_NAME","Groww","User")

# Time Window & Target
[Environment]::SetEnvironmentVariable("TIME_WINDOW_WEEKS","12","User")
[Environment]::SetEnvironmentVariable("TARGET_COUNT","100","User")

# Schedule Configuration
[Environment]::SetEnvironmentVariable("SCHEDULE_TIME","09:00","User")
[Environment]::SetEnvironmentVariable("SCHEDULE_DAY","monday","User")
[Environment]::SetEnvironmentVariable("TIMEZONE","Asia/Kolkata","User")

# API Keys (for LLM & Email)
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY","AIzaSyCj0APLH2rm-riDu6au2Hyuinj48liYTuo","User")
[Environment]::SetEnvironmentVariable("SMTP_HOST","smtp.gmail.com","User")
[Environment]::SetEnvironmentVariable("SMTP_PORT","587","User")
[Environment]::SetEnvironmentVariable("SMTP_USER","priyankakakar2020@gmail.com","User")
[Environment]::SetEnvironmentVariable("SMTP_PASS","Desigirl!@#2025","User")
[Environment]::SetEnvironmentVariable("EMAIL_FROM","priyankakakar2020@gmail.com","User")
[Environment]::SetEnvironmentVariable("EMAIL_TO","priyanka.kakar@sattva.co.in","User")
```

## Usage

### Start the Scheduler (Continuous)
Runs in background and executes every week at configured time:
```bash
py run_scheduler.py
```

### Manual Trigger (Run Once Now)
Execute the workflow immediately without waiting for schedule:
```bash
py run_scheduler.py --run-now
```

### Run Without Scheduler (Direct)
Execute the main pipeline once:
```bash
py main.py
```

## Scheduler Features

### 1. Workflow Parameters
- **Product ID**: Which app to scrape (e.g., `com.nextbillion.groww`)
- **Time Window**: How many weeks of reviews to fetch (default: 12)
- **Target Count**: Minimum reviews to collect (default: 100)
- **Language & Country**: Review filtering (default: `en`, `in`)

### 2. Schedule Configuration
- **Day**: monday, tuesday, wednesday, thursday, friday, saturday, sunday
- **Time**: HH:MM format (24-hour, local timezone)
- **Example**: Every Monday at 09:00 IST

### 3. State Tracking
- Records every run in `scheduler_state.json`
- Tracks success/failure rates
- Keeps last 50 run history
- Shows next scheduled run time

### 4. Error Handling
- Logs failures with error messages
- Continues running after failures
- Full stack traces for debugging

## Example Output

```
============================================================
WEEKLY REVIEW SCHEDULER
============================================================

Configuration:
  Product: Groww (com.nextbillion.groww)
  Time Window: 12 weeks
  Target Reviews: 100
  Schedule: Every Monday at 09:00
  Timezone: Asia/Kolkata

Last Run: 2025-11-25T09:00:15.123456
Total Runs: 8
Success Rate: 87.5%

Next Scheduled Run: 2025-12-02T09:00:00

============================================================
Scheduled weekly workflow: Every Monday at 09:00
Next scheduled run: 2025-12-02 09:00:00
Scheduler started (blocking mode). Press Ctrl+C to stop.
```

## Scheduler State File

`scheduler_state.json` tracks:
```json
{
  "last_run": "2025-11-25T09:00:15.123456",
  "next_scheduled_run": "2025-12-02T09:00:00",
  "total_runs": 8,
  "successful_runs": 7,
  "failed_runs": 1,
  "run_history": [
    {
      "timestamp": "2025-11-25T09:00:15.123456",
      "status": "SUCCESS",
      "error_message": ""
    }
  ]
}
```

## Integration with Layer 1

The scheduler is now part of **Layer 1: Data Import & Validation**:

```
Layer 1: Data Import & Validation
├─ Trigger and Scheduling (NEW)
│  └─ WeeklyScheduler (cron-based)
├─ ScraperClient
├─ SchemaValidator
├─ PIIDetector
└─ Deduplicator
```

## Running as Windows Service (Optional)

To run 24/7 in background on Windows:

1. Install `pywin32`:
```bash
pip install pywin32
```

2. Create Windows service or use Task Scheduler:
   - Open Task Scheduler
   - Create Basic Task
   - Trigger: Weekly (Monday 9 AM)
   - Action: Start Program
   - Program: `py`
   - Arguments: `C:\Users\Admin\milestone_2\run_scheduler.py --run-now`

## Notes

- The scheduler uses local system time; ensure your system timezone is set correctly
- For production deployment, consider using GitHub Actions or cloud schedulers (AWS EventBridge, etc.)
- Press `Ctrl+C` to gracefully stop the scheduler
