"""
AI Job Search Agent — FastAPI Server
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
import uvicorn
import httpx

load_dotenv()

from agent import JobAgent
from tools import JobTools

# ── Your Profile (EDIT THIS) ─────────────────────────────────────

MY_PROFILE = {
    "name": "Your Name",
    "title": "Software Engineer",
    "location": "Remote",
    "skills": ["Python", "JavaScript", "FastAPI", "React", "SQL", "Docker", "Git"],
    "experience": "3+ years building web applications and APIs. Experience with cloud platforms, CI/CD, and agile teams.",
    "preferences": {
        "roles": ["Backend Developer", "Full Stack Developer", "Software Engineer"],
        "work_type": ["remote", "hybrid"],
        "locations": ["USA", "Europe", "Remote"],
    },
}


def get_profile_text():
    """Convert profile dict to text for AI agent."""
    p = MY_PROFILE
    return (
        f"CANDIDATE PROFILE:\n"
        f"Name: {p['name']}\n"
        f"Title: {p['title']}\n"
        f"Location: {p['location']}\n"
        f"Skills: {', '.join(p['skills'])}\n"
        f"Experience: {p['experience']}\n"
        f"Target Roles: {', '.join(p['preferences']['roles'])}\n"
        f"Work Type: {', '.join(p['preferences']['work_type'])}\n"
        f"Locations: {', '.join(p['preferences']['locations'])}\n"
    )


# ── Output directory ──────────────────────────────────────────────

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "JobAgent-Outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "cover_letters"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "job_matches"), exist_ok=True)


# ── Pydantic Models ──────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = "python developer"
    source: str = "all"
    limit: int = 15

class CoverLetterRequest(BaseModel):
    company: str
    role: str
    job_description: str = ""

class HuntRequest(BaseModel):
    query: str = "python developer"
    limit: int = 10
    write_cover_letters: int = 3


# ── App Setup ─────────────────────────────────────────────────────

app = FastAPI(title="AI Job Search Agent", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

agent = JobAgent()
tools = JobTools()


# ── Routes ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard UI."""
    with open("index.html", "r") as f:
        return f.read()


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "ai_configured": agent.is_configured(),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/profile")
async def get_profile():
    return {"success": True, "profile": MY_PROFILE}


@app.put("/api/profile")
async def update_profile(updates: dict):
    MY_PROFILE.update(updates)
    return {"success": True, "profile": MY_PROFILE}


@app.post("/api/search")
async def search_jobs(req: SearchRequest):
    """Search jobs from all sources."""
    if req.source == "remotive":
        result = await tools.search_remotive(query=req.query, limit=req.limit)
    elif req.source == "arbeitnow":
        result = await tools.search_arbeitnow(query=req.query)
    else:
        result = await tools.search_all(query=req.query, limit=req.limit)

    # Save results
    if result.get("success"):
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filepath = os.path.join(OUTPUT_DIR, "job_matches", f"jobs_{ts}.json")
        with open(filepath, "w") as f:
            json.dump(result, f, indent=2)

    return result


@app.post("/api/cover-letter")
async def generate_cover_letter(req: CoverLetterRequest):
    """Generate a tailored cover letter using Claude AI."""
    letter = await agent.write_cover_letter(
        company=req.company,
        role=req.role,
        job_description=req.job_description,
        profile_text=get_profile_text(),
    )

    # Save to file
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    safe_co = "".join(c for c in req.company if c.isalnum() or c in " -_").strip().replace(" ", "_")
    filepath = os.path.join(OUTPUT_DIR, "cover_letters", f"cover_{safe_co}_{ts}.md")
    with open(filepath, "w") as f:
        f.write(f"# Cover Letter — {req.company}\n**Role:** {req.role}\n**Generated:** {datetime.now().strftime('%B %d, %Y')}\n\n---\n\n{letter}\n")

    return {"success": True, "company": req.company, "role": req.role, "letter": letter, "saved_to": filepath}


@app.post("/api/hunt")
async def full_hunt(req: HuntRequest):
    """Full pipeline: search → score → cover letters → notify."""
    # 1. Search
    results = await tools.search_all(query=req.query, limit=req.limit)
    if not results.get("success"):
        return {"success": False, "error": "No jobs found", "results": results}

    jobs = results["jobs"]
    jobs_text = tools.format_for_agent(results)
    profile_text = get_profile_text()

    # 2. Score with AI
    scores = await agent.score_jobs(jobs_text, profile_text)

    # 3. Generate cover letters for top jobs
    cover_letters = []
    for job in jobs[:req.write_cover_letters]:
        letter = await agent.write_cover_letter(
            company=job["company"],
            role=job["title"],
            job_description=job.get("description", ""),
            profile_text=profile_text,
        )
        cover_letters.append({"company": job["company"], "role": job["title"], "letter": letter})

    # 4. Telegram notification (if configured)
    telegram_sent = await _send_telegram(
        f"🎯 <b>Job Hunt Complete</b>\n"
        f"Query: {req.query}\n"
        f"Found: {len(jobs)} jobs\n"
        f"Cover letters: {len(cover_letters)}\n\n"
        f"Top matches:\n" +
        "\n".join(f"• {j['title']} at {j['company']}" for j in jobs[:5])
    )

    return {
        "success": True,
        "total_found": len(jobs),
        "scores": scores,
        "cover_letters": cover_letters,
        "telegram_sent": telegram_sent,
    }


async def _send_telegram(message):
    """Send Telegram notification (optional)."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not bot_token or not chat_id:
        return False
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            )
            return resp.status_code == 200
    except Exception:
        return False


if __name__ == "__main__":
    print("\n  🎯 AI Job Search Agent")
    print(f"  AI: {'configured' if agent.is_configured() else 'NOT configured — add ANTHROPIC_API_KEY to .env'}")
    print(f"  Dashboard: http://localhost:8000\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
