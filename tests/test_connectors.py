"""
Unit tests for Slack, Jira, and GitHub Connectors
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.integrations.slack_connector import SlackConnector
from src.integrations.jira_connector import JiraConnector
from src.integrations.github_connector import GitHubConnector


class TestConnectors(unittest.TestCase):
    def test_slack_connector_mock_fallback(self):
        slack = SlackConnector()
        feed = slack.fetch_recent_channel_messages()
        self.assertIsInstance(feed, list)
        self.assertGreater(len(feed), 0)
        self.assertIn("channel", feed[0])

    def test_jira_connector_mock_fallback(self):
        jira = JiraConnector()
        issues = jira.fetch_assigned_issues()
        self.assertIsInstance(issues, list)
        self.assertGreater(len(issues), 0)
        self.assertIn("key", issues[0])

    def test_github_connector_mock_fallback(self):
        github = GitHubConnector()
        activity = github.fetch_user_activity()
        self.assertIsInstance(activity, dict)
        self.assertIn("merged_prs", activity)


if __name__ == "__main__":
    unittest.main()
