import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import tempfile
import shutil

# Add src directory to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Note: DailyProgressExporter is a legacy class that has been superseded by ReportGenerator
# This test file is kept for backward compatibility testing
from daily_progress import DailyProgressExporter

class TestDailyProgressExporter(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.exporter = DailyProgressExporter(output_dir=self.test_dir)
        
        # Mock GitHub client
        self.mock_github_client = Mock()
        
        # Sample activity data (matching current format)
        self.sample_activity_data = {
            'commits': [
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
            ],
            'issues': [
                {
                    'number': 1,
                    'title': 'Test Issue',
                    'state': 'open',
                    'user': {'login': 'testuser'},
                    'created_at': '2024-01-01T10:00:00Z',
                    'updated_at': '2024-01-01T12:00:00Z',
                    'labels': [{'name': 'bug'}],
                    'assignees': [],
                    'body': 'This is a test issue',
                    'html_url': 'https://github.com/test/repo/issues/1'
                }
            ],
            'pull_requests': [
                {
                    'number': 2,
                    'title': 'Test PR',
                    'state': 'open',
                    'user': {'login': 'testuser'},
                    'created_at': '2024-01-01T11:00:00Z',
                    'updated_at': '2024-01-01T13:00:00Z',
                    'assignees': [],
                    'requested_reviewers': [],
                    'base': {'ref': 'main'},
                    'head': {'ref': 'feature-branch'},
                    'additions': 10,
                    'deletions': 5,
                    'body': 'This is a test PR',
                    'html_url': 'https://github.com/test/repo/pull/2',
                    'merged': False
                }
            ],
            'summary': {
                'commits': 1,
                'issues': 1,
                'pull_requests': 1,
                'total_commits': 1,
                'total_issues': 1,
                'total_prs': 1
            }
        }
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test DailyProgressExporter initialization"""
        self.assertEqual(self.exporter.output_dir, self.test_dir)
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_create_file_path_single_date(self):
        """Test file path creation for single date"""
        repo = 'test/repo'
        target_date = '2024-01-01'
        
        file_path = self.exporter._create_file_path(repo, target_date)
        
        expected_dir = os.path.join(self.test_dir, 'test_repo')
        expected_file = os.path.join(expected_dir, '2024-01-01.md')
        
        self.assertEqual(file_path, expected_file)
    
    def test_create_file_path_date_range(self):
        """Test file path creation for date range"""
        repo = 'test/repo'
        target_date = '2024-01-01'
        until_date = '2024-01-07'
        
        file_path = self.exporter._create_file_path(repo, target_date, until_date)
        
        expected_dir = os.path.join(self.test_dir, 'test_repo')
        expected_file = os.path.join(expected_dir, 'from_20240101_to_20240107.md')
        
        self.assertEqual(file_path, expected_file)
    
    def test_export_daily_activity(self):
        """Test exporting daily activity to markdown file"""
        # Mock the GitHub client method to return our test data
        self.mock_github_client.export_process_by_date_range.return_value = self.sample_activity_data
        
        filepath = self.exporter.export_daily_activity(
            self.mock_github_client, 
            'test/repo', 
            '2024-01-01'
        )
        
        # Check file was created
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
        
        self.assertIn('test/repo', content)
        self.assertIn('2024-01-01', content)
        self.assertIn('Test Issue', content)
        self.assertIn('Test PR', content)
        self.assertIn('Test commit message', content)
    
    def test_export_multiple_repos(self):
        """Test exporting daily activity for multiple repositories"""
        repos = ['test/repo1', 'test/repo2']
        self.mock_github_client.export_process_by_date_range.return_value = self.sample_activity_data
        
        exported_files = self.exporter.export_multiple_repos(
            self.mock_github_client,
            repos,
            '2024-01-01'
        )
        
        self.assertEqual(len(exported_files), 2)
        for filepath in exported_files:
            self.assertTrue(os.path.exists(filepath))
    
    def test_export_multiple_repos_with_error(self):
        """Test exporting with some repositories failing"""
        repos = ['test/repo1', 'test/repo2']
        
        # Mock first call to succeed, second to fail
        side_effects = [self.sample_activity_data, Exception("API Error")]
        self.mock_github_client.export_process_by_date_range.side_effect = side_effects
        
        exported_files = self.exporter.export_multiple_repos(
            self.mock_github_client,
            repos,
            '2024-01-01'
        )
        
        # Should return one successful export
        self.assertEqual(len(exported_files), 1)
        self.assertTrue(os.path.exists(exported_files[0]))
    
    def test_generate_markdown(self):
        """Test markdown generation from activity data"""
        markdown = self.exporter._generate_markdown('test/repo', '2024-01-01', None, self.sample_activity_data)
        
        # Check header and structure
        self.assertIn('Daily Progress Report: test/repo (2024-01-01)', markdown)
        self.assertIn('## Summary', markdown)
        self.assertIn('## Commits', markdown)
        self.assertIn('## Issues', markdown)
        self.assertIn('## Pull Requests', markdown)
        
        # Check specific content
        self.assertIn('Test commit message', markdown)
        self.assertIn('Test Issue', markdown)
        self.assertIn('Test PR', markdown)
        self.assertIn('Test Author', markdown)
    
    def test_generate_markdown_with_date_range(self):
        """Test markdown generation with date range"""
        markdown = self.exporter._generate_markdown('test/repo', '2024-01-01', '2024-01-07', self.sample_activity_data)
        
        self.assertIn('Daily Progress Report: test/repo (2024-01-01 to 2024-01-07)', markdown)
        self.assertIn('**Date Range:** 2024-01-01 to 2024-01-07', markdown)
    
    def test_get_exported_file_path(self):
        """Test getting expected file path"""
        filepath = self.exporter.get_exported_file_path('test/repo', '2024-01-01')
        expected = self.exporter._create_file_path('test/repo', '2024-01-01')
        self.assertEqual(filepath, expected)
    
    def test_generate_markdown_empty_data(self):
        """Test markdown generation with empty data"""
        empty_data = {
            'commits': [],
            'issues': [],
            'pull_requests': [],
            'summary': {
                'commits': 0,
                'issues': 0,
                'pull_requests': 0,
                'total_commits': 0,
                'total_issues': 0,
                'total_prs': 0
            }
        }
        
        markdown = self.exporter._generate_markdown('test/repo', '2024-01-01', None, empty_data)
        self.assertIn('No commits found', markdown)
        self.assertIn('No issues found', markdown)
        self.assertIn('No pull requests found', markdown)
    
    def test_repo_name_sanitization(self):
        """Test that repository names are properly sanitized for directory names"""
        repo = 'test-org/test-repo'
        target_date = '2024-01-01'
        
        file_path = self.exporter._create_file_path(repo, target_date)
        
        # Should convert slashes and dashes to underscores
        expected_dir = os.path.join(self.test_dir, 'test_org_test_repo')
        self.assertTrue(file_path.startswith(expected_dir))
    
    def test_directory_creation(self):
        """Test that directories are created automatically"""
        repo = 'new/repository'
        target_date = '2024-01-01'
        
        file_path = self.exporter._create_file_path(repo, target_date)
        
        # Directory should be created
        repo_dir = os.path.dirname(file_path)
        self.assertTrue(os.path.exists(repo_dir))

if __name__ == '__main__':
    unittest.main() 