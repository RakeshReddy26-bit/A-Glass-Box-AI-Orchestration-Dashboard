# Glass Box — AI Orchestration Dashboard

> A full-stack multi-agent AI orchestration platform with 6 autonomous agents,
> real-time dashboard, GitHub integration, job search automation, and a
> commercial AI template marketplace.

![Status](https://img.shields.io/badge/status-active-4ade80?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11-3776ab?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_Sonnet_4-Anthropic-cc785c?style=flat-square)
![Agents](https://img.shields.io/badge/agents-6-818cf8?style=flat-square)
![Pages](https://img.shields.io/badge/dashboard_pages-10-fbbf24?style=flat-square)
![Templates](https://img.shields.io/badge/sellable_templates-3-22d3ee?style=flat-square)

---

## What Is This?

Most AI agent systems are **black boxes** — you issue a goal, agents act invisibly, and you get output. What happened in between is opaque.

**Glass Box** inverts this. Every agent action, decision, confidence score, risk level, and approval gate is surfaced in a real-time dashboard. Plus:

- **NEXUS** — An AI-powered job search agent that scans multiple APIs, scores matches, and generates cover letters
- **GitHub Integration** — Live repo stats, commit activity, and profile sync
- **AI Template Store** — 3 production-ready, sellable AI agent templates

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/RakeshReddy26-bit/A-Glass-Box-AI-Orchestration-Dashboard.git
cd A-Glass-Box-AI-Orchestration-Dashboard

# 2. Set up environment
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt

# 3. Configure API keys
cp backend/.env.example backend/.env
# Edit backend/.env with your ANTHROPIC_API_KEY (required), TELEGRAM_BOT_TOKEN (optional)

# 4. Start the server
cd backend && python server.py
# Server runs on http://localhost:8000

# 5. Open the dashboard
open dashboard/agents.html
```

---

## Architecture

```
A-Glass-Box-AI-Orchestration-Dashboard/
├── backend/
│   ├── server.py              FastAPI server — 30+ endpoints, CORS, Telegram
│   ├── agents.py              6 AI agents with Claude Sonnet 4
│   ├── scout_tools.py         NewsAPI research tools
│   ├── job_tools.py           Remotive + Arbeitnow + Adzuna job APIs
│   ├── github_tools.py        GitHub API integration (8 methods)
│   ├── profile_manager.py     JSON profile persistence + cover letters
│   └── requirements.txt
├── dashboard/
│   ├── index.html             Command Center — KPIs, live feed, topology
│   ├── agents.html            Agent Registry — cards, trust scores, filters
│   ├── trace.html             Execution Trace — vertical timeline
│   ├── approvals.html         Approvals — interactive approve/reject
│   ├── decisions.html         Decision Attribution — context chains
│   ├── audit.html             Audit Log — filterable compliance table
│   ├── memory.html            Memory Inspector — token utilization
│   ├── jobs.html              NEXUS — AI job search + cover letters
│   ├── github.html            GitHub — repos, commits, profile sync
│   ├── store.html             Template Store — product cards, pricing
│   ├── css/styles.css         Design system — dark theme, glass effects
│   ├── js/data.js             Mock data for demo pages
│   └── assets/favicon.svg
├── templates/                 ⭐ Sellable AI agent templates
│   ├── job-search-agent/      $49 — AI job search + scoring + cover letters
│   ├── content-writer-agent/  $79 — Blog, social media, SEO, rewriting
│   └── research-agent/        $99 — Market research, competitors, SWOT, trends
└── docs/
    ├── architecture.md
    ├── agent-roles.md
    ├── approval-flow.md
    └── mental-model.md
```

---

## The 6 Agents

| Agent | Role | What It Does |
|-------|------|--------------|
| **Atlas** | Orchestrator | Coordinates all agents, assigns tasks, manages pipeline flow |
| **Scout** | Research | Gathers market data, news via NewsAPI |
| **Cipher** | Analysis | Runs financial models, risk assessments |
| **Scribe** | Writer | Drafts reports, cover letters (max 800 tokens) |
| **Sentinel** | Compliance | Reviews outputs for regulatory compliance |
| **NEXUS** | Job Hunter | Searches Remotive + Arbeitnow, scores jobs, generates cover letters |

All agents use **Claude Sonnet 4** with:
- Lean system prompts (~70 tokens each, 5x reduction from original)
- Anthropic prompt caching (`cache_control: ephemeral`)
- 6-message sliding context window
- Default 512 max tokens (800 for Scribe)

---

## Dashboard Pages (10)

| # | Page | Description |
|---|------|-------------|
| 1 | **Command Center** | KPIs, live activity feed, agent topology graph, system metrics |
| 2 | **Agent Registry** | Agent cards with trust scores, confidence, token usage, latency |
| 3 | **Execution Trace** | Vertical timeline of pipeline steps with reasoning |
| 4 | **Approvals** | Human-in-the-loop approve/reject queue with toast notifications |
| 5 | **Decision Attribution** | Full upstream context chain for every output |
| 6 | **Audit Log** | 20-row compliance-grade event log, filterable, CSV export |
| 7 | **Memory Inspector** | Agent context windows, token utilization bars |
| 8 | **NEXUS Jobs** | Job search across APIs, AI scoring, cover letter generation |
| 9 | **GitHub** | Repo cards, commit activity, language stats, profile sync |
| 10 | **Template Store** | Storefront with 3 product cards, pricing, bundle deal |

---

## API Endpoints

### Core
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server health + uptime |
| POST | `/api/chat` | Chat with any agent |
| GET | `/api/agents` | List all agents with status |

### NEXUS (Job Search)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs/search` | Search jobs (Remotive + Arbeitnow) |
| POST | `/api/jobs/score` | AI-score job matches (0-100) |
| POST | `/api/jobs/cover-letter` | Generate tailored cover letter |
| POST | `/api/jobs/hunt` | Full pipeline: search → score → letters → Telegram |

### GitHub
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/github/repos` | List user repositories |
| GET | `/api/github/commits/{repo}` | Recent commits for a repo |
| GET | `/api/github/languages/{repo}` | Language breakdown |
| GET | `/api/github/activity` | Commit activity across all repos |
| GET | `/api/github/stats` | Profile stats (repos, followers, stars) |
| POST | `/api/github/sync-profile` | Sync GitHub data to Glass Box profile |

### Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile` | Get saved profile |
| PUT | `/api/profile` | Update profile |
| GET | `/api/cover-letters` | List saved cover letters |

---

## Sellable AI Templates

Three standalone, production-ready AI agent templates in `/templates/`. Each is a complete project — zip it, sell it, buyer runs it in 5 minutes.

### 1. Job Search Agent — $49
> AI-powered job search that scans multiple APIs, scores matches against your profile, and generates tailored cover letters.

- **Files:** `server.py`, `agent.py`, `tools.py`, `index.html`, `README.md`
- **APIs:** Remotive, Arbeitnow (free), Adzuna (optional)
- **Features:** Multi-source search, 4-factor AI scoring (0-100), cover letter generation, Telegram notifications, auto-save results

### 2. Content Writer Agent — $79
> AI content creation suite: blog posts, social media, SEO analysis, and tone-matched rewriting.

- **Files:** `server.py`, `agent.py`, `index.html`, `README.md`
- **Features:** 6 writing tones, blog generation (up to 3000 words), multi-platform social posts, SEO keyword analysis, content rewriting, export history

### 3. Research Agent — $99
> AI market research analyst: deep research reports, competitor analysis, trend identification, and SWOT matrices.

- **Files:** `server.py`, `agent.py`, `tools.py`, `index.html`, `README.md`
- **APIs:** NewsAPI (free tier, 100 req/day)
- **Features:** Configurable depth (quick/standard/deep), competitor side-by-side, trend pattern detection, SWOT 2x2, executive summaries, auto-save reports

### Bundle — All 3 for $199 (Save $28)

Each template includes:
- Complete source code (no obfuscation)
- FastAPI backend + Claude AI integration
- Professional dark-theme dashboard UI
- Comprehensive README with API docs
- `.env.example` for easy setup
- No subscriptions, no recurring fees

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **AI** | Anthropic Claude Sonnet 4 (with prompt caching) |
| **Frontend** | HTML, Tailwind CSS (CDN), Vanilla JS |
| **Job APIs** | Remotive, Arbeitnow, Adzuna |
| **News API** | NewsAPI.org |
| **GitHub** | GitHub REST API v3 |
| **Notifications** | Telegram Bot API |
| **Storage** | JSON file persistence |

---

## Design System

- **Dark ops/mission control** aesthetic (slate-950 base)
- **Glass-card effect**: translucent backgrounds with backdrop-blur
- **Monospace typography**: JetBrains Mono / Fira Code
- **Neon accent palette**: consistent agent color identity

| Agent | Color | Hex |
|-------|-------|-----|
| Atlas | Indigo | `#818cf8` |
| Scout | Sky | `#38bdf8` |
| Cipher | Green | `#4ade80` |
| Scribe | Amber | `#fbbf24` |
| Sentinel | Red | `#f87171` |
| NEXUS | Cyan | `#22d3ee` |

---

## Glass Box vs Black Box

| Aspect | Black Box | Glass Box |
|--------|-----------|-----------|
| Agent actions | Hidden | Every step logged with reasoning |
| Decision making | Opaque | Full attribution chain visible |
| Risk assessment | Unknown | Real-time risk scores and badges |
| Human oversight | After the fact | Approval gates before high-risk actions |
| Compliance | Hope for the best | Immutable audit trail |
| Trust | Blind faith | Earned through transparency |

---

## Author

**Rakesh Reddy Kalamakuntla**
- CS Master's Student — Kiel, Germany
- GitHub: [@RakeshReddy26-bit](https://github.com/RakeshReddy26-bit)

---

## License

MIT
