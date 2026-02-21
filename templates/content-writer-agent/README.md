# ✍️ AI Content Writer Agent

**Generate blog posts, social media content, and SEO-optimized articles — powered by Claude AI.**

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-latest-green) ![Claude](https://img.shields.io/badge/Claude_AI-Sonnet_4-purple) ![License](https://img.shields.io/badge/License-Commercial-orange)

---

## What It Does

This agent automates content creation for blogs, social media, and marketing:

1. **Generate blog posts** from a topic or outline — complete with headings, intro, body, and conclusion
2. **SEO optimization** — keyword integration, meta descriptions, and readability scoring
3. **Social media variants** — Turn any blog post into Twitter threads, LinkedIn posts, and Instagram captions
4. **Multiple tones** — Professional, casual, technical, storytelling, persuasive
5. **Markdown + HTML output** — Ready to publish anywhere

## Features

- 📝 **Blog post generation** — Full articles from just a topic or outline
- 🔑 **SEO keyword integration** — Natural keyword placement with density scoring
- 📱 **Social media repurposing** — One article → 5 platform-specific posts
- 🎭 **Tone control** — Professional, casual, technical, witty, storytelling
- 📊 **Content scoring** — Readability, engagement, SEO scores (0-100)
- 💾 **Auto-save** — All content saved as Markdown files
- 🎨 **Browser UI** — Professional editing dashboard included
- ⚡ **Fast** — 800-1200 word articles in ~15 seconds

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
# Edit .env — add your Anthropic API key
```

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
| `POST` | `/api/blog` | Generate a blog post |
| `POST` | `/api/social` | Generate social media posts from text |
| `POST` | `/api/seo` | Analyze and optimize content for SEO |
| `POST` | `/api/rewrite` | Rewrite content in a different tone |
| `GET` | `/api/history` | List all generated content |

## Example Usage

```bash
# Generate a blog post
curl -X POST http://localhost:8000/api/blog \
  -H "Content-Type: application/json" \
  -d '{"topic": "Why FastAPI is the best Python framework in 2026", "tone": "technical", "word_count": 1000}'

# Generate social media posts
curl -X POST http://localhost:8000/api/social \
  -H "Content-Type: application/json" \
  -d '{"text": "Your blog post content here...", "platforms": ["twitter", "linkedin", "instagram"]}'

# SEO analysis
curl -X POST http://localhost:8000/api/seo \
  -H "Content-Type: application/json" \
  -d '{"content": "Your article...", "keywords": ["FastAPI", "Python", "web framework"]}'
```

## Customization

### Add new content types
Edit `agent.py` — add a new prompt constant and a corresponding method.

### Adjust default tone
In `server.py`, change the `DEFAULT_TONE` variable.

### Add content templates
Create template strings in `agent.py` that the AI uses as structural guides.

## Tech Stack

- **Backend:** Python + FastAPI + Uvicorn
- **AI:** Anthropic Claude API (Sonnet 4)
- **Frontend:** Vanilla HTML + TailwindCSS
- **Output:** Markdown + JSON

## File Structure

```
content-writer-agent/
├── server.py          # FastAPI backend + all endpoints
├── agent.py           # Claude AI content generation
├── index.html         # Browser dashboard UI
├── requirements.txt   # Python dependencies
├── .env.example       # Config template
└── README.md          # This file
```

---

**Built with [Glass Box AI](https://github.com/RakeshReddy26-bit/A-Glass-Box-AI-Orchestration-Dashboard)**
