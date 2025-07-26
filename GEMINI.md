# Gemini's Scratchpad

## Task

Analyze the codebase, especially under `/src`, and document the main architecture, workflow, classes, and their relationships in this file.

[ ] Task 1: Analyze the codebase
[ ] Task 2: Document the architecture
[ ] Task 3: Document the workflow
[ ] Task 4: Document the main classes and their relationships

---

## Project Understanding

Based on the analysis of the `src` directory, here's a breakdown of the GitHubSentinel project:

### Main Architecture

The application follows a modular architecture with clear separation of concerns. Key components include:

-   **Configuration (`config.py`):** A centralized `Config` class loads settings from `config.json` and environment variables (`.env`). It manages configurations for GitHub API, LLM providers (OpenAI, DeepSeek, Ollama), and notifications.
-   **Core Logic:**
    -   `github_client.py`: Handles all interactions with the GitHub API. The `GitHubClient` class is responsible for fetching data like commits, issues, and pull requests.
    -   `llm_client.py`: Provides an interface to Large Language Models. The `LLM` (aliased as `LLMClient`) class supports different providers and is used for generating summaries and reports.
    -   `report_generator.py`: The `ReportGenerator` class orchestrates the creation of reports. It uses `github_client` to get data, caches it, and then uses `llm_client` to generate AI-powered analysis.
-   **User Interfaces:** The application supports multiple modes of operation:
    -   `command_tool.py` & `command_handler.py`: A command-line interface (CLI) for interactive use. `CommandHandler` parses and executes commands.
    -   `daemon_process.py`: A background process that runs scheduled tasks, like daily report generation.
    -   `gradio_server.py`: A web-based UI built with Gradio for a more user-friendly experience.
-   **Supporting Modules:**
    -   `subscription_manager.py`: Manages the list of subscribed repositories.
    -   `prompt_manager.py`: Manages and loads prompts for the LLM, with support for provider-specific templates.
    -   `notifier.py`: Handles sending notifications, primarily via email.
    -   `logger.py`: Configures logging for the application using `loguru`.
    -   `main.py`: The main entry point that routes to the different execution modes (CLI, daemon, or web server).

### Main Workflow

The primary workflow of GitHubSentinel revolves around fetching data from GitHub, processing it, and generating reports.

1.  **Subscription:** The user subscribes to one or more GitHub repositories using the `add` command (or through configuration).
2.  **Data Fetching:** The `GitHubClient` fetches updates (commits, issues, PRs) for the subscribed repositories for a specified time range.
3.  **Progress Exporting:** The fetched data is first exported into a structured markdown file and stored in a cache directory (`reports/exports`). This is handled by the `ReportGenerator`. This cached file serves as the raw data for AI analysis.
4.  **Report Generation:**
    -   The `ReportGenerator` reads the cached markdown file.
    -   If there's meaningful activity, it passes the content to the `LLMClient`.
    -   The `LLMClient` uses a prompt from the `PromptManager` to generate a comprehensive, AI-powered report.
    -   The final report is saved in the `reports/ai_reports` directory.
5.  **Notification:** The `Notifier` can be used to send the generated report via email.

This workflow can be triggered manually via the CLI or automatically by the daemon process. The Gradio interface provides a web-based way to trigger report generation.

### Main Classes and Their Relationships

-   **`main.py`**: The entry point. It determines the execution mode and calls the appropriate main function from `command_tool.py`, `daemon_process.py`, or `gradio_server.py`.

-   **`Config`**: Instantiated by the main application classes (`GitHubSentinelCLI`, `GitHubSentinelGradio`, `daemon_process`). It's passed to other components that need access to configuration, such as `GitHubClient`, `LLMClient`, and `Notifier`.

-   **`GitHubClient`**: Used by `CommandHandler`, `ReportGenerator`, and the daemon process to fetch data from GitHub. It requires the GitHub token from the `Config` object.

-   **`SubscriptionManager`**: Manages the `subscriptions.json` file. It's used by `CommandHandler` and the daemon to get the list of repositories to process.

-   **`LLMClient` (`LLM`)**: The core of the AI functionality. It's instantiated by `ReportGenerator` and `GitHubSentinelCLI`. It uses the `Config` object to determine the provider and API keys. It also uses `PromptManager` to get the correct prompts.

-   **`PromptManager`**: Used by `LLMClient` to load and format prompts. It's initialized with a specific provider to load the correct templates.

-   **`ReportGenerator`**: A central class that ties together data fetching and AI analysis.
    -   It's used by `CommandHandler` and the daemon.
    -   It uses `GitHubClient` to fetch data if a cached file doesn't exist.
    -   It uses `LLMClient` to generate the final AI report from the cached data.

-   **`CommandHandler`**: The brain of the CLI.
    -   It uses `SubscriptionManager` to manage subscriptions.
    -   It uses `ReportGenerator` to create reports.
    -   It uses `GitHubClient` indirectly through `ReportGenerator`.
    -   It can use `Notifier` to send emails.

-   **`Notifier`**: Used by `CommandHandler` and the daemon to send notifications. It gets its settings from the `Config` object.

-   **`DailyProgressExporter`**: This class seems to be a precursor to the export functionality now integrated into `ReportGenerator`. It's responsible for creating the markdown files from GitHub activity. It is used by `CommandHandler`.

-   **`GitHubSentinelCLI`**, **`GitHubSentinelGradio`**, **`daemon_process.py`**: These are the top-level classes/modules for the different execution modes. They initialize all the necessary components (`Config`, `GitHubClient`, `ReportGenerator`, etc.) and manage the application's lifecycle in their respective modes.
