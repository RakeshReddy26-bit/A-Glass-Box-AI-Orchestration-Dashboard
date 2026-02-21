"""
AI Content Writer Agent — FastAPI Server
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

from agent import ContentAgent

# ── Output directory ──────────────────────────────────────────────

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "ContentWriter-Outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Pydantic Models ──────────────────────────────────────────────

class BlogRequest(BaseModel):
    topic: str
    tone: str = "professional"
    word_count: int = 800
    keywords: Optional[List[str]] = None
    outline: Optional[str] = None

class SocialRequest(BaseModel):
    text: str
    platforms: Optional[List[str]] = None

class SEORequest(BaseModel):
    content: str
    keywords: Optional[List[str]] = None

class RewriteRequest(BaseModel):
    text: str
    target_tone: str = "casual"


# ── App Setup ─────────────────────────────────────────────────────

app = FastAPI(title="AI Content Writer Agent", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

agent = ContentAgent()

# In-memory history
content_history = []


# ── Routes ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    with open("index.html", "r") as f:
        return f.read()


@app.get("/api/health")
async def health():
    return {"status": "ok", "ai_configured": agent.is_configured(), "timestamp": datetime.now().isoformat()}


@app.post("/api/blog")
async def generate_blog(req: BlogRequest):
    """Generate a blog post from topic/outline."""
    content = await agent.write_blog(
        topic=req.topic, tone=req.tone, word_count=req.word_count,
        keywords=req.keywords, outline=req.outline,
    )

    # Save to file
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    safe_topic = "".join(c for c in req.topic[:40] if c.isalnum() or c in " -_").strip().replace(" ", "_")
    filename = f"blog_{safe_topic}_{ts}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w") as f:
        f.write(content)

    entry = {
        "id": len(content_history) + 1,
        "type": "blog",
        "topic": req.topic,
        "tone": req.tone,
        "word_count": req.word_count,
        "filename": filename,
        "created_at": datetime.now().isoformat(),
    }
    content_history.insert(0, entry)

    return {"success": True, "content": content, "saved_to": filepath, "entry": entry}


@app.post("/api/social")
async def generate_social(req: SocialRequest):
    """Generate social media posts from text."""
    content = await agent.generate_social(text=req.text, platforms=req.platforms)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"social_{ts}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w") as f:
        f.write(content)

    entry = {
        "id": len(content_history) + 1,
        "type": "social",
        "platforms": req.platforms or ["twitter", "linkedin", "instagram"],
        "filename": filename,
        "created_at": datetime.now().isoformat(),
    }
    content_history.insert(0, entry)

    return {"success": True, "content": content, "saved_to": filepath}


@app.post("/api/seo")
async def analyze_seo(req: SEORequest):
    """Analyze content for SEO optimization."""
    analysis = await agent.analyze_seo(content=req.content, keywords=req.keywords)
    return {"success": True, "analysis": analysis}


@app.post("/api/rewrite")
async def rewrite_content(req: RewriteRequest):
    """Rewrite content in a different tone."""
    rewritten = await agent.rewrite(text=req.text, target_tone=req.target_tone)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"rewrite_{req.target_tone}_{ts}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w") as f:
        f.write(rewritten)

    return {"success": True, "content": rewritten, "original_length": len(req.text), "new_length": len(rewritten), "saved_to": filepath}


@app.get("/api/history")
async def get_history():
    """List all generated content."""
    return {"success": True, "total": len(content_history), "items": content_history[:50]}


@app.get("/api/tones")
async def get_tones():
    """List available writing tones."""
    from agent import TONES
    return {"success": True, "tones": TONES}


if __name__ == "__main__":
    print("\n  ✍️  AI Content Writer Agent")
    print(f"  AI: {'configured' if agent.is_configured() else 'NOT configured — add ANTHROPIC_API_KEY to .env'}")
    print(f"  Dashboard: http://localhost:8000\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
