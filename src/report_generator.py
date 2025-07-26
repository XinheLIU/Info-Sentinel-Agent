import os
from datetime import date, timedelta, datetime
from typing import Optional
from llm_client import LLMClient
from logger import LOG


class ReportGenerator:
    """Simplified report generator with separated export cache and AI reports"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None, 
                 export_cache_dir: str = "reports/exports", 
                 ai_reports_dir: str = "reports/ai_reports"):
        """Initialize with LLM client and separate directories for cache and reports"""
        self.llm = llm_client
        self.export_cache_dir = export_cache_dir
        self.ai_reports_dir = ai_reports_dir
        
        # Create directories if they don't exist
        os.makedirs(self.export_cache_dir, exist_ok=True)
        os.makedirs(self.ai_reports_dir, exist_ok=True)
    
    def _has_meaningful_updates(self, updates: dict) -> bool:
        """
        Check if the updates contain meaningful activity
        
        Args:
            updates: Updates dictionary from GitHub API
            
        Returns:
            True if there are meaningful updates, False otherwise
        """
        summary = updates.get('summary', {})
        return any(summary.get(k, 0) > 0 for k in ['commits', 'issues', 'pull_requests'])
    
    def _generate_no_change_content(self, repo: str, date_info: str) -> str:
        """
        Generate simple content for when there are no changes
        
        Args:
            repo: Repository name
            date_info: Date information string
            
        Returns:
            Simple markdown content indicating no changes
        """
        return f"""# No Activity Report for {repo}

{date_info}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

No significant activity found for this period.

- **Issues:** 0
- **Pull Requests:** 0  
- **Commits:** 0

