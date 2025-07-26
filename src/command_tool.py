#!/usr/bin/env python3
"""
GitHub Sentinel Command Line Tool
A standalone script that provides command-line functionality for GitHub Sentinel.
"""

import sys
import os
import shlex

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from github_client import GitHubClient
from subscription_manager import SubscriptionManager
from report_generator import ReportGenerator
from notifier import Notifier
from command_handler import CommandHandler
from logger import LOG
from llm_client import LLMClient, LLM


class GitHubSentinelCLI:
    """Command Line Interface for GitHub Sentinel"""
    
    def __init__(self):
        """Initialize the CLI application"""
        try:
            self.config = Config()
            self.github_client = GitHubClient(self.config.github_token)
            self.subscription_manager = SubscriptionManager(self.config.subscriptions_file)
            self.notifier = Notifier(self.config.notification_settings)
            
            # Initialize LLM client with new availability checking
            llm_client = None
            is_available, error_message = LLM.check_availability(self.config)
            if is_available:
                try:
                    llm_client = LLMClient(self.config)
                    provider = self.config.get_llm_provider()
                    LOG.info(f"LLM client initialized with {provider.upper()} provider")
                except Exception as e:
                    LOG.warning(f"LLM client initialization failed: {e}. AI features will be unavailable.")
            else:
                LOG.warning(f"LLM provider not available. AI features will be unavailable.")
            
            self.report_generator = ReportGenerator(
                llm_client=llm_client,
                export_cache_dir=self.config.export_cache_dir,
                ai_reports_dir=self.config.ai_reports_dir
            )
            
            self.command_handler = CommandHandler(
                config=self.config,
                github_client=self.github_client,
                subscription_manager=self.subscription_manager,
                report_generator=self.report_generator,
                notifier=self.notifier
            )
            
        except Exception as e:
            LOG.error(f"Error initializing CLI: {e}")
            sys.exit(1)


def main():
    """Main entry point for GitHub Sentinel Command Line Tool"""
    try:
        print("🚀 GitHub Sentinel v0.6 - Command Line Tool")
        print("=" * 50)
        
        cli = GitHubSentinelCLI()
        
        # Check if arguments were provided
        if len(sys.argv) > 1:
            # Execute command from command line arguments
            command_line = ' '.join(sys.argv[1:])
            cli.command_handler.execute_command(command_line)
        else:
            # Run interactive mode
            LOG.info("Starting interactive command line interface")
            cli.command_handler.print_help()
            
            while True:
                try:
                    user_input = input("GitHub Sentinel v0.6> ").strip()
                    if user_input.lower() in ['exit', 'quit']:
                        break
                    if not user_input:
                        continue
                        
                    try:
                        args = cli.command_handler.parser.parse_args(shlex.split(user_input))
                        if args.command is None:
                            continue
                        args.func(args)
                    except SystemExit:
                        LOG.error("Invalid command. Type 'help' to see the list of available commands.")
                except KeyboardInterrupt:
                    print("\nExiting GitHub Sentinel...")
                    break
                except Exception as e:
                    LOG.error(f"Unexpected error: {e}")
            
    except KeyboardInterrupt:
        print("\nExiting GitHub Sentinel...")
        sys.exit(0)
    except Exception as e:
        LOG.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 