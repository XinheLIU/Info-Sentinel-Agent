import argparse
import os
import shlex
from datetime import datetime, timedelta
from typing import Optional

from config import Config
from github_client import GitHubClient
from subscription_manager import SubscriptionManager
from report_generator import ReportGenerator
from daily_progress import DailyProgressExporter
from llm_client import LLMClient, LLM


class CommandHandler:
    """Handles all command-line interface logic for GitHubSentinel"""
    
    def __init__(self, config: Config, github_client: GitHubClient, 
                 subscription_manager: SubscriptionManager, 
                 report_generator: ReportGenerator, notifier=None):
        """
        Initialize the command handler
        
        Args:
            config: Application configuration
            github_client: GitHub API client
            subscription_manager: Repository subscription manager
            report_generator: Report generation service
            notifier: Optional notifier for email notifications
        """
        self.config = config
        self.github_client = github_client
        self.subscription_manager = subscription_manager
        self.report_generator = report_generator
        self.notifier = notifier
        
        # Initialize parser
        self.parser = self._create_parser()
        self._setup_commands()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser"""
        parser = argparse.ArgumentParser(description='GitHub Sentinel Command Line Interface v0.7')
        subparsers = parser.add_subparsers(title='Commands', dest='command')
        
        # Store subparsers for command setup
        self.subparsers = subparsers
        return parser
    
    def _setup_commands(self):
        """Setup all available commands"""
        # Add subscription
        parser_add = self.subparsers.add_parser('add', help='Add a subscription')
        parser_add.add_argument('repo', type=str, help='Repository to subscribe to (e.g., owner/repo)')
        parser_add.set_defaults(func=self._add_subscription)
        
        # Remove subscription
        parser_remove = self.subparsers.add_parser('remove', help='Remove a subscription')
        parser_remove.add_argument('repo', type=str, help='Repository to unsubscribe from (e.g., owner/repo)')
        parser_remove.set_defaults(func=self._remove_subscription)
        
        # List subscriptions
        parser_list = self.subparsers.add_parser('list', help='List all subscriptions')
        parser_list.set_defaults(func=self._list_subscriptions)
        
        # Export progress
        parser_export = self.subparsers.add_parser('export-progress', help='Export daily progress to markdown files')
        parser_export.add_argument('--repo', type=str, help='Specific repository (optional)')
        parser_export.add_argument('--date', type=str, help='Target date in YYYY-MM-DD format (optional)')
        parser_export.add_argument('--days', type=int, default=1, help='Number of days back to export (default: 1)')
        parser_export.set_defaults(func=self._export_daily_progress)
        
        # Generate report
        parser_report = self.subparsers.add_parser('generate-report', help='Generate LLM-powered daily reports')
        parser_report.add_argument('--repo', type=str, help='Specific repository (optional)')
        parser_report.add_argument('--date', type=str, help='Target date in YYYY-MM-DD format (optional)')
        parser_report.add_argument('--days', type=int, default=1, help='Number of days back to include (default: 1)')
        parser_report.add_argument('--email', action='store_true', help='Send report via email after generation')
        parser_report.set_defaults(func=self._generate_daily_report)
        
        # Daily workflow
        parser_workflow = self.subparsers.add_parser('daily-workflow', help='Run complete daily workflow')
        parser_workflow.add_argument('--date', type=str, help='Target date in YYYY-MM-DD format (optional)')
        parser_workflow.add_argument('--days', type=int, default=1, help='Number of days back to process (default: 1)')
        parser_workflow.set_defaults(func=self._run_full_daily_workflow)
        
        # Help
        parser_help = self.subparsers.add_parser('help', help='Show this help message')
        parser_help.set_defaults(func=self.print_help)
    
    def _add_subscription(self, args):
        """Add a repository subscription"""
        self.subscription_manager.add_subscription(args.repo)
        print(f"Added subscription: {args.repo}")
    
    def _remove_subscription(self, args):
        """Remove a repository subscription"""
        self.subscription_manager.remove_subscription(args.repo)
        print(f"Removed subscription: {args.repo}")
    
    def _list_subscriptions(self, args):
        """List all current subscriptions"""
        subscriptions = self.subscription_manager.get_subscriptions()
        print("Current subscriptions:")
        for sub in subscriptions:
            print(f"- {sub}")
    
    def _get_date_range(self, args) -> tuple[str, str, int]:
        """Parse date and days arguments to get a date range"""
        days_back = getattr(args, 'days', 1)
        target_date_str = getattr(args, 'date', None)

        if target_date_str:
            end_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.now()

        start_date = end_date - timedelta(days=days_back - 1)
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), days_back

    def _export_daily_progress(self, args):
        """Export daily progress for subscribed repositories"""
        start_date, end_date, days_back = self._get_date_range(args)
        
        repos_to_process = [args.repo] if hasattr(args, 'repo') and args.repo else self.subscription_manager.get_subscriptions()
        
        exported_count = 0
        for repo in repos_to_process:
            try:
                if repo.lower() == "hackernews":
                    filepath = self.report_generator.export_hackernews_report()
                else:
                    updates = self.github_client.fetch_updates(repo, since_date=start_date, until_date=end_date)
                    if days_back == 1:
                        filepath = self.report_generator.export_daily_progress(repo, updates)
                    else:
                        filepath = self.report_generator.export_progress_by_date_range(repo, updates, days_back)
                
                print(f"- {repo}: {filepath}")
                exported_count += 1
            except Exception as e:
                print(f"- {repo}: Error - {e}")
        
        print(f"\nDaily progress exported for {exported_count}/{len(repos_to_process)} repositories")
    
    def _check_llm_availability(self) -> bool:
        """Check if the LLM provider is properly configured"""
        # Try first with existing LLM instance if available
        if self.report_generator.llm is not None:
            is_available, error_message = self.report_generator.llm.is_available()
            if is_available:
                return True
            else:
                print(error_message)
                return False
        
        # If no LLM instance, check availability statically
        is_available, error_message = LLM.check_availability(self.config)
        if not is_available:
            print(error_message)
            print(f"   → For help, see: https://github.com/xinheliu/GitHubSentinel#quick-start")
        
        return is_available

    def _generate_daily_report(self, args):
        """Generate LLM-powered daily reports"""
        if not self._check_llm_availability():
            return
        
        start_date, end_date, days_back = self._get_date_range(args)
        
        repos_to_process = [args.repo] if hasattr(args, 'repo') and args.repo else self.subscription_manager.get_subscriptions()
        
        generated_count = 0
        for repo in repos_to_process:
            try:
                report, report_path = self.report_generator.generate_report_with_auto_export(
                    repo=repo,
                    target_date=end_date, 
                    days=days_back,
                    github_client=self.github_client,
                    interactive=len(repos_to_process) == 1  # Interactive only if single repo
                )
                print(f"- {repo}: {report_path}")
                
                # Send email notification if requested
                email_requested = getattr(args, 'email', False)
                if email_requested and self.notifier:
                    try:
                        self.notifier.notify(report, repo)
                        print(f"  📧 Email sent for {repo}")
                    except Exception as e:
                        print(f"  ⚠️ Email failed for {repo}: {e}")
                
                generated_count += 1
            except FileNotFoundError as e:
                print(f"❌ Export cancelled by user: {e}")
            except Exception as e:
                print(f"- {repo}: Error generating report - {e}")
        
        print(f"\n📊 Daily reports generated for {generated_count}/{len(repos_to_process)} repositories")
        print("💡 Reports are now organized in separate directories:")
        print(f"   📁 Export cache: {self.config.export_cache_dir}")
        print(f"   🤖 AI reports: {self.config.ai_reports_dir}")
    
    def _run_full_daily_workflow(self, args):
        """Run the complete daily workflow: export progress + generate reports"""
        start_date, end_date, days_back = self._get_date_range(args)
        
        print(f"Running full daily workflow for {end_date} ({days_back} days back)...")
        
        # Step 1: Export daily progress
        print("\n1. Exporting daily progress...")
        self._export_daily_progress(args)
        
        # Step 2: Generate reports (if LLM is available)
        if self._check_llm_availability():
            print("\n2. Generating daily reports...")
            self._generate_daily_report(args)
        
        print("\nDaily workflow completed!")
    
    def print_help(self, args=None):
        """Print help information"""
        help_text = """