*This repository had no commits, issues, or pull requests during the specified time period.*
"""
    
    def export_daily_progress(self, repo: str, updates: dict) -> str:
        """Export daily progress for a repository (today)"""
        # Validate repo parameter
        if not repo:
            raise ValueError("Repository name cannot be None or empty")
        
        # Build repository directory path using export cache directory
        repo_dir = os.path.join(self.export_cache_dir, repo.replace("/", "_"))
        os.makedirs(repo_dir, exist_ok=True)
        
        # Create and write daily progress markdown file
        file_path = os.path.join(repo_dir, f'{date.today()}.md')
        
        # Check if there are meaningful updates
        if not self._has_meaningful_updates(updates):
            LOG.info(f"No meaningful updates found for {repo} on {date.today()}")
            date_info = f"**Date:** {date.today()}"
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self._generate_no_change_content(repo, date_info))
            LOG.info(f"Exported no-change progress to {file_path}")
            return file_path
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# Daily Progress for {repo} ({date.today()})\n\n")
            file.write(f"Generated: {date.today()}\n\n")
            
            # Write Issues section
            file.write("## Issues\n")
            if 'issues' in updates and updates['issues']:
                for issue in updates['issues']:
                    title = issue.get('title', 'No title')
                    number = issue.get('number', 'N/A')
                    state = issue.get('state', 'unknown')
                    file.write(f"- [{state.upper()}] {title} #{number}\n")
            else:
                file.write("No issues found.\n")
            
            # Write Pull Requests section
            file.write("\n## Pull Requests\n")
            if 'pull_requests' in updates and updates['pull_requests']:
                for pr in updates['pull_requests']:
                    title = pr.get('title', 'No title')
                    number = pr.get('number', 'N/A')
                    state = pr.get('state', 'unknown')
                    file.write(f"- [{state.upper()}] {title} #{number}\n")
            else:
                file.write("No pull requests found.\n")
        
        LOG.info(f"Exported daily progress to {file_path}")
        return file_path
    
    def export_progress_by_date_range(self, repo: str, updates: dict, days: int) -> str:
        """Export progress for a specific date range"""
        # Validate repo parameter
        if not repo:
            raise ValueError("Repository name cannot be None or empty")
        
        # Build directory and write date range progress markdown file using export cache directory
        repo_dir = os.path.join(self.export_cache_dir, repo.replace("/", "_"))
        os.makedirs(repo_dir, exist_ok=True)
        
        today = date.today()
        since = today - timedelta(days=days-1)  # Fix: days-1 to include today
        
        # Use cleaner filename format
        if days == 1:
            filename = f"{today}.md"
        else:
            filename = f"{today}_{days}days.md"
        
        file_path = os.path.join(repo_dir, filename)
        
        # Check if there are meaningful updates
        if not self._has_meaningful_updates(updates):
            LOG.info(f"No meaningful updates found for {repo} in last {days} days")
            date_info = f"**Date Range:** {since} to {today} ({days} days)"
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self._generate_no_change_content(repo, date_info))
            LOG.info(f"Exported no-change progress to {file_path}")
            return file_path
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# Progress for {repo} ({since} to {today})\n\n")
            file.write(f"Generated: {today}\n")
            file.write(f"Date Range: Last {days} days\n\n")
            
            # Write Issues section
            file.write(f"## Issues from Last {days} Days\n")
            if 'issues' in updates and updates['issues']:
                for issue in updates['issues']:
                    title = issue.get('title', 'No title')
                    number = issue.get('number', 'N/A')
                    state = issue.get('state', 'unknown')
                    file.write(f"- [{state.upper()}] {title} #{number}\n")
            else:
                file.write("No issues found.\n")
            
            # Write Pull Requests section
            file.write(f"\n## Pull Requests from Last {days} Days\n")
            if 'pull_requests' in updates and updates['pull_requests']:
                for pr in updates['pull_requests']:
                    title = pr.get('title', 'No title')
                    number = pr.get('number', 'N/A')
                    state = pr.get('state', 'unknown')
                    file.write(f"- [{state.upper()}] {title} #{number}\n")
            else:
                file.write("No pull requests found.\n")
        
        LOG.info(f"Exported time-range progress to {file_path}")
        return file_path
    
    def _get_ai_report_path(self, cache_file_path: str, suffix: str = "_report.md") -> str:
        """
        Generate AI report path from cache file path
        
        Args:
            cache_file_path: Path to the cache file in export_cache_dir
            suffix: Suffix to add to the filename
            
        Returns:
            Path for the AI report in ai_reports_dir
        """
        # Extract repo name and filename from cache path
        cache_filename = os.path.basename(cache_file_path)
        repo_name = os.path.basename(os.path.dirname(cache_file_path))
        
        # Create AI reports directory for this repo
        ai_repo_dir = os.path.join(self.ai_reports_dir, repo_name)
        os.makedirs(ai_repo_dir, exist_ok=True)
        
        # Generate report filename
        report_filename = cache_filename.replace('.md', suffix)
        return os.path.join(ai_repo_dir, report_filename)
    
    def _get_cache_file_path(self, repo: str, target_date: str = None, days: int = 1) -> str:
        """
        Get the expected cache file path for a repository and date
        
        Args:
            repo: Repository name
            target_date: Target date in YYYY-MM-DD format (defaults to today)
            days: Number of days for range reports
            
        Returns:
            Expected cache file path
        """
        if target_date is None:
            target_date = date.today().strftime('%Y-%m-%d')
        
        repo_dir = os.path.join(self.export_cache_dir, repo.replace("/", "_"))
        
        if days == 1:
            filename = f"{target_date}.md"
        else:
            filename = f"{target_date}_{days}days.md"
        
        return os.path.join(repo_dir, filename)
    
    def _cache_file_exists(self, repo: str, target_date: str = None, days: int = 1) -> bool:
        """
        Check if cache file already exists for the given repo and date
        
        Args:
            repo: Repository name
            target_date: Target date in YYYY-MM-DD format (defaults to today)
            days: Number of days for range reports
            
        Returns:
            True if cache file exists, False otherwise
        """
        cache_path = self._get_cache_file_path(repo, target_date, days)
        return os.path.exists(cache_path)
    
    def _has_meaningful_content(self, markdown_content: str) -> bool:
        """
        Check if the markdown content indicates meaningful activity
        
        Args:
            markdown_content: The markdown content to check
            
        Returns:
            True if there is meaningful content, False if it's a "no changes" report
        """
        # Check for "No Activity Report" title which indicates no changes
        if "# No Activity Report" in markdown_content:
            return False
        
        # Check for other indicators of no activity
        no_activity_indicators = [
            "No significant activity found",
            "No issues found",
            "No pull requests found", 
            "No commits found"
        ]
        
        # If the content contains mostly "no activity" indicators, it's not meaningful
        indicator_count = sum(1 for indicator in no_activity_indicators if indicator in markdown_content)
        return indicator_count < 3  # Allow some "No X found" but not all
    
    def generate_daily_report(self, markdown_file_path: str) -> tuple[str, str]:
        """Generate daily report from markdown file using LLM"""
        # Read markdown file and use LLM to generate report
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        # Check if there's meaningful content to analyze
        if not self._has_meaningful_content(markdown_content):
            LOG.info("No meaningful activity detected, skipping LLM report generation to save tokens")
            
            # Create a simple report file without using LLM in AI reports directory
            report_file_path = self._get_ai_report_path(markdown_file_path)
            simple_report = f"""# Daily Report - No Activity

