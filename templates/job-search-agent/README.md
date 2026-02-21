# 🎯 AI Job Search Agent

**Automated job hunting powered by Claude AI — find jobs, score matches, and generate cover letters in seconds.**

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-latest-green) ![Claude](https://img.shields.io/badge/Claude_AI-Sonnet_4-purple) ![License](https://img.shields.io/badge/License-Commercial-orange)

---

## What It Does

This agent automates your entire job search pipeline:

1. **Search jobs** across multiple free APIs (Remotive, Arbeitnow) — no paid subscriptions needed
2. **Score & rank** each job against your profile (skills match, location, role fit, growth potential)
3. **Generate tailored cover letters** using Claude AI — personalized to each company
4. **Send daily digests** to Telegram with top matches
5. **Save everything** — job matches as JSON, cover letters as Markdown

## Features

- 🔍 **Multi-source search** — Remotive (worldwide remote) + Arbeitnow (Europe-focused)
- 🤖 **AI-powered scoring** — 4-factor scoring: Skills 40%, Location 20%, Role 20%, Growth 20%
- ✍️ **Cover letter generation** — Tailored to company culture with your real skills
- 📱 **Telegram notifications** — Daily digest with top job matches
- 💾 **Auto-save outputs** — Job matches and cover letters saved to your Desktop
- 🎨 **Browser-based UI** — Professional dashboard included
- ⚡ **Fast setup** — Running in under 5 minutes

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

You need:
- **Anthropic API key** (required) — [Get one here](https://console.anthropic.com/)
- **Telegram bot token** (optional) — [Create a bot](https://t.me/BotFather)

### 3. Edit your profile

Open `server.py` and edit the `MY_PROFILE` dict to match your skills, experience, and job preferences.

### 4. Run

```bash
python server.py
```

Open `http://localhost:8000` in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Dashboard UI |
| `GET` | `/api/health` | Server health check |
| `POST` | `/api/search` | Search jobs (`{"query": "python developer", "limit": 15}`) |
| `POST` | `/api/cover-letter` | Generate cover letter (`{"company": "...", "role": "...", "job_description": "..."}`) |
| `POST` | `/api/hunt` | Full pipeline: search → score → cover letters → Telegram |
| `GET` | `/api/profile` | View your profile |
| `PUT` | `/api/profile` | Update profile fields |

## Example Usage

```bash
# Search for Python jobs
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python developer", "limit": 10}'

# Generate a cover letter
curl -X POST http://localhost:8000/api/cover-letter \
  -H "Content-Type: application/json" \
  -d '{"company": "Stripe", "role": "Backend Engineer", "job_description": "..."}'

# Run full pipeline
curl -X POST http://localhost:8000/api/hunt \
  -H "Content-Type: application/json" \
  -d '{"query": "AI engineer", "limit": 10, "write_cover_letters": 3}'
```

## Customization

### Add more job sources
Edit `tools.py` and add a new `async def search_<source>()` method. The `search_all()` method will pick it up automatically.

### Change scoring weights
In `agent.py`, modify the `SCORING_PROMPT` to adjust the 4-factor weights.

### Adjust cover letter style
Edit the Scribe system prompt in `agent.py` to change tone, length, or structure.

## Tech Stack

- **Backend:** Python + FastAPI + Uvicorn
- **AI:** Anthropic Claude API (Sonnet 4)
- **Job APIs:** Remotive (free), Arbeitnow (free)
- **Notifications:** Telegram Bot API
- **Frontend:** Vanilla HTML + TailwindCSS

## File Structure

```
job-search-agent/
├── server.py          # FastAPI backend + all endpoints
├── agent.py           # Claude AI agent (scoring + cover letters)
├── tools.py           # Job search API integrations
├── index.html         # Browser dashboard UI
├── requirements.txt   # Python dependencies
├── .env.example       # Config template
└── README.md          # This file
```

## Support

Questions? Issues? Email support or open a GitHub issue.

---

**Built with [Glass Box AI](https://github.com/RakeshReddy26-bit/A-Glass-Box-AI-Orchestration-Dashboard)**
