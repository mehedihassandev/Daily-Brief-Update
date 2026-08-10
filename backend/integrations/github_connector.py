"""
GitHub Connector for Daily Brief (Python Backend)

Fetches user Pull Requests, merged PRs, assigned issues, and code reviews.
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional


class GitHubConnector:
    def __init__(self, pat_token: Optional[str] = None, username: Optional[str] = None):
        self.pat_token = pat_token
        self.username = username
        self.base_url = "https://api.github.com"

    def fetch_user_activity(self) -> Dict[str, Any]:
        if not self.pat_token:
            return self._get_mock_github_feed()

        headers = {
            "Authorization": f"Bearer {self.pat_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Daily-Brief-App"
        }

        activity = {"pull_requests": [], "issues": []}

        try:
            query = f"author:{self.username}+type:pr" if self.username else "type:pr"
            url = f"{self.base_url}/search/issues?q={query}&sort=updated&order=desc"
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                items = data.get("items", [])
                activity["pull_requests"] = [
                    {
                        "number": item.get("number"),
                        "title": item.get("title"),
                        "state": item.get("state"),
                        "html_url": item.get("html_url"),
                        "updated_at": item.get("updated_at")
                    }
                    for item in items[:10]
                ]
        except Exception as e:
            activity["error"] = str(e)

        return activity

    def _get_mock_github_feed(self) -> Dict[str, Any]:
        return {
            "merged_prs": [
                {
                    "pr_number": 142,
                    "repo": "pos-cws",
                    "title": "Verify v1.0.76 pos-cws deployment & CSV billing removal",
                    "merged_at": "Friday",
                    "author": "Me",
                    "url": "https://github.com/org/pos-cws/pull/142"
                }
            ],
            "open_prs": [
                {
                    "pr_number": 88,
                    "repo": "mobile-app-ios",
                    "title": "Fix iOS keyboard padding in order confirmation",
                    "status": "Changes Requested",
                    "author": "Me",
                    "url": "https://github.com/org/mobile-app-ios/pull/88"
                }
            ],
            "reviews_requested": [
                {
                    "pr_number": 955,
                    "repo": "payment-service",
                    "title": "EXOS-955 Duplicate payment validation check",
                    "author": "Minhaj",
                    "url": "https://github.com/org/payment-service/pull/955"
                }
            ]
        }
