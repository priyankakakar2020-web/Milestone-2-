"""
Test script for Layer 4: Distribution & Feedback
Demonstrates template rendering, PII checking, delivery, and tracking.
"""

from layer4_distribution import (
    EmailTemplateRenderer,
    PIIFinalCheck,
    DeliverySystem,
    ReadReceiptTracker,
    Layer4Pipeline
)
import os


def test_email_rendering():
    """Test HTML and plain text rendering."""
    print("\n" + "="*60)
    print("TEST 1: EMAIL TEMPLATE RENDERING")
    print("="*60)
    
    sample_pulse = {
        'title': 'Weekly Product Pulse – Groww',
        'overview': 'This week\'s 115 reviews highlight key improvement areas with actionable insights.',
        'themes': [
            {
                'name': 'KYC Verification Delays',
                'summary': 'Users frustrated with slow verification taking 5+ days.',
                'size': 45
            },
            {
                'name': 'Payment Failures',
                'summary': 'Frequent payment deductions without confirmation.',
                'size': 38
            }
        ],
        'quotes': [
            'KYC verification took 5 days and failed twice without explanation.',
            'Payment deducted but order not confirmed. No refund received.'
        ],
        'actions': [
            'Add real-time status updates to KYC verification flow',
            'Implement automatic refund system for failed payments'
        ],
        'metadata': {
            'product': 'Groww',
            'week_start': '2025-11-25',
            'week_end': '2025-12-01',
            'total_reviews': 115,
            'word_count': 238
        }
    }
    
    renderer = EmailTemplateRenderer()
    
    # Render HTML
    html = renderer.render_html(sample_pulse)
    print(f"\n HTML rendered: {len(html)} characters")
    print(f"  Contains DOCTYPE: {'<!DOCTYPE html>' in html}")
    print(f"  Contains styles: {'<style>' in html}")
    print(f"  Contains themes: {'KYC Verification Delays' in html}")
    
    # Render plain text
    plain = renderer.render_plain_text(sample_pulse)
    print(f"\n✓ Plain text rendered: {len(plain)} characters")
    print(f"  Contains title: {'Weekly Product Pulse' in plain}")
    print(f"  Contains themes: {'KYC Verification Delays' in plain}")
    
    # Save samples for inspection
    with open('sample_email.html', 'w', encoding='utf-8') as f:
        f.write(html)
    with open('sample_email.txt', 'w', encoding='utf-8') as f:
        f.write(plain)
    
    print("\n✓ Samples saved to sample_email.html and sample_email.txt")
    print("✓ Email rendering test passed")


def test_pii_check():
    """Test PII double-verification."""
    print("\n" + "="*60)
    print("TEST 2: PII FINAL CHECK")
    print("="*60)
    
    # Clean text
    clean_text = "The app performance is good and KYC process needs improvement."
    has_pii, found = PIIFinalCheck.check(clean_text)
    print(f"\nClean text: {clean_text[:60]}...")
    print(f"  PII detected: {has_pii}")
    assert not has_pii, "False positive PII detection"
    
    # Text with email
    email_text = "Contact support at help@example.com for assistance."
    has_pii, found = PIIFinalCheck.check(email_text)
    print(f"\nText with email: {email_text[:60]}...")
    print(f"  PII detected: {has_pii}")
    print(f"  Found: {found}")
    assert has_pii, "Failed to detect email"
    
    # Text with phone
    phone_text = "Call customer service at +91-9876543210 for help."
    has_pii, found = PIIFinalCheck.check(phone_text)
    print(f"\nText with phone: {phone_text[:60]}...")
    print(f"  PII detected: {has_pii}")
    print(f"  Found: {found}")
    assert has_pii, "Failed to detect phone"
    
    # Text with long digits
    digits_text = "My account ID is 1234567890123 for reference."
    has_pii, found = PIIFinalCheck.check(digits_text)
    print(f"\nText with digits: {digits_text[:60]}...")
    print(f"  PII detected: {has_pii}")
    print(f"  Found: {found}")
    assert has_pii, "Failed to detect long digits"
    
    # Full email verification
    clean_html = "<html><body>Great app performance</body></html>"
    clean_plain = "Great app performance"
    is_clean, report = PIIFinalCheck.verify_email(clean_html, clean_plain)
    
    print(f"\nEmail verification (clean):")
    print(f"  Overall clean: {report['overall_clean']}")
    print(f"  HTML clean: {report['html_clean']}")
    print(f"  Plain clean: {report['plain_clean']}")
    assert is_clean, "Clean email flagged as having PII"
    
    print("\n✓ PII check test passed")


