# Technical Architecture Guide

This document provides detailed technical information for developers working on GitHub Sentinel.

## 📁 Project Structure

GitHub Sentinel v0.6 features a modular architecture with clear separation of concerns:

```
GitHubSentinel/
├── src/
│   ├── command_tool.py        # Interactive CLI mode
│   ├── daemon_process.py      # Background scheduler mode
│   ├── gradio_server.py       # Web interface mode
│   ├── prompt_manager.py      # Prompt management system
│   ├── main.py                # Unified entry point
│   ├── llm_client.py          # AI/LLM integration
│   ├── github_client.py       # GitHub API client
│   ├── report_generator.py    # Report generation
│   ├── command_handler.py     # Command processing
│   ├── subscription_manager.py # Repository subscription handling
│   ├── notifier.py            # Notification system
│   ├── daily_progress.py      # Daily progress tracking
│   ├── utils.py               # Utility functions
│   ├── config.py              # Configuration management
│   └── logger.py              # Logging configuration
├── prompts/
│   ├── summary_prompt.txt     # Generic fallback template
│   ├── daily_report_prompt.txt # Generic fallback template
│   ├── ollama/                # Detailed prompts for local models
│   │   ├── daily_report_prompt.txt
│   │   └── summary_prompt.txt
│   ├── deepseek/              # Balanced prompts for cloud models
│   │   ├── daily_report_prompt.txt
│   │   └── summary_prompt.txt
│   └── openai/                # Concise prompts for premium models
│       ├── daily_report_prompt.txt
│       └── summary_prompt.txt
├── reports/
│   ├── exports/               # Raw activity exports (cache)
│   └── ai_reports/            # AI-generated reports
├── tests/                     # Comprehensive test suite
├── examples/                  # Demo scripts
├── logs/                      # Application logs
├── config.json               # Main configuration
└── requirements.txt          # Dependencies
```

## 🏗️ Core Architecture

### Multi-Mode Execution Framework

GitHub Sentinel v0.4+ introduces three distinct execution modes:

#### 1. Command-Line Tool Mode (`command_tool.py`)
- **Purpose**: Interactive CLI with REPL interface
- **Use Case**: Development, manual operations, testing
- **Features**: Enhanced interactive shell, command completion, error handling

#### 2. Daemon Process Mode (`daemon_process.py`)
- **Purpose**: Background service for automated monitoring
- **Use Case**: Production deployments, scheduled monitoring
- **Features**: Python-daemon implementation, signal handling, scheduled execution

#### 3. Gradio Server Mode (`gradio_server.py`)
- **Purpose**: Web-based interface for browser interaction
- **Use Case**: Team collaboration, non-technical users
- **Features**: Modern UI, file downloads, real-time status updates

### Unified Entry Point (`main.py`)

The main.py file serves as an intelligent router:

```python
def main():
    parser = argparse.ArgumentParser(description='GitHub Sentinel')
    parser.add_argument('--mode', choices=['command-tool', 'daemon', 'gradio-server'])
    
    args, remaining = parser.parse_known_args()
    
    if args.mode == 'daemon':
        from daemon_process import main as daemon_main
        daemon_main()
    elif args.mode == 'gradio-server':
        from gradio_server import main as gradio_main
        gradio_main()
    else:
        from command_tool import main as command_main
        command_main(remaining)
```

## 🤖 AI/LLM Architecture

### Provider-Specific Design (v0.6+)

GitHub Sentinel supports three AI providers with intelligent prompt optimization:

#### LLM Client Architecture

```python
class LLM:
    def __init__(self, config):
        self.config = config
        self.provider = config.get('llm', {}).get('model_type', 'ollama')
        self.prompt_manager = PromptManager()
        
    def generate_response(self, prompt_type, context):
        # Load provider-specific prompt
        prompt = self.prompt_manager.get_prompt(prompt_type, self.provider, context)
        
        # Route to appropriate provider
        if self.provider == 'ollama':
            return self._generate_response_ollama(prompt)
        elif self.provider == 'deepseek':
            return self._generate_response_cloud(prompt, 'deepseek')
        elif self.provider == 'openai':
            return self._generate_response_cloud(prompt, 'openai')
```

#### Provider Comparison

