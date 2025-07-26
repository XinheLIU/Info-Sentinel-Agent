import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from hacker_news_client import HackerNewsClient
from report_generator import ReportGenerator

class TestHackerNewsIntegration(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.export_dir = "test_reports/exports"
        self.ai_reports_dir = "test_reports/ai_reports"
        os.makedirs(os.path.join(self.export_dir, 'hackernews'), exist_ok=True)

    def tearDown(self):
        """Tear down after the tests."""
        if os.path.exists("test_reports"):
            shutil.rmtree("test_reports")

    @patch('hacker_news_client.requests.get')
    def test_fetch_top_stories(self, mock_get):
        """Test that HackerNewsClient fetches and parses stories correctly."""
        # Mock the HTML response from Hacker News
        mock_html = b'''
        <html>
            <body>
                <table>
                    <tr class='athing'><td><span class="titleline"><a href="http://example.com/story1">Story 1</a></span></td></tr>
                    <tr class='athing'><td><span class="titleline"><a href="http://example.com/story2">Story 2</a></span></td></tr>
                </table>
            </body>
        </html>
        '''
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        client = HackerNewsClient()
        stories = client.fetch_top_stories()

        self.assertEqual(len(stories), 2)
        self.assertEqual(stories[0]['title'], 'Story 1')
        self.assertEqual(stories[0]['link'], 'http://example.com/story1')
        self.assertEqual(stories[1]['title'], 'Story 2')
        self.assertEqual(stories[1]['link'], 'http://example.com/story2')

    @patch('report_generator.HackerNewsClient')
    def test_export_hackernews_report(self, MockHackerNewsClient):
        """Test that ReportGenerator can export a Hacker News report."""
        # Mock the HackerNewsClient
        mock_client_instance = MockHackerNewsClient.return_value
        mock_client_instance.fetch_top_stories.return_value = [
            {'title': 'Test Story 1', 'link': 'http://example.com/test1'},
            {'title': 'Test Story 2', 'link': 'http://example.com/test2'}
        ]

        # Initialize ReportGenerator with test directories
        report_generator = ReportGenerator(export_cache_dir=self.export_dir, ai_reports_dir=self.ai_reports_dir)
        report_path = report_generator.export_hackernews_report()

        self.assertTrue(os.path.exists(report_path))

        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("# Hacker News Top Stories", content)
            self.assertIn("- [Test Story 1](http://example.com/test1)", content)
            self.assertIn("- [Test Story 2](http://example.com/test2)", content)

if __name__ == '__main__':
    unittest.main()