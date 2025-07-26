import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from datetime import datetime

# Add src directory to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from github_client import GitHubClient

class TestGitHubClient(unittest.TestCase):
    def setUp(self):
        """Set up test GitHub client with mock token"""
        self.mock_token = "test_github_token"
        self.client = GitHubClient(self.mock_token)
        
        # Sample response data
        self.sample_commits = [
            {
                'sha': 'abc123def456',
                'commit': {
                    'message': 'Test commit message',
                    'author': {
                        'name': 'Test Author',
                        'date': '2024-01-01T10:00:00Z'
                    }
                }
            }
        ]
        
        self.sample_issues = [
            {
                'number': 1,
                'title': 'Test Issue',
                'state': 'open',
                'user': {'login': 'testuser'},
                'created_at': '2024-01-01T09:00:00Z',
                'updated_at': '2024-01-01T11:00:00Z',
                'pull_request': None  # This is an issue, not a PR
            }
        ]
        
        self.sample_pull_requests = [
            {
                'number': 2,
                'title': 'Test PR',
                'state': 'closed',
                'user': {'login': 'testuser'},
                'created_at': '2024-01-01T08:00:00Z',
                'updated_at': '2024-01-01T12:00:00Z'
            }
        ]
    
    def test_init(self):
        """Test GitHubClient initialization"""
        self.assertEqual(self.client.token, self.mock_token)
        self.assertEqual(self.client.base_url, "https://api.github.com")
        self.assertIn("Authorization", self.client.headers)
        self.assertEqual(self.client.headers["Authorization"], f"token {self.mock_token}")
    
    @patch('github_client.requests.get')
    def test_fetch_commits_success(self, mock_get):
        """Test successful commit fetching"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_commits
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.fetch_commits('test/repo', since_date='2024-01-01', until_date='2024-01-02')
        
        # Check API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('test/repo/commits', call_args[0][0])
        
        # Check parameters
        params = call_args[1]['params']
        self.assertIn('since', params)
        self.assertIn('until', params)
        
        # Check result
        self.assertEqual(result, self.sample_commits)
    
    @patch('github_client.requests.get')
    def test_fetch_issues_success(self, mock_get):
        """Test successful issue fetching"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_issues
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.fetch_issues('test/repo', since_date='2024-01-01', state='open')
        
        # Check API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('test/repo/issues', call_args[0][0])
        
        # Check parameters
        params = call_args[1]['params']
        self.assertEqual(params['state'], 'open')
        self.assertIn('since', params)
        self.assertEqual(params['pull_request'], 'false')  # Should exclude PRs
        
        # Check result
        self.assertEqual(result, self.sample_issues)
    
    @patch('github_client.requests.get')
    def test_fetch_pull_requests_success(self, mock_get):
        """Test successful pull request fetching"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_pull_requests
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.fetch_pull_requests('test/repo', state='closed')
        
        # Check API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('test/repo/pulls', call_args[0][0])
        
        # Check parameters
        params = call_args[1]['params']
        self.assertEqual(params['state'], 'closed')
        
        # Check result
        self.assertEqual(result, self.sample_pull_requests)
    
    @patch('github_client.requests.get')
    def test_fetch_updates_comprehensive(self, mock_get):
        """Test comprehensive update fetching"""
        # Mock responses for different endpoints
        def mock_response_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            
            if 'commits' in url:
                mock_response.json.return_value = self.sample_commits
            elif 'issues' in url:
                mock_response.json.return_value = self.sample_issues
            elif 'pulls' in url:
                mock_response.json.return_value = self.sample_pull_requests
            else:
                mock_response.json.return_value = []
            
            return mock_response
        
        mock_get.side_effect = mock_response_side_effect
        
        result = self.client.fetch_updates('test/repo', since_date='2024-01-01', until_date='2024-01-02')
        
        # Check that all three endpoints were called
        self.assertEqual(mock_get.call_count, 3)
        
        # Check result structure
        self.assertIn('commits', result)
        self.assertIn('issues', result)
        self.assertIn('pull_requests', result)
        self.assertIn('summary', result)
        
        # Check summary data
        summary = result['summary']
        self.assertEqual(summary['commits'], 1)
        self.assertEqual(summary['issues'], 1)
        self.assertEqual(summary['pull_requests'], 1)
        self.assertEqual(summary['total_commits'], 1)
        self.assertEqual(summary['total_issues'], 1)
        self.assertEqual(summary['total_prs'], 1)
        
        # Check actual data
        self.assertEqual(result['commits'], self.sample_commits)
        self.assertEqual(result['issues'], self.sample_issues)
        self.assertEqual(result['pull_requests'], self.sample_pull_requests)
    
    @patch('github_client.requests.get')
    def test_fetch_commits_with_error(self, mock_get):
        """Test commit fetching with API error"""
        # Mock error response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        result = self.client.fetch_commits('test/repo')
        
        # Should return empty list on error
        self.assertEqual(result, [])
    
    @patch('github_client.requests.get')
    def test_fetch_issues_with_error(self, mock_get):
        """Test issue fetching with API error"""
        # Mock error response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        result = self.client.fetch_issues('test/repo')
        
        # Should return empty list on error
        self.assertEqual(result, [])
    
    @patch('github_client.requests.get')
    def test_fetch_pull_requests_with_error(self, mock_get):
        """Test pull request fetching with API error"""
        # Mock error response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        result = self.client.fetch_pull_requests('test/repo')
        
        # Should return empty list on error
        self.assertEqual(result, [])
    
    @patch('github_client.requests.get')
    def test_export_process_by_date_range(self, mock_get):
        """Test export process by date range"""
        # Mock responses
        def mock_response_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            
            if 'commits' in url:
                mock_response.json.return_value = self.sample_commits
            elif 'issues' in url:
                mock_response.json.return_value = self.sample_issues
            elif 'pulls' in url:
                mock_response.json.return_value = self.sample_pull_requests
            else:
                mock_response.json.return_value = []
            
            return mock_response
        
        mock_get.side_effect = mock_response_side_effect
        
        result = self.client.export_process_by_date_range('test/repo', '2024-01-01', '2024-01-02')
        
        # Should return same structure as fetch_updates
        self.assertIn('commits', result)
        self.assertIn('issues', result)
        self.assertIn('pull_requests', result)
        self.assertIn('summary', result)
    
    def test_date_parameter_formatting(self):
        """Test that date parameters are properly formatted for API"""
        with patch('github_client.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            self.client.fetch_commits('test/repo', since_date='2024-01-01', until_date='2024-01-02')
            
            call_args = mock_get.call_args
            params = call_args[1]['params']
            
            # Check that dates are converted to ISO format with timezone
            self.assertIn('since', params)
            self.assertIn('until', params)
            self.assertIn('T', params['since'])  # ISO format includes T
            self.assertIn('T', params['until'])  # ISO format includes T
    
    @patch('github_client.requests.get')
    def test_fetch_releases_legacy(self, mock_get):
        """Test legacy fetch_releases method"""
        # Mock response for releases endpoint
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tag_name': 'v1.0.0',
            'name': 'Test Release',
            'published_at': '2024-01-01T12:00:00Z'
        }
        mock_get.return_value = mock_response
        
        result = self.client.fetch_releases(['test/repo'])
        
        # Check result structure
        self.assertIn('test/repo', result)
        self.assertEqual(result['test/repo']['tag_name'], 'v1.0.0')

if __name__ == '__main__':
    unittest.main()
