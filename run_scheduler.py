"""
Scheduler Runner - Entry point for scheduled weekly review processing
Run this to start the weekly scheduler.
"""

from scheduler import create_scheduler_from_env
import sys


def main():
    """Start the weekly scheduler."""
    print("\n" + "="*60)
    print("WEEKLY REVIEW SCHEDULER")
    print("="*60)
    
    # Create scheduler from environment
    scheduler = create_scheduler_from_env()
    
    # Display configuration
    stats = scheduler.get_stats()
    print(f"\nConfiguration:")
    print(f"  Product: {stats['config']['product_name']} ({stats['config']['product_id']})")
    print(f"  Time Window: {stats['config']['time_window_weeks']} weeks")
    print(f"  Target Reviews: {stats['config']['target_review_count']}")
    print(f"  Schedule: {stats['schedule']}")
    print(f"  Timezone: {stats['config']['timezone']}")
    
    if stats['last_run']:
        print(f"\nLast Run: {stats['last_run']}")
        print(f"Total Runs: {stats['total_runs']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
    
    if stats['next_scheduled_run']:
        print(f"\nNext Scheduled Run: {stats['next_scheduled_run']}")
    
    print("\n" + "="*60)
    
    # Check for manual trigger flag
    if len(sys.argv) > 1 and sys.argv[1] == '--run-now':
        print("Manual trigger requested")
        scheduler.run_once()
    else:
        # Start scheduler in blocking mode
        scheduler.start(blocking=True)


if __name__ == "__main__":
    main()
