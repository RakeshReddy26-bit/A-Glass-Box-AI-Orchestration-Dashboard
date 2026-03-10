# The Complete Guide to Glass Box AI + SkillVector

**Author:** Rakesh Reddy Kalamakuntla  
**Last Updated:** March 10, 2026  
**Version:** 2.0  

> This is your single source of truth. Everything about what we built, how it works, what went wrong, how we fixed it, and where we're going next. Written in plain English so you can use it for PPTs, pitch decks, NotebookLM, audio/video content, or just to remember how everything connects.

---

## Table of Contents

1. [The Big Picture — What Are We Building?](#1-the-big-picture)
2. [How Glass Box AI and SkillVector Connect](#2-how-they-connect)
3. [The Five Agents — Who Does What](#3-the-five-agents)
4. [The 10-Page Dashboard — What You See](#4-the-dashboard)
5. [The Daily Pipeline — What Happens at 8 AM](#5-the-daily-pipeline)
6. [The NEXUS Job Hunt Pipeline — Finding Jobs Automatically](#6-nexus-pipeline)
7. [Self-Healing — When Things Break, Atlas Fixes Them](#7-self-healing)
8. [The Learning Loop — Getting Smarter Every Day](#8-learning-loop)
9. [The Tech Stack — What Powers Everything](#9-tech-stack)
10. [The Full Timeline — Everything We Built, In Order](#10-timeline)
11. [What Went Wrong and How We Fixed It](#11-what-went-wrong)
12. [What's Working Right Now (March 2026)](#12-whats-working-now)
13. [The Money Side — Token Costs and Revenue Model](#13-money)
14. [Future Improvements — What's Next](#14-future)
15. [How to Pitch This to Investors](#15-pitch)
16. [Technical Reference — Every File Explained](#16-reference)

---

## 1. The Big Picture — What Are We Building? <a name="1-the-big-picture"></a>

We're building two products that work together:

### Product 1: SkillVector (The Career Platform)
**What it is:** An AI-powered career intelligence platform for ML engineers.  
**What it does:** Analyzes job postings, identifies skill gaps, matches engineers to roles, and provides personalized career guidance.  
**Where it lives:** [skill-vector.com](https://skill-vector.com) (frontend) and [api.skill-vector.com](https://api.skill-vector.com) (backend on Railway)  
**Tech:** FastAPI + Neo4j knowledge graph + Pinecone vector search + Claude AI  

### Product 2: Glass Box AI (The Orchestration Dashboard)
**What it is:** An AI agent orchestration system that automates everything around SkillVector — content creation, health monitoring, code improvement, competitor tracking, and job hunting.  
**What it does:** Runs 5 AI agents that work together like a small team. You give a directive, and the agents research, analyze, write, and review — all visible in a real-time dashboard.  
**Where it lives:** Locally on your Mac (FastAPI at localhost:8000) + GitHub repo  
**Tech:** FastAPI + Claude Sonnet 4 + 10-page vanilla HTML/JS dashboard + WebSocket real-time

### How They Work Together
Think of it like this:
- **SkillVector** is the product your users see — the career platform
- **Glass Box AI** is your operations team — it keeps SkillVector alive, markets it, monitors competitors, and improves the code automatically

```
YOU (Rakesh)
  │
  ├── Give a directive ("Research ML trends")
  │
  ▼
GLASS BOX AI DASHBOARD (localhost:8000)
  │
  ├── Atlas (boss) coordinates 4 agents
  ├── Scout researches → Cipher analyzes → Scribe writes → Sentinel reviews
  │
  ├── Daily: Generates posts → Emails you → Monitors health → Improves code
  │
  ▼
SKILLEVECTOR (api.skill-vector.com)
  │
  ├── Health checked every hour
  ├── Code improved Mon/Wed/Fri (auto-pushed + deployed)
  ├── Competitor intel updated daily
  └── Auto-redeployed if it goes down
```

### Why "Glass Box"?
Most AI systems are "black boxes" — you can't see what's happening inside. Our system is a "glass box" — every agent decision, every API call, every confidence score is visible in the dashboard. You always know exactly what the AI is doing and why.

---

## 2. How Glass Box AI and SkillVector Connect <a name="2-how-they-connect"></a>

These are two separate codebases that talk to each other through APIs and Git.

### The Connection Points

| What | How | Direction |
|------|-----|-----------|
| Health monitoring | HTTP GET to /health endpoint | Glass Box → SkillVector |
| Code improvements | Git push to skillvector-engine repo | Glass Box → GitHub → Railway → SkillVector |
| Auto-redeploy | Empty git commit triggers Railway rebuild | Glass Box → GitHub → Railway |
| Job data ingestion | POST to /automation/ingest-jobs | Glass Box → SkillVector API |
| Trend updates | POST to /automation/trend-update | Glass Box → SkillVector API |
| Daily insights | GET from /automation/daily-insight | SkillVector → Glass Box |
| Dashboard stats | GET from /dashboard/stats | SkillVector → Glass Box |

### Where Each Lives

```
Your Mac (Desktop)
├── ~/Desktop/A-Glass-Box-AI-Orchestration-Dashboard/  ← Glass Box code
├── ~/Documents/GitHub/skillvector-engine/              ← SkillVector code
└── ~/Desktop/GlassBox-Outputs/                        ← Cover letters, job matches, profile

Cloud
├── skill-vector.com              ← SkillVector frontend (Cloudflare DNS)
├── api.skill-vector.com          ← SkillVector backend (Railway)
└── GitHub repos                  ← Both codebases versioned
```

### Authentication Between Them
- **Glass Box → SkillVector API:** Uses `x-atlas-key` header (AUTOMATION_API_KEY in .env)
- **Glass Box → Claude AI:** ANTHROPIC_API_KEY in .env
- **Glass Box → GitHub:** Git SSH keys on your Mac
- **Glass Box → Gmail:** EMAIL_APP_PASSWORD (Gmail app-specific password)

---

## 3. The Five Agents — Who Does What <a name="3-the-five-agents"></a>

These are not five separate programs. They're five personas backed by Claude Sonnet 4, each with a different system prompt that tells Claude to behave differently. Think of them as five specialists on your team.

### Agent 1: ATLAS — The Orchestrator (Color: Indigo #818cf8)

**Role:** The boss. Coordinates all other agents, runs the daily pipeline, manages the schedule.

**What Atlas does:**
- Receives your directives ("Research AAPL trends" or "Hunt for ML jobs")
- Decides which agents to activate and in what order
- Runs the 8-step daily pipeline at 8 AM
- Monitors SkillVector's health every hour
- Calculates confidence scores for each pipeline run
- Records lessons when things fail

**System prompt** (what Claude is told): "Orchestrate Scout, Cipher, Scribe, Sentinel. Two modes: FINANCE (AAPL analysis) and NEXUS (job hunting). Be concise — max 3 sentences."

**Token budget:** 512 tokens per response (keeps things tight)

### Agent 2: SCOUT — The Researcher (Color: Sky Blue #38bdf8)

**Role:** Gathers real data from the internet. No hallucinating — only real sources.

**What Scout does:**
- Searches news articles via NewsAPI (100 free requests/day)
- Pulls SEC filings from EDGAR (free, no key needed)
- Gets stock prices via yfinance (free, real-time)
- Fetches stock history charts (6-month OHLCV data)
- In the daily pipeline: generates 3 research insights about ML careers

**Real APIs Scout uses:**
| API | Cost | What It Returns |
|-----|------|-----------------|
| NewsAPI.org | Free (100/day) | Headlines, sources, dates |
| SEC EDGAR | Free (10 req/sec) | 10-K, 10-Q filings |
| yfinance | Free (unlimited) | Prices, P/E, market cap |

**Example output:** "AI Safety Roles Growing 3x Faster Than ML — Companies hiring for alignment, interpretability, governance roles at 40% premium vs general ML."

### Agent 3: CIPHER — The Analyst (Color: Green #4ade80)

**Role:** Does the math. Scores jobs, calculates risks, runs quantitative analysis.

**What Cipher does:**
- Scores every job on a 0-100 scale using this formula:
  - **Skills Match (40%):** Do your skills match the requirements?
  - **Location (20%):** Is the job where you want to be?
  - **Role Fit (20%):** Does the title/level match your goals?
  - **Growth Potential (20%):** Will this advance your career?
- Flags scam jobs (no web presence, pay-to-apply, unrealistic salary)
- Ranks jobs from best to worst match
- Provides risk assessments for financial analysis (AAPL mode)

**Example output:** "Job #3 (Google ML Engineer): Score 87/100. Skills: 95% (Python, FastAPI, LLM — all match). Location: 70% (Mountain View, not remote). Role Fit: 85%. Growth: 90%. Verdict: STRONG MATCH."

### Agent 4: SCRIBE — The Writer (Color: Amber #fbbf24)

**Role:** Creates all written content. Posts, cover letters, reports — everything written.

**What Scribe does:**
- Generates daily posts for 4 platforms with strict format rules:
  - **LinkedIn** (150-200 words): Professional founder voice, 3 hashtags, ends with skill-vector.com
  - **Reddit** (150-250 words): Honest builder tone, zero hype, natural product mention
  - **Twitter/X** (max 280 chars): Punchy stat + link, NO hashtags
  - **Indie Hackers** (200-300 words): What I learned this week, transparent about challenges
- Writes tailored cover letters (250-400 words per letter)
- Generates Monday image prompts for DALL-E/Midjourney
- Creates weekly analytics reports (Sundays)

**Cover letter structure:** Why this company → 2-3 skill matches → Glass Box project mention → Professional close

**Token budget:** 2000 tokens for content generation (needs to output 4 full posts)

### Agent 5: SENTINEL — The Compliance Officer (Color: Red #f87171)

**Role:** Reviews everything before it goes out. Quality control + scam detection.

**What Sentinel does:**
- Reviews cover letters for: false claims, generic language, tone issues
- Reviews job listings for: scam indicators, missing company info, salary red flags
- Gives PASS/FAIL verdict with specific reasons
- Flags issues like: "Company has no web presence — possible scam" or "Cover letter mentions skills not in your profile — false claim"

**Decision output:** "PASS — Cover letter is specific to role, mentions correct tech stack, professional tone" or "FAIL — Generic language detected, no company-specific research shown"

### How They Work Together (Job Hunt Example)

```
Step 1: You say "Hunt for ML engineer jobs"
Step 2: Atlas activates the pipeline
Step 3: Scout → searches Remotive + Arbeitnow + Adzuna → finds 30 jobs
Step 4: Cipher → scores all 30 jobs → ranks them → top 10 returned
Step 5: Scribe → writes cover letters for top 3 jobs
Step 6: Sentinel → reviews jobs (flags 1 scam) + reviews letters (1 needs revision)
Step 7: Atlas → packages results → saves to Desktop → shows in dashboard
```

### Agent Communication

All agents share a conversation history. When Atlas broadcasts a directive, all 5 agents see it and respond. The history is kept to the last 20 messages per agent (sliding window of 6 sent to Claude API to save tokens).

**Prompt caching** is enabled — Claude caches the system prompt, so repeat calls are 90% cheaper on the system prompt portion.

---

## 4. The 10-Page Dashboard — What You See <a name="4-the-dashboard"></a>

The dashboard is 10 HTML pages with a dark theme (black and navy blue background, neon accent colors). It's built with vanilla HTML, CSS, and JavaScript — no React, no build tools, no complexity. You open it in a browser and it just works.

### Design Philosophy
- **Read-only by default:** The dashboard shows you what the agents are doing. It never executes actions itself.
- **Real-time via WebSocket:** When an agent does something, the dashboard updates instantly.
- **Works offline:** If the backend is down, the dashboard shows demo data so you can still present it.
- **Font:** JetBrains Mono (monospace) — gives it a professional developer/terminal feel.

### Page 1: Command Center (index.html)
**What you see:** The main overview. A live activity feed showing every agent action in real-time. KPI cards showing: agents active, confidence score, token cost, uptime. A directive input box where you type commands.

**Authority chain at top:** You (Director) → Atlas → Scout/Cipher/Scribe/Sentinel → SkillVector

### Page 2: Agent Registry (agents.html)
**What you see:** Five cards, one for each agent. Each shows: trust score (88-97), confidence score (72-94), risk level, latency, cost, uptime, tasks completed vs failed. Color-coded by agent color. Filter buttons: All / Active / Idle / Error.

### Page 3: Execution Trace (trace.html)
**What you see:** A vertical timeline of every step the pipeline executed. Step number, agent name, description, duration, status (completed/in-progress/failed). Export button to download as JSON.

### Page 4: Approval Queue (approvals.html)
**What you see:** Human-in-the-loop decisions. When an agent wants to do something risky (confidence below 80%, high-risk action), it pauses and asks for approval. Cards show: what the agent wants to do, why, risk level, confidence score. Three buttons: APPROVE / PAUSE / DENY.

### Page 5: Decision Attribution (decisions.html)
**What you see:** History of every decision made. Why was something approved or denied? Analytics: approval rate, trends over 7 days, which agents get paused most.

### Page 6: Audit Log (audit.html)
**What you see:** Compliance table. Every agent action logged: timestamp, agent, action, was approval needed?, was it approved?, risk score, summary. Downloadable as CSV.

### Page 7: Token Usage & Context (memory.html)
**What you see:** How many tokens each agent has used. Pie chart of input vs output tokens. Cost breakdown per agent. Context window usage (how much of Claude's memory each agent is using).

### Page 8: NEXUS — Job Search (jobs.html)
**What you see:** Interactive job hunting. Search box, source selector (Remotive/Arbeitnow/Adzuna/All), limit slider. Results show job cards with Cipher's scores. Generate cover letter buttons. Sentinel review status.

### Page 9: GitHub Portfolio (github.html)
**What you see:** Your GitHub profile pulled live. Avatar, bio, repo count, followers. Top repos with stars/forks/language. Language breakdown pie chart. Recent commits timeline.

### Page 10: Agent Template Store (store.html)
**What you see:** Three sellable products:
- **Job Search Agent** — $49
- **Content Writer Agent** — $79
- **Research Agent** — $99
- **Bundle (All 3)** — $199 (20% off)

Each has an "Add to Cart" button linking to Gumroad.

### The Dashboard CSS Design System

```
Background:     #020617 (near black)
Surface:        #0f172a (very dark navy)
Cards:          #1e293b (dark blue) with glass blur effect
Text:           #f1f5f9 (white) → #64748b (dim gray)
Agent colors:   Atlas=#818cf8  Scout=#38bdf8  Cipher=#4ade80  Scribe=#fbbf24  Sentinel=#f87171
```

---

## 5. The Daily Pipeline — What Happens at 8 AM <a name="5-the-daily-pipeline"></a>

Every day, a cron job on your Mac triggers the daily pipeline. Here's exactly what happens, step by step.

### How It's Triggered

Your Mac's cron runs a script called `run_if_needed.sh` every 15 minutes between 8 AM and 10 AM. The script checks: "Did the pipeline already run today?" If no, it runs it. If yes, it exits silently. This means even if your Mac was asleep at exactly 8:00 AM, the pipeline catches up when you open the lid.

```
Cron (every 15 min, 8-10 AM)
  → run_if_needed.sh (checks date marker file)
    → scheduler.py --run-now
      → daily_pipeline.py → run_daily_pipeline()
```

### Step 1: Health Check (Self-Healing)
**What:** Pings https://api.skill-vector.com/health  
**If UP:** Logs "SkillVector API is UP" → moves to Step 2  
**If DOWN:** Retries 3 times (10 seconds apart). If still down → triggers auto-redeploy (pushes empty commit to GitHub → Railway rebuilds → waits 2 minutes → checks again). If recovered → continues. If still down → sends alert email and continues with degraded confidence.  
**Token cost:** Zero (just an HTTP request)

### Step 2: Research
**What:** Asks Claude to generate 3 insights about ML/AI career trends  
**Output example:**
```json
[
  {
    "headline": "ML engineer hiring rebounds 65% YoY",
    "detail": "Companies shifting from generalist to specialist roles...",
    "relevance": "Engineers should specialize to command higher salaries"
  }
]
```
**Token cost:** ~700 tokens ($0.002)

### Step 3: Content Generation
**What:** Takes the 3 insights from Step 2 and generates posts for 4 platforms  
**Output:** 4 complete posts (LinkedIn, Reddit, Twitter, Indie Hackers) — each tailored to the platform's style and audience  
**Token cost:** ~2,400 tokens ($0.007)

### Step 3b: Monday Image Prompt (Mondays only)
**What:** Generates a DALL-E/Midjourney prompt for a social media cover image  
**Output:** "Modern dark-themed graphic with glowing green neural network nodes flowing into career path visualization..."  
**Saved to:** `posts/image_prompt_monday.txt`

### Step 4: Save Posts
**What:** Saves the 4 posts to disk  
**Files created:** `posts/linkedin_2026-03-10.md`, `posts/reddit_2026-03-10.md`, `posts/twitter_2026-03-10.md`, `posts/indie_hackers_2026-03-10.md`  
**Also updates:** `posts/linkedin_today.md`, etc. (always points to latest)  
**Token cost:** Zero

### Step 5: Email Digest
**What:** Sends you an HTML email with all 4 posts formatted beautifully  
**Subject:** "SkillVector Daily Posts — March 10, 2026"  
**Format:** Dark theme HTML table with platform headers (LinkedIn blue, Reddit orange, etc.), post text, and quick-click links to each platform  
**Retry logic:** If email fails, retries 3 times with 60-second gaps  
**Token cost:** Zero (just SMTP)

### Step 6: Code Improvement (Monday, Wednesday, Friday only)
**What:** Reads a SkillVector source file, sends it to Claude with "suggest safe improvements," and if Claude says yes → writes the improved code → commits → pushes to GitHub → Railway auto-deploys  
**Safety:** Only small, targeted changes. Never breaks existing tests.  
**Token cost:** ~2,000 tokens ($0.006)

### Step 7: Weekly Analytics (Sunday only)
**What:** Fetches SkillVector dashboard stats, asks Claude for a CEO-level weekly summary  
**Output:** Key metrics, growth trends, focus areas for next week  
**Saved to:** `posts/weekly_report_2026-03-10.md`

### Step 8: Competitor Monitoring
**What:** Asks Claude to list 3-5 competing ML career tools, what they do, how SkillVector is different  
**Saved to:** `tasks/competitor_intel.md`  
**Token cost:** ~800 tokens ($0.002)

### Pipeline Completion
After all steps finish:
- **Confidence score** is calculated (each step has a weight, earned points ÷ total points × 100)
- **Elapsed time** is logged (typically 55-90 seconds)
- **Failed steps** are auto-recorded as lessons in `tasks/lessons.md`
- Everything is logged to `logs/cron.log`

### Step Weights (How Confidence Is Calculated)

| Step | Weight | Why |
|------|--------|-----|
| Health check | 10 | Critical — if API is down, everything matters less |
| Research | 15 | Important — feeds content quality |
| Content generation | 25 | Highest value — this is the main output |
| Save posts | 10 | Low risk — just file I/O |
| Email | 25 | Highest value — if you don't get the email, pipeline was pointless |
| Code improvement | 5 | Optional — nice to have |
| Analytics | 5 | Optional — Sunday only |
| Competitor monitoring | 5 | Optional — supplementary |

---

## 6. The NEXUS Job Hunt Pipeline <a name="6-nexus-pipeline"></a>

NEXUS is the job-hunting mode. When you type "Hunt for ML engineer jobs" in the dashboard, this is what happens:

### Step 1: Scout Searches Three Job Platforms

| Platform | Coverage | Cost |
|----------|----------|------|
| Remotive | Remote tech jobs globally | Free |
| Arbeitnow | Europe-focused (Germany, NL, Austria) | Free |
| Adzuna | 15+ countries, salary data | Free tier (250/day) |

Scout queries all three in parallel, merges results, removes duplicates, and returns them sorted by date (newest first).

### Step 2: Cipher Scores and Ranks

Each job gets a 0-100 score:
- **Skills Match (40%)** — Python, FastAPI, Claude, Docker, etc.
- **Location Match (20%)** — Remote? Germany? US?
- **Role Fit (20%)** — ML Engineer? Data Scientist? Does it match your level?
- **Growth Potential (20%)** — Will you learn? Is the company growing?

Red flags are detected: no company website, pay-to-apply schemes, unrealistic salaries.

### Step 3: Scribe Writes Cover Letters

For the top 3 jobs by Cipher's score, Scribe generates tailored cover letters:
- Reads your profile (name, skills, education, experience)
- Structures: Why this company → skill matches → Glass Box project mention → close
- 250-400 words, professional but warm
- Saved to `~/Desktop/GlassBox-Outputs/cover_letters/`

### Step 4: Sentinel Reviews Everything

Sentinel checks:
- Jobs: Any scams? Missing info? Salary mismatch?
- Cover letters: Any false claims? Generic language? Wrong tone?
- Gives PASS/FAIL on each with specific reasons

### Step 5: Results Delivered

Everything packaged and saved:
- Job list with scores → saved as JSON
- Cover letters → saved as Markdown files
- Sentinel report → shown in dashboard
- All visible in the NEXUS (jobs.html) page

---

## 7. Self-Healing — When Things Break, Atlas Fixes Them <a name="7-self-healing"></a>

The system has multiple layers of automatic recovery. Here's every self-healing mechanism:

### 1. API Goes Down → Auto-Redeploy

```
Hourly health ping → api.skill-vector.com/health
  │
  ├── HTTP 200? → All good, log "UP"
  │
  └── Timeout or error?
       │
       ├── Retry 3x with 10s gaps
       │
       └── Still down after 3 retries?
            │
            ├── Push empty commit to skillvector-engine repo
            │     └── Railway detects push → auto-rebuild → redeploy (2 min)
            │
            ├── Wait 120 seconds → check again
            │     ├── Recovered → log "RECOVERED"
            │     └── Still down → send alert email + Telegram "API CRITICAL"
            │
            └── Record lesson in tasks/lessons.md
```

### 2. Email Fails → 3x Retry with 60s Gaps

```
Send email attempt 1
  ├── Success → done
  └── Fail → wait 60s → attempt 2
       ├── Success → done
       └── Fail → wait 60s → attempt 3
            ├── Success → done
            └── Fail → log error, continue pipeline (degraded confidence)
```

### 3. Content Generation Fails → Error Email

If Claude can't generate posts, the pipeline sends you an error notification email instead, so you always know something happened.

### 4. Code Improvement Fails → Skip and Continue

If the code improvement step crashes (bad JSON, file not found, push fails), the pipeline skips it and moves on. It's optional — the pipeline still works without it.

### 5. Mac Was Asleep at 8 AM → Catch-Up Script

```
run_if_needed.sh runs every 15 min (8-10 AM)
  │
  ├── Check .last_run_date marker file
  │     ├── Already ran today? → exit silently
  │     └── Not run yet? → run pipeline → write today's date to marker
  │
  └── Even if Mac wakes at 9:47, pipeline catches up by 10:00
```

### 6. Any Step Crashes → Caught, Logged, Continued

Every step is wrapped in try/except. If a step throws an unexpected error:
- The error is caught (pipeline doesn't crash)
- The error is logged with full traceback
- A lesson is auto-recorded for next run
- The pipeline continues with remaining steps
- Confidence score is reduced proportionally

---

## 8. The Learning Loop — Getting Smarter Every Day <a name="8-learning-loop"></a>

Atlas has a memory that persists between runs. Here's how the learning loop works:

### Before Every Pipeline Run
1. Atlas reads `tasks/lessons.md` — a file of past mistakes and patterns
2. These lessons are injected into Claude's context so it avoids repeating errors

### After Every Pipeline Run
1. If any step fails, Atlas auto-records a lesson:
   - What failed
   - When it failed
   - The confidence score for that run
   - Suggested fix
2. The lesson is appended to `tasks/lessons.md`

### Current Lessons (7 Manually Written + Auto-Generated)

| # | Lesson | What We Learned |
|---|--------|-----------------|
| 001 | SkillVector connection | Always check if API is alive FIRST. Render free tier sleeps. |
| 002 | .env loading | Always call load_dotenv() at top of every file. Without it, all API keys return None. |
| 003 | Git push conflicts | Always `git pull --rebase` before push. Prevents non-fast-forward errors. |
| 004 | Twitter API | Twitter requires payment for write access. Use Zapier instead. |
| 005 | LinkedIn OAuth | Auth codes expire in 30 seconds. Client credentials don't work for posting. Use Zapier. |
| 006 | API auto-recovery | Railway can go down from deploys, cold starts, or OOM. Atlas auto-detects and pushes empty commit to trigger redeploy. |
| 007 | Production URL | SKILLEVECTOR_URL in .env points to localhost for dev. Health checks must always hit the production URL constant. |

### Why This Matters

Traditional automation scripts break and you discover it days later. Our system:
- Detects failures immediately
- Records what happened
- Learns not to repeat it
- Gets more reliable over time

---

## 9. The Tech Stack — What Powers Everything <a name="9-tech-stack"></a>

### AI Layer

| Component | What | Cost |
|-----------|------|------|
| Claude Sonnet 4 (claude-sonnet-4-20250514) | All AI reasoning, content generation, analysis | ~$0.03/day |
| Prompt caching | System prompts cached (90% cheaper on repeats) | Saves ~$0.02/day |

**Why Sonnet (not Opus)?** We originally used Opus ($15/M input tokens) but switched to Sonnet ($3/M tokens) — same quality for our use cases, 5x cheaper.

### Backend

| Component | What | Why |
|-----------|------|-----|
| FastAPI | 30+ REST endpoints + WebSocket | Fast, async, Python-native, auto-docs |
| Uvicorn | ASGI server | Production-ready, handles WebSocket |
| httpx | Async HTTP client | For Claude API calls and health checks |
| Anthropic SDK | Claude API wrapper | Used in code_improver.py |
| python-dotenv | Environment variable loading | Keeps secrets out of code |

### Frontend

| Component | What | Why |
|-----------|------|-----|
| Vanilla HTML/CSS/JS | 10 pages, no framework | Transparency — no build complexity, easy to understand |
| WebSocket | Real-time updates | Dashboard updates instantly when agents act |
| JetBrains Mono font | Typography | Professional developer aesthetic |
| CSS custom properties | Design system | Consistent colors across all 10 pages |

### Data Sources (All Free)

| API | Purpose | Limit |
|-----|---------|-------|
| NewsAPI.org | Headlines and articles | 100 req/day |
| SEC EDGAR | Financial filings | 10 req/sec |
| yfinance | Stock prices and history | Unlimited |
| Remotive | Remote tech jobs | Unlimited |
| Arbeitnow | European tech jobs | Unlimited |
| Adzuna | Global jobs with salary | 250 req/day |
| GitHub API (public) | Portfolio data | 60 req/hour |

### Infrastructure

| Component | Where | Cost |
|-----------|-------|------|
| SkillVector backend | Railway (Frankfurt) | Free tier → paid as users grow |
| SkillVector frontend | Cloudflare Pages | Free |
| DNS | Cloudflare | Free |
| Glass Box dashboard | Your Mac (localhost:8000) | Free |
| Scheduling | macOS cron job | Free |
| Email | Gmail SMTP (app password) | Free |
| Version control | GitHub (2 repos) | Free |

### Total Monthly Cost (Current)

| Item | Cost |
|------|------|
| Claude API (daily pipeline) | ~$0.90/month |
| Claude API (code improvement 3x/week) | ~$0.36/month |
| Claude API (dashboard chat) | ~$0.50/month |
| Railway hosting | Free tier (currently) |
| Everything else | Free |
| **TOTAL** | **~$1.76/month** |

---

## 10. The Full Timeline — Everything We Built, In Order <a name="10-timeline"></a>

### Phase 1: Foundation (Commit 886bb4c)
**What:** Initial commit. Empty repo, basic structure.

### Phase 2: Full Platform (Commit 1f14661)
**What:** Built the entire platform from scratch in one push:
- 5 AI agents with Claude integration
- 10-page dashboard (all HTML/CSS/JS)
- FastAPI backend with 30+ endpoints
- WebSocket real-time activity feed
- Agent template store (3 products)
- Complete dark theme design system

### Phase 3: Deployment (Commit 9efd794)
**What:** Made it deployable on Render:
- Static file serving for dashboard
- Dynamic API URLs (localhost vs production)
- render.yaml configuration
- runtime.txt for Python version

### Phase 4: Testing (Commit 4b0af44)
**What:** Added 29 tests covering:
- API endpoints (health, agents, chat, profile)
- Agent manager (all 5 agents, state management)
- Job search (Remotive, Arbeitnow)
- Profile management (save, load, update)
- Static file serving

### Phase 5: Store + SkillVector Integration (Commit c6ef98c → 4a8015b)
**What:** Connected the two products:
- Gumroad links for template store
- SkillVector API client (health check, job ingestion, trend updates)
- LinkedIn Zapier integration setup
- Scheduler skeleton

### Phase 6: Full Automation (Commit 84dc44b)
**What:** Built the automation layer:
- GitHub pusher (auto-commit + push improvements)
- Dashboard updater (sync SkillVector stats)
- Code improver (Claude reviews and fixes code)

### Phase 7: Agentic Workflow (Commit a0bcc7f)
**What:** Made agents actually plan and track work:
- Workflow manager (task planning, progress tracking)
- Lessons system (learn from failures)
- Verification steps (check results before proceeding)

### Phase 8: Email Automation (Commit 15b527f → da943ca)
**What:** Email digest system:
- Single-post email → multi-platform email
- HTML dark theme formatting
- Platform-specific headers and quick-links
- Gmail SMTP integration

### Phase 9: Atlas Daily Automation v2.0 (Commit a5e2877)
**What:** Complete pipeline rewrite — the big one:
- Rewrote daily_pipeline.py from 666 to 835 lines
- 8-step pipeline with proper error handling
- Confidence scoring (0-100%)
- Learning loop (reads and writes lessons)
- Token usage tracking per Claude call
- Self-healing health checks
- Full end-to-end test completed in 68.4 seconds

### Phase 10: Scheduling Fix (Commit fa54931)
**What:** Made it actually run automatically:
- Tried macOS launchd → failed (TCC permission blocks ~/Desktop access)
- Switched to crontab
- Created run_scheduler.sh wrapper

### Phase 11: Token Optimization (Commit 10319e8)
**What:** Reduced costs by 15x:
- Switched code_improver from Claude Opus to Sonnet
- Reduced max_tokens across pipeline (4000→2000 for code improvement)
- Added per-call token logging
- Wired up learning loop with confidence scoring

### Phase 12: Self-Healing API (Commit 40533f4)
**What:** Atlas auto-fixes SkillVector downtime:
- Auto-redeploy via empty git commit to Railway
- Health check retries 3x before triggering
- Hourly ping triggers redeploy after 2 consecutive failures
- SKILLEVECTOR_PROD_URL constant for production

### Phase 13: README Rewrite (Commit de09355)
**What:** Complete 431-line README in plain English:
- ASCII architecture diagram
- Step-by-step daily workflow
- Self-healing flow chart
- Manual vs automated comparison table
- Token cost breakdown

### Phase 14: Catch-Up Scheduler (Commit 0f4af26)
**What:** Fixed the "Mac was asleep" problem:
- run_if_needed.sh — runs every 15 min between 8-10 AM
- Date marker file prevents double-runs
- Switched from .venv Python to pyenv Python 3.11.9 (fixed macOS TCC permission error)
- Pipeline confirmed working: 55.5s, email sent, 4 posts saved

---

## 11. What Went Wrong and How We Fixed It <a name="11-what-went-wrong"></a>

### Problem 1: macOS TCC Permission (The Recurring Nightmare)

**What happened:** macOS has a security feature called TCC (Transparency, Consent, and Control) that blocks apps from accessing protected folders like ~/Desktop. When cron or launchd tried to run our Python script, macOS blocked it because Python was reading files from ~/Desktop.

**How it showed up:** 500 lines of `PermissionError: [Errno 1] Operation not permitted: '.venv/pyvenv.cfg'` in cron.log. Nothing ran. For 3 days.

**What we tried:**
1. ❌ launchd with direct Python path → blocked
2. ❌ launchd with bash wrapper → blocked
3. ❌ cron with .venv Python → blocked (same error)
4. ✅ cron with pyenv Python 3.11.9 → WORKS (lives outside ~/Desktop)

**Root cause:** The .venv/ folder was inside ~/Desktop, and any Python venv tries to read pyvenv.cfg during startup. macOS blocks this for cron/launchd processes.

**Fix:** Use `/Users/kalamakuntlarakeshreddy/.pyenv/versions/3.11.9/bin/python3` — it's installed under ~/.pyenv, which isn't a protected folder.

**Lesson:** Never put Python virtual environments inside macOS protected folders (Desktop, Documents, Downloads) if you need cron/launchd access.

### Problem 2: Mac Asleep at 8 AM (Missed Cron Jobs)

**What happened:** Cron only runs when the Mac is awake. If you opened your laptop at 8:30 AM, the 8:00 AM job was already missed and wouldn't retry.

**How it showed up:** No email, no posts, empty cron.log for the day.

**Fix:** `run_if_needed.sh` — runs every 15 minutes from 8-10 AM, uses a date marker file to ensure it only runs once per day. Even if the Mac wakes at 9:45, the pipeline catches up.

### Problem 3: Claude Opus Token Cost (15x Too Expensive)

**What happened:** The code_improver.py was using Claude Opus ($15/M input tokens) instead of Sonnet ($3/M tokens). Didn't notice until we audited costs.

**Fix:** Changed model string from `claude-opus` to `claude-sonnet-4-20250514` and reduced max_tokens from 4000 to 2000.

### Problem 4: JSON Parse Errors from Claude

**What happened:** When Claude's response was truncated (hit max_tokens limit), the JSON was incomplete and `json.loads()` threw "Unterminated string" errors. Code improvement step failed every time.

**Fix:** Bumped max_tokens to 4096 for code improvement. Added fallback: if JSON parse fails but response contains `"should_improve": false`, gracefully skip instead of crashing.

### Problem 5: Git Push Conflicts

**What happened:** github_pusher.py would commit and push, but if someone else had pushed in between, it failed with "non-fast-forward" error.

**Fix:** Always run `git pull --rebase` before push. Recorded as Lesson 003.

### Problem 6: Twitter/LinkedIn API Access

**What happened:** Twitter API requires paid access for write endpoints. LinkedIn OAuth codes expire in 30 seconds and client credentials flow doesn't support posting.

**Fix:** Both platforms routed through Zapier webhooks (manual posting for now). Posts generated by pipeline, user copy-pastes from email.

### Problem 7: Python 3.9 Type Hint Compatibility

**What happened:** github_pusher.py used `list[str]` and `str | None` syntax (Python 3.10+), but the system Python was 3.9.6. Import errors crashed the pipeline.

**Fix:** Changed to `List[str]` and `Optional[str]` from the `typing` module (works with Python 3.9+).

---

## 12. What's Working Right Now (March 2026) <a name="12-whats-working-now"></a>

### Fully Automated (No Human Action Needed)

| What | When | Status |
|------|------|--------|
| Daily pipeline (8 steps) | 8-10 AM daily | ✅ Working since March 9 |
| Health ping to SkillVector | Every hour | ✅ Working |
| Email with 4 platform posts | Daily (part of pipeline) | ✅ Working |
| Competitor intel update | Daily (part of pipeline) | ✅ Working |
| Code improvement push | Mon/Wed/Fri | ✅ Working (fixed JSON parse March 10) |
| Auto-redeploy if API down | On detection | ✅ Working (tested March 9) |
| Learning from failures | Every pipeline run | ✅ Working |

### Working But Manual

| What | Why Manual |
|------|-----------|
| Posting to LinkedIn | OAuth complexity — copy from email |
| Posting to Reddit | No API yet — copy from email |
| Posting to Twitter | Paid API required — copy from email |
| Posting to Indie Hackers | No API available — copy from email |
| Using the DALL-E image prompt | Need to paste into Midjourney/DALL-E manually |
| Approving code improvements | Sentinel review is advisory, not blocking |

### Dashboard Features

| Feature | Backed by Real Data? |
|---------|---------------------|
| Agent cards with status | ✅ Yes (from /api/agents) |
| Live activity feed | ✅ Yes (WebSocket real-time) |
| Chat with agents | ✅ Yes (Claude API) |
| Job search (NEXUS) | ✅ Yes (3 real APIs) |
| Cover letter generation | ✅ Yes (Claude + profile) |
| GitHub portfolio | ✅ Yes (GitHub public API) |
| Approval queue | ✅ Yes (backend + WebSocket) |
| Token usage metrics | Partial (agent-level tracking) |
| Store/templates | ✅ Yes (Gumroad links) |

---

## 13. The Money Side — Token Costs and Revenue Model <a name="13-money"></a>

### Current Operating Cost

**Daily Claude API usage:**
| Call | Tokens | Cost |
|------|--------|------|
| Research (3 insights) | ~700 | $0.002 |
| Content generation (4 posts) | ~2,400 | $0.007 |
| Monday image prompt (1x/week) | ~300 | $0.001 |
| Code improvement (3x/week) | ~2,000 | $0.006 |
| Weekly analytics (1x/week) | ~500 | $0.002 |
| Competitor monitoring | ~800 | $0.002 |
| **Daily total** | **~4,000-6,000** | **~$0.02** |
| **Monthly total** | **~150,000** | **~$0.60** |

Including dashboard chat and job hunting: **~$1.76/month total.**

### Revenue Model (Template Store)

| Product | Price | What's Included |
|---------|-------|-----------------|
| Job Search Agent | $49 | Search + score + cover letters + review |
| Content Writer Agent | $79 | Research + multi-platform writer + quality check |
| Research Agent | $99 | Competitive intel + trend analysis + SWOT |
| Bundle (All 3) | $199 | All templates + integration guide |

Each template is a self-contained FastAPI + HTML project that buyers can deploy and customize.

### Funding Pitch Numbers

**Why investors should care:**
- Running cost: $1.76/month (practically free)
- Fully automated content pipeline — zero human time per day
- Self-healing infrastructure — handles downtime automatically
- Revenue potential: Templates at $49-$199/unit
- SkillVector: B2C career platform for ML engineers (massive TAM)
- Glass Box: B2B AI orchestration framework (enterprise potential)

---

## 14. Future Improvements — What's Next <a name="14-future"></a>

### High Priority (Should Do Soon)

| Improvement | Why | Effort |
|-------------|-----|--------|
| **Auto-post to LinkedIn via Zapier webhook** | Eliminate manual copy-paste | Medium — need Zapier Pro account |
| **Auto-post to Twitter via Buffer/Zapier** | Same as above | Medium |
| **Telegram approval for code changes** | Human reviews before code pushes to SkillVector | Small — Telegram bot already built |
| **Token usage dashboard with real data** | memory.html currently shows mock data | Small — add tracking per agent |
| **confidence score fix** | Pipeline reports "unknown" for some steps | Small — fix status parsing in pipeline |
| **Persistent agent memory** | Agents forget context between sessions | Medium — store in SQLite or JSON |

### Medium Priority (Would Be Nice)

| Improvement | Why | Effort |
|-------------|-----|--------|
| **Deploy Glass Box to Railway** | Access dashboard from anywhere, not just localhost | Medium — already has render.yaml |
| **Multi-user support** | Let SkillVector users use Glass Box agents | Large — auth system needed |
| **Stripe payment for templates** | Real checkout flow (not just Gumroad) | Medium |
| **Voice interface** | "Hey Atlas, what's the pipeline status?" | Medium — Whisper API for STT |
| **Chrome extension** | One-click job application from LinkedIn/Indeed | Large |
| **Mobile dashboard** | Check pipeline status from phone | Medium — responsive CSS exists |

### Moonshot Ideas (Future Vision)

| Idea | Impact |
|------|--------|
| **White-label Glass Box for enterprises** | B2B SaaS — companies deploy their own agent teams |
| **Agent marketplace** | Users create and sell custom agents |
| **Real-time interview prep** | Claude-powered mock interviews with feedback |
| **Portfolio auto-builder** | Generate personal site from GitHub + profile data |
| **Salary negotiation agent** | Claude analyzes offers and suggests counter-offers |

### Known Issues to Fix

| Issue | Impact | Fix |
|-------|--------|-----|
| Pipeline reports "unknown" status for research/content/save steps | Confidence score lower than actual | Fix status return values in each step function |
| Lessons auto-record mentions "unknown" steps | Lesson quality is low | Only record specific failure reasons |
| Weekly analytics skips even on Sunday (sometimes) | Miss weekly report | Check DAY_OF_WEEK timezone |
| Code improvement JSON truncation | Step fails occasionally | Already fixed (max_tokens 4096 + fallback) |

---

## 15. How to Pitch This to Investors <a name="15-pitch"></a>

### The One-Liner
"We built an AI operations team that runs a career intelligence platform 24/7 for $1.76/month."

### The Problem
ML engineers struggle to navigate a rapidly changing job market. Traditional career advice is too slow, too generic, and too expensive.

### The Solution — Two Products

**SkillVector (B2C):**
An AI career intelligence platform that analyzes job postings, identifies skill gaps, and provides personalized career guidance for ML engineers. Uses Neo4j knowledge graph + Pinecone vector search + Claude AI.

**Glass Box AI (B2B potential):**
An AI agent orchestration framework where every decision is transparent, every action is auditable, and every mistake is learned from. Unlike black-box AI systems, Glass Box shows you exactly what the AI is doing and why.

### The Traction
- Daily automated content pipeline — 4 platforms, every day, zero manual effort
- Self-healing infrastructure — detects and fixes downtime automatically
- 29 automated tests — production-grade code quality
- Working product at skill-vector.com
- 3 sellable agent templates on Gumroad ($49-$199)
- 16 commits of iterative development (not vaporware)

### The Market
- 1.2 million ML engineers worldwide (growing 25% YoY)
- AI career tools market: $4.2B by 2027
- AI agent orchestration: nascent market, no clear leader

### The Moat
1. **Learning loop** — our system gets smarter every day (competitors don't learn from failures)
2. **Transparency** — "glass box" approach (every decision visible, auditable)
3. **Cost efficiency** — $1.76/month to operate (competitors spend $50-200/month on API calls)
4. **Self-healing** — auto-recovers from failures (competitors need manual intervention)

### The Ask
Seed funding for:
1. Deploy Glass Box as a cloud service (multi-user)
2. Build SkillVector user base (ML engineer community)
3. Enterprise pilot — white-label Glass Box for 3 companies
4. Hire 1 frontend developer (React migration for SkillVector)

### The Team
- **Rakesh Reddy Kalamakuntla** — Master's in Computer Science (in progress), builder of both products, handles backend, AI integration, and daily operations. Built the entire system solo.

---

## 16. Technical Reference — Every File Explained <a name="16-reference"></a>

### Root Files

| File | Lines | Purpose |
|------|-------|---------|
| `scheduler.py` | 152 | Production scheduler — daily pipeline + hourly health. CLI: `--run-now`, `--health` |
| `run_if_needed.sh` | 20 | Catch-up script for cron — runs pipeline if not yet run today |
| `run_scheduler.sh` | 15 | Bash wrapper (originally for launchd, now backup) |
| `healthcheck.sh` | 5 | Railway deployment health check |
| `render.yaml` | 20 | Railway/Render deployment configuration |
| `runtime.txt` | 1 | Python version specification (3.11.9) |
| `README.md` | 431 | Project documentation (plain English) |

### Backend (`backend/`)

| File | Lines | Purpose |
|------|-------|---------|
| `agents.py` | ~200 | AgentManager class — 5 agents with Claude, prompt caching, conversation history |
| `server.py` | ~800 | FastAPI app — 30+ endpoints, WebSocket, Telegram, all routing |
| `scout_tools.py` | ~250 | ScoutTools — NewsAPI, SEC EDGAR, yfinance price/history |
| `job_tools.py` | ~350 | JobTools — Remotive, Arbeitnow, Adzuna search + merge |
| `github_tools.py` | ~150 | GitHubTools — profile, repos, commits, language stats (public API) |
| `profile_manager.py` | ~150 | ProfileManager — user profile + cover letter + job storage |
| `requirements.txt` | 10 | Python dependencies |
| `tests/test_glassbox.py` | ~300 | 29 tests — endpoints, agents, jobs, profile |

### Integrations (`integrations/`)

| File | Lines | Purpose |
|------|-------|---------|
| `daily_pipeline.py` | 835 | The big one — 8-step automated pipeline with self-healing |
| `email_sender.py` | 138 | HTML email sender — dark theme, 4 platform posts |
| `github_pusher.py` | 104 | Git operations — commit, pull, push, write files |
| `code_improver.py` | 106 | Claude reviews code → suggests fix → pushes to GitHub |
| `skillevector_client.py` | ~100 | SkillVector API wrapper (health, ingest, trends, insights) |
| `dashboard_updater.py` | ~80 | Fetches SkillVector stats → pushes to frontend |
| `workflow_manager.py` | ~100 | Task planning, progress tracking, lesson recording |
| `langchain_tools.py` | ~80 | LangChain tool decorators (ready for future use) |
| `social/linkedin_poster.py` | ~30 | LinkedIn posting template (not yet active) |
| `social/twitter_poster.py` | ~30 | Twitter posting template (not yet active) |

### Dashboard (`dashboard/`)

| File | Purpose |
|------|---------|
| `index.html` | Command Center — live feed, KPIs, directive input |
| `agents.html` | Agent Registry — 5 agent cards with metrics |
| `trace.html` | Execution Trace — step-by-step timeline |
| `approvals.html` | Approval Queue — APPROVE/PAUSE/DENY buttons |
| `decisions.html` | Decision Attribution — why did we approve that? |
| `audit.html` | Audit Log — compliance table, CSV export |
| `memory.html` | Token Usage — cost breakdown, context window |
| `jobs.html` | NEXUS — job search, scoring, cover letters |
| `github.html` | GitHub Portfolio — live profile/repos/commits |
| `store.html` | Template Store — 3 products with Gumroad links |
| `css/styles.css` | Design system — dark theme, agent colors, glass cards |
| `js/api.js` | Backend connection — auto-detect, WebSocket, fallback |
| `js/data.js` | Mock data — demo mode when backend is offline |

### Templates (`templates/`) — Sellable Products

| Template | Price | Files |
|----------|-------|-------|
| `job-search-agent/` | $49 | agent.py, server.py, tools.py, index.html, README.md |
| `content-writer-agent/` | $79 | agent.py, server.py, index.html, README.md |
| `research-agent/` | $99 | agent.py, server.py, tools.py, index.html, README.md |

### Documentation (`docs/`)

| File | Topic |
|------|-------|
| `architecture.md` | 3-layer model: Observation → Approval → Execution |
| `mental-model.md` | Glass box vs black box, confidence vs risk |
| `agent-roles.md` | 6 agent archetypes mapped to our 5 agents |
| `approval-flow.md` | When gates trigger, 4-step approval process |

### Tasks & Posts

| File | Purpose |
|------|---------|
| `tasks/todo.md` | Daily task checklist (v2.0 pipeline steps) |
| `tasks/lessons.md` | Auto-generated + manual lessons (7+ entries) |
| `tasks/competitor_intel.md` | Daily competitive landscape analysis |
| `posts/*_today.md` | Latest generated posts (4 platforms) |
| `posts/*_2026-03-XX.md` | Dated post archive |

---

## Environment Variables (.env)

```
# AI
ANTHROPIC_API_KEY=sk-ant-...              # Claude API access

# Notifications
TELEGRAM_BOT_TOKEN=123456:ABC...           # Telegram bot for alerts
TELEGRAM_CHAT_ID=999999                    # Your Telegram chat

# Data Sources
NEWSAPI_KEY=...                            # News articles (free tier)
ADZUNA_APP_ID=...                          # Job listings (optional)
ADZUNA_API_KEY=...                         # Job listings (optional)

# Email
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=your-email@gmail.com
EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx     # Gmail app-specific password

# SkillVector Connection
SKILLEVECTOR_URL=https://api.skill-vector.com
SKILLEVECTOR_REPO_PATH=/path/to/skillvector-engine
AUTOMATION_API_KEY=...                     # x-atlas-key for SkillVector API

# GitHub
GITHUB_USERNAME=RakeshReddy26-bit
```

---

## API Endpoint Reference

### System
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | Health check (returns OK + agent count) |
| GET | `/api/agents` | All 5 agents with status/metrics |
| GET | `/api/activity` | Last 50 activity events |

### Chat
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/chat` | Send directive to agent (or all) |

### Approvals
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/approvals` | Pending + history |
| POST | `/api/approvals/{id}/decide` | APPROVE/PAUSE/DENY |

### Research
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/scout/research` | Search news, SEC filings, stock data |

### Jobs (NEXUS)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/jobs/search` | Search across 3 platforms |
| POST | `/api/jobs/cover-letter` | Generate tailored cover letter |
| POST | `/api/jobs/hunt` | Full pipeline: search → score → write → review |

### Profile
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/profile` | Get user profile |
| POST | `/api/profile` | Update profile fields |

### WebSocket
| Protocol | Endpoint | Purpose |
|----------|----------|---------|
| WS | `/ws` | Real-time events (activity, decisions) |

---

## How to Run Everything

### Start the Dashboard
```bash
cd ~/Desktop/A-Glass-Box-AI-Orchestration-Dashboard
source .venv/bin/activate  # or use pyenv
python backend/server.py
# Open http://localhost:8000
```

### Run Pipeline Manually
```bash
python scheduler.py --run-now
```

### Quick Health Check
```bash
python scheduler.py --health
```

### Run Tests
```bash
cd backend && pytest tests/ -v
```

### Check Cron Status
```bash
crontab -l                          # See scheduled jobs
cat logs/cron.log | tail -20        # See recent runs
```

---

## Glossary

| Term | Meaning |
|------|---------|
| **Atlas** | The orchestrator agent — the boss that coordinates everything |
| **Scout** | Research agent — fetches real data from APIs |
| **Cipher** | Analysis agent — scores jobs, calculates risk |
| **Scribe** | Writer agent — generates posts, cover letters, reports |
| **Sentinel** | Compliance agent — reviews quality, detects scams |
| **NEXUS** | The job hunting pipeline mode |
| **Pipeline** | The 8-step daily automation sequence |
| **Confidence** | 0-100% score of how well the pipeline ran |
| **Self-healing** | System auto-recovers from failures |
| **Learning loop** | System records mistakes and avoids repeating them |
| **TCC** | macOS security that blocks app access to protected folders |
| **Railway** | Cloud hosting platform for SkillVector backend |
| **Prompt caching** | Claude caches system prompts = 90% cheaper on repeats |
| **Glass box** | Opposite of black box — all AI decisions are visible and auditable |

---

*This guide will be updated as the project evolves. Last verified: March 10, 2026 — all systems operational.*
