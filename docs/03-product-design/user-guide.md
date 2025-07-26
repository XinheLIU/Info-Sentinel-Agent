# GitHub Sentinel 

GitHub Sentinel is an intelligent AI-powered tool designed for developers and project managers. 

- [GitHub Sentinel](#github-sentinel)
  - [� Prerequisites](#-prerequisites)
  - [🛠️ Installation](#️-installation)
    - [Using Conda (Recommended)](#using-conda-recommended)
    - [Using pip](#using-pip)
  - [🦙 Ollama Setup (Recommended)](#-ollama-setup-recommended)
    - [Install Ollama](#install-ollama)
    - [Download AI Models](#download-ai-models)
    - [Start Ollama Service](#start-ollama-service)
  - [⚙️ Configuration](#️-configuration)
    - [Environment Variables](#environment-variables)
    - [Application Settings](#application-settings)
  - [🎯 Quick Start](#-quick-start)
    - [🦙 5-Minute Local Setup (Recommended - Free \& Local)](#-5-minute-local-setup-recommended---free--local)
  - [🎯 Usage](#-usage)
    - [A. Command-Line Tool (Interactive)](#a-command-line-tool-interactive)
    - [B. Daemon Process (Background)](#b-daemon-process-background)
    - [C. Web Interface (Browser)](#c-web-interface-browser)
  - [Command Reference](#command-reference)
    - [Basic Commands](#basic-commands)
    - [Report Generation](#report-generation)
    - [Provider Switching](#provider-switching)
  - [🛠️ Troubleshooting](#️-troubleshooting)
    - [Common Issues](#common-issues)
  - [📁 Output Structure](#-output-structure)
  - [📚 Advanced Features](#-advanced-features)
    - [Prompt Customization (v0.6+)](#prompt-customization-v06)
    - [Automation \& Integration](#automation--integration)


## 📋 Prerequisites

- Python 3.8+
- GitHub Personal Access Token
- **Ollama** (recommended, default - free local AI processing)
- *Optional*: DeepSeek API Key or OpenAI API Key (for cloud-based AI providers)
- Conda (recommended) or pip for package management

## 🛠️ Installation

### Using Conda (Recommended)

1. **Create and activate conda environment:**
   ```bash
   conda create -n githubsentinel python=3.11
   conda activate githubsentinel
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/GitHubSentinel.git
   cd GitHubSentinel
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Using pip

1. **Clone and install:**
   ```bash
   git clone https://github.com/xinheliu/GitHubSentinel.git
   cd GitHubSentinel
   pip install -r requirements.txt
   ```

## 🦙 Ollama Setup (Recommended)

GitHub Sentinel v0.6 defaults to **Ollama** for completely free, local AI processing. This provides privacy-focused analysis without requiring API keys or internet connectivity for AI features.

### Install Ollama

**macOS/Linux:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Or with Homebrew on macOS
brew install ollama
```

**Windows:**
- Download from [https://ollama.ai/download/windows](https://ollama.ai/download/windows)
- Run the installer

**Docker:**
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### Download AI Models

```bash
# Default model (recommended) - Llama 3.1 8B
ollama pull llama3.1

# Alternative models
ollama pull mistral          # Mistral 7B - faster inference
ollama pull qwen:4b         # Qwen 4B - lightweight option
ollama pull phi3            # Microsoft Phi-3 - efficient model

# List available models
ollama list
```

### Start Ollama Service

```bash
# Start Ollama server (runs on http://localhost:11434)
ollama serve

# Or run in background
nohup ollama serve > ollama.log 2>&1 &

# Verify it's running
curl http://localhost:11434/api/tags
```

**Note:** The Ollama service must be running for GitHub Sentinel to generate AI reports. You can start it once and leave it running in the background.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required - GitHub Personal Access Token
GITHUB_TOKEN=your_github_personal_access_token

# Optional - Only needed if using cloud AI providers
# Ollama (default) requires no API keys - completely free local processing

# DeepSeek API Key (cost-effective cloud option)
DEEPSEEK_API_KEY=your_deepseek_api_key

# OpenAI API Key (premium cloud option)
OPENAI_API_KEY=your_openai_api_key
```

### Application Settings

Configure `config.json` with your preferences:

```json
{
    "notification_settings": {
        "email": "your_email@example.com",
        "slack_webhook_url": "your_slack_webhook_url"
    },
    "subscriptions_file": "subscriptions.json",
    "update_interval": 86400,
    "enable_daily_reports": true,
    "export_cache_dir": "reports/exports",
    "ai_reports_dir": "reports/ai_reports",
    "llm": {
        "model_type": "ollama",
        "openai_model_name": "gpt-4o-mini",
        "deepseek_model_name": "deepseek-chat",
        "ollama_model_name": "llama3.1",
        "ollama_api_url": "http://localhost:11434/api/chat"
    },
    "generate_consolidated_reports": false
}
```

**Available AI Providers:**
- **`ollama`** (default): Free local processing, no API keys required
- **`deepseek`**: Cost-effective cloud processing ($0.14 per 1M tokens)
- **`openai`**: Premium cloud processing with GPT models

## 🎯 Quick Start

### 🦙 5-Minute Local Setup (Recommended - Free & Local)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Download AI model (one-time setup)
ollama pull llama3.1

# 3. Start Ollama service
ollama serve &

# 4. Clone and setup GitHub Sentinel
git clone https://github.com/xinheliu/GitHubSentinel.git
cd GitHubSentinel
pip install -r requirements.txt

# 5. Configure GitHub token (create .env file)
echo "GITHUB_TOKEN=your_github_token_here" > .env

# 6. Add repositories and generate reports
python src/main.py add microsoft/vscode
python src/main.py daily-workflow
```

**That's it!** You now have completely free, local AI-powered GitHub monitoring with no API costs.

## 🎯 Usage

GitHub Sentinel offers three flexible execution modes:

### A. Command-Line Tool (Interactive)

```bash
# Start interactive CLI
python src/main.py

GitHub Sentinel v0.6> add microsoft/vscode
GitHub Sentinel v0.6> daily-workflow
GitHub Sentinel v0.6> help
```

### B. Daemon Process (Background)

```bash
# Start background monitoring
python src/main.py --mode daemon

# Or run daemon directly
python src/daemon_process.py
```

### C. Web Interface (Browser)

```bash
# Start web interface
python src/main.py --mode gradio-server
# Access at http://localhost:7860
```

## Command Reference

### Basic Commands
```bash
add <repo>          # Add repository subscription
remove <repo>       # Remove repository subscription  
list               # List all current subscriptions
```

### Report Generation
```bash
export-progress [--repo <repo>] [--date YYYY-MM-DD]
generate-report [--repo <repo>] [--date YYYY-MM-DD]
daily-workflow [--date YYYY-MM-DD]  # Complete workflow
```

### Provider Switching
```bash
# Switch to Ollama (free, local)
python -c "
import json
with open('config.json', 'r') as f: config = json.load(f)
config['llm']['model_type'] = 'ollama'
with open('config.json', 'w') as f: json.dump(config, f, indent=4)
"

# Switch to DeepSeek (cost-effective cloud)
# Update model_type to 'deepseek' and add DEEPSEEK_API_KEY to .env
```

## 🛠️ Troubleshooting

### Common Issues

1. **"GITHUB_TOKEN environment variable is required"**
   - Create `.env` file with `GITHUB_TOKEN=your_token`
   - Ensure the token has proper repository access permissions

2. **Ollama connection errors**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama if not running
   ollama serve
   
   # Verify your model is downloaded
   ollama list
   
   # Pull the default model if missing
   ollama pull llama3.1
   ```

3. **"Error generating response with ollama LLM"**
   - Ensure Ollama service is running: `ollama serve`
   - Check model is available: `ollama list`
   - Verify API URL in config.json: `"ollama_api_url": "http://localhost:11434/api/chat"`

4. **Slow AI report generation with Ollama**
   - Use a smaller model: `ollama pull qwen:4b` and update config
   - Ensure sufficient RAM (8GB+ recommended for llama3.1)
   - Consider using cloud providers for faster processing

## 📁 Output Structure

```
reports/
├── exports/                     # Raw activity exports (cache)
│   ├── microsoft_vscode/        
│   │   ├── 2024-01-15.md
│   │   └── 2024-01-10_to_2024-01-15.md
│   └── facebook_react/
│       └── 2024-01-15.md
└── ai_reports/                  # AI-generated reports
    ├── microsoft_vscode/
    │   ├── daily_report_2024-01-15.md
    │   └── daily_report_2024-01-10_to_2024-01-15.md
    └── consolidated_reports/
        └── consolidated_daily_report_2024-01-15.md
```

## 📚 Advanced Features

### Prompt Customization (v0.6+)

Customize AI behavior with **provider-specific prompt engineering**:

```bash
# Edit provider-specific prompts for optimal performance
nano prompts/ollama/summary_prompt.txt      # Detailed prompts for local models
nano prompts/deepseek/summary_prompt.txt    # Balanced prompts for cloud efficiency
nano prompts/openai/summary_prompt.txt      # Concise prompts for premium models

# Test prompts with dry-run mode
python src/main.py generate-report --dry-run
```

### Automation & Integration

Use cron or task scheduler for automated daily reports:

```bash
# Daily at 9 AM
0 9 * * * cd /path/to/githubsentinel && conda activate githubsentinel && python src/main.py daily-workflow
```