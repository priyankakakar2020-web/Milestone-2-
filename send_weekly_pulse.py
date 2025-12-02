"""
Integrated script to send weekly pulse email with full Layer 4 integration.
Includes Gmail SMTP, PII scrubbing, and detailed logging.
"""

import os
import sys
import json
import re
import csv
from datetime import datetime
from typing import Dict
from layer4_distribution import (
    EmailTemplateRenderer,
    PIIFinalCheck,
    DeliverySystem,
    Layer4Pipeline
)


class PIIScrubber:
    """Final PII scrubber with masking capability."""
    
    @staticmethod
    def scrub_and_mask(text: str) -> str:
        """
        Remove or mask PII patterns from text.
        
        Args:
            text: Input text
            
        Returns:
            Scrubbed text with PII masked
        """
        # Mask emails
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '***@***.***', text)
        
        # Mask phone numbers
        text = re.sub(r'\+91-\d{10}', '+91-**********', text)
        text = re.sub(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '***-***-****', text)
        
        # Mask long digit sequences (account IDs)
        text = re.sub(r'\b\d{10,}\b', '**********', text)
        
        # Mask names with titles
        text = re.sub(r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+', 'Mr./Ms. ***', text, flags=re.IGNORECASE)
        
        return text


class SendLogger:
    """Log email send status for traceability."""
    
    def __init__(self, log_file: str = 'email_send_log.csv'):
        """
        Initialize send logger.
        
        Args:
            log_file: Path to CSV log file
        """
        self.log_file = log_file
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create log file with headers if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'week_start',
                    'week_end',
                    'subject',
                    'recipient',
                    'status',
                    'attempts',
                    'error_message',
                    'pii_clean'
                ])
    
    def log_send(self,
                 week_start: str,
                 week_end: str,
                 subject: str,
                 recipient: str,
                 status: str,
                 attempts: int = 1,
                 error_message: str = '',
                 pii_clean: bool = True):
        """
        Log email send attempt.
        
        Args:
            week_start: Week start date
            week_end: Week end date
            subject: Email subject
            recipient: Recipient email
            status: Send status (SENT, ERROR, BLOCKED)
            attempts: Number of send attempts
            error_message: Error message if failed
            pii_clean: Whether PII check passed
        """
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                week_start,
                week_end,
                subject,
                recipient,
                status,
                attempts,
                error_message,
                pii_clean
            ])
        
        print(f"\n✓ Logged send status to {self.log_file}")


