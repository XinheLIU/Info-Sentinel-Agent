import os
from datetime import datetime
from typing import List
from logger import LOG


class DailyProgressExporter:
    """Export daily GitHub activity to structured markdown files"""
    
    def __init__(self, output_dir: str = "reports/daily_progress"):
        """
        Initialize the Daily Progress Exporter
        
        Args:
            output_dir: Base directory for daily progress files
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    def _create_file_path(self, repo: str, target_date: str, until_date: str = None) -> str:
        """
        Create file path with two-level directory structure
        
        Args:
            repo: Repository name in format 'owner/repo'
            target_date: Target date in YYYY-MM-DD format
            until_date: Optional end date for date ranges
            
        Returns:
            Full file path for the daily progress file
        """
        # Convert repo name to safe directory name
        repo_name = repo.replace('/', '_').replace('-', '_')
        
        # Create repo-specific directory
        repo_dir = os.path.join(self.output_dir, repo_name)
        os.makedirs(repo_dir, exist_ok=True)
        
        # Create filename based on date range
        if until_date and until_date != target_date:
            # Date range format: from_YYYYMMDD_to_YYYYMMDD.md
            start_date_clean = target_date.replace('-', '')
            end_date_clean = until_date.replace('-', '')
            filename = f"from_{start_date_clean}_to_{end_date_clean}.md"
        else:
            # Single date format: YYYY-MM-DD.md
            filename = f"{target_date}.md"
        
        return os.path.join(repo_dir, filename)

    def export_daily_activity(self, github_client, repo: str, target_date: str, until_date: str = None) -> str:
        """
        Export daily activity for a single repository
        
        Args:
            github_client: GitHubClient instance
            repo: Repository name in format 'owner/repo'
            target_date: Target date in YYYY-MM-DD format
            until_date: Optional end date for date ranges
            
        Returns:
            Path to the generated markdown file
        """
        # Get activity data using the new method name
        activity_data = github_client.export_process_by_date_range(repo, target_date, until_date)
        
        # Create the markdown content
        markdown_content = self._generate_markdown(repo, target_date, until_date, activity_data)
        
        # Create file path and save
        filepath = self._create_file_path(repo, target_date, until_date)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        LOG.info(f"Daily progress exported to {filepath}")
        return filepath

    def export_multiple_repos(self, github_client, repos: List[str], target_date: str, until_date: str = None) -> List[str]:
        """
        Export daily activity for multiple repositories
        
        Args:
            github_client: GitHubClient instance
            repos: List of repository names in format 'owner/repo'
            target_date: Target date in YYYY-MM-DD format
            until_date: Optional end date for date ranges
            
        Returns:
            List of paths to generated markdown files
        """
        exported_files = []
        
        for repo in repos:
            try:
                filepath = self.export_daily_activity(github_client, repo, target_date, until_date)
                exported_files.append(filepath)
            except Exception as e:
                LOG.error(f"Failed to export daily activity for {repo}: {str(e)}")
        
        return exported_files

    def get_exported_file_path(self, repo: str, target_date: str, until_date: str = None) -> str:
        """
        Get the file path for an exported daily progress file without creating it
        
        Args:
            repo: Repository name in format 'owner/repo'
            target_date: Target date in YYYY-MM-DD format
            until_date: Optional end date for date ranges
            
        Returns:
            Expected file path for the daily progress file
        """
        return self._create_file_path(repo, target_date, until_date)

    def _generate_markdown(self, repo: str, target_date: str, until_date: str, activity_data: dict) -> str:
        """Generate markdown content from activity data"""
        
        # Create title based on date range
        if until_date and until_date != target_date:
            title = f"Daily Progress Report: {repo} ({target_date} to {until_date})"
            date_info = f"**Date Range:** {target_date} to {until_date}"
        else:
            title = f"Daily Progress Report: {repo} ({target_date})"
            date_info = f"**Date:** {target_date}"
        
        markdown_content = f"# {title}\n\n"
        markdown_content += f"{date_info}\n"
        markdown_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Add summary section
        summary = activity_data.get('summary', {})
        markdown_content += "## Summary\n\n"
        markdown_content += f"- **Commits:** {summary.get('commits', 0)}\n"
        markdown_content += f"- **Issues:** {summary.get('issues', 0)}\n"
        markdown_content += f"- **Pull Requests:** {summary.get('pull_requests', 0)}\n\n"
        
        # Add commits section
        commits = activity_data.get('commits', [])
        if commits:
            markdown_content += "## Commits\n\n"
            for commit in commits:
                commit_sha = commit.get('sha', '')[:8]
                commit_message = commit.get('commit', {}).get('message', '').split('\n')[0]  # First line only
                commit_author = commit.get('commit', {}).get('author', {}).get('name', 'Unknown')
                commit_date = commit.get('commit', {}).get('author', {}).get('date', '')
                
                markdown_content += f"- **{commit_sha}** by {commit_author}\n"
                markdown_content += f"  - {commit_message}\n"
                if commit_date:
                    markdown_content += f"  - Date: {commit_date}\n"
                markdown_content += "\n"
        else:
            markdown_content += "## Commits\n\nNo commits found for this date range.\n\n"
        
        # Add issues section
        issues = activity_data.get('issues', [])
        if issues:
            markdown_content += "## Issues\n\n"
            for issue in issues:
                issue_number = issue.get('number', '')
                issue_title = issue.get('title', '')
                issue_state = issue.get('state', '')
                issue_author = issue.get('user', {}).get('login', 'Unknown')
                issue_date = issue.get('created_at', '') or issue.get('updated_at', '')
                
                markdown_content += f"- **#{issue_number}** [{issue_state.upper()}] {issue_title}\n"
                markdown_content += f"  - Author: {issue_author}\n"
                if issue_date:
                    markdown_content += f"  - Date: {issue_date}\n"
                markdown_content += "\n"
        else:
            markdown_content += "## Issues\n\nNo issues found for this date range.\n\n"
        
        # Add pull requests section
        pull_requests = activity_data.get('pull_requests', [])
        if pull_requests:
            markdown_content += "## Pull Requests\n\n"
            for pr in pull_requests:
                pr_number = pr.get('number', '')
                pr_title = pr.get('title', '')
                pr_state = pr.get('state', '')
                pr_author = pr.get('user', {}).get('login', 'Unknown')
                pr_date = pr.get('created_at', '') or pr.get('updated_at', '')
                
                markdown_content += f"- **#{pr_number}** [{pr_state.upper()}] {pr_title}\n"
                markdown_content += f"  - Author: {pr_author}\n"
                if pr_date:
                    markdown_content += f"  - Date: {pr_date}\n"
                markdown_content += "\n"
        else:
            markdown_content += "## Pull Requests\n\nNo pull requests found for this date range.\n\n"
        
        return markdown_content 