#!/usr/bin/env python3

"""
GitHub Sentinel - Unified Entry Point
A tool for monitoring GitHub repository releases and daily progress.

 Now supports three execution modes:
- Command Line Tool (default/interactive)
- Daemon Process (background scheduler)
- Gradio Server (web interface)
"""

import sys
import os
import argparse

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import LOG


def print_version_info():
    """Print GitHub Sentinel version and mode information"""
    print("🚀 GitHub Sentinel v0.7")
    print("=" * 50)
    print("Intelligent GitHub Repository Monitoring with AI-Powered Insights")
    print()
    print("Available execution modes:")
    print("  • Command Line Tool   - Interactive CLI interface")
    print("  • Daemon Process      - Background automated monitoring")
    print("  • Gradio Server       - Web-based user interface")
    print()


def main():
    """Main entry point with mode selection for GitHub Sentinel v0.7"""
    
    # Create argument parser for mode selection
    parser = argparse.ArgumentParser(
        description="GitHub Sentinel v0.7 - Intelligent Repository Monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Execution Modes:
  command-tool    Interactive command line interface (default)
  daemon         Background scheduler for automated monitoring  
  gradio-server  Web interface accessible via browser

Examples:
  python src/main.py                    # Interactive CLI (default)
  python src/main.py --mode daemon      # Background daemon
  python src/main.py --mode gradio      # Web interface
  python src/main.py add microsoft/vscode  # Direct command execution

For backward compatibility, direct commands are still supported.
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['command-tool', 'daemon', 'gradio-server'],
        default='command-tool',
        help='Execution mode (default: command-tool)'
    )
    
    parser.add_argument(
        '--version', 
        action='store_true',
        help='Show version information'
    )
    
    # Parse known args to allow for command pass-through
    args, remaining_args = parser.parse_known_args()
    
    if args.version:
        print_version_info()
        return
    
    # If there are remaining arguments and no explicit mode, assume command execution
    if remaining_args and args.mode == 'command-tool':
        # Pass through to command tool with arguments
        LOG.info("Executing direct command via command line tool")
        sys.argv = ['command_tool.py'] + remaining_args
        try:
            from command_tool import main as command_main
            command_main()
        except ImportError as e:
            LOG.error(f"Failed to import command_tool: {e}")
            sys.exit(1)
        return
    
    # Route to appropriate mode
    try:
        if args.mode == 'command-tool':
            print_version_info()
            print("🔧 Starting Command Line Tool mode...")
            print("Type 'help' for available commands or 'exit' to quit.")
            print()
            from command_tool import main as command_main
            command_main()
            
        elif args.mode == 'daemon':
            print_version_info()
            print("🔄 Starting Daemon Process mode...")
            print("Background scheduler will monitor repositories automatically.")
            print()
            from daemon_process import main as daemon_main
            daemon_main()
            
        elif args.mode == 'gradio-server':
            print_version_info()
            print("🌐 Starting Gradio Server mode...")
            print("Web interface will be available at http://localhost:7860")
            print()
            from gradio_server import main as gradio_main
            gradio_main()
            
    except ImportError as e:
        LOG.error(f"Failed to import {args.mode} module: {e}")
        print(f"❌ Error: Could not start {args.mode} mode")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting GitHub Sentinel...")
        sys.exit(0)
    except Exception as e:
        LOG.error(f"Error in {args.mode} mode: {e}")
        print(f"❌ Error in {args.mode} mode: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
