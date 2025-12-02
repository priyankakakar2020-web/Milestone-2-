"""
Complete 4-Layer Integration & Automation
End-to-end automated weekly product pulse system
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedPulsePipeline:
    """
    Complete 4-layer pipeline integration.
    
    Architecture:
        Layer 1: Data Import & Validation
        Layer 2: Theme Extraction & Classification  
        Layer 3: Content Generation
        Layer 4: Distribution & Feedback
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize integrated pipeline.
        
        Args:
            config: Configuration dictionary (optional, uses env vars if None)
        """
        self.config = config or self._load_config()
        self.stats = {
            'layer1': {},
            'layer2': {},
            'layer3': {},
            'layer4': {},
            'execution_time': {}
        }
        
    def _load_config(self) -> Dict:
        """Load configuration from environment variables."""
        return {
            # Product configuration
            'app_id': os.getenv('APP_ID', 'com.nextbillion.groww'),
            'product_name': os.getenv('PRODUCT_NAME', 'Groww'),
            'lang': os.getenv('LANG', 'en'),
            'country': os.getenv('COUNTRY', 'in'),
            
            # Data collection
            'time_window_weeks': int(os.getenv('TIME_WINDOW_WEEKS', '12')),
            'target_review_count': int(os.getenv('TARGET_COUNT', '100')),
            'min_review_length': int(os.getenv('MIN_REVIEW_LENGTH', '100')),
            
            # Layer 2: Theme extraction
            'embedding_model': os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
            'min_cluster_size': int(os.getenv('MIN_CLUSTER_SIZE', '15')),
            'min_samples': int(os.getenv('MIN_SAMPLES', '5')),
            'max_themes': int(os.getenv('MAX_THEMES', '5')),
            
            # Layer 3: Content generation
            'max_word_count': int(os.getenv('MAX_WORD_COUNT', '250')),
            'quotes_per_theme': int(os.getenv('QUOTES_PER_THEME', '3')),
            
            # Layer 4: Distribution
            'email_sender': os.getenv('EMAIL_SENDER', 'priyankakakar2020@gmail.com'),
            'email_password': os.getenv('EMAIL_PASSWORD', ''),
            'email_to': os.getenv('EMAIL_TO', 'priyanka.kakar@sattva.co.in'),
            'smtp_host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            
            # Gemini API
            'gemini_api_key': os.getenv('GEMINI_API_KEY', '')
        }
    
    def run(self, dry_run: bool = False) -> Dict:
        """
        Execute complete 4-layer pipeline.
        
        Args:
            dry_run: If True, skip email sending
            
        Returns:
            Execution report with stats from all layers
        """
        start_time = datetime.now()
        
        logger.info("="*70)
        logger.info("STARTING 4-LAYER INTEGRATED PULSE PIPELINE")
        logger.info("="*70)
        logger.info(f"Product: {self.config['product_name']} ({self.config['app_id']})")
        logger.info(f"Time Window: {self.config['time_window_weeks']} weeks")
        logger.info(f"Target Reviews: {self.config['target_review_count']}")
        logger.info(f"Dry Run: {dry_run}")
        logger.info("="*70)
        
        try:
            # Calculate date range
            week_end = datetime.now() - timedelta(days=7)
            week_start = week_end - timedelta(days=6)
            data_start = datetime.now() - timedelta(weeks=self.config['time_window_weeks'])
            
            # Layer 1: Data Import & Validation
            logger.info("\n" + "="*70)
            logger.info("LAYER 1: DATA IMPORT & VALIDATION")
            logger.info("="*70)
            layer1_start = datetime.now()
            
            valid_reviews = self._run_layer1(data_start, week_end)
            
            self.stats['execution_time']['layer1'] = (datetime.now() - layer1_start).total_seconds()
            logger.info(f"✓ Layer 1 completed in {self.stats['execution_time']['layer1']:.2f}s")
            logger.info(f"✓ Valid reviews: {len(valid_reviews)}")
            
            if len(valid_reviews) == 0:
                raise Exception("No valid reviews collected. Cannot proceed.")
            
            # Layer 2: Theme Extraction & Classification
            logger.info("\n" + "="*70)
            logger.info("LAYER 2: THEME EXTRACTION & CLASSIFICATION")
            logger.info("="*70)
            layer2_start = datetime.now()
            
            enriched_reviews, theme_metadata = self._run_layer2(valid_reviews)
            
            self.stats['execution_time']['layer2'] = (datetime.now() - layer2_start).total_seconds()
            logger.info(f"✓ Layer 2 completed in {self.stats['execution_time']['layer2']:.2f}s")
            logger.info(f"✓ Themes identified: {len(theme_metadata['themes'])}")
            
            # Layer 3: Content Generation
            logger.info("\n" + "="*70)
            logger.info("LAYER 3: CONTENT GENERATION")
            logger.info("="*70)
            layer3_start = datetime.now()
            
            pulse_document = self._run_layer3(
                enriched_reviews, 
                theme_metadata,
                week_start,
                week_end
            )
            
            self.stats['execution_time']['layer3'] = (datetime.now() - layer3_start).total_seconds()
            logger.info(f"✓ Layer 3 completed in {self.stats['execution_time']['layer3']:.2f}s")
            logger.info(f"✓ Word count: {pulse_document['metadata']['word_count']}/250")
            
            # Layer 4: Distribution & Feedback
            logger.info("\n" + "="*70)
            logger.info("LAYER 4: DISTRIBUTION & FEEDBACK")
            logger.info("="*70)
            layer4_start = datetime.now()
            
            delivery_result = self._run_layer4(pulse_document, dry_run)
            
            self.stats['execution_time']['layer4'] = (datetime.now() - layer4_start).total_seconds()
            logger.info(f"✓ Layer 4 completed in {self.stats['execution_time']['layer4']:.2f}s")
            logger.info(f"✓ Delivery status: {delivery_result['status']}")
            
            # Final report
            total_time = (datetime.now() - start_time).total_seconds()
            self.stats['execution_time']['total'] = total_time
            
            logger.info("\n" + "="*70)
            logger.info("PIPELINE EXECUTION COMPLETE")
            logger.info("="*70)
            logger.info(f"Total execution time: {total_time:.2f}s")
            logger.info(f"  Layer 1: {self.stats['execution_time']['layer1']:.2f}s")
            logger.info(f"  Layer 2: {self.stats['execution_time']['layer2']:.2f}s")
            logger.info(f"  Layer 3: {self.stats['execution_time']['layer3']:.2f}s")
            logger.info(f"  Layer 4: {self.stats['execution_time']['layer4']:.2f}s")
            logger.info("="*70)
            
            return {
                'status': 'SUCCESS',
                'stats': self.stats,
                'pulse_document': pulse_document,
                'delivery_result': delivery_result,
                'execution_time': total_time
            }
            
        except Exception as e:
            logger.error(f"✗ Pipeline failed: {str(e)}", exc_info=True)
            return {
                'status': 'FAILED',
                'error': str(e),
                'stats': self.stats
            }
    
    def _run_layer1(self, data_start: datetime, week_end: datetime) -> List[Dict]:
        """Execute Layer 1: Data Import & Validation."""
        from layer1_import import Layer1Pipeline
        from cleaner import clean_text
        
        layer1 = Layer1Pipeline(
            app_id=self.config['app_id'],
            lang=self.config['lang'],
            country=self.config['country']
        )
        
        all_reviews = []
        continuation_token = None
        target_count = self.config['target_review_count']
        
        logger.info(f"Fetching reviews from {data_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
        
        while len(all_reviews) < target_count:
            batch, continuation_token = layer1.process_batch(
                count=200,
                continuation_token=continuation_token
            )
            
            if not batch:
                logger.warning("No more reviews available")
                break
            
            # Filter by date range and clean
            for review in batch:
                review_date = review['at']
                
                if data_start <= review_date <= week_end:
                    review['text'] = clean_text(review.get('content', ''))
                    
                    # Skip short reviews
                    if len(review['text']) >= self.config['min_review_length']:
                        all_reviews.append(review)
            
            logger.info(f"Progress: {len(all_reviews)}/{target_count} valid reviews")
            
            if len(all_reviews) >= target_count:
                break
            
            if not continuation_token:
                logger.warning("Reached end of available reviews")
                break
        
        # Store stats
        stats = layer1.get_stats()
        self.stats['layer1'] = {
            'valid_reviews': len(all_reviews),
            'total_seen': stats.get('total_seen_reviews', 0),
            'duplicates_filtered': stats.get('duplicates_filtered', 0),
            'pii_flagged': stats.get('pii_flagged', 0)
        }
        
        logger.info(f"Layer 1 Stats:")
        logger.info(f"  Valid reviews: {len(all_reviews)}")
        logger.info(f"  Total seen: {stats['total_seen_reviews']}")
        logger.info(f"  Duplicates filtered: {stats['duplicates_filtered']}")
        logger.info(f"  PII flagged: {stats['pii_flagged']}")
        
        return all_reviews
    
    def _run_layer2(self, reviews: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Execute Layer 2: Theme Extraction & Classification."""
        from layer2_themes import Layer2Pipeline
        
        layer2 = Layer2Pipeline(
            embedding_model=self.config['embedding_model'],
            min_cluster_size=self.config['min_cluster_size'],
            min_samples=self.config['min_samples'],
            max_themes=self.config['max_themes']
        )
        
        enriched_reviews, theme_metadata = layer2.process(reviews)
        
        # Store stats
        self.stats['layer2'] = {
            'themes_found': len(theme_metadata['themes']),
            'reviews_clustered': theme_metadata.get('clustered_reviews', 0),
            'themes': [
                {
                    'name': t['theme_name'],
                    'size': t['size']
                }
                for t in theme_metadata['themes']
            ]
        }
        
        logger.info(f"Layer 2 Stats:")
        logger.info(f"  Themes identified: {len(theme_metadata['themes'])}")
        for theme in theme_metadata['themes']:
            logger.info(f"    • {theme['theme_name']}: {theme['size']} reviews")
        
        return enriched_reviews, theme_metadata
    
    def _run_layer3(self, 
                    reviews: List[Dict], 
                    theme_metadata: Dict,
                    week_start: datetime,
                    week_end: datetime) -> Dict:
        """Execute Layer 3: Content Generation."""
        from layer3_content import Layer3Pipeline
        
        layer3 = Layer3Pipeline(
            product_name=self.config['product_name'],
            week_start=week_start.strftime('%Y-%m-%d'),
            week_end=week_end.strftime('%Y-%m-%d')
        )
        
        pulse_document = layer3.process(reviews, theme_metadata)
        
        # Save pulse document
        filename = f"weekly_pulse_{week_start.strftime('%Y_%m_%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(pulse_document, f, indent=2, ensure_ascii=False)
        
        # Store stats
        self.stats['layer3'] = {
            'word_count': pulse_document['metadata']['word_count'],
            'themes_included': len(pulse_document['themes']),
            'quotes_extracted': len(pulse_document['quotes']),
            'actions_generated': len(pulse_document['actions']),
            'output_file': filename
        }
        
        logger.info(f"Layer 3 Stats:")
        logger.info(f"  Title: {pulse_document['title']}")
        logger.info(f"  Word count: {pulse_document['metadata']['word_count']}/250")
        logger.info(f"  Themes: {len(pulse_document['themes'])}")
        logger.info(f"  Quotes: {len(pulse_document['quotes'])}")
        logger.info(f"  Actions: {len(pulse_document['actions'])}")
        logger.info(f"  Saved to: {filename}")
        
        return pulse_document
    
    def _run_layer4(self, pulse_document: Dict, dry_run: bool) -> Dict:
        """Execute Layer 4: Distribution & Feedback."""
        from send_weekly_pulse import send_pulse_email
        
        result = send_pulse_email(
            pulse_document=pulse_document,
            recipient=self.config['email_to'],
            sender=self.config['email_sender'],
            password=self.config['email_password'],
            dry_run=dry_run
        )
        
        # Store stats
        self.stats['layer4'] = {
            'status': result['status'],
            'recipient': self.config['email_to'],
            'sender': self.config['email_sender'],
            'dry_run': dry_run,
            'pii_clean': result.get('pii_clean', True)
        }
        
        if result['status'] == 'SENT':
            self.stats['layer4']['sent_at'] = result['metadata']['sent_at']
            self.stats['layer4']['attempts'] = result['metadata']['attempts']
        
        logger.info(f"Layer 4 Stats:")
        logger.info(f"  Status: {result['status']}")
        logger.info(f"  Recipient: {self.config['email_to']}")
        logger.info(f"  PII clean: {result.get('pii_clean', True)}")
        if result['status'] == 'SENT':
            logger.info(f"  Sent at: {result['metadata']['sent_at']}")
            logger.info(f"  Attempts: {result['metadata']['attempts']}")
        
        return result


def main():
    """Main entry point for integrated pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run integrated 4-layer pulse pipeline')
    parser.add_argument('--dry-run', action='store_true', help='Preview without sending email')
    parser.add_argument('--config', type=str, help='Path to config JSON file')
    args = parser.parse_args()
    
    # Load config if provided
    config = None
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Initialize and run pipeline
    pipeline = IntegratedPulsePipeline(config=config)
    result = pipeline.run(dry_run=args.dry_run)
    
    # Exit with appropriate code
    if result['status'] == 'SUCCESS':
        print("\n✓ Pipeline executed successfully!")
        sys.exit(0)
    else:
        print(f"\n✗ Pipeline failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
