# Glass Box AI — Multi-Agent Orchestration with a Human Gate

Six AI agents running an unattended 8-step daily pipeline: research, content
generation, competitor monitoring, scheduled code improvement, analytics and
email reporting. It operates [SkillVector](https://skill-vector.com) — an AI
career intelligence platform — without me touching it.

The name is the design goal. Most agent systems are black boxes: something ran,
something changed, and you find out later. This one shows its work. Every
execution is traced, every decision is attributed to the agent that made it, and
anything high-risk stops at a human approval gate before it reaches production.

**Stack:** Python · FastAPI · Claude API · WebSockets · cron
**Scale:** 6 agents · 8 pipeline steps · 10 dashboard pages · 152 automated tests · 32 skills in the DAG

---

## Three things worth looking at

**1. A self-healing operations loop.** Hourly health probes hit the production
API. Sustained failure triggers an automatic redeploy. Pipeline steps retry
independently, so one flaky step does not kill the run. Failures are written to
a persisted lessons file that the orchestrator reads **before every run**, so the
system does not repeat a known-bad path. Details in *Self-Healing* below.

**2. LLM cost held to roughly $1/month.** Not by calling the model less, but by
prompt caching, a 6-message sliding context window, and per-call token accounting
that makes cost a dashboard metric rather than an invoice surprise. Details in
*Token Costs* below.

**3. A human-in-the-loop gate.** High-risk agent actions queue for approval
instead of executing. The dashboard carries execution traces, decision
attribution and CSV-exportable audit logs — so "why did it do that?" has an
answer.

---

## How the Two Projects Connect

```
┌──────────────────────────────────────────────────────────────────┐
│                   YOUR MACBOOK (local machine)                    │
│                                                                   │
│  ┌─────────────────────────────────┐                              │
│  │  Glass Box AI Dashboard         │                              │
│  │  (THIS REPO)                    │                              │
│  │                                 │                              │
│  │  scheduler.py ──→ runs daily    │    ┌──────────────────────┐  │
│  │       │            at 8 AM      │    │  skillvector-engine/  │  │
│  │       ▼                         │    │  (separate repo)      │  │
│  │  daily_pipeline.py              │───▶│                       │  │
│  │       │                         │    │  FastAPI backend       │  │
│  │       ├─ Research (Claude AI)   │    │  Neo4j + Pinecone     │  │
│  │       ├─ Write 4 social posts   │    │  ML career analysis   │  │
│  │       ├─ Save posts to files    │    │                       │  │
│  │       ├─ Email you the digest   │    │  Deployed on Railway  │  │
│  │       ├─ Monitor competitors    │    │  api.skill-vector.com │  │
│  │       ├─ Improve code (M/W/F)  │    └──────────────────────┘  │
│  │       └─ Health check API ──────│──────────▶ /health           │
│  │          (if down → auto-fix)   │                              │
│  └─────────────────────────────────┘                              │
└──────────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Railway (cloud)     │
              │  api.skill-vector.com│
              │  skill-vector.com    │
              └─────────────────────┘
```

**In simple terms:**
- **SkillVector** is a website (skill-vector.com) that helps ML engineers find career opportunities
- **Glass Box AI** is the operations center that runs SkillVector — it creates content, monitors the API, fixes crashes, and reports everything to you via email
- They live in two separate GitHub repos but Glass Box knows the path to SkillVector's code and can push changes to it

---

## What Happens Every Day (The Full Workflow)

Every morning at **8:00 AM**, this is what runs automatically:

### Step 1 — Health Check (self-healing)
Atlas pings `https://api.skill-vector.com/health` three times.
- **If UP:** Continues to next step
- **If DOWN:** Pushes an empty commit to the SkillVector repo → Railway auto-redeploys → waits 2 min → checks again → if still down, sends you an alert email

### Step 2 — Research
Claude AI generates 3 fresh insights about the ML/AI career landscape — hiring trends, salary shifts, new tools launching.

### Step 3 — Content Generation
Using those insights, Claude writes 4 social media posts:
- **LinkedIn** — Professional, 150-200 words, founder voice
- **Reddit** (r/MachineLearning) — Honest, helpful, zero hype
- **Twitter/X** — Punchy, max 280 characters, one surprising stat
- **Indie Hackers** — Builder story, what you learned this week

### Step 4 — Save Posts
All 4 posts are saved to the `posts/` folder with dated filenames (e.g., `linkedin_2026-03-06.md`) plus `*_today.md` copies that always have the latest.

### Step 5 — Email Digest
A formatted HTML email with all 4 posts is sent to your Gmail. If email fails, it retries 3 times with 60-second gaps.

### Step 6 — Code Improvement (Monday, Wednesday, Friday)
Atlas reads your SkillVector code, asks Claude for a small safe improvement, writes the fix, and pushes it to GitHub. Railway auto-deploys the change.

### Step 7 — Weekly Analytics (Sunday)
Fetches usage stats from the SkillVector API and generates a CEO-level weekly summary.

### Step 8 — Competitor Monitoring (daily)
Claude researches 3-5 competitors in the AI career tools space and saves intel to `tasks/competitor_intel.md`.

### After Every Run
- **Confidence score** logged (0-100%) — how many steps succeeded
- **Failed steps** auto-recorded in `tasks/lessons.md` so Atlas avoids the same mistakes next run
- **Token usage** logged per Claude call (input/output/total)

---

## Hourly Health Ping

Besides the daily pipeline, a separate cron job pings `api.skill-vector.com` every hour.
- If the API is down **2 hours in a row**, Atlas auto-triggers a Railway redeploy
- If the redeploy doesn't fix it, you get an alert email

---

## The 6 AI Agents

| Agent | Role | What It Does |
|-------|------|--------------|
| **Atlas** | Orchestrator | Runs the daily pipeline, coordinates all agents, auto-fixes API downtime |
| **Scout** | Research | Gathers market data, ML career trends, news via Claude + NewsAPI |
| **Cipher** | Analysis | Scores job matches (0-100), runs risk models, analyzes data |
| **Scribe** | Writer | Writes social posts, cover letters, reports — tailored to each platform |
| **Sentinel** | Compliance | Reviews all outputs for quality, flags scam jobs, checks cover letters |
| **NEXUS** | Job Hunter | Searches Remotive + Arbeitnow, scores jobs, generates tailored cover letters |

All agents use **Claude Sonnet 4** (`claude-sonnet-4-20250514`) with:
- Lean system prompts (~70 tokens each)
- Prompt caching (90% cheaper on cache hits)
- 6-message sliding context window (not full history)
- Default 512 max tokens to keep costs low

---

## What It Can Do (Full Feature List)

### Automated (no action needed from you)
- ✅ Daily social media content for 4 platforms
- ✅ Daily email digest with all posts
- ✅ Hourly API health monitoring
- ✅ Auto-redeploy SkillVector if it crashes
- ✅ Competitor intel gathering
- ✅ Code improvements pushed to SkillVector (Mon/Wed/Fri)
- ✅ Weekly analytics report (Sunday)
- ✅ Self-healing: retries on failure, skips broken steps, keeps going
- ✅ Learning loop: records mistakes, reads them before next run
- ✅ Confidence scoring after every pipeline run
- ✅ Token usage tracking per Claude call

### Dashboard (interactive, you use the UI)
- ✅ 10-page real-time dashboard with dark theme
- ✅ Chat with any of the 6 agents
- ✅ Job search across Remotive, Arbeitnow, Adzuna
- ✅ AI-powered job scoring (Skills 40%, Location 20%, Role 20%, Growth 20%)
- ✅ Cover letter generation tailored to each company
- ✅ GitHub repo stats, commit activity, language breakdown
- ✅ Approval queue — approve/reject high-risk agent actions
- ✅ Audit log with CSV export
- ✅ Decision attribution — see why each agent made each decision

### Sellable Templates
- ✅ 3 ready-to-sell AI agent templates ($49, $79, $99)
- ✅ Bundle deal: all 3 for $199

---

## What You Do Manually

These are the **only things** that need your hands:

| Task | How Often | What To Do |
|------|-----------|------------|
| **Post to social media** | Daily | Copy posts from email/`posts/` folder → paste to LinkedIn, Reddit, Twitter, Indie Hackers (or set up Zapier to auto-post) |
| **Review code improvements** | Mon/Wed/Fri | Check the auto-pushed commits to SkillVector repo — they're usually small/safe but worth a glance |
| **Check email digest** | Daily | Read the morning email to see what Atlas did |
| **Handle alert emails** | Rare | If Atlas can't auto-fix the API, you'll get an email — check Railway dashboard |
| **Update .env if keys expire** | Rare | If Anthropic API key, Gmail app password, or any key rotates |
| **Keep your Mac on** | Always | Cron jobs only run when your Mac is awake (or use Railway/cloud scheduler) |

Everything else is automatic.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/RakeshReddy26-bit/A-Glass-Box-AI-Orchestration-Dashboard.git
cd A-Glass-Box-AI-Orchestration-Dashboard

# 2. Set up environment
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt

# 3. Configure API keys (copy and fill in your keys)
cp backend/.env.example backend/.env
# Required: ANTHROPIC_API_KEY, EMAIL_FROM, EMAIL_TO, EMAIL_APP_PASSWORD
# Required: SKILLEVECTOR_REPO_PATH (path to your skillvector-engine repo)
# Optional: TELEGRAM_BOT_TOKEN, Twitter/LinkedIn tokens

# 4. Start the dashboard server
cd backend && python server.py
# Server runs on http://localhost:8000

# 5. Open the dashboard
open http://localhost:8000

# 6. Run the daily pipeline manually (to test)
cd .. && python scheduler.py --run-now

# 7. Verify cron is set (runs automatically at 8 AM daily)
crontab -l
```

---

## Project Structure

```
A-Glass-Box-AI-Orchestration-Dashboard/
│
├── scheduler.py                  ⏰ Main scheduler — daily pipeline + hourly health
├── run_scheduler.sh              🔧 Bash wrapper for launchd/cron
│
├── backend/                      🖥️ FastAPI server + AI agents
│   ├── server.py                 30+ REST endpoints, WebSocket, Telegram
│   ├── agents.py                 6 AI agents with Claude Sonnet 4
│   ├── scout_tools.py            NewsAPI research tools
│   ├── job_tools.py              Job search: Remotive + Arbeitnow + Adzuna
│   ├── github_tools.py           GitHub API integration (8 methods)
│   ├── profile_manager.py        User profile + cover letter storage
│   └── tests/                    152 automated tests
│
├── integrations/                 🔗 Automation layer (this is where the magic happens)
│   ├── daily_pipeline.py         835 lines — the full 8-step daily pipeline
│   ├── email_sender.py           HTML email with all 4 platform posts
│   ├── code_improver.py          Auto-improve SkillVector code via Claude
│   ├── github_pusher.py          Git commit + push automation
│   ├── skillevector_client.py    Health check + API client for SkillVector
│   ├── dashboard_updater.py      Update dashboard stats
│   ├── workflow_manager.py       Task tracking + workflow state
│   └── langchain_tools.py        LangChain tool wrappers
│
├── dashboard/                    📊 10-page real-time UI
│   ├── index.html                Command Center — KPIs, live feed, topology
│   ├── agents.html               Agent cards, trust scores, status
│   ├── trace.html                Pipeline execution timeline
│   ├── approvals.html            Approve/reject high-risk actions
│   ├── decisions.html            Why each agent made each decision
│   ├── audit.html                Compliance log, CSV export
│   ├── memory.html               Token usage, context windows
│   ├── jobs.html                 NEXUS job search + cover letters
│   ├── github.html               Repo stats, commits, languages
│   └── store.html                Template marketplace
│
├── templates/                    💰 Sellable AI agent templates
│   ├── job-search-agent/         $49 — search + score + cover letters
│   ├── content-writer-agent/     $79 — blog + social + SEO
│   └── research-agent/           $99 — research + competitors + SWOT
│
├── posts/                        📝 Generated social media posts (auto-updated daily)
├── tasks/                        📋 Lessons, competitor intel, task tracking
├── logs/                         📄 atlas.log, cron.log
└── docs/                         📚 Architecture docs
```

---

## How SkillVector Connects (Technical)

| Connection | How |
|------------|-----|
| **Health check** | Glass Box pings `https://api.skill-vector.com/health` every hour |
| **Auto-redeploy** | If API is down, Glass Box pushes an empty commit to skillvector-engine repo → Railway auto-deploys |
| **Code improvement** | Glass Box reads SkillVector source code via `SKILLEVECTOR_REPO_PATH`, asks Claude for improvements, writes the fix, pushes to GitHub |
| **Dashboard stats** | Glass Box fetches `/dashboard/stats` from SkillVector API for weekly reports |
| **Content** | Glass Box generates LinkedIn/Reddit/Twitter/IndieHackers posts that promote SkillVector |

**Environment variables that connect them:**
```
SKILLEVECTOR_URL=http://localhost:8000          # Local dev URL
SKILLEVECTOR_REPO_PATH=/path/to/skillvector-engine  # Local repo path
```
The pipeline always checks the **production URL** (`https://api.skill-vector.com`) for health monitoring, regardless of what `SKILLEVECTOR_URL` is set to.

---

## Self-Healing: What Happens When Things Break

```
Something fails
    │
    ├─ API is down?
    │   └─ Atlas retries 3x → pushes empty commit → Railway redeploys
    │       └─ Still down? → Sends you alert email
    │
    ├─ Email fails?
    │   └─ Retries 3 times, 60s apart
    │
    ├─ Content generation fails?
    │   └─ Email still sends (with error message instead of posts)
    │
    ├─ Code improvement fails?
    │   └─ Skipped, rest of pipeline continues
    │
    └─ Any step crashes?
        └─ Caught, logged, lesson recorded, next step runs
```

The pipeline **never stops entirely**. Even if 7 out of 8 steps fail, the email step still runs to tell you what broke.

---

## Token Costs (How Much It Costs to Run)

All Claude calls use **Sonnet** (not Opus) to keep costs minimal:

| Step | Input Tokens | Output Tokens | Cost Per Run |
|------|-------------|---------------|-------------|
| Research | ~200 | ~500 | $0.003 |
| Content (4 posts) | ~500 | ~2000 | $0.012 |
| Competitors | ~200 | ~600 | $0.004 |
| Code improvement | ~3000 | ~2000 | $0.021 |
| **Daily total** | | | **~$0.02-0.04** |
| **Monthly total** | | | **~$0.60-1.20** |

Every Claude call logs `[TOKENS] in=X out=Y total=Z` in `logs/atlas.log` so you can track actual usage.

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

| Template | Price | What It Does |
|----------|-------|-------------|
| **Job Search Agent** | $49 | Scans job APIs, scores matches, writes cover letters |
| **Content Writer Agent** | $79 | Blog posts, social media, SEO analysis, rewriting |
| **Research Agent** | $99 | Market research, competitor analysis, SWOT, trends |
| **Bundle (all 3)** | $199 | Save $28 |

Each includes: complete source code, FastAPI backend, Claude integration, dark-theme UI, README with docs, `.env.example`.

---

## Dashboard Pages

| # | Page | What You See |
|---|------|-------------|
| 1 | **Command Center** | KPIs, live activity feed, agent topology graph |
| 2 | **Agent Registry** | Agent cards — trust scores, confidence, token usage |
| 3 | **Execution Trace** | Step-by-step timeline of what each agent did and why |
| 4 | **Approvals** | Approve or reject high-risk agent actions before they execute |
| 5 | **Decision Attribution** | Full chain: what data → what reasoning → what output |
| 6 | **Audit Log** | 20-row compliance log, filterable, CSV export |
| 7 | **Memory Inspector** | What each agent remembers, token utilization bars |
| 8 | **NEXUS Jobs** | Job search + AI scoring + cover letter generation |
| 9 | **GitHub** | Your repos, commits, languages, profile sync |
| 10 | **Template Store** | Storefront with product cards and pricing |

---

## Glass Box vs Black Box

| Aspect | Black Box AI | Glass Box AI |
|--------|-------------|-------------|
| Agent actions | Hidden | Every step logged with reasoning |
| Decision making | Opaque | Full attribution chain visible |
| Risk assessment | Unknown | Real-time confidence scores |
| Human oversight | After the fact | Approval gates before high-risk actions |
| Compliance | Hope for the best | Immutable audit trail |
| When it breaks | You find out later | Auto-fixes itself, emails you if it can't |
| Learning | Repeats mistakes | Records lessons, reads them next run |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.9+, FastAPI, Uvicorn |
| **AI** | Anthropic Claude Sonnet 4 (with prompt caching) |
| **Frontend** | HTML, Tailwind CSS (CDN), Vanilla JS |
| **Automation** | Cron scheduler, self-healing pipeline |
| **Job APIs** | Remotive, Arbeitnow, Adzuna |
| **Email** | Gmail SMTP (app password) |
| **Deployment** | Railway (SkillVector), GitHub auto-deploy |
| **Storage** | JSON file persistence, markdown posts |

---

## Author

**Rakesh Reddy Kalamakuntla**
- CS Master's Student — Kiel, Germany
- Building: [skill-vector.com](https://skill-vector.com)
- GitHub: [@RakeshReddy26-bit](https://github.com/RakeshReddy26-bit)

---

## License

MIT
