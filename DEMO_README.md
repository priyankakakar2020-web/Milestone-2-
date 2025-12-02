# 🌐 Weekly Pulse Demo - Working Prototype

## Overview

This is a **working web-based demo/prototype** of the Weekly Product Pulse system that you can run locally and share.

**Live Demo URL**: `http://localhost:5000` (when running)

---

## 🚀 Quick Start

### Step 1: Install Flask
```bash
pip install flask
```

### Step 2: Start the Demo Server
```bash
cd c:\Users\Admin\milestone_2
python demo_app.py
```

### Step 3: Open in Browser
Navigate to: **http://localhost:5000**

---

## 📸 Demo Features

### Interactive Web Interface
- ✅ Visual pipeline stages (4 layers)
- ✅ Real-time progress tracking
- ✅ Live status updates
- ✅ Email preview in browser
- ✅ Pipeline statistics dashboard
- ✅ Dry run & full run modes

### What You Can Do
1. **Run Dry Run** - Test pipeline without sending email
2. **See Real-time Progress** - Watch each layer execute
3. **View Statistics** - Reviews collected, themes found, word count
4. **Preview Email** - See generated HTML email in browser
5. **Send Actual Email** - (Optional) Send to real recipient

---

## 🎯 Demo Workflow

### 1. Landing Page
Beautiful gradient interface showing:
- 4 pipeline stages with icons
- Run Demo button (Dry Run - Safe)
- Send Email button (Actual delivery)

### 2. Execution View
Real-time progress display:
- Progress bar (0-100%)
- Current stage (Layer 1-4)
- Status messages
- Live updates every second

### 3. Results Dashboard
After completion:
- **Statistics Cards**:
  - Reviews Collected
  - Themes Found
  - Word Count
  - Execution Time
- **Email Preview** (full HTML email rendered)

---

## 🖥️ Screenshots

### Main Interface
```
┌──────────────────────────────────────────────────────────┐
│          🚀 Weekly Product Pulse                         │
│     Automated Review Analysis & Email Generation Demo    │
├──────────────────────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                 │
│  │ 📥   │  │ 🎯   │  │ ✍️    │  │ 📧   │                 │
│  │Layer1│  │Layer2│  │Layer3│  │Layer4│                 │
│  └──────┘  └──────┘  └──────┘  └──────┘                 │
│                                                          │
│     [▶️ Run Demo (Dry Run)]  [📨 Send Actual Email]      │
│                                                          │
│  Progress: ████████░░░░░░░░░░  40%                      │
│  Layer 2: Extracting themes with ML clustering...       │
└──────────────────────────────────────────────────────────┘
```

### Results View
```
┌──────────────────────────────────────────────────────────┐
│  📊 Pipeline Statistics                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │   106    │ │    5     │ │  238/250 │ │   69s    │   │
│  │ Reviews  │ │  Themes  │ │   Words  │ │   Time   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│                                                          │
│  📧 Generated Email Preview                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Weekly Product Pulse – Groww                       │ │
│  │                                                    │ │
│  │ 📊 Top Themes                                      │ │
│  │ • KYC Verification Delays (45 reviews)            │ │
│  │ • Payment Failures (38 reviews)                   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints

The demo exposes these REST APIs:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main demo interface |
| `/api/run-pipeline` | POST | Start pipeline execution |
| `/api/status` | GET | Get current execution status |
| `/api/preview-email` | GET | Get HTML email preview |
| `/api/download/<filename>` | GET | Download generated files |

### Example API Usage

```javascript
// Start pipeline
fetch('/api/run-pipeline', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({dry_run: true})
});

// Check status
fetch('/api/status')
    .then(r => r.json())
    .then(data => {
        console.log(data.progress); // 0-100
        console.log(data.stage);    // "Layer 1", "Layer 2", etc.
    });
```

---

## 🎨 Customization

### Change Colors
Edit `templates/index.html` CSS:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Change to your brand colors */
```

### Modify Product
Edit `demo_app.py` configuration:
```python
config = {
    'product_name': 'Your Product',
    'app_id': 'com.your.app',
    # ... other settings
}
```

---

## 🌐 Deploying Demo Online

### Option 1: Heroku (Free Tier)
```bash
# Create Procfile
echo "web: python demo_app.py" > Procfile

# Deploy
heroku create your-pulse-demo
git push heroku main
```

### Option 2: PythonAnywhere
1. Upload files to PythonAnywhere
2. Set up Flask app
3. Configure WSGI file
4. Access at: `your-username.pythonanywhere.com`

### Option 3: Replit
1. Import GitHub repo
2. Run `demo_app.py`
3. Share public URL

---

## 🔒 Security Notes

**⚠️ Important for Public Deployment**:

1. **Never expose real credentials** in demo
2. **Disable actual email sending** for public demos
3. **Rate limit API endpoints**
4. **Add authentication** if needed
5. **Use environment variables** for secrets

### Safe Demo Mode
```python
# In demo_app.py, force dry run for public demos
dry_run = True  # Always true for public
```

---

## 🧪 Testing the Demo

### Local Testing
```bash
# Start server
python demo_app.py

# In another terminal, test API
curl http://localhost:5000/api/status
```

### Browser Testing
1. Open http://localhost:5000
2. Click "Run Demo (Dry Run)"
3. Watch progress bar
4. View results
5. Inspect email preview

---

## 📊 Demo Performance

| Metric | Value |
|--------|-------|
| **Startup Time** | < 2 seconds |
| **UI Load Time** | < 500ms |
| **Pipeline Execution** | 50-100 seconds |
| **Memory Usage** | ~500MB |
| **Port** | 5000 (configurable) |

---

## 🔧 Troubleshooting

### Issue: Port 5000 Already in Use

**Solution**: Change port in `demo_app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Use 8080
```

### Issue: Email Preview Not Loading

**Solution**: Run dry run first to generate preview files
```bash
python integrated_pipeline.py --dry-run
```

### Issue: Pipeline Hangs

**Solution**: Check console logs in terminal for errors

---

## 📁 Demo Files

```
milestone_2/
├── demo_app.py              # Flask web server
├── templates/
│   └── index.html          # Web interface
├── integrated_pipeline.py   # Pipeline logic
└── [other pipeline files]
```

---

## 🎯 Use Cases

### 1. **Client Demos**
- Show live system to stakeholders
- Interactive demonstration
- No technical knowledge needed

### 2. **Internal Testing**
- Quick validation
- Visual debugging
- Progress monitoring

### 3. **Training**
- Onboard new team members
- Explain pipeline visually
- Interactive learning

### 4. **Presentations**
- Live demo in meetings
- Impress investors
- Product showcases

---

## 🚀 Next Steps

1. **Start the demo**: `python demo_app.py`
2. **Open browser**: http://localhost:5000
3. **Click Run Demo**: Test the pipeline
4. **View results**: See generated email
5. **Share with team**: Demo the system

---

## 📞 Support

**Demo Issues**:
- Check terminal for error logs
- Verify all dependencies installed
- Ensure port 5000 is available

**Demo Working?**
✅ You should see the web interface  
✅ Pipeline should execute successfully  
✅ Email preview should render

---

**🎉 Your working prototype is ready to demo!**

Access it at: **http://localhost:5000**
