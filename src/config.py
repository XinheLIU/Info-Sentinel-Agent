import json
import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Load GitHub token from environment variables
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        # Load LLM API keys from environment variables (for v0.2+ features)
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Load email credentials from environment variables (for security)
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        # Load other config from JSON file
        with open('config.json', 'r') as f:
            config = json.load(f)
            # Load notification settings from JSON and merge with environment variables
            json_notification_settings = config.get('notification_settings', {})
            self.notification_settings = self._merge_notification_settings(json_notification_settings)
            self.subscriptions_file = config.get('subscriptions_file')
            self.update_interval = config.get('update_interval', 24 * 60 * 60)  # Default to 24 hours
            self.github_progress_frequency_days = config.get('github_progress_frequency_days', 1)
            self.github_progress_execution_time = config.get('github_progress_execution_time', "08:00")
            
            # Version 0.2+ configuration options with DeepSeek as default
            self.enable_daily_reports = config.get('enable_daily_reports', True)
            
            # Separate directories for export cache and AI reports
            self.export_cache_dir = config.get('export_cache_dir', 'reports/exports')
            self.ai_reports_dir = config.get('ai_reports_dir', 'reports/ai_reports')
            
            # Legacy support - fallback to old names if new ones don't exist
            if 'daily_progress_dir' in config and 'export_cache_dir' not in config:
                self.export_cache_dir = config.get('daily_progress_dir', 'reports/daily_progress')
            if 'daily_reports_dir' in config and 'ai_reports_dir' not in config:
                self.ai_reports_dir = config.get('daily_reports_dir', 'reports/daily_reports')
            
            # LLM configuration - support both old and new formats
            if 'llm' in config:
                # New format with explicit configuration
                self.llm = config['llm']
                # For backward compatibility, set legacy fields
                self.llm_provider = self.llm.get('model_type', 'ollama')
                if self.llm_provider == 'openai':
                    self.llm_model = self.llm.get('openai_model_name', 'gpt-4o-mini')
                elif self.llm_provider == 'deepseek':
                    self.llm_model = self.llm.get('deepseek_model_name', 'deepseek-chat')
                else:  # ollama
                    self.llm_model = self.llm.get('ollama_model_name', 'llama3.1')
            else:
                # Legacy format - fallback to old configuration
                self.llm_provider = config.get('llm_provider', 'auto')  # auto, deepseek, openai
                self.llm_model = config.get('llm_model', 'deepseek-chat')  # Default to DeepSeek model
                
                # Create new llm structure from legacy config
                self.llm = {
                    'model_type': self.llm_provider if self.llm_provider != 'auto' else 'deepseek',
                    'openai_model_name': 'gpt-4o-mini',
                    'deepseek_model_name': 'deepseek-chat',
                    'ollama_model_name': 'llama3.1',
                    'ollama_api_url': 'http://localhost:11434/api/chat'
                }
                
                # Legacy OpenAI config for backward compatibility
                if 'openai_model' in config:
                    # If user has explicitly set openai_model, migrate to new format
                    if self.llm_provider == 'auto' and 'llm_model' not in config:
                        self.llm_model = config.get('openai_model', 'gpt-4o')
                        self.llm_provider = 'openai'
                        self.llm['model_type'] = 'openai'
                        self.llm['openai_model_name'] = self.llm_model
            
            self.generate_consolidated_reports = config.get('generate_consolidated_reports', False)
            
    def get_llm_provider(self):
        """
        Determine which LLM provider to use based on configuration and available API keys
        
        Returns:
            str: Provider name ('deepseek', 'openai', or 'ollama')
        """
        if self.llm_provider in ['deepseek', 'openai', 'ollama']:
            return self.llm_provider
        else:  # auto detection (legacy)
            # Check model name first
            if self.llm_model.startswith(("gpt-", "o1-", "text-", "davinci", "curie", "babbage", "ada")):
                return 'openai'
            elif self.llm_model.startswith(("deepseek-", "deepseek")):
                return 'deepseek'
            elif self.llm_model.startswith(("llama", "mistral", "qwen", "phi")):
                return 'ollama'
            
            # Check available API keys
            if self.deepseek_api_key and not self.openai_api_key:
                return 'deepseek'
            elif self.openai_api_key and not self.deepseek_api_key:
                return 'openai'
            elif self.deepseek_api_key and self.openai_api_key:
                # Both available, prefer DeepSeek as default
                return 'deepseek'
            else:
                # Neither available, default to Ollama (local)
                return 'ollama'
    
    def get_llm_api_key(self):
        """
        Get the appropriate API key based on the LLM provider
        
        Returns:
            str: API key for the selected provider (None for Ollama)
        """
        provider = self.get_llm_provider()
        if provider == 'deepseek':
            return self.deepseek_api_key
        elif provider == 'openai':
            return self.openai_api_key
        elif provider == 'ollama':
            return None  # Ollama doesn't require an API key
        else:
            return None
            
    def validate_v2_requirements(self):
        """Validate that all requirements for v0.2+ features are met"""
        if not self.enable_daily_reports:
            return True
            
        provider = self.get_llm_provider()
        api_key = self.get_llm_api_key()
        
        if provider == 'ollama':
            # Ollama doesn't require an API key, just return True
            return True
        elif not api_key:
            if provider == 'deepseek':
                raise ValueError("DEEPSEEK_API_KEY environment variable is required for daily report generation with DeepSeek")
            elif provider == 'openai':
                raise ValueError("OPENAI_API_KEY environment variable is required for daily report generation with OpenAI")
            else:
                raise ValueError("Either DEEPSEEK_API_KEY or OPENAI_API_KEY environment variable is required for daily report generation")
        
        return True

    def _merge_notification_settings(self, json_settings):
        """
        Merge notification settings from JSON with environment variables
        Environment variables take precedence for security
        
        Args:
            json_settings: Notification settings from config.json
            
        Returns:
            dict: Merged notification settings
        """
        # Start with JSON settings as base
        merged_settings = json_settings.copy()
        
        # Override with environment variables if they exist
        if self.email_address:
            merged_settings['email'] = self.email_address
        if self.email_password:
            merged_settings['email_password'] = self.email_password
        if self.recipient_email:
            merged_settings['recipient_email'] = self.recipient_email
        
        return merged_settings
