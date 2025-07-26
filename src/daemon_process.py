#!/usr/bin/env python3

"""
GitHub Sentinel - Simple Daemon Process (Schedule-based)
Runs periodic GitHub repo monitoring using the schedule library.

Version: 0.5 (lightweight, no threading/daemon)
"""

import sys
import os
import time
import signal
import schedule
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from github_client import GitHubClient
from subscription_manager import SubscriptionManager
from report_generator import ReportGenerator
from notifier import Notifier
from llm_client import LLMClient, LLM
from logger import LOG

# Graceful shutdown flag
graceful_exit = False

def signal_handler(sig, frame):
    global graceful_exit
    LOG.info("Received exit signal, shutting down gracefully...")
    graceful_exit = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def run_github_progress_job():
    """
    Main job: Check all subscribed repos, generate reports, and send notifications.
    """
    LOG.info("Running scheduled GitHub progress job...")
    config = Config()
    github_client = GitHubClient(config.github_token)
    notifier = Notifier(config.notification_settings)
    subscription_manager = SubscriptionManager(config.subscriptions_file)
    
    # Initialize LLM client with new availability checking
    llm_client = None
    is_available, error_message = LLM.check_availability(config)
    if is_available:
        try:
            llm_client = LLMClient(config)
            provider = config.get_llm_provider()
            LOG.info(f"LLM client initialized with {provider.upper()} provider")
        except Exception as e:
            LOG.warning(f"LLM client initialization failed: {e}. AI features will be unavailable.")
    else:
        LOG.warning(f"LLM provider not available: {error_message}. AI features will be unavailable.")
    
    report_generator = ReportGenerator(llm_client=llm_client, export_cache_dir=config.export_cache_dir, ai_reports_dir=config.ai_reports_dir)

    try:
        subscriptions = subscription_manager.get_subscriptions()
        if not subscriptions:
            LOG.info("No subscriptions found, skipping update check")
            return
        end_date = datetime.now()
        start_date = end_date - timedelta(days=config.github_progress_frequency_days)
        for repo in subscriptions:
            try:
                LOG.info(f"Checking updates for {repo}")
                updates = github_client.fetch_updates(
                    repo=repo,
                    since_date=start_date.strftime('%Y-%m-%d'),
                    until_date=end_date.strftime('%Y-%m-%d')
                )
                # Only notify if there are meaningful updates
                summary = updates.get('summary', {})
                if any(summary.get(k, 0) > 0 for k in ['commits', 'issues', 'pull_requests']):
                    report = report_generator.generate_notification_report(repo, updates)
                    notifier.notify(report, repo)
                    LOG.info(f"Notification sent for repository: {repo}")
                else:
                    LOG.info(f"No significant updates for {repo}")
            except Exception as e:
                LOG.error(f"Error checking updates for {repo}: {e}")
    except Exception as e:
        LOG.error(f"Error in scheduled job: {e}")

def main():
    LOG.info("🚀 GitHub Sentinel v0.7 - Simple Daemon Process (Schedule-based)")
    config = Config()
    # Schedule the job at the configured time, every N days
    schedule_time = config.github_progress_execution_time
    frequency_days = config.github_progress_frequency_days
    schedule.every(frequency_days).days.at(schedule_time).do(run_github_progress_job)
    LOG.info(f"Scheduled GitHub progress job every {frequency_days} day(s) at {schedule_time}")
    # Run once at startup
    run_github_progress_job()
    # Main loop
    while not graceful_exit:
        schedule.run_pending()
        time.sleep(1)
    LOG.info("GitHub Sentinel Daemon exited cleanly.")

if __name__ == '__main__':
    main() 