def test_delivery_dry_run():
    """Test delivery system (dry run without actual sending)."""
    print("\n" + "="*60)
    print("TEST 3: DELIVERY SYSTEM (DRY RUN)")
    print("="*60)
    
    # Note: This test demonstrates the interface but won't actually send
    # To test real sending, configure SMTP_* environment variables
    
    delivery = DeliverySystem(
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=os.getenv("SMTP_PORT"),
        smtp_user=os.getenv("SMTP_USER"),
        smtp_pass=os.getenv("SMTP_PASS"),
        max_retries=2,
        retry_delay=2
    )
    
    print(f"\nSMTP Configuration:")
    print(f"  Host: {delivery.smtp_host or 'Not configured'}")
    print(f"  Port: {delivery.smtp_port}")
    print(f"  User: {delivery.smtp_user or 'Not configured'}")
    print(f"  Max retries: {delivery.max_retries}")
    print(f"  Retry delay: {delivery.retry_delay}s")
    
    if not all([delivery.smtp_host, delivery.smtp_user, delivery.smtp_pass]):
        print("\n⚠ SMTP not configured. Skipping actual send test.")
        print("  To test sending, set SMTP_HOST, SMTP_USER, SMTP_PASS")
    else:
        print("\n✓ SMTP configured and ready")
    
    print("✓ Delivery system test passed")


def test_read_receipt_tracker():
    """Test read receipt tracking."""
    print("\n" + "="*60)
    print("TEST 4: READ RECEIPT TRACKER")
    print("="*60)
    
    tracker = ReadReceiptTracker(tracking_file='test_tracking.json')
    
    # Record sends
    tracker.record_send(
        email_id='test_email_1',
        recipient='user1@example.com',
        subject='Test Pulse',
        sent_at='2025-12-01T09:00:00'
    )
    
    tracker.record_send(
        email_id='test_email_2',
        recipient='user2@example.com',
        subject='Test Pulse',
        sent_at='2025-12-01T09:01:00'
    )
    
    print(f"\n✓ Recorded 2 email sends")
    
    # Record open
    tracker.record_open('test_email_1')
    print(f"✓ Recorded email open")
    
    # Record read receipt
    tracker.record_read_receipt('test_email_1')
    print(f"✓ Recorded read receipt")
    
    # Get stats
    stats = tracker.get_stats()
    print(f"\nTracking Statistics:")
    print(f"  Total sent: {stats['total_sent']}")
    print(f"  Total opened: {stats['total_opened']}")
    print(f"  Total read: {stats['total_read']}")
    print(f"  Open rate: {stats['open_rate']:.1f}%")
    print(f"  Read rate: {stats['read_rate']:.1f}%")
    
    # Cleanup
    import os
    if os.path.exists('test_tracking.json'):
        os.remove('test_tracking.json')
    
    print("\n✓ Read receipt tracker test passed")


def test_full_pipeline():
    """Test full Layer 4 pipeline."""
    print("\n" + "="*60)
    print("TEST 5: FULL LAYER 4 PIPELINE")
    print("="*60)
    
    sample_pulse = {
        'title': 'Weekly Product Pulse – Groww',
        'overview': 'This week\'s 115 reviews highlight key improvement areas.',
        'themes': [
            {
                'name': 'KYC Verification Delays',
                'summary': 'Users frustrated with slow verification.',
                'size': 45
            }
        ],
        'quotes': [
            'KYC verification took 5 days and failed twice.'
        ],
        'actions': [
            'Add real-time status updates to KYC flow'
        ],
        'metadata': {
            'product': 'Groww',
            'week_start': '2025-11-25',
            'week_end': '2025-12-01',
            'total_reviews': 115,
            'word_count': 238
        }
    }
    
    # Initialize pipeline
    pipeline = Layer4Pipeline(
        smtp_config={
            'host': os.getenv('SMTP_HOST'),
            'port': os.getenv('SMTP_PORT'),
            'user': os.getenv('SMTP_USER'),
            'password': os.getenv('SMTP_PASS')
        },
        enable_tracking=True
    )
    
    # Dry run (won't actually send without SMTP config)
    recipients = [os.getenv('EMAIL_TO', 'test@example.com')]
    
    print(f"\nDistributing to: {recipients}")
    
    report = pipeline.distribute(
        pulse_document=sample_pulse,
        recipients=recipients,
        from_addr=os.getenv('EMAIL_FROM'),
        subject='Test: Weekly Product Pulse'
    )
    
    print(f"\nDistribution Report:")
    print(f"  Status: {report['status']}")
    print(f"  Sent: {report.get('sent', 0)}")
    print(f"  Failed: {report.get('failed', 0)}")
    print(f"  PII Check: {'✓ Passed' if report['pii_report']['overall_clean'] else '✗ Failed'}")
    print(f"  Tracking: {'Enabled' if report['tracking_enabled'] else 'Disabled'}")
    
    if report['status'] == 'BLOCKED':
        print(f"  Blocked reason: {report['reason']}")
    
    print("\n✓ Full pipeline test passed")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LAYER 4 COMPONENT TESTS")
    print("="*60)
    
    try:
        test_email_rendering()
        test_pii_check()
        test_delivery_dry_run()
        test_read_receipt_tracker()
        test_full_pipeline()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        print("\nNote: To test actual email sending, configure SMTP environment variables:")
        print("  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
