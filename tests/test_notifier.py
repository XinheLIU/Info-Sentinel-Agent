import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add src directory to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from notifier import Notifier

class TestNotifier(unittest.TestCase):
    def test_notify_no_config(self):
        """Test notifier handles missing email configuration gracefully"""
        notifier = Notifier(None)
        # Should not raise exception, just log warning
        notifier.notify("Test report", "test/repo")
    
    def test_notify_empty_config(self):
        """Test notifier handles empty email configuration gracefully"""
        notifier = Notifier({})
        # Should not raise exception, just log warning
        notifier.notify("Test report", "test/repo")
    
    def test_notify_incomplete_config(self):
        """Test notifier handles incomplete email configuration gracefully"""
        incomplete_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587
            # Missing email and password
        }
        notifier = Notifier(incomplete_config)
        # Should not raise exception, just log warning
        notifier.notify("Test report", "test/repo")
    
    def test_markdown_detection(self):
        """Test markdown detection heuristic"""
        notifier = Notifier({})
        
        # Should detect markdown
        self.assertTrue(notifier._is_markdown("# Header"))
        self.assertTrue(notifier._is_markdown("**bold**"))
        self.assertTrue(notifier._is_markdown("```code```"))
        self.assertTrue(notifier._is_markdown("[link](url)"))
        
        # Should not detect markdown
        self.assertFalse(notifier._is_markdown("Plain text report"))
        self.assertFalse(notifier._is_markdown("Simple text without markdown"))

if __name__ == '__main__':
    unittest.main()
