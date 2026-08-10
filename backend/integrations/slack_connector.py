"""
Slack Connector for Daily Brief (Python Backend)

Fetches recent channel conversations, thread messages, and direct mentions
using the Slack Web API.
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional


class SlackConnector:
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"

    def fetch_recent_channel_messages(self, channel_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if not self.bot_token:
            return self._get_mock_slack_feed()

        channel_ids = channel_ids or []
        summaries = []

        for ch in channel_ids:
            try:
                req = urllib.request.Request(
                    f"{self.base_url}/conversations.history?channel={ch}&limit=30",
                    headers={"Authorization": f"Bearer {self.bot_token}"}
                )
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode())
                    if data.get("ok"):
                        messages = data.get("messages", [])
                        summaries.append({
                            "channel_id": ch,
                            "messages_count": len(messages),
                            "recent_messages": [
                                {
                                    "user": m.get("user", "unknown"),
                                    "text": m.get("text", ""),
                                    "ts": m.get("ts")
                                }
                                for m in messages[:10]
                            ]
                        })
            except Exception as e:
                summaries.append({"channel_id": ch, "error": str(e)})

        return summaries

    def _get_mock_slack_feed(self) -> List[Dict[str, Any]]:
        return [
            {
                "channel": "#proj-pos-bulk-payment",
                "topic": "Duplicate payment investigation & RCA",
                "summary": "Saifur reported bulk payment failures in production. Minhaj confirmed payment service validation fix is on staging. Sumiya asked if EXOS-972 account payment fix covers CSV billing removal.",
                "key_messages": [
                    {"user": "@saifur", "text": "Filed EXOS-971 for bulk payment failures. Need RCA draft by EOD."},
                    {"user": "@minhaj", "text": "Duplicate payment validation patch is deployed on payment-service pre-prod."},
                    {"user": "@sumiya", "text": "@me Can you verify v1.0.76 pos-cws deployment status at 11 AM sync?"}
                ]
            },
            {
                "channel": "#mobile-app-ios",
                "topic": "My-care iOS keyboard fix & order cleanup",
                "summary": "Discussion on AT-590 iOS keyboard overlapping issue on order screen.",
                "key_messages": [
                    {"user": "@sumiya", "text": "AT-590 iOS build fix merged. Waiting for keyboard padding adjustment on order cleanup."}
                ]
            }
        ]
