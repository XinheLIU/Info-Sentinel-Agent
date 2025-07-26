import os
import json
from logger import LOG
from typing import Dict, Any


class PromptManager:
    """Manager for loading and formatting prompt templates with provider-specific support"""
    
    def __init__(self, prompts_dir: str = "prompts", provider: str = None):
        """
        Initialize the prompt manager
        
        Args:
            prompts_dir: Directory containing prompt template files
            provider: AI provider name (ollama, openai, deepseek) for specific prompts
        """
        self.prompts_dir = prompts_dir
        self.provider = provider
        self.prompts_cache = {}
        
        # Load all prompt templates
        self._load_prompts()
    
    def _load_prompts(self):
        """Load prompt templates with provider-specific prioritization"""
        if not os.path.exists(self.prompts_dir):
            LOG.warning(f"Prompts directory {self.prompts_dir} does not exist")
            return
        
        try:
            # Load summary prompt (provider-specific first, then generic)
            summary_prompt = self._load_prompt_with_fallback("summary_prompt.txt")
            if summary_prompt:
                self.prompts_cache["summary"] = summary_prompt
                source = f"{self.provider}-specific" if self.provider and self._provider_prompt_exists("summary_prompt.txt") else "generic"
                LOG.debug(f"Loaded {source} summary prompt template")
            
            # Load daily report prompt (provider-specific first, then generic)
            daily_report_prompt = self._load_prompt_with_fallback("daily_report_prompt.txt")
            if daily_report_prompt:
                self.prompts_cache["daily_report"] = daily_report_prompt
                source = f"{self.provider}-specific" if self.provider and self._provider_prompt_exists("daily_report_prompt.txt") else "generic"
                LOG.debug(f"Loaded {source} daily report prompt template")
            
            provider_info = f" (provider: {self.provider})" if self.provider else ""
            LOG.info(f"Loaded {len(self.prompts_cache)} prompt templates{provider_info}")
            
        except Exception as e:
            LOG.error(f"Error loading prompt templates: {str(e)}")
            raise
    
    def _load_prompt_with_fallback(self, filename: str) -> str:
        """
        Load a prompt file with provider-specific fallback logic
        
        Args:
            filename: Name of the prompt file to load
            
        Returns:
            Prompt content string or None if not found
        """
        # Try provider-specific prompt first
        if self.provider:
            provider_path = os.path.join(self.prompts_dir, self.provider, filename)
            if os.path.exists(provider_path):
                with open(provider_path, "r", encoding='utf-8') as f:
                    return f.read()
        
        # Fall back to generic prompt
        generic_path = os.path.join(self.prompts_dir, filename)
        if os.path.exists(generic_path):
            with open(generic_path, "r", encoding='utf-8') as f:
                return f.read()
        
        return None
    
    def _provider_prompt_exists(self, filename: str) -> bool:
        """Check if a provider-specific prompt exists"""
        if not self.provider:
            return False
        provider_path = os.path.join(self.prompts_dir, self.provider, filename)
        return os.path.exists(provider_path)
    
    def get_summary_prompt(self, issues_content: str, prs_content: str) -> str:
        """
        Get formatted summary prompt
        
        Args:
            issues_content: Raw issues content
            prs_content: Raw pull requests content
            
        Returns:
            Formatted prompt string
        """
        template = self.prompts_cache.get("summary")
        if not template:
            LOG.warning("Summary prompt template not found, using fallback")
            return self._get_fallback_summary_prompt(issues_content, prs_content)
        
        return template.format(
            issues_content=issues_content,
            prs_content=prs_content
        )
    
    def get_daily_report_prompt(self, issues_content: str, prs_content: str, 
                               repo_name: str, date: str) -> str:
        """
        Get formatted daily report prompt
        
        Args:
            issues_content: Raw issues content
            prs_content: Raw pull requests content
            repo_name: Repository name
            date: Date string
            
        Returns:
            Formatted prompt string
        """
        template = self.prompts_cache.get("daily_report")
        if not template:
            LOG.warning("Daily report prompt template not found, using fallback")
            return self._get_fallback_daily_report_prompt(issues_content, prs_content, repo_name, date)
        
        return template.format(
            issues_content=issues_content,
            prs_content=prs_content,
            repo_name=repo_name,
            date=date
        )
    
    def save_prompt_to_file(self, prompt: str, filename: str = "debug_prompt.txt"):
        """
        Save prompt to file for debugging purposes
        
        Args:
            prompt: Prompt content to save
            filename: Filename to save to
        """
        try:
            os.makedirs("logs", exist_ok=True)
            filepath = os.path.join("logs", filename)
            with open(filepath, "w", encoding='utf-8') as f:
                f.write(prompt)
            LOG.debug(f"Prompt saved to {filepath}")
        except Exception as e:
            LOG.error(f"Error saving prompt to file: {str(e)}")
    
    def save_messages_to_file(self, messages: list, filename: str = "debug_messages.json"):
        """
        Save messages array to JSON file for debugging
        
        Args:
            messages: Messages array to save
            filename: Filename to save to
        """
        try:
            os.makedirs("logs", exist_ok=True)
            filepath = os.path.join("logs", filename)
            with open(filepath, "w", encoding='utf-8') as f:
                json.dump(messages, f, indent=4, ensure_ascii=False)
            LOG.debug(f"Messages saved to {filepath}")
        except Exception as e:
            LOG.error(f"Error saving messages to file: {str(e)}")
    
    def _get_fallback_summary_prompt(self, issues_content: str, prs_content: str) -> str:
        """Fallback summary prompt if template file is missing"""
        return f"""
        Please provide a concise summary of the following GitHub activity:
        
        Issues:
        {issues_content}
        
        Pull Requests:
        {prs_content}
        
        Focus on the main themes, important changes, and overall activity level.
        """
    
    def _get_fallback_daily_report_prompt(self, issues_content: str, prs_content: str, 
                                        repo_name: str, date: str) -> str:
        """Fallback daily report prompt if template file is missing"""
        return f"""
        Create a professional daily report for the GitHub repository "{repo_name}" for {date}.
        
        Based on the following data:
        
        Issues:
        {issues_content}
        
        Pull Requests:
        {prs_content}
        
        Please create a comprehensive daily report that includes:
        1. Executive Summary
        2. Key Highlights
        3. Issues Analysis
        4. Pull Requests Analysis
        5. Recommendations or Next Steps
        
        Format the output as a well-structured markdown document.
        """
    
    def reload_prompts(self):
        """Reload all prompt templates from files"""
        self.prompts_cache.clear()
        self._load_prompts()
        LOG.info("Prompt templates reloaded")
    
    def set_provider(self, provider: str):
        """
        Change the provider and reload prompts
        
        Args:
            provider: New provider name (ollama, openai, deepseek)
        """
        if provider != self.provider:
            self.provider = provider
            self.reload_prompts()
            LOG.info(f"Switched to {provider} provider prompts") 