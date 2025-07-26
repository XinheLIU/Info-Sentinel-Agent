# Info Sentinel Agent v0.6

Info Sentinel Agent is an intelligent AI-powered information monitoring and analysis tool designed for developers, project managers, and information seekers.

*This is an independent project inspired and extended based on [@DjangoPeng/GitHubSentinel](https://github.com/DjangoPeng/GitHubSentinel). It goes beyond GitHub monitoring to include comprehensive information gathering from multiple sources including HackerNews, Personal RSS Feeds, and more.*

Info Sentinel Agent automatically monitors various information sources, tracks daily activity, and generates comprehensive reports using advanced AI analysis.

## Core Features

- **Multi-Source Monitoring**: GitHub repositories, HackerNews, RSS feeds, and more information sources
- **GitHub Repository Tracking**: Automated monitoring of repository activity and changes
- **News & Trend Analysis**: HackerNews trending topics and technology discussions
- **RSS Feed Integration**: Monitor personal RSS feeds and blogs
- AI-generated daily summaries and analytical reports across all sources
- Scheduled email delivery of comprehensive reports to user-defined recipients

## 📋 Prerequisites

- Python 3.8+
- GitHub Personal Access Token
- **Ollama** (recommended, default - free local AI processing)
- *Optional*: DeepSeek API Key or OpenAI API Key (for cloud-based AI providers)
- Conda (recommended) or pip for package management


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

## Detailed User' Guides and 🛠️ Troubleshooting

See [User Guide](docs/03-product-design/user-guide.md)

## 📚 Documentation

For comprehensive documentation, see: [Documentation](docs/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request


## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/GitHubSentinel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/GitHubSentinel/discussions)
- **Email**: your-email@example.com

---

**GitHubSentinel v0.6** - Intelligent GitHub Repository Monitoring with Local AI Revolution, Provider-Specific Prompt Engineering, and Complete AI Independence
