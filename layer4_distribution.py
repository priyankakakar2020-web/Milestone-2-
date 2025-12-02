"""
Layer 4: Distribution & Feedback
- Email Template Renderer (HTML + plain text)
- PII Final Check (double-verification)
- Delivery System (with retry logic)
- Read Receipt Tracker (optional)
"""

import os
import re
import json
import smtplib
import time
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailTemplateRenderer:
    """Render pulse document as HTML and plain text email."""
    
    @staticmethod
    def render_html(pulse_document: Dict) -> str:
        """
        Render pulse document as HTML email.
        
        Args:
            pulse_document: Pulse document from Layer 3
            
        Returns:
            HTML string
        """
        title = pulse_document.get('title', 'Weekly Product Pulse')
        overview = pulse_document.get('overview', '')
        themes = pulse_document.get('themes', [])
        quotes = pulse_document.get('quotes', [])
        actions = pulse_document.get('actions', [])
        metadata = pulse_document.get('metadata', {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a1a1a;
            font-size: 24px;
            margin-bottom: 10px;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .meta {{
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        .overview {{
            background-color: #f9f9f9;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin: 20px 0;
            font-size: 15px;
        }}
        h2 {{
            color: #2c3e50;
            font-size: 18px;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        .theme {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #fafafa;
            border-radius: 5px;
        }}
        .theme-name {{
            font-weight: 600;
            color: #2c3e50;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        .theme-size {{
            color: #666;
            font-size: 13px;
            font-style: italic;
        }}
        .theme-summary {{
            margin-top: 8px;
            color: #444;
        }}
        .quote {{
            border-left: 3px solid #ddd;
            padding-left: 15px;
            margin: 10px 0;
            font-style: italic;
            color: #555;
        }}
        .action {{
            margin: 10px 0;
            padding: 12px;
            background-color: #e8f5e9;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }}
        .action-number {{
            font-weight: 600;
            color: #2e7d32;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 13px;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="meta">
            {metadata.get('product', 'Product')} | 
            {metadata.get('week_start', '')} to {metadata.get('week_end', '')} | 
            {metadata.get('total_reviews', 0)} reviews analyzed
        </div>
        
        <div class="overview">
            {overview}
        </div>
        
        <h2>📊 Top Themes</h2>
"""
        
        # Add themes
        for theme in themes:
            html += f"""
        <div class="theme">
            <div class="theme-name">{theme['name']}</div>
            <div class="theme-size">{theme['size']} reviews</div>
            <div class="theme-summary">{theme['summary']}</div>
        </div>
"""
        
        # Add quotes
        html += """
        <h2>💬 User Feedback</h2>
"""
        for quote in quotes:
            html += f"""
        <div class="quote">"{quote}"</div>
"""
        
        # Add actions
        html += """
        <h2>🎯 Recommended Actions</h2>
"""
        for i, action in enumerate(actions, 1):
            html += f"""
        <div class="action">
            <span class="action-number">{i}.</span> {action}
        </div>
"""
        
        # Footer
        html += f"""
        <div class="footer">
            <p>This pulse was generated automatically from user feedback analysis.</p>
            <p>Questions or feedback? Reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    @staticmethod
    def render_plain_text(pulse_document: Dict) -> str:
        """
        Render pulse document as plain text email.
        
        Args:
            pulse_document: Pulse document from Layer 3
            
        Returns:
            Plain text string
        """
        title = pulse_document.get('title', 'Weekly Product Pulse')
        overview = pulse_document.get('overview', '')
        themes = pulse_document.get('themes', [])
        quotes = pulse_document.get('quotes', [])
        actions = pulse_document.get('actions', [])
        metadata = pulse_document.get('metadata', {})
        
        lines = []
        lines.append("=" * 60)
        lines.append(title)
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"{metadata.get('product', 'Product')} | {metadata.get('week_start', '')} to {metadata.get('week_end', '')}")
        lines.append(f"{metadata.get('total_reviews', 0)} reviews analyzed")
        lines.append("")
        lines.append("-" * 60)
        lines.append("OVERVIEW")
        lines.append("-" * 60)
        lines.append(overview)
        lines.append("")
        
        # Themes
        lines.append("-" * 60)
        lines.append("TOP THEMES")
        lines.append("-" * 60)
        for i, theme in enumerate(themes, 1):
            lines.append(f"\n{i}. {theme['name']} ({theme['size']} reviews)")
            lines.append(f"   {theme['summary']}")
        lines.append("")
        
        # Quotes
        lines.append("-" * 60)
        lines.append("USER FEEDBACK")
        lines.append("-" * 60)
        for quote in quotes:
            lines.append(f'• "{quote}"')
        lines.append("")
        
        # Actions
        lines.append("-" * 60)
        lines.append("RECOMMENDED ACTIONS")
        lines.append("-" * 60)
        for i, action in enumerate(actions, 1):
            lines.append(f"{i}. {action}")
        lines.append("")
        
        # Footer
        lines.append("=" * 60)
        lines.append("This pulse was generated automatically from user feedback.")
        lines.append("Questions or feedback? Reply to this email.")
        lines.append("=" * 60)
        
        return "\n".join(lines)


class PIIFinalCheck:
    """Double-verification for PII before sending."""
    
    # Comprehensive PII patterns
    EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+', re.IGNORECASE)
    PHONE_PATTERN = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    LONG_DIGITS_PATTERN = re.compile(r'\b\d{10,}\b')
    NAME_PATTERN = re.compile(r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+', re.IGNORECASE)
    
    @staticmethod
    def check(text: str) -> Tuple[bool, List[str]]:
        """
        Perform final PII check on text.
        
        Args:
            text: Text to check
            
        Returns:
            (has_pii, list_of_found_pii_examples)
        """
        found_pii = []
        
        # Check email
        emails = PIIFinalCheck.EMAIL_PATTERN.findall(text)
        if emails:
            found_pii.extend([f"EMAIL: {e}" for e in emails[:3]])
        
        # Check phone
        phones = PIIFinalCheck.PHONE_PATTERN.findall(text)
        if phones:
            found_pii.extend([f"PHONE: {p}" for p in phones[:3]])
        
        # Check long digits
        digits = PIIFinalCheck.LONG_DIGITS_PATTERN.findall(text)
        if digits:
            found_pii.extend([f"DIGITS: {d}" for d in digits[:3]])
        
        # Check names
        names = PIIFinalCheck.NAME_PATTERN.findall(text)
        if names:
            found_pii.extend([f"NAME: {n}" for n in names[:3]])
        
        return len(found_pii) > 0, found_pii
    
    @staticmethod
    def verify_email(html_body: str, plain_body: str) -> Tuple[bool, Dict]:
        """
        Verify both HTML and plain text for PII.
        
        Returns:
            (is_clean, report_dict)
        """
        html_has_pii, html_pii = PIIFinalCheck.check(html_body)
        plain_has_pii, plain_pii = PIIFinalCheck.check(plain_body)
        
        report = {
            'html_clean': not html_has_pii,
            'plain_clean': not plain_has_pii,
            'html_pii_found': html_pii,
            'plain_pii_found': plain_pii,
            'overall_clean': not (html_has_pii or plain_has_pii)
        }
        
        return report['overall_clean'], report


class DeliverySystem:
    """Email delivery with retry logic."""
    
    def __init__(self, 
                 smtp_host: str = None,
                 smtp_port: int = None,
                 smtp_user: str = None,
                 smtp_pass: str = None,
                 max_retries: int = 3,
                 retry_delay: int = 5):
        """
        Initialize delivery system.
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_pass: SMTP password
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries (seconds)
        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self.smtp_port = int(smtp_port or os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_pass = smtp_pass or os.getenv("SMTP_PASS")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def send_email(self,
                   to_addr: str,
                   from_addr: str,
                   subject: str,
                   html_body: str,
                   plain_body: str,
                   track_open: bool = False) -> Tuple[str, str, Dict]:
        """
        Send email with retry logic.
        
        Args:
            to_addr: Recipient email
            from_addr: Sender email
            subject: Email subject
            html_body: HTML content
            plain_body: Plain text content
            track_open: Enable read receipt tracking
            
        Returns:
            (status, error_message, metadata)
        """
        if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_pass]):
            return ("ERROR", "Missing SMTP configuration", {})
        
        metadata = {
            'attempts': 0,
            'sent_at': None,
            'tracking_enabled': track_open
        }
        
        for attempt in range(1, self.max_retries + 1):
            metadata['attempts'] = attempt
            
            try:
                logger.info(f"Sending email (attempt {attempt}/{self.max_retries})...")
                
                # Create multipart message
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = from_addr
                msg['To'] = to_addr
                msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
                
                # Add read receipt if requested
                if track_open:
                    msg['Disposition-Notification-To'] = from_addr
                    msg['Return-Receipt-To'] = from_addr
                
                # Attach plain text and HTML
                part_plain = MIMEText(plain_body, 'plain', 'utf-8')
                part_html = MIMEText(html_body, 'html', 'utf-8')
                
                msg.attach(part_plain)
                msg.attach(part_html)
                
                # Send via SMTP
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(self.smtp_user, self.smtp_pass)
                    server.send_message(msg)
                
                metadata['sent_at'] = datetime.now().isoformat()
                logger.info(f"✓ Email sent successfully on attempt {attempt}")
                
                return ("SENT", "", metadata)
                
            except smtplib.SMTPAuthenticationError as e:
                error_msg = f"SMTP authentication failed: {str(e)}"
                logger.error(error_msg)
                return ("ERROR", error_msg, metadata)  # Don't retry auth errors
                
            except smtplib.SMTPException as e:
                error_msg = f"SMTP error: {str(e)}"
                logger.warning(f"Attempt {attempt} failed: {error_msg}")
                
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All {self.max_retries} attempts failed")
                    return ("ERROR", error_msg, metadata)
                    
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(error_msg)
                
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    return ("ERROR", error_msg, metadata)
        
        return ("ERROR", "Max retries exceeded", metadata)


class ReadReceiptTracker:
    """Track email opens and read receipts (optional)."""
    
    def __init__(self, tracking_file: str = 'email_tracking.json'):
        """
        Initialize read receipt tracker.
        
        Args:
            tracking_file: Path to tracking database file
        """
        self.tracking_file = tracking_file
        self.tracking_data = self._load_tracking()
    
    def _load_tracking(self) -> Dict:
        """Load tracking data from disk."""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading tracking data: {e}")
        return {'emails': []}
    
    def _save_tracking(self):
        """Save tracking data to disk."""
        try:
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.tracking_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tracking data: {e}")
    
    def record_send(self, 
                   email_id: str,
                   recipient: str,
                   subject: str,
                   sent_at: str):
        """
        Record email send event.
        
        Args:
            email_id: Unique email identifier
            recipient: Recipient email
            subject: Email subject
            sent_at: ISO timestamp
        """
        record = {
            'email_id': email_id,
            'recipient': recipient,
            'subject': subject,
            'sent_at': sent_at,
            'opened_at': None,
            'read_receipt_at': None,
            'status': 'sent'
        }
        
        self.tracking_data['emails'].append(record)
        self._save_tracking()
        
        logger.info(f"Recorded send: {email_id} to {recipient}")
    
    def record_open(self, email_id: str):
        """Record email open event."""
        for email in self.tracking_data['emails']:
            if email['email_id'] == email_id:
                email['opened_at'] = datetime.now().isoformat()
                email['status'] = 'opened'
                self._save_tracking()
                logger.info(f"Recorded open: {email_id}")
                return
    
    def record_read_receipt(self, email_id: str):
        """Record read receipt."""
        for email in self.tracking_data['emails']:
            if email['email_id'] == email_id:
                email['read_receipt_at'] = datetime.now().isoformat()
                email['status'] = 'read'
                self._save_tracking()
                logger.info(f"Recorded read receipt: {email_id}")
                return
    
    def get_stats(self) -> Dict:
        """Get tracking statistics."""
        emails = self.tracking_data['emails']
        
        total = len(emails)
        opened = sum(1 for e in emails if e['opened_at'])
        read = sum(1 for e in emails if e['read_receipt_at'])
        
        return {
            'total_sent': total,
            'total_opened': opened,
            'total_read': read,
            'open_rate': (opened / total * 100) if total > 0 else 0,
            'read_rate': (read / total * 100) if total > 0 else 0
        }


class Layer4Pipeline:
    """Orchestrates Layer 4: Distribution & Feedback."""
    
    def __init__(self,
                 smtp_config: Dict = None,
                 enable_tracking: bool = False):
        """
        Initialize Layer 4 pipeline.
        
        Args:
            smtp_config: SMTP configuration dict
            enable_tracking: Enable read receipt tracking
        """
        self.renderer = EmailTemplateRenderer()
        self.pii_checker = PIIFinalCheck()
        
        smtp_config = smtp_config or {}
        self.delivery = DeliverySystem(
            smtp_host=smtp_config.get('host'),
            smtp_port=smtp_config.get('port'),
            smtp_user=smtp_config.get('user'),
            smtp_pass=smtp_config.get('password')
        )
        
        self.tracker = ReadReceiptTracker() if enable_tracking else None
        self.enable_tracking = enable_tracking
    
    def distribute(self,
                  pulse_document: Dict,
                  recipients: List[str],
                  from_addr: str = None,
                  subject: str = None) -> Dict:
        """
        Distribute pulse document via email.
        
        Args:
            pulse_document: Pulse document from Layer 3
            recipients: List of recipient email addresses
            from_addr: Sender email (default: SMTP_USER)
            subject: Email subject (default: from pulse title)
            
        Returns:
            Distribution report dict
        """
        logger.info("="*60)
        logger.info("LAYER 4: DISTRIBUTION & FEEDBACK")
        logger.info("="*60)
        
        from_addr = from_addr or os.getenv("EMAIL_FROM") or self.delivery.smtp_user
        subject = subject or pulse_document.get('title', 'Weekly Product Pulse')
        
        # Step 1: Render email templates
        logger.info("Step 1: Rendering email templates...")
        html_body = self.renderer.render_html(pulse_document)
        plain_body = self.renderer.render_plain_text(pulse_document)
        
        logger.info(f"  HTML: {len(html_body)} chars")
        logger.info(f"  Plain: {len(plain_body)} chars")
        
        # Step 2: PII final check
        logger.info("Step 2: Performing final PII check...")
        is_clean, pii_report = self.pii_checker.verify_email(html_body, plain_body)
        
        if not is_clean:
            logger.error("✗ PII detected in email content!")
            logger.error(f"  HTML PII: {pii_report['html_pii_found']}")
            logger.error(f"  Plain PII: {pii_report['plain_pii_found']}")
            
            return {
                'status': 'BLOCKED',
                'reason': 'PII detected in email content',
                'pii_report': pii_report,
                'sent': 0,
                'failed': 0
            }
        
        logger.info("✓ PII check passed")
        
        # Step 3: Deliver to recipients
        logger.info(f"Step 3: Delivering to {len(recipients)} recipient(s)...")
        
        results = []
        for recipient in recipients:
            logger.info(f"  Sending to {recipient}...")
            
            status, error, metadata = self.delivery.send_email(
                to_addr=recipient,
                from_addr=from_addr,
                subject=subject,
                html_body=html_body,
                plain_body=plain_body,
                track_open=self.enable_tracking
            )
            
            result = {
                'recipient': recipient,
                'status': status,
                'error': error,
                'metadata': metadata
            }
            results.append(result)
            
            # Track if enabled
            if self.enable_tracking and status == 'SENT' and self.tracker:
                email_id = f"{recipient}_{metadata.get('sent_at', '')}"
                self.tracker.record_send(
                    email_id=email_id,
                    recipient=recipient,
                    subject=subject,
                    sent_at=metadata.get('sent_at', '')
                )
        
        # Step 4: Generate report
        sent = sum(1 for r in results if r['status'] == 'SENT')
        failed = sum(1 for r in results if r['status'] == 'ERROR')
        
        report = {
            'status': 'COMPLETE',
            'sent': sent,
            'failed': failed,
            'recipients': len(recipients),
            'results': results,
            'pii_report': pii_report,
            'tracking_enabled': self.enable_tracking
        }
        
        if self.tracker:
            report['tracking_stats'] = self.tracker.get_stats()
        
        logger.info("="*60)
        logger.info("LAYER 4 COMPLETE")
        logger.info(f"Sent: {sent}/{len(recipients)}")
        if failed > 0:
            logger.warning(f"Failed: {failed}/{len(recipients)}")
        logger.info("="*60)
        
        return report
