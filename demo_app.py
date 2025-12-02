"""
Web Demo/Prototype for Weekly Pulse System
A simple Flask web interface to demonstrate the pipeline
"""

from flask import Flask, render_template, jsonify, request, send_file
import json
import os
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Store execution status
execution_status = {
    'running': False,
    'progress': 0,
    'stage': '',
    'message': '',
    'result': None,
    'error': None
}


@app.route('/')
def index():
    """Main demo page."""
    return render_template('index.html')


@app.route('/api/run-pipeline', methods=['POST'])
def run_pipeline():
    """Run the pipeline in background."""
    global execution_status
    
    if execution_status['running']:
        return jsonify({'error': 'Pipeline already running'}), 400
    
    # Get parameters
    data = request.json
    dry_run = data.get('dry_run', True)
    
    # Reset status
    execution_status = {
        'running': True,
        'progress': 0,
        'stage': 'Starting',
        'message': 'Initializing pipeline...',
        'result': None,
        'error': None
    }
    
    # Run pipeline in background thread
    thread = threading.Thread(target=execute_pipeline, args=(dry_run,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})


@app.route('/api/status')
def get_status():
    """Get current execution status."""
    return jsonify(execution_status)


@app.route('/api/preview-email')
def preview_email():
    """Get email preview."""
    try:
        with open('preview_email.html', 'r', encoding='utf-8') as f:
            html = f.read()
        return html
    except FileNotFoundError:
        return '<p>No preview available. Run the pipeline first.</p>', 404


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated files."""
    allowed_files = ['weekly_pulse', 'preview_email', 'email_send_log']
    
    # Check if filename is allowed
    if not any(allowed in filename for allowed in allowed_files):
        return jsonify({'error': 'File not allowed'}), 403
    
    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


def execute_pipeline(dry_run=True):
    """Execute the pipeline and update status."""
    global execution_status
    
    try:
        from integrated_pipeline import IntegratedPulsePipeline
        
        # Layer 1
        execution_status.update({
            'progress': 10,
            'stage': 'Layer 1',
            'message': 'Fetching and validating reviews...'
        })
        time.sleep(1)  # Simulate processing
        
        # Layer 2
        execution_status.update({
            'progress': 40,
            'stage': 'Layer 2',
            'message': 'Extracting themes with ML clustering...'
        })
        time.sleep(1)
        
        # Layer 3
        execution_status.update({
            'progress': 70,
            'stage': 'Layer 3',
            'message': 'Generating pulse content with LLM...'
        })
        time.sleep(1)
        
        # Initialize pipeline
        pipeline = IntegratedPulsePipeline()
        
        # Layer 4
        execution_status.update({
            'progress': 85,
            'stage': 'Layer 4',
            'message': 'Rendering email template...'
        })
        
        # Run pipeline
        result = pipeline.run(dry_run=dry_run)
        
        # Complete
        execution_status.update({
            'running': False,
            'progress': 100,
            'stage': 'Complete',
            'message': 'Pipeline completed successfully!',
            'result': {
                'status': result['status'],
                'execution_time': result.get('execution_time', 0),
                'stats': result.get('stats', {}),
                'pulse_document': result.get('pulse_document', {})
            }
        })
        
    except Exception as e:
        execution_status.update({
            'running': False,
            'progress': 0,
            'stage': 'Error',
            'message': f'Pipeline failed: {str(e)}',
            'error': str(e)
        })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 WEEKLY PULSE DEMO SERVER")
    print("="*60)
    print("\nStarting web demo on: http://localhost:5000")
    print("\nOpen your browser and navigate to:")
    print("  👉 http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