**Status:** No meaningful activity detected for this period.

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

This repository had no significant commits, issues, or pull requests during the specified time period. No AI analysis was performed to conserve resources.

## Recommendation

Consider checking back when there is more activity to analyze.
"""
            with open(report_file_path, 'w', encoding='utf-8') as report_file:
                report_file.write(simple_report)
            
            LOG.info(f"Generated simple no-activity report saved to {report_file_path}")
            return simple_report, report_file_path
        
        # Generate report using LLM with new simplified interface
        LOG.info("Meaningful activity detected, generating AI-powered report")
        report = self.llm.generate_report_from_markdown(markdown_content)
        
        # Save report file in AI reports directory
        report_file_path = self._get_ai_report_path(markdown_file_path)
        with open(report_file_path, 'w', encoding='utf-8') as report_file:
            report_file.write(report)
        
        LOG.info(f"Generated daily report saved to {report_file_path}")
        return report, report_file_path
    
    def generate_report_by_date_range(self, markdown_file_path: str, days: int) -> tuple[str, str]:
        """Generate report for specific date range, similar to daily report generation"""
        # Read markdown file and use LLM to generate range report
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        # Check if there's meaningful content to analyze
        if not self._has_meaningful_content(markdown_content):
            LOG.info(f"No meaningful activity detected for {days}-day period, skipping LLM report generation to save tokens")
            
            # Create a simple report file without using LLM in AI reports directory
            report_file_path = self._get_ai_report_path(markdown_file_path)
            simple_report = f"""# {days}-Day Period Report - No Activity

**Status:** No meaningful activity detected for this {days}-day period.

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

This repository had no significant commits, issues, or pull requests during the specified {days}-day time period. No AI analysis was performed to conserve resources.

## Recommendation

