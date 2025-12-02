"""
Layer 1: Trigger and Scheduling
Scheduler component for weekly review processing automation.
Supports cron-based scheduling, configurable time windows, and workflow parameters.
"""

import os
import json
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkflowConfig:
    """Workflow parameters for scheduled runs."""
    
    def __init__(self, 
                 product_id: str = 'com.nextbillion.groww',
                 product_name: str = 'Groww',
                 time_window_weeks: int = 12,
                 target_review_count: int = 100,
                 lang: str = 'en',
                 country: str = 'in',
                 timezone: str = 'Asia/Kolkata'):
        self.product_id = product_id
        self.product_name = product_name
        self.time_window_weeks = time_window_weeks
        self.target_review_count = target_review_count
        self.lang = lang
        self.country = country
        self.timezone = timezone
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary."""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'time_window_weeks': self.time_window_weeks,
            'target_review_count': self.target_review_count,
            'lang': self.lang,
            'country': self.country,
            'timezone': self.timezone
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkflowConfig':
        """Create config from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> 'WorkflowConfig':
        """Load configuration from environment variables."""
        return cls(
            product_id=os.getenv('APP_ID', 'com.nextbillion.groww'),
            product_name=os.getenv('PRODUCT_NAME', 'Groww'),
            time_window_weeks=int(os.getenv('TIME_WINDOW_WEEKS', '12')),
            target_review_count=int(os.getenv('TARGET_COUNT', '100')),
            lang=os.getenv('LANG', 'en'),
            country=os.getenv('COUNTRY', 'in'),
            timezone=os.getenv('TIMEZONE', 'Asia/Kolkata')
        )


class SchedulerState:
    """Tracks scheduler run history and state."""
    
    def __init__(self, state_file: str = 'scheduler_state.json'):
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load scheduler state from disk."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading scheduler state: {e}")
        return {
            'last_run': None,
            'next_scheduled_run': None,
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'run_history': []
        }
    
    def _save_state(self):
        """Persist scheduler state to disk."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving scheduler state: {e}")
    
    def record_run(self, status: str, error_msg: str = ""):
        """Record a scheduler run."""
        run_record = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'error_message': error_msg
        }
        
        self.state['last_run'] = run_record['timestamp']
        self.state['total_runs'] += 1
        
        if status == 'SUCCESS':
            self.state['successful_runs'] += 1
        else:
            self.state['failed_runs'] += 1
        
        # Keep last 50 runs
        self.state['run_history'].insert(0, run_record)
        self.state['run_history'] = self.state['run_history'][:50]
        
        self._save_state()
    
    def set_next_run(self, next_run_time: str):
        """Set next scheduled run time."""
        self.state['next_scheduled_run'] = next_run_time
        self._save_state()
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics."""
        return {
            'last_run': self.state.get('last_run'),
            'next_scheduled_run': self.state.get('next_scheduled_run'),
            'total_runs': self.state.get('total_runs', 0),
            'successful_runs': self.state.get('successful_runs', 0),
            'failed_runs': self.state.get('failed_runs', 0),
            'success_rate': (
                self.state['successful_runs'] / self.state['total_runs'] * 100
                if self.state['total_runs'] > 0 else 0
            )
        }