| Provider | Integration Method | Prompt Strategy | Performance |
|----------|-------------------|-----------------|-------------|
| **Ollama** | HTTP API (requests) | Detailed 1800-char prompts | Local, private |
| **DeepSeek** | OpenAI-compatible API | Balanced 800-char prompts | Cost-effective |
| **OpenAI** | Official SDK | Concise 300-char prompts | Premium quality |

### Prompt Engineering System

#### Hierarchical Prompt Loading

```python
class PromptManager:
    def get_prompt(self, prompt_type, provider, context):
        # 1. Try provider-specific prompt
        provider_prompt = f"prompts/{provider}/{prompt_type}.txt"
        if os.path.exists(provider_prompt):
            return self._load_and_substitute(provider_prompt, context)
        
        # 2. Fallback to generic prompt
        generic_prompt = f"prompts/{prompt_type}.txt"
        if os.path.exists(generic_prompt):
            return self._load_and_substitute(generic_prompt, context)
        
        # 3. Return default prompt
        return self._get_default_prompt(prompt_type, context)
```

#### Template Variable System

Prompts support dynamic variable substitution:

- `{repo_name}` - Repository name (e.g., "microsoft/vscode")
- `{date}` - Report date (e.g., "2024-01-15")
- `{org_name}` - Organization name (e.g., "microsoft")
- `{repo_simple}` - Simple repo name (e.g., "vscode")

## 🔌 GitHub API Integration

### GitHub Client Architecture

```python
class GitHubClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        })
    
    def fetch_issues(self, repo, since_date=None, until_date=None, state='closed'):
        """Fetch issues with intelligent filtering"""
        # Client-side date filtering for precision
        return self._filter_by_date_range(issues, since_date, until_date)
```

### API Rate Limiting

- **Primary Rate Limit**: 5,000 requests per hour
- **Search Rate Limit**: 30 requests per minute
- **Mitigation Strategy**: Intelligent caching, date-range filtering
- **Error Handling**: Exponential backoff, retry mechanisms

### Data Filtering Strategy

By default, GitHub Sentinel filters for the most relevant information:

- **Pull Requests**: Only merged PRs (configurable)
- **Issues**: Only closed issues (configurable)
- **Date Filtering**: Client-side precision filtering
- **Content Filtering**: Focus on meaningful activity

## 🗄️ Data Management

### Two-Level Directory Structure

```
reports/
├── exports/                     # Raw activity exports (cache layer)
│   ├── microsoft_vscode/        # Repository-specific directories
│   │   ├── 2024-01-15.md       # Single-day exports
│   │   └── 2024-01-10_to_2024-01-15.md  # Date range exports
│   └── facebook_react/
│       └── 2024-01-15.md
└── ai_reports/                  # AI-generated reports (user layer)
    ├── microsoft_vscode/
    │   ├── daily_report_2024-01-15.md
    │   └── daily_report_2024-01-10_to_2024-01-15.md
    └── consolidated_reports/    # Multi-repository reports
        └── consolidated_daily_report_2024-01-15.md
```

### Cache Strategy

- **Export Cache**: Raw GitHub data stored for reuse
- **Smart Invalidation**: Cache invalidated on new activity
- **Token Optimization**: Avoid redundant AI API calls
- **Incremental Updates**: Only process new/changed data

## 🔧 Configuration Management

### Configuration Hierarchy

1. **Environment Variables** (.env file) - Sensitive credentials
2. **Configuration File** (config.json) - Application settings
3. **Command Line Arguments** - Runtime overrides
4. **Default Values** - Fallback configuration

### Configuration Schema

```json
{
    "notification_settings": {
        "email": "string",
        "slack_webhook_url": "string",
        "smtp_server": "string",
        "smtp_port": "integer"
    },
    "subscriptions_file": "string",
    "update_interval": "integer",
    "enable_daily_reports": "boolean",
    "export_cache_dir": "string",
    "ai_reports_dir": "string",
    "llm": {
        "model_type": "enum[ollama|deepseek|openai]",
        "openai_model_name": "string",
        "deepseek_model_name": "string",
        "ollama_model_name": "string",
        "ollama_api_url": "string"
    },
    "generate_consolidated_reports": "boolean"
}
```

## 🧵 Concurrency and Threading

### Daemon Process Threading

