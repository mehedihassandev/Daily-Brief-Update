# Daily Brief Update 🌅

Automated AI Daily Work Brief generator powered by **Gemini AI**, **Slack**, **Jira / Atlassian**, and **GitHub**.

![Daily Brief UI Layout](src/web/index.html)

## Features
- **Editorial UI Design**: "The Monday Brief" layout with dark mode, rotated side metadata axes (`DATE` / `TIME`), starburst action badges (*"Let's do it →"*), and calendar schedule.
- **Slack Integration**: Scans recent channel discussions, threads, and direct `@mentions`.
- **Jira Integration**: Queries pending assigned tasks (`In Progress`, `To Do`, `Open`) and sprint blockers.
- **GitHub Integration**: Ingests open & merged Pull Requests, code review requests, and commit updates.
- **Gemini AI Synthesis**: Generates structured daily briefs using Gemini 2.5 / 3.0 Flash with JSON Schema.

## Quick Start

### 1. Run Web Dashboard
```bash
cd ~/Desktop/daily-brief
python3 main.py
```
Open **[http://localhost:8090](http://localhost:8090)** in your browser.

### 2. Run Terminal CLI Digest
```bash
python3 cli.py --generate
```

### 3. Run Unit Tests
```bash
python3 -m unittest discover tests
```

## Environment Configuration
Copy `.env.example` to `.env` and fill in your API credentials:
```env
GEMINI_API_KEY=AIzaSy...
SLACK_BOT_TOKEN=xoxb-...
JIRA_DOMAIN=yourcompany.atlassian.net
JIRA_EMAIL=you@company.com
JIRA_API_TOKEN=your_token
GITHUB_PAT=ghp_...
```

## License
MIT License
