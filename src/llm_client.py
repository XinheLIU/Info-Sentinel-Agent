import os
import json
import requests
from datetime import datetime
from typing import Optional, Tuple
from logger import LOG
from prompt_manager import PromptManager

try:
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI library is not installed. Please run: pip install openai")
    raise


class LLM:
    """Simplified LLM client with explicit configuration support for OpenAI, Ollama, and DeepSeek"""
    
    def __init__(self, config):
        """
        Initialize the LLM Client based on configuration
        
        Args:
            config: Configuration object with LLM settings
        """
        self.config = config
        self.model_type = config.llm.get('model_type', 'ollama')
        
        # Initialize prompt manager with provider information
        self.prompt_manager = PromptManager(provider=self.model_type)
        
        # Set system prompt for report generation
        self.system_prompt = """You are an AI assistant that analyzes GitHub repository activity and generates comprehensive reports. 
        Please provide detailed, well-structured analysis with clear sections including Executive Summary, Key Highlights, Activity Analysis, Trends and Insights, and Recommendations.
        Format your response as professional markdown with appropriate headers and bullet points."""
        
        # Initialize the appropriate client based on model type
        client_initializers = {
            "openai": self._init_openai_client,
            "deepseek": self._init_deepseek_client,
            "ollama": self._init_ollama_client
        }
        
        initializer = client_initializers.get(self.model_type)
        if initializer:
            initializer()
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    @staticmethod
    def check_availability(config) -> Tuple[bool, str]:
        """
        Check if LLM provider is available and properly configured without instantiating LLM
        
        Args:
            config: Configuration object with LLM settings
            
        Returns:
            Tuple of (is_available: bool, error_message: str)
        """
        if not config.enable_daily_reports:
            return False, "❌ Error: Daily reports are disabled in configuration.\n   → Set 'enable_daily_reports': true in config.json"
        
        try:
            # Try to create an LLM instance to test availability
            llm = LLM(config)
            return llm.is_available()
        except Exception as e:
            provider = config.get_llm_provider()
            return False, LLM._get_provider_error_message(provider, str(e))
    
    def is_available(self) -> Tuple[bool, str]:
        """
        Check if this LLM instance is ready for use
        
        Returns:
            Tuple of (is_available: bool, error_message: str)
        """
        try:
            if self.model_type == "ollama":
                return self._check_ollama_availability()
            elif self.model_type in ["openai", "deepseek"]:
                return self._check_cloud_availability()
            else:
                return False, f"❌ Error: Unsupported model type: {self.model_type}"
        except Exception as e:
            return False, self._get_provider_error_message(self.model_type, str(e))
    
    def _check_ollama_availability(self) -> Tuple[bool, str]:
        """Check Ollama availability by testing the API"""
        try:
            # Test connection to Ollama
            test_url = self.api_url.replace('/api/chat', '/api/tags')
            response = requests.get(test_url, timeout=5)
            response.raise_for_status()
            
            # Check if the model is available
            models_data = response.json()
            model_names = [model.get('name', '') for model in models_data.get('models', [])]
            if not any(self.model_name in name for name in model_names):
                return False, (f"❌ Error: Ollama model '{self.model_name}' is not available.\n"
                             f"   → Download model: ollama pull {self.model_name}\n"
                             f"   → Available models: {', '.join(model_names) if model_names else 'none'}")
            
            return True, ""
        except requests.exceptions.ConnectionError:
            return False, self._get_provider_error_message("ollama", "Connection failed")
        except Exception as e:
            return False, self._get_provider_error_message("ollama", str(e))
    
    def _check_cloud_availability(self) -> Tuple[bool, str]:
        """Check cloud provider availability (OpenAI/DeepSeek)"""
        try:
            # Test with a minimal API call
            test_messages = [{"role": "user", "content": "test"}]
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=test_messages,
                max_tokens=1,
                temperature=0
            )
            return True, ""
        except Exception as e:
            return False, self._get_provider_error_message(self.model_type, str(e))
    
    @staticmethod
    def _get_provider_error_message(provider: str, error_details: str = "") -> str:
        """Get detailed error message and troubleshooting steps for a provider"""
        base_error = f"❌ Error: LLM provider '{provider}' is not properly configured."
        
        if provider == "ollama":
            return f"""{base_error}
   → Make sure Ollama is installed and running:
     • Install: curl -fsSL https://ollama.ai/install.sh | sh
     • Download model: ollama pull llama3.1
     • Start service: ollama serve
     • Verify: curl http://localhost:11434/api/tags
   → Error details: {error_details}"""
            
        elif provider == "deepseek":
            return f"""{base_error}
   → Make sure DEEPSEEK_API_KEY is set in your .env file
     • Get key from: https://platform.deepseek.com
     • Add to .env: DEEPSEEK_API_KEY=your_key_here
   → Error details: {error_details}"""
            
        elif provider == "openai":
            return f"""{base_error}
   → Make sure OPENAI_API_KEY is set in your .env file
     • Get key from: https://platform.openai.com
     • Add to .env: OPENAI_API_KEY=your_key_here
     • Check if you have sufficient credits
   → Error details: {error_details}"""
        
        else:
            return f"""{base_error}
   → Unknown provider: {provider}
   → Error details: {error_details}
   → For help, see: https://github.com/xinheliu/GitHubSentinel#quick-start"""
    
    def _init_openai_client(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI models")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = self.config.llm.get('openai_model_name', 'gpt-4o-mini')
        LOG.info(f"Using OpenAI API with model: {self.model_name}")
    
    def _init_deepseek_client(self):
        """Initialize DeepSeek client"""
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required for DeepSeek models")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.model_name = self.config.llm.get('deepseek_model_name', 'deepseek-chat')
        LOG.info(f"Using DeepSeek API with model: {self.model_name}")
    
    def _init_ollama_client(self):
        """Initialize Ollama client"""
        self.api_url = self.config.llm.get('ollama_api_url', 'http://localhost:11434/api/chat')
        self.model_name = self.config.llm.get('ollama_model_name', 'llama3.1')
        LOG.info(f"Using Ollama API at {self.api_url} with model: {self.model_name}")
    
    def generate_summary(self, issues_content: str, prs_content: str, dry_run: bool = False) -> str:
        """
        Generate a summary from issues and pull requests content
        
        Args:
            issues_content: Raw issues content
            prs_content: Raw pull requests content
            dry_run: If True, save prompt to file without making API call
            
        Returns:
            Generated summary text
        """
        prompt = self.prompt_manager.get_summary_prompt(issues_content, prs_content)
        
        if dry_run:
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            self.prompt_manager.save_prompt_to_file(prompt, "summary_prompt_debug.txt")
            return "DRY RUN - Summary prompt saved to logs/summary_prompt_debug.txt"
        
        messages = [{"role": "user", "content": prompt}]
        return self._generate_response(messages, max_tokens=500)
    
    def generate_daily_report(self, issues_content: str = None, prs_content: str = None, 
                            repo_name: str = None, date: str = None, 
                            markdown_content: str = None, dry_run: bool = False) -> str:
        """
        Generate a comprehensive daily report
        
        Args:
            issues_content: Raw issues content (legacy parameter)
            prs_content: Raw pull requests content (legacy parameter)
            repo_name: Repository name (legacy parameter)
            date: Date string (legacy parameter)
            markdown_content: Markdown content to analyze (preferred parameter)
            dry_run: If True, save prompt to file without making API call
            
        Returns:
            Generated daily report in markdown format
        """
        # Support both old and new calling patterns
        if markdown_content:
            content = markdown_content
        elif issues_content and prs_content and repo_name and date:
            content = self.prompt_manager.get_daily_report_prompt(issues_content, prs_content, repo_name, date)
        else:
            raise ValueError("Either markdown_content or (issues_content, prs_content, repo_name, date) must be provided")
        
        if dry_run:
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": content}
            ]
            self.prompt_manager.save_messages_to_file(messages, "daily_report_messages_debug.json")
            self.prompt_manager.save_prompt_to_file(content, "daily_report_prompt_debug.txt")
            return "DRY RUN - Daily report prompt saved to logs/daily_report_prompt_debug.txt"
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": content}
        ]
        return self._generate_response(messages, max_tokens=1500)
    
    def generate_report_from_markdown(self, markdown_content: str, dry_run: bool = False) -> str:
        """
        Generate an AI report from markdown content
        
        Args:
            markdown_content: The markdown content to analyze
            dry_run: If True, save prompt to file without making API call
            
        Returns:
            Generated AI report in markdown format
        """
        return self.generate_daily_report(markdown_content=markdown_content, dry_run=dry_run)
    
    def _generate_response(self, messages: list, max_tokens: int = 1500) -> str:
        """
        Generate response using the configured model
        
        Args:
            messages: List of messages for the conversation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response content
        """
        try:
            if self.model_type in ["openai", "deepseek"]:
                return self._generate_response_cloud(messages, max_tokens)
            elif self.model_type == "ollama":
                return self._generate_response_ollama(messages)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
        except Exception as e:
            LOG.error(f"Error generating response with {self.model_type} ({self.model_name}): {str(e)}")
            return f"Error generating response with {self.model_type} LLM: {str(e)}"

    def _generate_response_cloud(self, messages: list, max_tokens: int) -> str:
        """Generate response using a cloud-based LLM API (OpenAI, DeepSeek)"""
        LOG.info(f"Using {self.model_type} {self.model_name} model to generate response")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    
    def _generate_response_ollama(self, messages: list) -> str:
        """Generate response using Ollama API"""
        LOG.info(f"Using Ollama {self.model_name} model to generate response")
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        LOG.debug(f"Ollama response: {response_data}")
        
        message_content = response_data.get("message", {}).get("content", None)
        if message_content:
            return message_content
        else:
            LOG.error("Unable to extract content from Ollama response")
            raise ValueError("Invalid response structure from Ollama API")


# Backward compatibility - alias the old class name to the new one
LLMClient = LLM 