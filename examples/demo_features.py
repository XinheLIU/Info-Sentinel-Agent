#!/usr/bin/env python3
"""
GitHubSentinel Feature Demonstration (v0.2+)

This script demonstrates the core features available from version 0.2 onwards:
1. Daily Progress Export
2. LLM-powered Report Generation (DeepSeek/OpenAI)
3. Complete Workflow Integration

Usage:
    python examples/demo_features.py
"""

import os
import sys
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from github_client import GitHubClient
from daily_progress import DailyProgressExporter
from llm_client import LLMClient
from report_generator import ReportGenerator
from subscription_manager import SubscriptionManager

def demo_daily_progress_export(config, github_client, subscriptions):
    """Demonstrate daily progress export functionality"""
    print("🔄 Demo: Daily Progress Export")
    print("=" * 50)
    
    # Initialize daily progress exporter
    exporter = DailyProgressExporter(output_dir=config.daily_progress_dir)
    
    # Example: Export for yesterday (to ensure we have some data)
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"📅 Exporting daily progress for {yesterday}")
    
    # Export for first subscription (if any)
    if subscriptions:
        repo = subscriptions[0]
        try:
            filepath = exporter.export_daily_activity(github_client, repo, yesterday)
            print(f"✅ Exported: {filepath}")
            
            # Show file size and brief content preview
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath) / 1024  # KB
                print(f"📊 File size: {file_size:.1f} KB")
                
                with open(filepath, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    print(f"📄 Content preview (first 10 lines):")
                    for i, line in enumerate(lines[:10]):
                        print(f"   {i+1}: {line}")
                    if len(lines) > 10:
                        print(f"   ... and {len(lines)-10} more lines")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⚠️  No subscriptions found. Add repositories first.")
    
    print()

def demo_llm_report_generation(config):
    """Demonstrate LLM-powered report generation"""
    print("🤖 Demo: LLM Report Generation")
    print("=" * 50)
    
    try:
        # Initialize LLM client
        llm_client = LLMClient(config)
        provider = config.get_llm_provider()
        print(f"🔗 Connected to {provider} model: {config.llm_model}")
        
        # Example: Generate a simple summary
        sample_content = """
        ## Issues
        - Issue #123: Memory leak in extension system (open, bug)
        - Issue #124: Feature request for dark theme (closed, enhancement)
        
        ## Pull Requests  
        - PR #456: Fix memory leak in extension loader (merged)
        - PR #457: Add dark theme support (open, in review)
        """
        
        print("📝 Generating sample summary...")
        summary = llm_client.generate_summary(sample_content)
        print("✅ Generated Summary:")
        print("-" * 30)
        print(summary)
        print("-" * 30)
        
    except Exception as e:
        print(f"❌ Error with LLM: {e}")
    
    print()

def demo_complete_workflow(config, github_client, subscriptions):
    """Demonstrate the complete v0.2 workflow"""
    print("🔄 Demo: Complete v0.2 Workflow")
    print("=" * 50)
    
    if not subscriptions:
        print("⚠️  No subscriptions found. Add repositories first.")
        print()
        return
    
    # Yesterday's date for demo
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"📅 Running complete workflow for {yesterday}")
    print(f"📚 Repositories: {', '.join(subscriptions[:3])}{'...' if len(subscriptions) > 3 else ''}")
    
    try:
        # Step 1: Export daily progress
        print("\n📤 Step 1: Exporting daily progress...")
        exporter = DailyProgressExporter(output_dir=config.daily_progress_dir)
        
        exported_files = []
        for repo in subscriptions[:2]:  # Limit to first 2 repos for demo
            try:
                filepath = exporter.export_daily_activity(github_client, repo, yesterday)
                exported_files.append(filepath)
                print(f"   ✅ {repo} → {os.path.basename(filepath)}")
            except Exception as e:
                print(f"   ❌ {repo} → Error: {e}")
        
        # Step 2: Generate reports (if LLM configured)
        if config.enable_daily_reports:
            print("\n🤖 Step 2: Generating AI reports...")
            try:
                llm_client = LLMClient(config)
                report_generator = ReportGenerator(llm_client=llm_client)
                
                for repo in subscriptions[:2]:  # Limit to first 2 repos for demo
                    try:
                        report_path = report_generator.generate_daily_report(repo, yesterday, config.daily_progress_dir)
                        print(f"   ✅ {repo} → {os.path.basename(report_path)}")
                    except FileNotFoundError:
                        print(f"   ⚠️  {repo} → No progress data found")
                    except Exception as e:
                        print(f"   ❌ {repo} → Error: {e}")
                        
            except Exception as e:
                print(f"   ❌ LLM Error: {e}")
        else:
            print(f"\n⚠️  Step 2: Skipping AI reports (daily reports disabled)")
        
        print("\n✅ Workflow completed!")
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")
    
    print()

