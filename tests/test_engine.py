"""
Unit tests for Gemini Synthesis Engine
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine.gemini_engine import GeminiBriefEngine
from src.integrations.slack_connector import SlackConnector
from src.integrations.jira_connector import JiraConnector
from src.integrations.github_connector import GitHubConnector


class TestGeminiEngine(unittest.TestCase):
    def test_brief_synthesis(self):
        engine = GeminiBriefEngine()
        slack_feed = SlackConnector().fetch_recent_channel_messages()
        jira_feed = JiraConnector().fetch_assigned_issues()
        github_feed = GitHubConnector().fetch_user_activity()

        brief = engine.synthesize_brief(slack_feed, jira_feed, github_feed)

        self.assertIsInstance(brief, dict)
        self.assertIn("title", brief)
        self.assertIn("push_work_title", brief)
        self.assertIn("top_todos", brief)
        self.assertIn("slack_brief", brief)
        self.assertIsInstance(brief["top_todos"], list)


if __name__ == "__main__":
    unittest.main()
