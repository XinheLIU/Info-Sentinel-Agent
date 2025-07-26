import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add src directory to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm_client import LLMClient

class TestLLMClient(unittest.TestCase):
    def setUp(self):
        # Mock environment variables
        self.original_env = {}
        self.mock_deepseek_key = "test_deepseek_key"
        self.mock_openai_key = "test_openai_key"
        
        # Store original values
        for key in ['DEEPSEEK_API_KEY', 'OPENAI_API_KEY']:
            if key in os.environ:
                self.original_env[key] = os.environ[key]
    
    def tearDown(self):
        # Clean up environment variables
        for key in ['DEEPSEEK_API_KEY', 'OPENAI_API_KEY']:
            if key in os.environ:
                del os.environ[key]
        
        # Restore original values
        for key, value in self.original_env.items():
            os.environ[key] = value
    
    def test_init_with_deepseek_api_key(self):
        """Test LLMClient initialization with DeepSeek API key"""
        os.environ['DEEPSEEK_API_KEY'] = self.mock_deepseek_key
        client = LLMClient(api_key=self.mock_deepseek_key, model="deepseek-chat")
        self.assertEqual(client.api_key, self.mock_deepseek_key)
        self.assertEqual(client.model, "deepseek-chat")
        self.assertEqual(client.provider, "deepseek")
    
    def test_init_with_openai_api_key(self):
        """Test LLMClient initialization with OpenAI API key"""
        os.environ['OPENAI_API_KEY'] = self.mock_openai_key
        client = LLMClient(api_key=self.mock_openai_key, model="gpt-4o")
        self.assertEqual(client.api_key, self.mock_openai_key)
        self.assertEqual(client.model, "gpt-4o")
        self.assertEqual(client.provider, "openai")
    
    def test_init_with_env_variable_deepseek(self):
        """Test LLMClient initialization with DeepSeek environment variable"""
        os.environ['DEEPSEEK_API_KEY'] = self.mock_deepseek_key
        client = LLMClient()
        self.assertEqual(client.api_key, self.mock_deepseek_key)
        self.assertEqual(client.provider, "deepseek")
    
    def test_init_with_env_variable_openai(self):
        """Test LLMClient initialization with OpenAI environment variable"""
        os.environ['OPENAI_API_KEY'] = self.mock_openai_key
        client = LLMClient(model="gpt-4o")
        self.assertEqual(client.api_key, self.mock_openai_key)
        self.assertEqual(client.provider, "openai")
    
    def test_init_without_api_key(self):
        """Test LLMClient initialization without API key raises error"""
        with self.assertRaises(ValueError) as context:
            LLMClient()
        self.assertIn("DEEPSEEK_API_KEY", str(context.exception))
    
    def test_provider_detection_by_model_name(self):
        """Test provider detection based on model name"""
        os.environ['DEEPSEEK_API_KEY'] = self.mock_deepseek_key
        os.environ['OPENAI_API_KEY'] = self.mock_openai_key
        
        # Test DeepSeek model detection
        client = LLMClient(model="deepseek-chat")
        self.assertEqual(client.provider, "deepseek")
        
        # Test OpenAI model detection
        client = LLMClient(model="gpt-4o")
        self.assertEqual(client.provider, "openai")
    
    def test_provider_detection_prefers_deepseek(self):
        """Test provider detection prefers DeepSeek when both keys available"""
        os.environ['DEEPSEEK_API_KEY'] = self.mock_deepseek_key
        os.environ['OPENAI_API_KEY'] = self.mock_openai_key
        
        client = LLMClient()  # Default model should prefer DeepSeek
        self.assertEqual(client.provider, "deepseek")
    
    @patch('llm_client.OpenAI')
    def test_generate_summary_deepseek(self, mock_openai):
        """Test summary generation with DeepSeek"""
        os.environ['DEEPSEEK_API_KEY'] = self.mock_deepseek_key
        
        # Mock the OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated summary"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        client = LLMClient(api_key=self.mock_deepseek_key)
        result = client.generate_summary("Test issues", "Test PRs")
        
        self.assertEqual(result, "Generated summary")
        mock_client.chat.completions.create.assert_called_once()
        
        # Check that the call was made with correct parameters
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['model'], 'deepseek-chat')
    
    @patch('llm_client.OpenAI')
    def test_generate_daily_report_openai(self, mock_openai):
        """Test daily report generation with OpenAI"""
        os.environ['OPENAI_API_KEY'] = self.mock_openai_key
        
        # Mock the OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated daily report"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        client = LLMClient(api_key=self.mock_openai_key, model="gpt-4o")
        result = client.generate_daily_report(
            issues_content="Test issues",
            prs_content="Test PRs", 
            repo_name="test/repo",
            date="2024-01-01"
        )
        
        self.assertEqual(result, "Generated daily report")
        mock_client.chat.completions.create.assert_called_once()
        
        # Check that the call was made with correct parameters
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['model'], 'gpt-4o')
    
    @patch('llm_client.OpenAI')
    def test_generate_report_from_markdown(self, mock_openai):
        """Test report generation from markdown content"""
        os.environ['DEEPSEEK_API_KEY'] = self.mock_deepseek_key
        
        # Mock the OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated markdown report"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        client = LLMClient(api_key=self.mock_deepseek_key)
        result = client.generate_report_from_markdown("# Test Markdown\n\nSome content")
        
        self.assertEqual(result, "Generated markdown report")
        mock_client.chat.completions.create.assert_called_once()
    
    def test_dry_run_mode_summary(self):
        """Test dry run mode for summary generation"""
        os.environ['DEEPSEEK_API_KEY'] = self.mock_deepseek_key
        
        client = LLMClient(api_key=self.mock_deepseek_key)
        result = client.generate_summary("Test issues", "Test PRs", dry_run=True)
        
        self.assertIn("DRY RUN", result)
        self.assertIn("summary_prompt_debug.txt", result)
    
    def test_dry_run_mode_daily_report(self):
        """Test dry run mode for daily report generation"""
        os.environ['DEEPSEEK_API_KEY'] = self.mock_deepseek_key
        
        client = LLMClient(api_key=self.mock_deepseek_key)
        result = client.generate_daily_report(
            issues_content="Test issues",
            prs_content="Test PRs",
            repo_name="test/repo",
            date="2024-01-01",
            dry_run=True
        )
        
        self.assertIn("DRY RUN", result)
        self.assertIn("daily_report_prompt_debug.txt", result)
    
    def test_dry_run_mode_markdown_report(self):
        """Test dry run mode for markdown report generation"""
        os.environ['DEEPSEEK_API_KEY'] = self.mock_deepseek_key
        
        client = LLMClient(api_key=self.mock_deepseek_key)
        result = client.generate_report_from_markdown("# Test", dry_run=True)
        
        self.assertIn("DRY RUN", result)
        self.assertIn("markdown_report_prompt_debug.txt", result)
    
    @patch('llm_client.OpenAI')
    def test_api_error_handling(self, mock_openai):
        """Test error handling when API call fails"""
        os.environ['DEEPSEEK_API_KEY'] = self.mock_deepseek_key
        
        # Mock API error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        client = LLMClient(api_key=self.mock_deepseek_key)
        result = client.generate_summary("Test issues", "Test PRs")
        
        self.assertIn("Error generating summary", result)
        self.assertIn("deepseek", result.lower())
    
    def test_create_deepseek_client(self):
        """Test creating DeepSeek client using class method"""
        client = LLMClient.create_deepseek_client(api_key=self.mock_deepseek_key)
        self.assertEqual(client.provider, "deepseek")
        self.assertEqual(client.model, "deepseek-chat")
    
    def test_create_openai_client(self):
        """Test creating OpenAI client using class method"""
        client = LLMClient.create_openai_client(api_key=self.mock_openai_key)
        self.assertEqual(client.provider, "openai")
        self.assertEqual(client.model, "gpt-4o")

if __name__ == '__main__':
    unittest.main() 