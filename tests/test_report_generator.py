import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import tempfile
import shutil
from datetime import date

# Add src directory to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.test_cache_dir = tempfile.mkdtemp()
        self.test_reports_dir = tempfile.mkdtemp()
        
        # Mock LLM client
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate_report_from_markdown.return_value = "# AI Generated Report\n\nTest AI analysis."
        
        # Create report generator
        self.report_generator = ReportGenerator(
            llm_client=self.mock_llm_client,
            export_cache_dir=self.test_cache_dir,
            ai_reports_dir=self.test_reports_dir
        )
        
        # Sample updates data
        self.sample_updates = {
            'issues': [
                {
                    'number': 1,
                    'title': 'Test Issue',
                    'state': 'open'
                }
            ],
            'pull_requests': [
                {
                    'number': 2,
                    'title': 'Test PR',
                    'state': 'closed'
                }
            ],
            'commits': [
                {
                    'sha': 'abc123def456',
                    'commit': {
                        'message': 'Test commit',
                        'author': {'name': 'Test Author'}
                    }
                }
            ],
            'summary': {
                'commits': 1,
                'issues': 1,
                'pull_requests': 1
            }
        }
        
        # Sample empty updates
        self.empty_updates = {
            'issues': [],
            'pull_requests': [],
            'commits': [],
            'summary': {
                'commits': 0,
                'issues': 0,
                'pull_requests': 0
            }
        }
    
    def tearDown(self):
        # Clean up temporary directories
        shutil.rmtree(self.test_cache_dir)
        shutil.rmtree(self.test_reports_dir)
    
    def test_init(self):
        """Test ReportGenerator initialization"""
        self.assertEqual(self.report_generator.export_cache_dir, self.test_cache_dir)
        self.assertEqual(self.report_generator.ai_reports_dir, self.test_reports_dir)
        self.assertTrue(os.path.exists(self.test_cache_dir))
        self.assertTrue(os.path.exists(self.test_reports_dir))
    
    def test_has_meaningful_updates_true(self):
        """Test meaningful updates detection with actual updates"""
        result = self.report_generator._has_meaningful_updates(self.sample_updates)
        self.assertTrue(result)
    
    def test_has_meaningful_updates_false(self):
        """Test meaningful updates detection with no updates"""
        result = self.report_generator._has_meaningful_updates(self.empty_updates)
        self.assertFalse(result)
    
    def test_export_daily_progress_with_updates(self):
        """Test exporting daily progress with meaningful updates"""
        repo = 'test/repo'
        file_path = self.report_generator.export_daily_progress(repo, self.sample_updates)
        
        # Check file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Check file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        self.assertIn('Daily Progress for test/repo', content)
        self.assertIn('Test Issue #1', content)
        self.assertIn('Test PR #2', content)
    
    def test_export_daily_progress_no_updates(self):
        """Test exporting daily progress with no updates"""
        repo = 'test/repo'
        file_path = self.report_generator.export_daily_progress(repo, self.empty_updates)
        
        # Check file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Check file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        self.assertIn('No Activity Report for test/repo', content)
        self.assertIn('No significant activity found', content)
    
    def test_export_progress_by_date_range(self):
        """Test exporting progress by date range"""
        repo = 'test/repo'
        days = 7
        file_path = self.report_generator.export_progress_by_date_range(repo, self.sample_updates, days)
        
        # Check file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Check filename format
        expected_filename = f"{date.today()}_{days}days.md"
        self.assertTrue(file_path.endswith(expected_filename))
        
        # Check file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        self.assertIn(f'Progress for test/repo', content)
        self.assertIn(f'Last {days} days', content)
    
    def test_get_cache_file_path(self):
        """Test cache file path generation"""
        repo = 'test/repo'
        target_date = '2024-01-15'
        
        # Single day
        path = self.report_generator._get_cache_file_path(repo, target_date, 1)
        expected = os.path.join(self.test_cache_dir, 'test_repo', '2024-01-15.md')
        self.assertEqual(path, expected)
        
        # Multiple days
        path = self.report_generator._get_cache_file_path(repo, target_date, 7)
        expected = os.path.join(self.test_cache_dir, 'test_repo', '2024-01-15_7days.md')
        self.assertEqual(path, expected)
    
    def test_get_ai_report_path(self):
        """Test AI report path generation"""
        cache_path = os.path.join(self.test_cache_dir, 'test_repo', '2024-01-15.md')
        ai_path = self.report_generator._get_ai_report_path(cache_path)
        
        expected = os.path.join(self.test_reports_dir, 'test_repo', '2024-01-15_report.md')
        self.assertEqual(ai_path, expected)
    
    def test_has_meaningful_content_true(self):
        """Test meaningful content detection with actual content"""
        content = "# Daily Progress\n\n## Issues\n- [OPEN] Test Issue #1\n\n## Pull Requests\n- [CLOSED] Test PR #2"
        result = self.report_generator._has_meaningful_content(content)
        self.assertTrue(result)
    
    def test_has_meaningful_content_false(self):
        """Test meaningful content detection with no activity content"""
        content = "# No Activity Report for test/repo\n\nNo significant activity found"
        result = self.report_generator._has_meaningful_content(content)
        self.assertFalse(result)
    
    def test_generate_daily_report_with_activity(self):
        """Test generating daily report with meaningful activity"""
        # First create a cache file
        cache_path = self.report_generator.export_daily_progress('test/repo', self.sample_updates)
        
        # Generate report
        report_content, report_path = self.report_generator.generate_daily_report(cache_path)
        
        # Check LLM was called
        self.mock_llm_client.generate_report_from_markdown.assert_called_once()
        
        # Check report file was created in AI reports directory
        self.assertTrue(os.path.exists(report_path))
        self.assertIn(self.test_reports_dir, report_path)
        
        # Check content
        self.assertEqual(report_content, "# AI Generated Report\n\nTest AI analysis.")
    
    def test_generate_daily_report_no_activity(self):
        """Test generating daily report with no meaningful activity"""
        # First create a no-activity cache file
        cache_path = self.report_generator.export_daily_progress('test/repo', self.empty_updates)
        
        # Generate report
        report_content, report_path = self.report_generator.generate_daily_report(cache_path)
        
        # Check LLM was NOT called
        self.mock_llm_client.generate_report_from_markdown.assert_not_called()
        
        # Check report file was created in AI reports directory
        self.assertTrue(os.path.exists(report_path))
        self.assertIn(self.test_reports_dir, report_path)
        
        # Check content
        self.assertIn("Daily Report - No Activity", report_content)
        self.assertIn("No meaningful activity detected", report_content)
    
    @patch('src.report_generator.datetime')
    def test_generate_report_with_auto_export(self, mock_datetime):
        """Test auto-export functionality"""
        # Mock current date
        mock_datetime.now.return_value.strftime.return_value = '2024-01-15'
        mock_datetime.strptime.return_value = Mock()
        
        # Mock GitHub client
        mock_github_client = Mock()
        mock_github_client.fetch_updates.return_value = self.sample_updates
        
        # Test with non-interactive mode (no cache exists)
        repo = 'test/repo'
        report_content, report_path = self.report_generator.generate_report_with_auto_export(
            repo=repo,
            target_date='2024-01-15',
            days=1,
            github_client=mock_github_client,
            interactive=False
        )
        
        # Check GitHub client was called
        mock_github_client.fetch_updates.assert_called_once()
        
        # Check report was generated
        self.assertIsNotNone(report_content)
        self.assertTrue(os.path.exists(report_path))
    
    def test_generate_notification_report(self):
        """Test notification report generation"""
        repo = 'test/repo'
        report = self.report_generator.generate_notification_report(repo, self.sample_updates)
        
        # Check content structure
        self.assertIn('GitHub Sentinel Update Report', report)
        self.assertIn('test/repo', report)
        self.assertIn('Summary', report)
        self.assertIn('Recent Commits', report)
        self.assertIn('Recent Issues', report)
        self.assertIn('Recent Pull Requests', report)
        
        # Check specific data
        self.assertIn('Test commit', report)
        self.assertIn('Test Issue', report)
        self.assertIn('Test PR', report)

if __name__ == '__main__':
    unittest.main()