class WeeklyScheduler:
    """
    Scheduler for weekly review processing.
    Runs once a week (e.g., every Monday 9 AM IST).
    """
    
    def __init__(self, 
                 workflow_func: Callable,
                 config: Optional[WorkflowConfig] = None,
                 schedule_time: str = "09:00",
                 schedule_day: str = "monday",
                 state_file: str = 'scheduler_state.json'):
        """
        Initialize scheduler.
        
        Args:
            workflow_func: Function to execute on schedule (e.g., fetch_and_process_reviews)
            config: Workflow configuration
            schedule_time: Time to run in HH:MM format (24-hour, local timezone)
            schedule_day: Day of week (monday, tuesday, etc.)
            state_file: Path to scheduler state file
        """
        self.workflow_func = workflow_func
        self.config = config or WorkflowConfig.from_env()
        self.schedule_time = schedule_time
        self.schedule_day = schedule_day.lower()
        self.state = SchedulerState(state_file)
        self.is_running = False
    
    def _execute_workflow(self):
        """Execute the scheduled workflow."""
        logger.info("=" * 60)
        logger.info("SCHEDULED WORKFLOW EXECUTION STARTED")
        logger.info("=" * 60)
        logger.info(f"Product: {self.config.product_name} ({self.config.product_id})")
        logger.info(f"Time Window: {self.config.time_window_weeks} weeks")
        logger.info(f"Target Count: {self.config.target_review_count}")
        logger.info(f"Timezone: {self.config.timezone}")
        logger.info("=" * 60)
        
        try:
            # Execute the workflow function
            self.workflow_func()
            
            # Record successful run
            self.state.record_run('SUCCESS')
            logger.info("=" * 60)
            logger.info("SCHEDULED WORKFLOW EXECUTION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            
        except Exception as e:
            # Record failed run
            error_msg = str(e)
            self.state.record_run('FAILED', error_msg)
            logger.error("=" * 60)
            logger.error(f"SCHEDULED WORKFLOW EXECUTION FAILED: {error_msg}")
            logger.error("=" * 60)
            import traceback
            traceback.print_exc()
    
    def schedule(self):
        """Set up the schedule."""
        # Map day name to schedule method
        day_map = {
            'monday': schedule.every().monday,
            'tuesday': schedule.every().tuesday,
            'wednesday': schedule.every().wednesday,
            'thursday': schedule.every().thursday,
            'friday': schedule.every().friday,
            'saturday': schedule.every().saturday,
            'sunday': schedule.every().sunday
        }
        
        if self.schedule_day not in day_map:
            raise ValueError(f"Invalid schedule day: {self.schedule_day}")
        
        # Schedule the job
        day_map[self.schedule_day].at(self.schedule_time).do(self._execute_workflow)
        
        # Calculate next run
        next_run = schedule.next_run()
        self.state.set_next_run(next_run.isoformat() if next_run else None)
        
        logger.info(f"Scheduled weekly workflow: Every {self.schedule_day.capitalize()} at {self.schedule_time}")
        logger.info(f"Next scheduled run: {next_run}")
    
    def run_once(self):
        """Execute workflow immediately (manual trigger)."""
        logger.info("Manual workflow trigger initiated")
        self._execute_workflow()
    
    def start(self, blocking: bool = True):
        """
        Start the scheduler.
        
        Args:
            blocking: If True, runs in blocking loop. If False, returns immediately.
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.schedule()
        self.is_running = True
        
        if blocking:
            logger.info("Scheduler started (blocking mode). Press Ctrl+C to stop.")
            try:
                while self.is_running:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                self.is_running = False
        else:
            logger.info("Scheduler started (non-blocking mode)")
    
    def stop(self):
        """Stop the scheduler."""
        self.is_running = False
        schedule.clear()
        logger.info("Scheduler stopped")
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics."""
        stats = self.state.get_stats()
        stats['config'] = self.config.to_dict()
        stats['schedule'] = f"Every {self.schedule_day.capitalize()} at {self.schedule_time}"
        return stats


def create_scheduler_from_env() -> WeeklyScheduler:
    """
    Create a scheduler instance from environment variables.
    
    Environment variables:
    - APP_ID: Product/app ID
    - PRODUCT_NAME: Product name
    - TIME_WINDOW_WEEKS: Review time window (default: 12)
    - TARGET_COUNT: Target review count (default: 100)
    - SCHEDULE_TIME: Time to run in HH:MM (default: 09:00)
    - SCHEDULE_DAY: Day of week (default: monday)
    - TIMEZONE: Timezone (default: Asia/Kolkata)
    """
    from main import fetch_and_process_reviews
    
    config = WorkflowConfig.from_env()
    schedule_time = os.getenv('SCHEDULE_TIME', '09:00')
    schedule_day = os.getenv('SCHEDULE_DAY', 'monday')
    
    scheduler = WeeklyScheduler(
        workflow_func=fetch_and_process_reviews,
        config=config,
        schedule_time=schedule_time,
        schedule_day=schedule_day
    )
    
    return scheduler
