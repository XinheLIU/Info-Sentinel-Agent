#!/usr/bin/env python3

"""
GitHubSentinel v0.3 - DeepSeek Integration Demo

This demo showcases the new DeepSeek API integration and multi-provider LLM support.
"""

import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm_client import LLMClient
from config import Config


def demo_deepseek_provider():
    """Demonstrate DeepSeek provider functionality"""
    print("🤖 Demo: DeepSeek Provider")
    print("=" * 50)
    
    # Set test DeepSeek API key
    os.environ['DEEPSEEK_API_KEY'] = 'sk-test-deepseek-key-12345'
    
    try:
        # Create a config with DeepSeek settings
        config = Config()
        config.llm = {'model_type': 'deepseek', 'deepseek_model_name': 'deepseek-chat'}
        
        # Create DeepSeek client
        client = LLMClient(config)
        print(f"✅ DeepSeek LLM Client initialized")
        print(f"   Provider: {client.model_type}")
        print(f"   Model: {client.model_name}")
        
        # Test with reasoning model
        config.llm['deepseek_model_name'] = 'deepseek-reasoner'
        deepseek_client = LLMClient(config)
        print(f"\n✅ Explicit DeepSeek client with reasoning model")
        print(f"   Provider: {deepseek_client.model_type}")
        print(f"   Model: {deepseek_client.model_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def demo_openai_provider():
    """Demonstrate OpenAI provider functionality"""
    print("🧠 Demo: OpenAI Provider")
    print("=" * 50)
    
    # Set test OpenAI API key
    os.environ['OPENAI_API_KEY'] = 'sk-test-openai-key-67890'
    
    try:
        # Create a config with OpenAI settings
        config = Config()
        config.llm = {'model_type': 'openai', 'openai_model_name': 'gpt-4o'}
        
        # Create OpenAI client
        openai_client = LLMClient(config)
        print(f"✅ OpenAI LLM Client initialized")
        print(f"   Provider: {openai_client.model_type}")
        print(f"   Model: {openai_client.model_name}")
        
        # Test with GPT-3.5
        config.llm['openai_model_name'] = 'gpt-3.5-turbo'
        gpt35_client = LLMClient(config)
        print(f"\n✅ OpenAI client with GPT-3.5")
        print(f"   Provider: {gpt35_client.model_type}")
        print(f"   Model: {gpt35_client.model_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def demo_ollama_provider():
    """Demonstrate Ollama provider functionality"""
    print("🦙 Demo: Ollama Provider")
    print("=" * 50)
    
    try:
        # Create a config with Ollama settings
        config = Config()
        config.llm = {
            'model_type': 'ollama', 
            'ollama_model_name': 'llama3.1',
            'ollama_api_url': 'http://localhost:11434/api/chat'
        }
        
        # Create Ollama client
        ollama_client = LLMClient(config)
        print(f"✅ Ollama LLM Client initialized")
        print(f"   Provider: {ollama_client.model_type}")
        print(f"   Model: {ollama_client.model_name}")
        print(f"   API URL: {ollama_client.api_url}")
        
        # Test with different model
        config.llm['ollama_model_name'] = 'mistral'
        mistral_client = LLMClient(config)
        print(f"\n✅ Ollama client with Mistral model")
        print(f"   Provider: {mistral_client.model_type}")
        print(f"   Model: {mistral_client.model_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def demo_configuration_scenarios():
    """Demonstrate different configuration scenarios"""
    print("⚙️  Demo: Configuration Scenarios")
    print("=" * 50)
    
    # Scenario 1: DeepSeek only
    print("📌 Scenario 1: DeepSeek configuration")
    os.environ['DEEPSEEK_API_KEY'] = 'sk-test-deepseek-key-12345'
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    try:
        config = Config()
        config.llm = {'model_type': 'deepseek', 'deepseek_model_name': 'deepseek-chat'}
        client = LLMClient(config)
        print(f"   Result: {client.model_type} with {client.model_name}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Scenario 2: OpenAI only
    print("\n📌 Scenario 2: OpenAI configuration")
    if 'DEEPSEEK_API_KEY' in os.environ:
        del os.environ['DEEPSEEK_API_KEY']
    os.environ['OPENAI_API_KEY'] = 'sk-test-openai-key-67890'
    
    try:
        config = Config()
        config.llm = {'model_type': 'openai', 'openai_model_name': 'gpt-4o'}
        client = LLMClient(config)
        print(f"   Result: {client.model_type} with {client.model_name}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Scenario 3: Ollama (no API key needed)
    print("\n📌 Scenario 3: Ollama configuration (no API key needed)")
    if 'DEEPSEEK_API_KEY' in os.environ:
        del os.environ['DEEPSEEK_API_KEY']
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    try:
        config = Config()
        config.llm = {'model_type': 'ollama', 'ollama_model_name': 'llama3.1'}
        client = LLMClient(config)
        print(f"   Result: {client.model_type} with {client.model_name} (local)")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Scenario 4: Invalid configuration
    print("\n📌 Scenario 4: Invalid configuration")
    
    try:
        config = Config()
        config.llm = {'model_type': 'invalid_provider'}
        client = LLMClient(config)
        print(f"   Result: {client.model_type} with {client.model_name}")
    except Exception as e:
        print(f"   Expected Error: {e}")
    
    print()


def main():
    """Main demonstration function"""
    print("🚀 GitHubSentinel LLM Integration Demo")
    print("=" * 50)
    print()
    
    # Run demonstrations
    demo_deepseek_provider()
    demo_openai_provider()
    demo_ollama_provider()
    demo_configuration_scenarios()
    
    print("🎉 LLM Integration Demo completed!")
    print()
    print("Key Features:")
    print("1. ✅ Simplified configuration-based initialization")
    print("2. ✅ Three provider support: OpenAI, DeepSeek, Ollama")
    print("3. ✅ No auto-detection complexity")
    print("4. ✅ Local model support via Ollama")
    print("5. ✅ Explicit error handling")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 