# Daily Brief Update 🌅

Automated AI Daily Work Brief generator powered by **Gemini AI**, **Slack**, **Jira / Atlassian**, and **GitHub**.
Built with a **Python Backend** and a **React Frontend (Yarn + Vite)**.

## Project Structure
- `backend/`: Python REST API & Gemini AI Synthesis Engine
- `frontend/`: React + Vite Single Page Application (Yarn)
- `start.sh` / `start.py`: Single command launcher for Backend & Frontend

## Quick Start

### 1. Launch Both Backend & Frontend (1 Command)
```bash
cd ~/Desktop/daily-brief
./start.sh
# or python3 start.py
```
Open **[http://localhost:3000](http://localhost:3000)** for live React UI.

### 2. React Frontend Development (Yarn)
```bash
cd ~/Desktop/daily-brief/frontend
yarn install
yarn dev
```

### 3. Build Production Bundle (Yarn)
```bash
cd ~/Desktop/daily-brief/frontend
yarn build
```

### 4. Terminal CLI Digest
```bash
cd ~/Desktop/daily-brief/backend
python3 cli.py --generate
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