GitHub Sentinel Command Line Interface (v0.7)

Available commands:
  add <repo|hackernews>     Add a subscription (e.g., owner/repo or hackernews)
  remove <repo|hackernews>  Remove a subscription
  list                      List all subscriptions
  
  export-progress [--repo <repo>] [--date YYYY-MM-DD] [--days N]
                            Export daily progress to markdown files
                            --days: Number of days back to export (default: 1)
  
  generate-report [--repo <repo>] [--date YYYY-MM-DD] [--days N]
                            Generate LLM-powered daily reports
                            --days: Number of days back to include (default: 1)
  
  daily-workflow [--date YYYY-MM-DD] [--days N]
                            Run complete daily workflow (export + report)
                            --days: Number of days back to process (default: 1)
  
  help                      Show this help message
  exit                      Exit the tool
  quit                      Exit the tool

Examples:
  export-progress --repo owner/repo --days 7
  generate-report --days 3
  daily-workflow --date 2024-01-15 --days 5

Note: Set DEEPSEEK_API_KEY (default) or OPENAI_API_KEY environment variable for LLM features.

Tip: GitHubSentinel v0.7 also supports daemon and web interface modes!
     Run 'python src/main.py --help' to see all execution modes.
"""
        print(help_text)
    
    def execute_command(self, command_line: str):
        """Execute a command from a string"""
        try:
            args = self.parser.parse_args(shlex.split(command_line))
            if args.command is not None:
                args.func(args)
            else:
                self.parser.print_help()
        except Exception as e:
            print(f"Error: {e}")
    
    def run_interactive(self):
        """Run the interactive command loop"""
        self.print_help()
        
        while True:
            try:
                user_input = input("GitHub Sentinel v0.7> ")
                if user_input in ["exit", "quit"]:
                    print("Exiting GitHub Sentinel...")
                    break
                self.execute_command(user_input)
            except KeyboardInterrupt:
                print("\nExiting GitHub Sentinel...")
                break
            except Exception as e:
                print(f"Error: {e}")
