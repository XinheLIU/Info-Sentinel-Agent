import requests
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dateutil import parser as date_parser
from logger import LOG


class GitHubClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_updates(self, repo: str, since_date: str = None, until_date: str = None) -> Dict[str, Any]:
        """
        Fetch comprehensive updates for a single repository
        
        Args:
            repo: Repository name in format 'owner/repo'
            since_date: Start date in YYYY-MM-DD format (optional)
            until_date: End date in YYYY-MM-DD format (optional)
            
        Returns:
            Dictionary containing commits, issues, pull_requests, and summary
        """
        LOG.info(f"Fetching comprehensive updates for {repo}")
        
        # Fetch all data types
        commits = self.fetch_commits(repo, since_date, until_date)
        issues = self.fetch_issues(repo, since_date, until_date)
        pull_requests = self.fetch_pull_requests(repo, since_date, until_date)
        
        # Create summary statistics
        summary = {
            'commits': len(commits),
            'issues': len(issues),
            'pull_requests': len(pull_requests),
            'total_commits': len(commits),
            'total_issues': len(issues),
            'total_prs': len(pull_requests)
        }
        
        updates = {
            'commits': commits,
            'issues': issues,
            'pull_requests': pull_requests,
            'summary': summary
        }
        
        LOG.info(f"Fetched {updates['summary']['total_commits']} commits, "
                f"{updates['summary']['total_issues']} issues, "
                f"{updates['summary']['total_prs']} pull requests for {repo}")
        
        return updates

    def fetch_commits(self, repo: str, since_date: str = None, until_date: str = None, state: str = "all") -> List[Dict]:
        """
        Fetch commits for a repository within a date range
        
        Args:
            repo: Repository name in format 'owner/repo'
            since_date: Start date in YYYY-MM-DD format (optional)
            until_date: End date in YYYY-MM-DD format (optional)
            state: Not used for commits, included for consistency
            
        Returns:
            List of commit dictionaries
        """
        url = f"{self.base_url}/repos/{repo}/commits"
        params = {"per_page": 100}
        
        # Add date filters if provided
        if since_date:
            # Convert YYYY-MM-DD to ISO format for GitHub API
            since_datetime = datetime.strptime(since_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            params["since"] = since_datetime.isoformat()
        
        if until_date:
            # Convert YYYY-MM-DD to ISO format for GitHub API
            until_datetime = datetime.strptime(until_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            params["until"] = until_datetime.isoformat()
        
        commits = []
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            commits = response.json()
            
            LOG.info(f"Fetched {len(commits)} commits for {repo}")
            
        except requests.exceptions.RequestException as e:
            LOG.error(f"Error fetching commits for {repo}: {str(e)}")
            
        return commits

    def _filter_by_date_range(self, items: List[Dict], since_date: str = None, until_date: str = None) -> List[Dict]:
        """Filter a list of items by date range"""
        if not since_date and not until_date:
            return items

        filtered_items = []
        since_datetime = datetime.strptime(since_date, '%Y-%m-%d').replace(tzinfo=timezone.utc) if since_date else None
        until_datetime = datetime.strptime(until_date, '%Y-%m-%d').replace(tzinfo=timezone.utc) if until_date else None

        for item in items:
            item_date_str = item.get('updated_at') or item.get('created_at')
            if not item_date_str:
                continue

            item_date = date_parser.parse(item_date_str)

            if since_datetime and item_date < since_datetime:
                continue
            if until_datetime and item_date > until_datetime:
                continue
            
            filtered_items.append(item)

        return filtered_items

    def fetch_issues(self, repo: str, since_date: str = None, until_date: str = None, state: str = "closed") -> List[Dict]:
        """
        Fetch issues for a repository within a date range
        
        Args:
            repo: Repository name in format 'owner/repo'
            since_date: Start date in YYYY-MM-DD format (optional)
            until_date: End date in YYYY-MM-DD format (optional)
            state: Issue state filter ('open', 'closed', 'all'), defaults to 'closed'
            
        Returns:
            List of issue dictionaries
        """
        url = f"{self.base_url}/repos/{repo}/issues"
        params = {
            "state": state,
            "per_page": 100,
            "pull_request": "false"  # Exclude pull requests from issues
        }
        
        # Add date filter if provided
        if since_date:
            # Convert YYYY-MM-DD to ISO format for GitHub API
            since_datetime = datetime.strptime(since_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            params["since"] = since_datetime.isoformat()
        
        issues = []
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            all_issues = response.json()
            
            issues = self._filter_by_date_range(all_issues, since_date, until_date)
                
            LOG.info(f"Fetched {len(issues)} issues for {repo}")
            
        except requests.exceptions.RequestException as e:
            LOG.error(f"Error fetching issues for {repo}: {str(e)}")
            
        return issues

    def fetch_pull_requests(self, repo: str, since_date: str = None, until_date: str = None, state: str = "closed") -> List[Dict]:
        """
        Fetch pull requests for a repository within a date range
        
        Args:
            repo: Repository name in format 'owner/repo'
            since_date: Start date in YYYY-MM-DD format (optional)
            until_date: End date in YYYY-MM-DD format (optional)
            state: PR state filter ('open', 'closed', 'all'), defaults to 'closed'
            
        Returns:
            List of pull request dictionaries
        """
        url = f"{self.base_url}/repos/{repo}/pulls"
        params = {
            "state": state,
            "per_page": 100
        }
        
        pull_requests = []
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            all_prs = response.json()
            
            pull_requests = self._filter_by_date_range(all_prs, since_date, until_date)
                
            LOG.info(f"Fetched {len(pull_requests)} pull requests for {repo}")
            
        except requests.exceptions.RequestException as e:
            LOG.error(f"Error fetching pull requests for {repo}: {str(e)}")
            
        return pull_requests

    def export_process_by_date_range(self, repo: str, target_date: str, until_date: str = None) -> Dict[str, Any]:
        """
        Export daily activity for a repository on a specific date or date range
        
        Args:
            repo: Repository name in format 'owner/repo'
            target_date: Target date in YYYY-MM-DD format (acts as since_date for ranges)
            until_date: Optional end date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing activity data for the specified date(s)
        """
        LOG.info(f"Fetching daily activity for {repo} on {target_date}")
        
        # Use target_date as since_date and until_date (if not provided) for the day
        since_date = target_date
        end_date = until_date if until_date else target_date
        
        return self.fetch_updates(repo, since_date, end_date)

    def fetch_releases(self, subscriptions):
        """Legacy method for backward compatibility"""
        releases = {}
        for repo in subscriptions:
            url = f"{self.base_url}/repos/{repo}/releases/latest"
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    releases[repo] = response.json()
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                print(f"Error fetching releases for {repo}: {e}")
        return releases
