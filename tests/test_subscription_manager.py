import unittest
from unittest.mock import Mock, patch, mock_open
import os
import sys
import json
import tempfile

# Add src directory to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from subscription_manager import SubscriptionManager

class TestSubscriptionManager(unittest.TestCase):
    def setUp(self):
        """Set up test subscription manager with temporary file"""
        # Create a temporary file for testing
        self.test_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_subscriptions = ["test/repo1", "test/repo2", "owner/project"]
        
        # Write initial test data
        json.dump(self.test_subscriptions, self.test_file)
        self.test_file.close()
        
        self.manager = SubscriptionManager(self.test_file.name)
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)
    
    def test_init(self):
        """Test SubscriptionManager initialization"""
        self.assertEqual(self.manager.subscriptions_file, self.test_file.name)
        self.assertEqual(self.manager.subscriptions, self.test_subscriptions)
    
    def test_load_subscriptions(self):
        """Test loading subscriptions from file"""
        loaded_subscriptions = self.manager.load_subscriptions()
        self.assertEqual(loaded_subscriptions, self.test_subscriptions)
    
    def test_get_subscriptions(self):
        """Test getting current subscriptions"""
        subscriptions = self.manager.get_subscriptions()
        self.assertEqual(subscriptions, self.test_subscriptions)
    
    def test_add_subscription_new(self):
        """Test adding a new subscription"""
        new_repo = "new/repository"
        self.manager.add_subscription(new_repo)
        
        # Check subscription was added
        self.assertIn(new_repo, self.manager.subscriptions)
        
        # Verify it was saved to file
        with open(self.test_file.name, 'r') as f:
            saved_subscriptions = json.load(f)
        self.assertIn(new_repo, saved_subscriptions)
    
    def test_add_subscription_existing(self):
        """Test adding an existing subscription (should not duplicate)"""
        existing_repo = "test/repo1"
        original_count = len(self.manager.subscriptions)
        
        self.manager.add_subscription(existing_repo)
        
        # Count should remain the same
        self.assertEqual(len(self.manager.subscriptions), original_count)
        
        # Should still only appear once
        self.assertEqual(self.manager.subscriptions.count(existing_repo), 1)
    
    def test_remove_subscription_existing(self):
        """Test removing an existing subscription"""
        repo_to_remove = "test/repo1"
        self.manager.remove_subscription(repo_to_remove)
        
        # Check subscription was removed
        self.assertNotIn(repo_to_remove, self.manager.subscriptions)
        
        # Verify it was saved to file
        with open(self.test_file.name, 'r') as f:
            saved_subscriptions = json.load(f)
        self.assertNotIn(repo_to_remove, saved_subscriptions)
    
    def test_remove_subscription_non_existing(self):
        """Test removing a non-existing subscription (should not error)"""
        non_existing_repo = "nonexistent/repo"
        original_subscriptions = self.manager.subscriptions.copy()
        
        # Should not raise an exception
        self.manager.remove_subscription(non_existing_repo)
        
        # Subscriptions should remain unchanged
        self.assertEqual(self.manager.subscriptions, original_subscriptions)
    
    def test_save_subscriptions(self):
        """Test saving subscriptions to file"""
        # Modify subscriptions in memory
        self.manager.subscriptions.append("new/test-repo")
        
        # Save to file
        self.manager.save_subscriptions()
        
        # Verify file was updated
        with open(self.test_file.name, 'r') as f:
            saved_subscriptions = json.load(f)
        
        self.assertIn("new/test-repo", saved_subscriptions)
        self.assertEqual(len(saved_subscriptions), len(self.manager.subscriptions))
    
    @patch('builtins.open', mock_open(read_data='["test/repo"]'))
    def test_load_subscriptions_with_mock(self):
        """Test loading subscriptions with mocked file"""
        manager = SubscriptionManager('mock_file.json')
        self.assertEqual(manager.subscriptions, ["test/repo"])
    
    def test_file_operations_integration(self):
        """Test complete file operations integration"""
        # Create a new manager instance to test file loading
        manager2 = SubscriptionManager(self.test_file.name)
        
        # Should load the same data
        self.assertEqual(manager2.subscriptions, self.test_subscriptions)
        
        # Add subscription with first manager
        self.manager.add_subscription("integration/test")
        
        # Create another manager instance - should see the changes
        manager3 = SubscriptionManager(self.test_file.name)
        self.assertIn("integration/test", manager3.subscriptions)
    
    def test_empty_subscriptions_file(self):
        """Test handling of empty subscriptions file"""
        # Create empty file
        empty_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump([], empty_file)
        empty_file.close()
        
        try:
            manager = SubscriptionManager(empty_file.name)
            self.assertEqual(manager.subscriptions, [])
            
            # Test adding to empty list
            manager.add_subscription("first/repo")
            self.assertEqual(manager.subscriptions, ["first/repo"])
            
        finally:
            os.unlink(empty_file.name)
    
    def test_multiple_operations(self):
        """Test multiple operations in sequence"""
        # Add multiple subscriptions
        new_repos = ["multi/repo1", "multi/repo2", "multi/repo3"]
        for repo in new_repos:
            self.manager.add_subscription(repo)
        
        # Check all were added
        for repo in new_repos:
            self.assertIn(repo, self.manager.subscriptions)
        
        # Remove some subscriptions
        self.manager.remove_subscription("multi/repo2")
        self.manager.remove_subscription("test/repo1")
        
        # Check final state
        expected = ["test/repo2", "owner/project", "multi/repo1", "multi/repo3"]
        self.assertEqual(sorted(self.manager.subscriptions), sorted(expected))
        
        # Verify persistence
        manager2 = SubscriptionManager(self.test_file.name)
        self.assertEqual(sorted(manager2.subscriptions), sorted(expected))

if __name__ == '__main__':
    unittest.main()
