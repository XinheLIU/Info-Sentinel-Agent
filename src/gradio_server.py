#!/usr/bin/env python3

"""
GitHub Sentinel - Gradio Server Mode
Simplified web interface for GitHub repository monitoring and reporting.

Version: 0.4
"""

import sys
import os
import threading
import time
import signal
import atexit
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import gradio as gr
except ImportError:
    print("Error: Gradio is not installed. Please run: pip install gradio")
    sys.exit(1)

from config import Config
from github_client import GitHubClient
from subscription_manager import SubscriptionManager
from report_generator import ReportGenerator
from command_handler import CommandHandler
from scheduler import Scheduler
from notifier import Notifier
from llm_client import LLMClient, LLM
from logger import LOG


class GitHubSentinelGradio:
    """Simplified Gradio web interface for GitHub Sentinel"""
    
    def __init__(self):
        """Initialize the Gradio interface server"""
        try:
            LOG.info("Initializing GitHub Sentinel web interface components...")
            
            self.config = Config()
            self.github_client = GitHubClient(self.config.github_token)
            self.subscription_manager = SubscriptionManager(self.config.subscriptions_file)
            self.notifier = Notifier(self.config.notification_settings)
            
            # Initialize LLM client with new availability checking
            self.llm_client = None
            is_available, error_message = LLM.check_availability(self.config)
            if is_available:
                try:
                    self.llm_client = LLMClient(self.config)
                    provider = self.config.get_llm_provider()
                    LOG.info(f"LLM client initialized with {provider.upper()} provider")
                except Exception as e:
                    LOG.warning(f"LLM client initialization failed: {e}. AI features will be unavailable.")
                    error_message = f"LLM initialization failed: {e}"
            else:
                LOG.warning(f"LLM provider not available. AI features will be unavailable.")
            
            self.llm_status = "✅ Ready" if self.llm_client else f"❌ Not Available: {error_message}"
            
            self.report_generator = ReportGenerator(
                llm_client=self.llm_client,
                export_cache_dir=self.config.export_cache_dir,
                ai_reports_dir=self.config.ai_reports_dir
            )
            
            LOG.info("All components initialized successfully")

        except Exception as e:
            LOG.error(f"Error initializing components: {e}")
            sys.exit(1)
    
    def get_subscription_list(self) -> List[str]:
        """Get list of subscribed repositories"""
        try:
            subscriptions = self.subscription_manager.get_subscriptions()
            if not subscriptions:
                return ["No repositories subscribed"]
            return subscriptions
        except Exception as e:
            LOG.error(f"Error getting subscriptions: {e}")
            return ["Error loading subscriptions"]
    
    def generate_report_with_download(self, repo: str, days: int) -> Tuple[str, str]:
        """Generate complete report and return both preview and file path for download"""
        try:
            # Validate inputs
            if not repo or repo == "No repositories subscribed" or repo == "Error loading subscriptions":
                return "❌ Error: Please select a valid repository from the dropdown.", None
            
            if not self.config.get_llm_api_key():
                return "❌ Error: No LLM API key configured. Please set DEEPSEEK_API_KEY or OPENAI_API_KEY environment variable.", None
            
            LOG.info(f"Generating report for {repo} with {days} days back")
            
            # Use auto-export functionality (no user interaction in web mode)
            today = datetime.now()
            target_date = today.strftime('%Y-%m-%d')
            
            report_content, report_file = self.report_generator.generate_report_with_auto_export(
                repo=repo,
                target_date=target_date,
                days=days,
                github_client=self.github_client,
                interactive=False  # Web mode - no user confirmation needed
            )
            
            # Create preview
            preview = f"""# ✅ Report Generated Successfully!

**Repository**: {repo}  
**Time Period**: Last {days} day(s)  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**File**: {os.path.basename(report_file)}

---

## 📊 Activity Summary

"""
            
            # Extract summary info from the report content or provide simple status
            if "No Activity Report" in report_content or "No meaningful activity" in report_content:
                preview += "- **Issues**: 0\n"
                preview += "- **Pull Requests**: 0\n"
                preview += "- **Commits**: 0\n"
                preview += "- **Status**: No activity detected\n\n"
            else:
                preview += "- **Status**: Activity detected and analyzed by AI\n"
                preview += "- **Report Type**: AI-powered analysis\n\n"
            
            preview += "---\n\n"
            preview += "**💡 The complete AI-generated report is available for download above.**"
            
            LOG.info(f"Report generated successfully: {report_file}")
            return preview, report_file
            
        except Exception as e:
            LOG.error(f"Error generating report: {e}")
            error_msg = f"❌ Error generating report: {str(e)}"
            return error_msg, None
    
    def create_interface(self):
        """Create the simplified Gradio interface"""
        
        # Get subscription list for dropdown
        subscription_choices = self.get_subscription_list()
        default_repo = subscription_choices[0] if subscription_choices and subscription_choices[0] != "No repositories subscribed" else None
        
        # Create the interface using gr.Interface for simplicity
        interface = gr.Interface(
            fn=self.generate_report_with_download,
            title="🚀 GitHubSentinel - AI-Powered Repository Reports",
            description="""
            **Generate intelligent reports for your GitHub repositories with AI analysis.**
            
            Simply select a repository and time range, then click submit to get your comprehensive report with AI insights.
            """,
            inputs=[
                gr.Dropdown(
                    choices=subscription_choices,
                    label="📚 Repository",
                    info="Select from your subscribed GitHub repositories",
                    value=default_repo
                ),
                gr.Slider(
                    value=1,
                    minimum=1,
                    maximum=30,
                    step=1,
                    label="📅 Report Period",
                    info="Number of days to analyze (1 = today only, 7 = last week, etc.)"
                )
            ],
            outputs=[
                gr.Markdown(label="📋 Report Preview"),
                gr.File(label="📥 Download Complete Report")
            ],
            examples=[
                ["langchain-ai/langchain", 1],
                ["microsoft/vscode", 3],
                ["openai/openai-python", 7]
            ],
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 900px;
                margin: auto;
            }
            .examples {
                margin-top: 20px;
            }
            """,
            allow_flagging="never"
        )
        
        return interface


def main():
    """Main entry point for GitHub Sentinel Gradio Server"""
    print("🚀 GitHub Sentinel v0.7 - Simplified Web Interface")
    print("=" * 50)
    
    try:
        # Initialize the Gradio interface
        sentinel = GitHubSentinelGradio()
        
        # Create and launch the interface
        interface = sentinel.create_interface()
        
        LOG.info("Starting simplified Gradio web interface...")
        print("\n✅ Web interface will be available at:")
        print("   Local:   http://localhost:7860")
        print("   Network: http://0.0.0.0:7860")
        print("\n💡 Simply select a repository and time range to generate reports!")
        
        interface.launch(
            server_name="0.0.0.0",  # Allow external connections
            server_port=7860,       # Default Gradio port
            share=False,            # Set to True to create a public link
            show_error=True,
            quiet=False
        )
        
    except KeyboardInterrupt:
        LOG.info("Shutting down Gradio server...")
        sys.exit(0)
    except Exception as e:
        LOG.error(f"Error starting Gradio server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 