def send_pulse_email(pulse_document: Dict,
                    recipient: str = None,
                    sender: str = None,
                    password: str = None,
                    dry_run: bool = False) -> Dict:
    """
    Send weekly pulse email with full safety checks and logging.
    
    Args:
        pulse_document: Pulse document from Layer 3
        recipient: Recipient email (default: EMAIL_TO env var)
        sender: Sender email (default: EMAIL_SENDER env var)
        password: Email password (default: EMAIL_PASSWORD env var)
        dry_run: If True, only render and check but don't send
        
    Returns:
        Send report dict
    """
    # Load credentials from environment
    recipient = recipient or os.getenv('EMAIL_TO', 'priyanka.kakar@sattva.co.in')
    sender = sender or os.getenv('EMAIL_SENDER', 'priyankakakar2020@gmail.com')
    password = password or os.getenv('EMAIL_PASSWORD', 'Desigirl!@#2025')
    
    metadata = pulse_document.get('metadata', {})
    week_start = metadata.get('week_start', '')
    week_end = metadata.get('week_end', '')
    
    print("="*60)
    print("WEEKLY PULSE EMAIL DELIVERY")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  From: {sender}")
    print(f"  To: {recipient}")
    print(f"  Week: {week_start} to {week_end}")
    print(f"  Dry Run: {dry_run}")
    print()
    
    # Initialize logger
    logger = SendLogger()
    
    # Step 1: Render email templates
    print("Step 1: Rendering email templates...")
    renderer = EmailTemplateRenderer()
    html_body = renderer.render_html(pulse_document)
    plain_body = renderer.render_plain_text(pulse_document)
    print(f"  ✓ HTML: {len(html_body)} chars")
    print(f"  ✓ Plain: {len(plain_body)} chars")
    
    # Step 2: PII Final Check
    print("\nStep 2: Performing final PII check...")
    checker = PIIFinalCheck()
    is_clean, pii_report = checker.verify_email(html_body, plain_body)
    
    if not is_clean:
        print("  ⚠ PII detected! Attempting to scrub...")
        print(f"    HTML PII: {pii_report['html_pii_found'][:3]}")
        print(f"    Plain PII: {pii_report['plain_pii_found'][:3]}")
        
        # Scrub PII
        scrubber = PIIScrubber()
        html_body = scrubber.scrub_and_mask(html_body)
        plain_body = scrubber.scrub_and_mask(plain_body)
        
        # Re-check
        is_clean_after, pii_report_after = checker.verify_email(html_body, plain_body)
        
        if not is_clean_after:
            print("  ✗ PII still present after scrubbing. Blocking send.")
            
            logger.log_send(
                week_start=week_start,
                week_end=week_end,
                subject=pulse_document.get('title', 'Weekly Pulse'),
                recipient=recipient,
                status='BLOCKED',
                error_message='PII detected and could not be scrubbed',
                pii_clean=False
            )
            
            return {
                'status': 'BLOCKED',
                'reason': 'PII detected after scrubbing',
                'pii_report': pii_report_after
            }
        else:
            print("  ✓ PII successfully scrubbed")
    else:
        print("  ✓ No PII detected")
    
    # Dry run exit
    if dry_run:
        print("\n✓ Dry run complete. Skipping actual send.")
        
        # Save rendered emails for inspection
        with open('preview_email.html', 'w', encoding='utf-8') as f:
            f.write(html_body)
        with open('preview_email.txt', 'w', encoding='utf-8') as f:
            f.write(plain_body)
        
        print("  Saved preview: preview_email.html, preview_email.txt")
        
        return {
            'status': 'DRY_RUN',
            'pii_clean': True,
            'preview_saved': True
        }
    
    # Step 3: Send email via Gmail SMTP
    print("\nStep 3: Sending email via Gmail SMTP...")
    
    subject = pulse_document.get('title', 'Weekly Product Pulse')
    
    delivery = DeliverySystem(
        smtp_host='smtp.gmail.com',
        smtp_port=587,
        smtp_user=sender,
        smtp_pass=password,
        max_retries=3,
        retry_delay=5
    )
    
    status, error, send_metadata = delivery.send_email(
        to_addr=recipient,
        from_addr=sender,
        subject=subject,
        html_body=html_body,
        plain_body=plain_body,
        track_open=True
    )
    
    # Step 4: Log send status
    print("\nStep 4: Logging send status...")
    
    logger.log_send(
        week_start=week_start,
        week_end=week_end,
        subject=subject,
        recipient=recipient,
        status=status,
        attempts=send_metadata.get('attempts', 1),
        error_message=error,
        pii_clean=True
    )
    
    # Final report
    print("\n" + "="*60)
    if status == 'SENT':
        print("✓ EMAIL SENT SUCCESSFULLY")
        print("="*60)
        print(f"  Subject: {subject}")
        print(f"  To: {recipient}")
        print(f"  Sent at: {send_metadata.get('sent_at')}")
        print(f"  Attempts: {send_metadata.get('attempts')}")
    else:
        print("✗ EMAIL SEND FAILED")
        print("="*60)
        print(f"  Status: {status}")
        print(f"  Error: {error}")
        print(f"  Attempts: {send_metadata.get('attempts')}")
    print("="*60)
    
    return {
        'status': status,
        'error': error,
        'metadata': send_metadata,
        'pii_clean': True,
        'subject': subject,
        'recipient': recipient
    }


if __name__ == "__main__":
    # Example usage: load pulse document and send
    
    # Check for dry run flag
    dry_run = '--dry-run' in sys.argv
    
    # Try to load a recent pulse document
    import glob
    pulse_files = glob.glob('weekly_pulse_*.json')
    
    if not pulse_files:
        print("Error: No pulse document found. Run Layer 3 first.")
        sys.exit(1)
    
    # Load most recent pulse
    latest_pulse_file = sorted(pulse_files)[-1]
    print(f"Loading pulse document: {latest_pulse_file}")
    
    with open(latest_pulse_file, 'r', encoding='utf-8') as f:
        pulse_document = json.load(f)
    
    # Send email
    result = send_pulse_email(
        pulse_document=pulse_document,
        dry_run=dry_run
    )
    
    # Exit with appropriate code
    if result['status'] in ['SENT', 'DRY_RUN']:
        sys.exit(0)
    else:
        sys.exit(1)
