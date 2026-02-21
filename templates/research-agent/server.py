"""
AI Research Agent — FastAPI Server
Complete standalone backend. Run: python server.py
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

load_dotenv()

from agent import ResearchAgent
from tools import ResearchTools

# ── Output directory ──────────────────────────────────────────────

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "ResearchAgent-Outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Pydantic Models ──────────────────────────────────────────────

class ResearchRequest(BaseModel):
    topic: str
    depth: str = "detailed"  # "brief" or "detailed"
    news_count: int = 10

class CompetitorRequest(BaseModel):
    companies: List[str]
    focus: str = "overall"
    include_news: bool = True

class TrendRequest(BaseModel):
    topic: str
    news_count: int = 15

class SWOTRequest(BaseModel):
    subject: str
    context: Optional[str] = ""

class SummaryRequest(BaseModel):
    text: str


# ── App Setup ─────────────────────────────────────────────────────

app = FastAPI(title="AI Research Agent", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

agent = ResearchAgent()
tools = ResearchTools()

report_history = []


def _save_report(report_type, topic, content):
    """Save report to file and history."""
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    safe_topic = "".join(c for c in topic[:40] if c.isalnum() or c in " -_").strip().replace(" ", "_")
    filename = f"{report_type}_{safe_topic}_{ts}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w") as f:
        f.write(f"# {report_type.title()} Report: {topic}\n")
        f.write(f"*Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}*\n\n---\n\n")
        f.write(content)

    entry = {
        "id": len(report_history) + 1,
        "type": report_type,
        "topic": topic,
        "filename": filename,
        "created_at": datetime.now().isoformat(),
    }
    report_history.insert(0, entry)
    return filepath, entry


# ── Routes ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    with open("index.html", "r") as f:
        return f.read()


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "ai_configured": agent.is_configured(),
        "news_configured": tools.is_configured(),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/research")
async def market_research(req: ResearchRequest):
    """Run market research with real news data + AI analysis."""
    # Fetch news
    news = await tools.search_news(req.topic, page_size=req.news_count)
    news_context = tools.format_articles(news) if news.get("success") else "No news data available."

    # Generate report
    report = await agent.research(topic=req.topic, news_context=news_context, depth=req.depth)
    filepath, entry = _save_report("research", req.topic, report)

    return {
        "success": True,
        "report": report,
        "news_articles": news.get("total", 0),
        "saved_to": filepath,
        "entry": entry,
    }


@app.post("/api/competitor")
async def competitor_analysis(req: CompetitorRequest):
    """Compare competitors with optional news context."""
    news_context = ""
    if req.include_news:
        query = " OR ".join(req.companies[:3])
        news = await tools.search_news(query, page_size=10)
        if news.get("success"):
            news_context = tools.format_articles(news)

    report = await agent.competitor_analysis(
        companies=req.companies, focus=req.focus, news_context=news_context,
    )
    filepath, entry = _save_report("competitor", " vs ".join(req.companies), report)

    return {"success": True, "report": report, "saved_to": filepath, "entry": entry}


@app.post("/api/trends")
async def trend_report(req: TrendRequest):
    """Generate trend report from real news data."""
    news = await tools.search_news(req.topic, page_size=req.news_count, days_back=60)
    if not news.get("success") or not news.get("articles"):
        return {"success": False, "error": f"No news found for '{req.topic}'"}

    news_context = tools.format_articles(news)
    report = await agent.trend_report(topic=req.topic, news_context=news_context)
    filepath, entry = _save_report("trends", req.topic, report)

    return {
        "success": True,
        "report": report,
        "news_articles": news["total"],
        "saved_to": filepath,
        "entry": entry,
    }


@app.post("/api/swot")
async def swot_analysis(req: SWOTRequest):
    """SWOT analysis for any company or product."""
    report = await agent.swot_analysis(subject=req.subject, context=req.context)
    filepath, entry = _save_report("swot", req.subject, report)
    return {"success": True, "report": report, "saved_to": filepath, "entry": entry}


@app.post("/api/summary")
async def executive_summary(req: SummaryRequest):
    """Distill raw text into an executive summary."""
    summary = await agent.executive_summary(raw_text=req.text)
    return {"success": True, "summary": summary, "original_length": len(req.text), "summary_length": len(summary)}


@app.get("/api/history")
async def get_history():
    return {"success": True, "total": len(report_history), "reports": report_history[:50]}


if __name__ == "__main__":
    print("\n  🔬 AI Research Agent")
    print(f"  AI: {'configured' if agent.is_configured() else 'NOT configured — add ANTHROPIC_API_KEY to .env'}")
    print(f"  News: {'configured' if tools.is_configured() else 'NOT configured — add NEWSAPI_KEY to .env'}")
    print(f"  Dashboard: http://localhost:8000\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
