"""
HTTP API Server for Daily Brief Project

Serves the Web Dashboard UI and REST API endpoints:
- GET /               -> Web Dashboard UI
- GET /api/status     -> Check integration connection states & domain config
- POST /api/brief     -> Generate Daily Brief with Gemini
- POST /api/settings   -> Save API keys/tokens
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add src parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.integrations.slack_connector import SlackConnector
from src.integrations.jira_connector import JiraConnector
from src.integrations.github_connector import GitHubConnector
from src.engine.gemini_engine import GeminiBriefEngine


def load_env_file():
    """Helper to auto-load key=value lines from .env file into os.environ if present."""
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ[k.strip()] = v

load_env_file()

# In-Memory Configuration Store
APP_CONFIG = {
    "slack_token": os.environ.get("SLACK_BOT_TOKEN", ""),
    "jira_domain": os.environ.get("JIRA_DOMAIN", "exos-systems.atlassian.net"),
    "jira_email": os.environ.get("JIRA_EMAIL", ""),
    "jira_token": os.environ.get("JIRA_API_TOKEN", ""),
    "github_token": os.environ.get("GITHUB_PAT", ""),
    "gemini_key": os.environ.get("GEMINI_API_KEY", "")
}


class DailyBriefRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ["/", "/index.html"]:
            web_file = os.path.join(os.path.dirname(__file__), "../web/index.html")
            if os.path.exists(web_file):
                with open(web_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self._set_headers(200, "text/html; charset=utf-8")
                self.wfile.write(content.encode("utf-8"))
            else:
                self._set_headers(404, "text/plain")
                self.wfile.write(b"404 Not Found")

        elif path == "/api/status":
            status = {
                "slack": bool(APP_CONFIG["slack_token"]),
                "jira": bool(APP_CONFIG["jira_domain"] and APP_CONFIG["jira_token"]),
                "github": bool(APP_CONFIG["github_token"]),
                "gemini": bool(APP_CONFIG["gemini_key"]),
                "jira_domain": APP_CONFIG["jira_domain"] or "exos-systems.atlassian.net"
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(status).encode("utf-8"))

        elif path == "/api/brief":
            brief = self._generate_brief()
            self._set_headers(200)
            self.wfile.write(json.dumps(brief).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else ""

        if path == "/api/brief":
            req_data = json.loads(body) if body else {}
            api_key = req_data.get("gemini_key") or APP_CONFIG["gemini_key"]
            brief = self._generate_brief(api_key=api_key)
            self._set_headers(200)
            self.wfile.write(json.dumps(brief).encode("utf-8"))

        elif path == "/api/settings":
            try:
                data = json.loads(body)
                APP_CONFIG.update({
                    "slack_token": data.get("slack_token", APP_CONFIG["slack_token"]),
                    "jira_domain": data.get("jira_domain", APP_CONFIG["jira_domain"]),
                    "jira_email": data.get("jira_email", APP_CONFIG["jira_email"]),
                    "jira_token": data.get("jira_token", APP_CONFIG["jira_token"]),
                    "github_token": data.get("github_token", APP_CONFIG["github_token"]),
                    "gemini_key": data.get("gemini_key", APP_CONFIG["gemini_key"])
                })
                self._set_headers(200)
                self.wfile.write(json.dumps({"success": True, "message": "Settings updated successfully"}).encode("utf-8"))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def _generate_brief(self, api_key: str = None) -> dict:
        slack_client = SlackConnector(bot_token=APP_CONFIG["slack_token"])
        jira_client = JiraConnector(
            domain=APP_CONFIG["jira_domain"],
            email=APP_CONFIG["jira_email"],
            api_token=APP_CONFIG["jira_token"]
        )
        github_client = GitHubConnector(
            pat_token=APP_CONFIG["github_token"]
        )
        engine = GeminiBriefEngine(api_key=api_key or APP_CONFIG["gemini_key"])

        slack_feed = slack_client.fetch_recent_channel_messages()
        jira_feed = jira_client.fetch_assigned_issues()
        github_feed = github_client.fetch_user_activity()

        return engine.synthesize_brief(slack_feed, jira_feed, github_feed)


def run_server(port=8090):
    server_address = ("", port)
    httpd = HTTPServer(server_address, DailyBriefRequestHandler)
    print(f"🚀 Daily Brief Server running at http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    run_server(port)
