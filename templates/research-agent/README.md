# 🔬 AI Research Agent

**Automated market research, competitor analysis, and trend reports — powered by Claude AI.**

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-latest-green) ![Claude](https://img.shields.io/badge/Claude_AI-Sonnet_4-purple) ![License](https://img.shields.io/badge/License-Commercial-orange)

---

## What It Does

This agent automates research tasks for founders, marketers, and analysts:

1. **Market research** — Analyze industries, trends, and market size using real news data
2. **Competitor analysis** — Compare companies, features, pricing, and positioning
3. **Trend reports** — Identify emerging trends from news feeds with AI analysis
4. **Executive summaries** — Turn raw research into actionable briefs
5. **SWOT analysis** — Automated strength/weakness/opportunity/threat breakdowns

## Features

- 📰 **Real-time news data** — Powered by NewsAPI (100 free requests/day)
- 🏢 **Competitor profiling** — Side-by-side comparison of up to 5 companies
- 📈 **Trend detection** — AI identifies patterns across news articles
- 📋 **Structured reports** — Markdown reports saved automatically
- 🧠 **SWOT generator** — One-click SWOT analysis for any company/product
- 📊 **Market sizing** — TAM/SAM/SOM estimates with reasoning
- 🎨 **Browser UI** — Professional research dashboard included
- ⚡ **Fast** — Complete market reports in ~30 seconds

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env — add your Anthropic + NewsAPI keys
```

You need:
- **Anthropic API key** (required) — [console.anthropic.com](https://console.anthropic.com/)
- **NewsAPI key** (required for news) — [newsapi.org](https://newsapi.org/) (free tier: 100 req/day)

### 3. Run

```bash
python server.py
```

Open `http://localhost:8000` in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Dashboard UI |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/research` | Run market research on a topic |
| `POST` | `/api/competitor` | Competitor analysis |
| `POST` | `/api/trends` | Trend report from news data |
| `POST` | `/api/swot` | SWOT analysis for a company/product |
| `POST` | `/api/summary` | Executive summary from raw text |
| `GET` | `/api/history` | List generated reports |

## Example Usage

```bash
# Market research
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI agent market 2026", "depth": "detailed"}'

# Competitor analysis
curl -X POST http://localhost:8000/api/competitor \
  -H "Content-Type: application/json" \
  -d '{"companies": ["OpenAI", "Anthropic", "Google DeepMind"], "focus": "AI models"}'

# SWOT analysis
curl -X POST http://localhost:8000/api/swot \
  -H "Content-Type: application/json" \
  -d '{"subject": "Tesla", "context": "Electric vehicle market in Europe"}'
```

## Tech Stack

- **Backend:** Python + FastAPI + Uvicorn
- **AI:** Anthropic Claude API (Sonnet 4)
- **Data:** NewsAPI (real-time news)
- **Frontend:** Vanilla HTML + TailwindCSS
- **Output:** Markdown + JSON

## File Structure

```
research-agent/
├── server.py          # FastAPI backend + all endpoints
├── agent.py           # Claude AI research engine
├── tools.py           # NewsAPI integration
├── index.html         # Browser dashboard UI
├── requirements.txt   # Python dependencies
├── .env.example       # Config template
└── README.md          # This file
```

---

**Built with [Glass Box AI](https://github.com/RakeshReddy26-bit/A-Glass-Box-AI-Orchestration-Dashboard)**