def show_directory_structure(config):
    """Show the created directory structure"""
    print("📁 Demo: Generated Files Structure")
    print("=" * 50)
    
    def show_directory(path, prefix=""):
        if not os.path.exists(path):
            print(f"{prefix}📂 {path} (not created yet)")
            return
            
        print(f"{prefix}📂 {path}/")
        try:
            files = sorted(os.listdir(path))
            for i, file in enumerate(files[:5]):  # Show max 5 files
                is_last = i == len(files) - 1 or i == 4
                connector = "└── " if is_last else "├── "
                print(f"{prefix}    {connector}📄 {file}")
            
            if len(files) > 5:
                print(f"{prefix}    └── ... and {len(files) - 5} more files")
        except PermissionError:
            print(f"{prefix}    (Permission denied)")
    
    print("Generated reports structure:")
    show_directory(config.daily_progress_dir)
    show_directory(config.daily_reports_dir)
    print()

def main():
    """Main demonstration function"""
    print("🚀 GitHubSentinel Core Features Demo")
    print("=" * 50)
    print()
    
    try:
        # Load configuration
        config = Config()
        print(f"⚙️  Configuration loaded")
        print(f"   GitHub Token: {'✅ Set' if config.github_token else '❌ Missing'}")
        provider = config.get_llm_provider()
        api_key = config.get_llm_api_key()
        print(f"   LLM Provider: {provider.upper()}")
        print(f"   LLM Model: {config.llm_model}")
        print(f"   API Key Required: {'No' if provider == 'ollama' else 'Yes'}")
        if provider != 'ollama':
            print(f"   API Key Status: {'✅ Set' if api_key else '❌ Missing'}")
        print(f"   Daily Reports: {'✅ Enabled' if config.enable_daily_reports else '❌ Disabled'}")
        print()
        
        # Initialize clients
        github_client = GitHubClient(config.github_token)
        subscription_manager = SubscriptionManager(config.subscriptions_file)
        subscriptions = subscription_manager.get_subscriptions()
        
        print(f"📚 Subscribed repositories: {len(subscriptions)}")
        if subscriptions:
            for repo in subscriptions[:3]:
                print(f"   - {repo}")
            if len(subscriptions) > 3:
                print(f"   ... and {len(subscriptions) - 3} more")
        else:
            print("   (No repositories subscribed yet)")
        print()
        
        # Run demonstrations
        demo_daily_progress_export(config, github_client, subscriptions)
        demo_llm_report_generation(config)
        demo_complete_workflow(config, github_client, subscriptions)
        show_directory_structure(config)
        
        print("🎉 Demo completed!")
        print()
        print("Next steps:")
        print("1. Add repositories: python src/main.py add <owner/repo>")
        print("2. Export progress: python src/main.py export-progress")
        print("3. Generate reports: python src/main.py generate-report")
        print("4. Run full workflow: python src/main.py daily-workflow")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 