Consider checking back when there is more activity to analyze, or extend the time range to capture more activity.
"""
            with open(report_file_path, 'w', encoding='utf-8') as report_file:
                report_file.write(simple_report)
            
            LOG.info(f"Generated simple no-activity report saved to {report_file_path}")
            return simple_report, report_file_path
        
        # Generate report using LLM with new simplified interface
        LOG.info(f"Meaningful activity detected for {days}-day period, generating AI-powered report")
        report = self.llm.generate_report_from_markdown(markdown_content)
        
        # Save report file in AI reports directory
        report_file_path = self._get_ai_report_path(markdown_file_path)
        with open(report_file_path, 'w', encoding='utf-8') as report_file:
            report_file.write(report)
        
        LOG.info(f"Generated date range report saved to {report_file_path}")
        return report, report_file_path
    
    def generate_report_with_auto_export(self, repo: str, target_date: str = None, days: int = 1, 
                                       github_client=None, interactive: bool = True) -> tuple[str, str]:
        """
        Generate report with automatic export if cache doesn't exist
        
        Args:
            repo: Repository name
            target_date: Target date in YYYY-MM-DD format (defaults to today)
            days: Number of days for range reports
            github_client: GitHub client for fetching data (required if cache doesn't exist)
            interactive: Whether to ask user confirmation in CLI mode
            
        Returns:
            Tuple of (report_content, report_file_path)
        """
        if target_date is None:
            target_date = date.today().strftime('%Y-%m-%d')
        
        # Check if cache file exists
        cache_path = self._get_cache_file_path(repo, target_date, days)
        
        if not self._cache_file_exists(repo, target_date, days):
            if github_client is None:
                raise ValueError("GitHub client is required to fetch data when cache doesn't exist")
            
            # Ask user confirmation in interactive mode
            if interactive:
                print(f"⚠️  Export cache not found for {repo} ({target_date}, {days} days)")
                print(f"📁 Expected cache file: {cache_path}")
                response = input("🤔 Would you like to run export-progress first? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    raise FileNotFoundError(f"Cache file not found: {cache_path}")
            
            # Auto-export the data
            LOG.info(f"Auto-exporting data for {repo} to create cache")
            from datetime import datetime, timedelta
            if days == 1:
                updates = github_client.fetch_updates(repo, since_date=target_date, until_date=target_date)
                cache_path = self.export_daily_progress(repo, updates)
            else:
                end_date = datetime.strptime(target_date, '%Y-%m-%d')
                start_date = end_date - timedelta(days=days-1)
                updates = github_client.fetch_updates(repo, 
                                                    since_date=start_date.strftime('%Y-%m-%d'), 
                                                    until_date=end_date.strftime('%Y-%m-%d'))
                cache_path = self.export_progress_by_date_range(repo, updates, days)
            
            print(f"✅ Export cache created: {cache_path}")
        
        # Now generate the report from cache
        if days == 1:
            return self.generate_daily_report(cache_path)
        else:
            return self.generate_report_by_date_range(cache_path, days)

    def generate_notification_report(self, repo: str, updates: dict) -> str:
        """Generate a notification report for a single repository from updates data"""
        report = f"# GitHub Sentinel Update Report\n\n"
        report += f"**Repository:** {repo}  \n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n\n"
        
        summary = updates.get('summary', {})
        report += f"## 📊 Summary\n\n"
        report += f"- **Commits:** {summary.get('commits', 0)}\n"
        report += f"- **Issues:** {summary.get('issues', 0)}\n"
        report += f"- **Pull Requests:** {summary.get('pull_requests', 0)}\n"
        
        # Add details for commits
        commits = updates.get('commits', [])
        if commits:
            report += f"## 💻 Recent Commits ({len(commits)})\n\n"
            for commit in commits[:5]:  # Show first 5 commits
                sha = commit.get('sha', '')[:8]
                message = commit.get('commit', {}).get('message', '').split('\n')[0]  # First line only
                author = commit.get('commit', {}).get('author', {}).get('name', 'Unknown')
                report += f"- **{sha}** by {author}: {message}\n"
            if len(commits) > 5:
                report += f"\n*... and {len(commits) - 5} more commits*\n"
            report += "\n"
        
        # Add details for issues
        issues = updates.get('issues', [])
        if issues:
            report += f"## 🐛 Recent Issues ({len(issues)})\n\n"
            for issue in issues[:5]:  # Show first 5 issues
                number = issue.get('number', 'N/A')
                title = issue.get('title', 'No title')
                state = issue.get('state', 'unknown')
                report += f"- **#{number}** [{state.upper()}]: {title}\n"
            if len(issues) > 5:
                report += f"\n*... and {len(issues) - 5} more issues*\n"
            report += "\n"
        
        # Add details for PRs
        prs = updates.get('pull_requests', [])
        if prs:
            report += f"## 🔄 Recent Pull Requests ({len(prs)})\n\n"
            for pr in prs[:5]:  # Show first 5 PRs
                number = pr.get('number', 'N/A')
                title = pr.get('title', 'No title')
                state = pr.get('state', 'unknown')
                report += f"- **#{number}** [{state.upper()}]: {title}\n"
            if len(prs) > 5:
                report += f"\n*... and {len(prs) - 5} more pull requests*\n"
            report += "\n"
        
        return report
