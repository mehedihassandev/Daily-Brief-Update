"""
Jira / Atlassian Connector for Dia Daily Brief

Fetches pending tasks, assigned tickets, and issue updates via Atlassian Jira REST API
or simulated Jira dataset.
"""

import json
import base64
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional


class JiraConnector:
    def __init__(self, domain: Optional[str] = None, email: Optional[str] = None, api_token: Optional[str] = None):
        self.domain = domain
        self.email = email
        self.api_token = api_token

    def fetch_assigned_issues(self, jql_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch pending and assigned Jira tickets.
        Default JQL query: assignee = currentUser() AND status in ('In Progress', 'To Do', 'Open')
        """
        if not (self.domain and self.email and self.api_token):
            return self._get_mock_jira_feed()

        jql = jql_query or "assignee = currentUser() AND status in ('In Progress', 'To Do', 'Open') ORDER BY priority DESC"
        url = f"https://{self.domain}/rest/api/3/search?jql={urllib.parse.quote(jql)}&maxResults=20"
        
        credentials = f"{self.email}:{self.api_token}"
        encoded_creds = base64.b64encode(credentials.encode()).decode()

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Basic {encoded_creds}",
                    "Accept": "application/json"
                }
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                issues = data.get("issues", [])
                return [
                    {
                        "key": issue.get("key"),
                        "summary": issue.get("fields", {}).get("summary"),
                        "status": issue.get("fields", {}).get("status", {}).get("name"),
                        "priority": issue.get("fields", {}).get("priority", {}).get("name"),
                        "updated": issue.get("fields", {}).get("updated")
                    }
                    for issue in issues
                ]
        except Exception as e:
            return [{"error": f"Failed to fetch Jira issues: {str(e)}"}]

    def _get_mock_jira_feed(self) -> List[Dict[str, Any]]:
        """Mock fallback dataset mimicking Jira issues."""
        return [
            {
                "key": "EXOS-972",
                "summary": "Continue account payment work in bulk payment",
                "status": "In Progress",
                "priority": "High",
                "description": "Removing RillNo payload so payments post as Account Payments fix for duplicate payment issue.",
                "assignee": "Me",
                "project": "POS Bulk Payment"
            },
            {
                "key": "AT-590",
                "summary": "Resolve My-care app iOS build keyboard issue",
                "status": "Open",
                "priority": "Medium",
                "description": "iOS keyboard overlap issue on order confirmation screen. Loop back with Sumiya.",
                "assignee": "Me",
                "project": "My-care iOS"
            },
            {
                "key": "EXOS-971",
                "summary": "Draft RCA for bulk payment failures",
                "status": "In Progress",
                "priority": "High",
                "description": "Saifur filed RCA for bulk payment failures in production.",
                "assignee": "Saifur",
                "project": "POS Bulk Payment"
            }
        ]