```python
def daemon_main():
    # Main daemon thread
    daemon_thread = threading.Thread(target=run_scheduler, daemon=True)
    daemon_thread.start()
    
    # Signal handling for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Daemon process interrupted")
```

### Scheduler Implementation

- **Library**: `schedule` library for simplicity
- **Interval**: Configurable (default: 24 hours)
- **Execution**: Non-blocking with proper error handling
- **Logging**: Comprehensive logging with rotation

## 📝 Logging Architecture

### Loguru Integration (v0.5+)

```python
from loguru import logger

# Configure logger with rotation and formatting
logger.add(
    "logs/app.log",
    rotation="1 MB",
    retention="10 days",
    format="{time} | {level} | {module}:{function}:{line} | {message}",
    level="INFO"
)
```

### Log Routing Strategy

- **Stdout**: Info and debug messages (colorized)
- **Stderr**: Error and warning messages
- **File**: All messages with rotation (logs/app.log)
- **Format**: Timestamp, level, module, function, line, message

## 🧪 Testing Architecture

### Test Structure

```python
tests/
├── test_github_client.py      # GitHub API integration tests
├── test_llm_client.py         # AI provider testing
├── test_report_generator.py   # Report generation tests
├── test_command_handler.py    # Command processing tests
├── test_subscription_manager.py # Subscription management tests
├── test_notifier.py           # Notification system tests
├── test_daily_progress.py     # Progress tracking tests
└── test_utils.py              # Utility function tests
```

### Mock Strategy

- **External APIs**: Comprehensive mocking for GitHub, OpenAI, DeepSeek, Ollama
- **File System**: Isolated file operations with temporary directories
- **Network**: Mock HTTP requests and responses
- **Time**: Mock datetime for consistent testing

### Coverage Goals

- **Unit Tests**: >95% coverage for core modules
- **Integration Tests**: End-to-end workflow validation
- **Error Scenarios**: Comprehensive error handling testing

## 🚀 Deployment Considerations

### Environment Requirements

- **Python**: 3.8+ (tested on 3.11)
- **Memory**: 8GB+ recommended for local AI models
- **Storage**: 2GB+ for models and reports
- **Network**: Internet required for cloud providers, optional for Ollama

### Production Deployment

```bash
# Systemd service configuration
[Unit]
Description=GitHub Sentinel Daemon
After=network.target

[Service]
Type=simple
User=githubsentinel
WorkingDirectory=/opt/githubsentinel
ExecStart=/opt/conda/envs/githubsentinel/bin/python src/main.py --mode daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "src/main.py", "--mode", "daemon"]
```

## 🔮 Future Architecture Considerations

### Scalability Improvements

- **Database Integration**: PostgreSQL for large-scale deployments
- **Message Queues**: Redis/Celery for distributed processing
- **Microservices**: Service decomposition for enterprise deployments
- **API Gateway**: RESTful API for external integrations

### AI Provider Expansion

- **Provider Registry**: Plugin-based AI provider system
- **Model Management**: Automatic model download and versioning
- **Performance Monitoring**: AI response quality tracking
- **Cost Optimization**: Intelligent provider routing based on cost/quality

### Enhanced Features

- **Real-time Processing**: WebSocket integration for live updates
- **Advanced Analytics**: Trend analysis and predictive insights
- **Team Collaboration**: Multi-user support with role-based access
- **Enterprise Integration**: SSO, audit logging, compliance features

## 📚 Development Resources

### Key Dependencies

```
requests>=2.31.0          # HTTP client
python-dotenv>=1.0.0      # Environment variables
gradio>=4.0.0             # Web interface
loguru>=0.7.0             # Enhanced logging
schedule>=1.2.0           # Task scheduling
python-daemon>=3.0.0      # Daemon process
```

### Code Style Guidelines

- **PEP 8**: Python code style compliance
- **Type Hints**: Use type annotations where applicable
- **Docstrings**: Comprehensive function and class documentation
- **Error Handling**: Graceful error handling with meaningful messages
- **Testing**: Test-driven development with comprehensive coverage

### Performance Optimization

- **Caching**: Intelligent caching at multiple levels
- **Lazy Loading**: Load resources only when needed
- **Batch Processing**: Group API calls for efficiency
- **Memory Management**: Proper cleanup and resource management 