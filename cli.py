"""
CLI Interface for Daily Brief Project

Usage:
  python main.py                     # Starts Web Server on port 8090
  python main.py --port 8090         # Starts Web Server on custom port
  python cli.py --generate           # Generates Daily Brief in terminal
"""

import sys
import argparse
import json
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.server.app import load_env_file, get_current_env_config, run_server

from src.integrations.slack_connector import SlackConnector
from src.integrations.jira_connector import JiraConnector
from src.integrations.github_connector import GitHubConnector
from src.engine.gemini_engine import GeminiBriefEngine


def main():
    parser = argparse.ArgumentParser(description="Daily Brief CLI")
    parser.add_argument("--generate", action="store_true", help="Generate Daily Brief JSON")
    parser.add_argument("--server", action="store_true", help="Start Web Dashboard HTTP Server")
    parser.add_argument("--port", type=int, default=8090, help="Port for Web Server (default: 8090)")
    args = parser.parse_args()

    if args.server or "--port" in sys.argv or (not args.generate and len(sys.argv) <= 3):
        run_server(port=args.port)

    elif args.generate:
        config = get_current_env_config()
        print(f"🔍 Fetching workspace streams (.env config: Jira Domain={config['jira_domain']})...")
        
        slack_client = SlackConnector(bot_token=config["slack_token"])
        jira_client = JiraConnector(
            domain=config["jira_domain"],
            email=config["jira_email"],
            api_token=config["jira_token"]
        )
        github_client = GitHubConnector(pat_token=config["github_token"])
        engine = GeminiBriefEngine(api_key=config["gemini_key"])

        slack_feed = slack_client.fetch_recent_channel_messages()
        jira_feed = jira_client.fetch_assigned_issues()
        github_feed = github_client.fetch_user_activity()

        print("✨ Synthesizing Daily Brief with Gemini...")
        brief = engine.synthesize_brief(slack_feed, jira_feed, github_feed)

        print("\n========================================================")
        print(f"               {brief.get('title', 'THE MONDAY BRIEF').upper()}")
        print("========================================================")
        print(f"Subtitle: {brief.get('subtitle')}\n")
        print(f"🎯 PUSH WORK FORWARD: {brief.get('push_work_title')}")
        print(f"   {brief.get('push_work_desc')}\n")

        print("💬 SLACK CHANNEL BRIEF:")
        slack_brief = brief.get("slack_brief", {})
        print(f"   {slack_brief.get('headline')}")
        for disc in slack_brief.get("key_discussions", []):
            print(f"   - [{disc.get('channel')}] {disc.get('summary')}")
        print()

        print("📋 TOP TO-DOS:")
        for todo in brief.get("top_todos", []):
            print(f"   [ ] {todo.get('title')} ({todo.get('ticket_id')})")
            print(f"       {todo.get('detail')}")
        print()

        print("📰 NEW UPDATES:")
        for update in brief.get("new_updates", []):
            print(f"   • {update.get('headline')} [{update.get('project_tag')}]")
            print(f"     {update.get('body')}")
        print("========================================================\n")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
