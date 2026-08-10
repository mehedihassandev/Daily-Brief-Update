"""
Python REST API Backend for Daily Brief Project

Serves:
- React Single Page Application (from frontend/dist or frontend/index.html)
- REST API Endpoints (/api/status, /api/brief, /api/settings)
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from integrations.slack_connector import SlackConnector
from integrations.jira_connector import JiraConnector
from integrations.github_connector import GitHubConnector
from engine.gemini_engine import GeminiBriefEngine


def load_env_file():
    """Helper to auto-load key=value lines from .env file into os.environ."""
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ[k.strip()] = v


def get_current_env_config():
    """Fetch all parameters dynamically from environment variables."""
    load_env_file()
    return {
        "slack_token": os.environ.get("SLACK_BOT_TOKEN", "").strip(),
        "jira_domain": os.environ.get("JIRA_DOMAIN", "").strip(),
        "jira_email": os.environ.get("JIRA_EMAIL", "").strip(),
        "jira_token": os.environ.get("JIRA_API_TOKEN", "").strip(),
        "github_token": os.environ.get("GITHUB_PAT", "").strip(),
        "gemini_key": os.environ.get("GEMINI_API_KEY", "").strip()
    }


class BackendRequestHandler(BaseHTTPRequestHandler):
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
        config = get_current_env_config()

        if path == "/api/status":
            status = {
                "slack": bool(config["slack_token"]),
                "jira": bool(config["jira_domain"] and config["jira_token"]),
                "github": bool(config["github_token"]),
                "gemini": bool(config["gemini_key"]),
                "jira_domain": config["jira_domain"],
                "jira_email": config["jira_email"]
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(status).encode("utf-8"))

        elif path == "/api/brief":
            brief = self._generate_brief(config)
            self._set_headers(200)
            self.wfile.write(json.dumps(brief).encode("utf-8"))

        else:
            # Serve React Production Build Files (frontend/dist)
            dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))
            rel_file = path.lstrip("/") or "index.html"
            file_path = os.path.join(dist_dir, rel_file)

            if not os.path.exists(file_path):
                file_path = os.path.join(dist_dir, "index.html")

            if os.path.exists(file_path):
                mime = "text/html; charset=utf-8"
                if file_path.endswith(".js"):
                    mime = "application/javascript"
                elif file_path.endswith(".css"):
                    mime = "text/css"
                elif file_path.endswith(".json"):
                    mime = "application/json"
                elif file_path.endswith(".svg"):
                    mime = "image/svg+xml"

                with open(file_path, "rb") as f:
                    content = f.read()
                self._set_headers(200, mime)
                self.wfile.write(content)
            else:
                self._set_headers(404)
                self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        config = get_current_env_config()
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else ""

        if path == "/api/brief":
            req_data = json.loads(body) if body else {}
            brief = self._generate_brief(config, request_gemini_key=req_data.get("gemini_key"))
            self._set_headers(200)
            self.wfile.write(json.dumps(brief).encode("utf-8"))

        elif path == "/api/settings":
            try:
                data = json.loads(body)
                env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
                new_env_lines = [
                    f"GEMINI_API_KEY={data.get('gemini_key', config['gemini_key'])}\n",
                    f"SLACK_BOT_TOKEN={data.get('slack_token', config['slack_token'])}\n",
                    f"JIRA_DOMAIN={data.get('jira_domain', config['jira_domain'])}\n",
                    f"JIRA_EMAIL={data.get('jira_email', config['jira_email'])}\n",
                    f"JIRA_API_TOKEN={data.get('jira_token', config['jira_token'])}\n",
                    f"GITHUB_PAT={data.get('github_token', config['github_token'])}\n"
                ]
                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(new_env_lines)

                load_env_file()
                self._set_headers(200)
                self.wfile.write(json.dumps({"success": True, "message": "Saved to .env"}).encode("utf-8"))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def _generate_brief(self, config: dict, request_gemini_key: str = None) -> dict:
        slack_client = SlackConnector(bot_token=config["slack_token"])
        jira_client = JiraConnector(
            domain=config["jira_domain"],
            email=config["jira_email"],
            api_token=config["jira_token"]
        )
        github_client = GitHubConnector(pat_token=config["github_token"])
        engine = GeminiBriefEngine(api_key=request_gemini_key or config["gemini_key"])

        slack_feed = slack_client.fetch_recent_channel_messages()
        jira_feed = jira_client.fetch_assigned_issues()
        github_feed = github_client.fetch_user_activity()

        return engine.synthesize_brief(slack_feed, jira_feed, github_feed)


def run_backend_server(port=8090):
    server_address = ("", port)
    httpd = HTTPServer(server_address, BackendRequestHandler)
    print(f"🚀 Python Backend API & React UI running at http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    run_backend_server(port)
