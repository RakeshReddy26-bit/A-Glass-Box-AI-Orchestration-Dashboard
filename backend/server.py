"""
Glass Box AI Dashboard — Backend Server
FastAPI app with REST endpoints, WebSocket, and Telegram bot integration.
Run: python server.py
"""

import os
import json
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import httpx

# Load environment variables (override=True so .env takes priority over shell env)
load_dotenv(override=True)

from agents import AgentManager
from scout_tools import ScoutTools
from job_tools import JobTools
from profile_manager import ProfileManager
from github_tools import GitHubTools


# ── Pydantic Models ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    agent: str
    message: str


class DecisionRequest(BaseModel):
    decision: str  # "approved", "paused", "denied"


class ResearchRequest(BaseModel):
    query: str
    tool: str = "news"  # "news", "sec", "stock", "history"
    ticker: str = "AAPL"


class JobSearchRequest(BaseModel):
    query: str = "python developer"
    source: str = "all"  # "all", "remotive", "arbeitnow", "adzuna"
    limit: int = 15


class CoverLetterRequest(BaseModel):
    company: str
    role: str
    job_description: str = ""


class ProfileUpdateRequest(BaseModel):
    updates: dict


class JobHuntRequest(BaseModel):
    query: str = "python developer"
    limit: int = 10
    write_cover_letters: int = 3  # top N jobs to write cover letters for


class GitHubSetupRequest(BaseModel):
    username: str


# ── State ────────────────────────────────────────────────────────

agent_manager = AgentManager()
scout_tools = ScoutTools()
job_tools = JobTools()
profile_mgr = ProfileManager()

# GitHub integration — reads username from profile if set
_gh_username = profile_mgr.get_profile().get("portfolio_links", {}).get("github_username", "")
github_tools = GitHubTools(username=_gh_username)

# In-memory activity feed
activity_feed = []

# In-memory approval queue
approval_queue = [
    {
        "id": "APR-001",
        "agent": "Cipher",
        "agentId": "cipher",
        "title": "Publish risk model with sub-threshold confidence",
        "description": "Cipher completed a Monte Carlo risk model for AAPL with 72% confidence. The publication threshold is 80%.",
        "riskLevel": "high",
        "confidenceScore": 72,
        "impact": "If published with inaccurate projections, client investment decisions could be misinformed.",
        "status": "pending",
    },
    {
        "id": "APR-002",
        "agent": "Scribe",
        "agentId": "scribe",
        "title": "Distribute draft report to client stakeholders",
        "description": "Scribe has completed the AAPL sector overview draft. Sentinel flagged a missing risk disclaimer in section 3.2.",
        "riskLevel": "medium",
        "confidenceScore": 87,
        "impact": "Report distribution to 12 client stakeholders. Once sent, cannot be recalled.",
        "status": "pending",
    },
]

# Decision history
decision_history = []

# Connected WebSocket clients
ws_clients = set()


# ── WebSocket Manager ────────────────────────────────────────────

async def broadcast(event):
    """Broadcast an event to all connected WebSocket clients."""
    global ws_clients
    if not ws_clients:
        return
    message = json.dumps(event)
    disconnected = set()
    for ws in ws_clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)
    ws_clients -= disconnected


def make_event(agent_name, agent_id, text, event_type="status"):
    """Create a timestamped event dict."""
    now = datetime.now()
    evt = {
        "id": f"evt-{now.strftime('%H%M%S')}-{len(activity_feed)}",
        "time": now.strftime("%H:%M:%S"),
        "agent": agent_name,
        "agentId": agent_id,
        "text": text,
        "type": event_type,
    }
    activity_feed.insert(0, evt)
    if len(activity_feed) > 50:
        activity_feed.pop()
    return evt


# ── Telegram Integration ─────────────────────────────────────────

async def send_telegram(message):
    """Send a message to the configured Telegram chat."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    if not bot_token or not chat_id:
        return False
    if bot_token == "PASTE_YOUR_BOT_TOKEN_HERE":
        return False

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                },
            )
            return resp.status_code == 200
    except Exception:
        return False


# ── App Lifespan ──────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    status = "configured" if agent_manager.is_configured() else "no API key"
    print(f"\n  Glass Box Backend")
    print(f"  Claude API: {status}")
    print(f"  Server: http://localhost:8000")
    print(f"  Health: http://localhost:8000/api/health\n")

    # Send Telegram startup notification
    await send_telegram(
        "<b>Glass Box Dashboard</b>\nBackend server started.\n"
        f"Claude API: {status}"
    )

    yield

    # Shutdown
    print("\n  Server shutting down...\n")


# ── FastAPI App ───────────────────────────────────────────────────

app = FastAPI(title="Glass Box AI Dashboard", lifespan=lifespan)

# CORS — allow dashboard to connect from file:// and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ──────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "claude_api": agent_manager.is_configured(),
        "agents": len(agent_manager.agent_states),
        "timestamp": datetime.now().isoformat(),
    }


# ── Agents ────────────────────────────────────────────────────────

@app.get("/api/agents")
async def get_agents():
    return agent_manager.get_all_states()


# ── Activity Feed ─────────────────────────────────────────────────

@app.get("/api/activity")
async def get_activity():
    return activity_feed


# ── Chat with Agent ───────────────────────────────────────────────

@app.post("/api/chat")
async def chat_with_agent(req: ChatRequest):
    agent_id = req.agent.lower()

    if agent_id == "all":
        # Send to all agents
        responses = await agent_manager.chat_all(req.message)

        results = []
        for aid, response in responses.items():
            info = agent_manager.get_agent_info(aid)
            evt = make_event(info["name"], aid, response, "status")
            await broadcast({"type": "activity", "event": evt})
            results.append({
                "agent": info["name"],
                "agentId": aid,
                "response": response,
                "time": evt["time"],
            })

        # Log the directive
        dir_evt = make_event("Nicholas", "nicholas", f"Directive to All Agents: {req.message}", "directive")
        await broadcast({"type": "activity", "event": dir_evt})

        return {"responses": results}

    else:
        # Send to specific agent
        response = await agent_manager.chat(agent_id, req.message)
        info = agent_manager.get_agent_info(agent_id)

        if not info:
            return {"error": f"Unknown agent: {agent_id}"}

        # Log events
        dir_evt = make_event("Nicholas", "nicholas", f"Directive to {info['name']}: {req.message}", "directive")
        resp_evt = make_event(info["name"], agent_id, response, "status")

        await broadcast({"type": "activity", "event": dir_evt})
        await broadcast({"type": "activity", "event": resp_evt})

        return {
            "agent": info["name"],
            "agentId": agent_id,
            "response": response,
            "time": resp_evt["time"],
        }


# ── Approvals ─────────────────────────────────────────────────────

@app.get("/api/approvals")
async def get_approvals():
    pending = [a for a in approval_queue if a["status"] == "pending"]
    return {
        "pending": pending,
        "history": decision_history,
    }


@app.post("/api/approvals/{approval_id}/decide")
async def decide_approval(approval_id: str, req: DecisionRequest):
    # Find the approval
    item = None
    for a in approval_queue:
        if a["id"] == approval_id:
            item = a
            break

    if not item:
        return {"error": f"Approval {approval_id} not found"}

    # Update status
    item["status"] = req.decision
    now = datetime.now()

    decision_record = {
        "id": item["id"],
        "title": item["title"],
        "agent": item["agent"],
        "agentId": item["agentId"],
        "decision": req.decision,
        "time": now.strftime("%H:%M:%S"),
        "decidedBy": "Nicholas",
    }
    decision_history.append(decision_record)

    # Log event
    evt = make_event(
        "Nicholas", "nicholas",
        f"{req.decision.upper()}: {item['title']}",
        "approval" if req.decision != "approved" else "success",
    )
    await broadcast({"type": "activity", "event": evt})
    await broadcast({"type": "decision", "decision": decision_record})

    # Send Telegram notification
    emoji = {"approved": "\u2705", "paused": "\u23f8\ufe0f", "denied": "\u274c"}.get(req.decision, "\u2753")
    await send_telegram(
        f"{emoji} <b>Decision: {req.decision.upper()}</b>\n"
        f"<i>{item['title']}</i>\n"
        f"Agent: {item['agent']}\n"
        f"Risk: {item['riskLevel']}\n"
        f"Time: {now.strftime('%H:%M:%S')}"
    )

    return {"success": True, "decision": decision_record}


# ── Scout Research Tools ──────────────────────────────────────────

@app.post("/api/scout/research")
async def scout_research(req: ResearchRequest):
    if req.tool == "news":
        result = await scout_tools.search_news(req.query)
    elif req.tool == "sec":
        result = await scout_tools.search_sec_filings(req.ticker)
    elif req.tool == "stock":
        result = await scout_tools.get_stock_price(req.ticker)
    elif req.tool == "history":
        result = await scout_tools.get_stock_history(req.ticker)
    else:
        return {"error": f"Unknown tool: {req.tool}"}

    # Log the research event
    evt = make_event(
        "Scout", "scout",
        f"Research query: {req.query or req.ticker} ({req.tool})",
        "data",
    )
    await broadcast({"type": "activity", "event": evt})

    return result


# ── NEXUS (Job Intelligence) Endpoints ────────────────────────────

@app.get("/api/profile")
async def get_profile():
    """Get the current user profile."""
    return profile_mgr.get_profile()


@app.post("/api/profile")
async def update_profile(req: ProfileUpdateRequest):
    """Update user profile fields."""
    updated = profile_mgr.update_profile(req.updates)
    evt = make_event("Atlas", "atlas", "Profile updated by Nicholas", "status")
    await broadcast({"type": "activity", "event": evt})
    return {"success": True, "profile": updated}


@app.post("/api/jobs/search")
async def search_jobs(req: JobSearchRequest):
    """Search for jobs across all configured sources."""
    evt = make_event("Scout", "scout", f"Searching jobs: '{req.query}' via {req.source}", "data")
    await broadcast({"type": "activity", "event": evt})

    if req.source == "remotive":
        result = await job_tools.search_remotive(query=req.query, limit=req.limit)
    elif req.source == "arbeitnow":
        result = await job_tools.search_arbeitnow(query=req.query)
    elif req.source == "adzuna":
        result = await job_tools.search_adzuna(query=req.query)
    else:
        result = await job_tools.search_all(query=req.query, limit=req.limit)

    # Save results to Desktop
    if result.get("success") and result.get("jobs"):
        filepath = profile_mgr.save_job_matches(result["jobs"], query=req.query)
        result["saved_to"] = filepath

    evt2 = make_event("Scout", "scout", f"Found {result.get('total', 0)} jobs for '{req.query}'", "data")
    await broadcast({"type": "activity", "event": evt2})

    return result


@app.post("/api/jobs/cover-letter")
async def generate_cover_letter(req: CoverLetterRequest):
    """Use Scribe agent to write a tailored cover letter."""
    profile_text = profile_mgr.get_profile_text()

    prompt = (
        f"Write a professional cover letter for this job application.\n\n"
        f"CANDIDATE:\n{profile_text}\n\n"
        f"JOB:\n"
        f"Company: {req.company}\n"
        f"Role: {req.role}\n"
        f"Description: {req.job_description}\n\n"
        f"Write the cover letter now. Be specific to this company and role. "
        f"Keep it 250-400 words. Use a professional but warm tone."
    )

    evt = make_event("Scribe", "scribe", f"Writing cover letter for {req.role} at {req.company}", "status")
    await broadcast({"type": "activity", "event": evt})

    letter = await agent_manager.chat("scribe", prompt, max_tokens=800)

    # Save to Desktop
    filepath = profile_mgr.save_cover_letter(req.company, req.role, letter)

    evt2 = make_event("Scribe", "scribe", f"Cover letter saved: {req.company}", "success")
    await broadcast({"type": "activity", "event": evt2})

    return {
        "success": True,
        "company": req.company,
        "role": req.role,
        "cover_letter": letter,
        "saved_to": filepath,
    }


@app.post("/api/jobs/hunt")
async def full_job_hunt(req: JobHuntRequest):
    """
    Full automated job hunt pipeline:
    1. Scout searches jobs
    2. Cipher scores/ranks them
    3. Scribe writes cover letters for top N
    4. Sentinel reviews everything
    5. Results sent to Telegram + saved to Desktop
    """
    results = {"steps": [], "jobs": [], "cover_letters": [], "sentinel_review": ""}

    # ── Step 1: Scout searches ────────────────────────────────────
    evt = make_event("Atlas", "atlas", f"Job hunt pipeline started: '{req.query}'", "directive")
    await broadcast({"type": "activity", "event": evt})

    search_result = await job_tools.search_all(query=req.query, limit=req.limit)
    results["steps"].append({"agent": "Scout", "status": "done", "found": search_result.get("total", 0)})

    if not search_result.get("success") or not search_result.get("jobs"):
        return {"success": False, "error": "No jobs found", "results": results}

    jobs = search_result["jobs"]
    filepath = profile_mgr.save_job_matches(jobs, query=req.query)
    results["jobs"] = jobs
    results["jobs_saved_to"] = filepath

    evt2 = make_event("Scout", "scout", f"Found {len(jobs)} jobs from {', '.join(search_result.get('sources', []))}", "data")
    await broadcast({"type": "activity", "event": evt2})

    # ── Step 2: Cipher ranks them ─────────────────────────────────
    profile_text = profile_mgr.get_profile_text()
    jobs_text = job_tools.format_for_agent(search_result)

    rank_prompt = (
        f"Score and rank these jobs for the following candidate. "
        f"Give each job a MATCH SCORE from 0-100 and explain why.\n\n"
        f"{profile_text}\n\n"
        f"JOBS:\n{jobs_text}\n\n"
        f"List the top {req.write_cover_letters} jobs with scores and brief reasoning."
    )

    cipher_response = await agent_manager.chat("cipher", rank_prompt)
    results["steps"].append({"agent": "Cipher", "status": "done", "ranking": cipher_response[:200]})

    evt3 = make_event("Cipher", "cipher", f"Ranked {len(jobs)} jobs by match score", "status")
    await broadcast({"type": "activity", "event": evt3})

    # ── Step 3: Scribe writes cover letters for top jobs ──────────
    cover_letters = []
    top_jobs = jobs[:req.write_cover_letters]

    for job in top_jobs:
        letter_prompt = (
            f"Write a professional cover letter for this job application.\n\n"
            f"CANDIDATE:\n{profile_text}\n\n"
            f"JOB:\n"
            f"Title: {job['title']}\n"
            f"Company: {job['company']}\n"
            f"Location: {job['location']}\n"
            f"Description: {job.get('description_snippet', 'Not available')}\n\n"
            f"Write the cover letter now. Be specific. 250-400 words."
        )

        letter = await agent_manager.chat("scribe", letter_prompt, max_tokens=800)
        saved = profile_mgr.save_cover_letter(job["company"], job["title"], letter)

        cover_letters.append({
            "company": job["company"],
            "role": job["title"],
            "letter": letter,
            "saved_to": saved,
        })

        evt_cl = make_event("Scribe", "scribe", f"Cover letter written for {job['company']}", "success")
        await broadcast({"type": "activity", "event": evt_cl})

    results["cover_letters"] = cover_letters
    results["steps"].append({"agent": "Scribe", "status": "done", "letters_written": len(cover_letters)})

    # ── Step 4: Sentinel reviews ──────────────────────────────────
    review_prompt = (
        f"Review these cover letters for quality, accuracy, and professionalism.\n\n"
        f"CANDIDATE PROFILE:\n{profile_text}\n\n"
    )
    for cl in cover_letters:
        review_prompt += f"\n--- COVER LETTER FOR {cl['company']} ({cl['role']}) ---\n{cl['letter']}\n"

    review_prompt += (
        f"\n\nFor each cover letter, give:\n"
        f"1. PASS or NEEDS REVISION\n"
        f"2. Specific issues (if any)\n"
        f"3. Overall quality score (1-10)\n"
    )

    sentinel_review = await agent_manager.chat("sentinel", review_prompt)
    results["sentinel_review"] = sentinel_review
    results["steps"].append({"agent": "Sentinel", "status": "done"})

    evt4 = make_event("Sentinel", "sentinel", f"Reviewed {len(cover_letters)} cover letters", "status")
    await broadcast({"type": "activity", "event": evt4})

    # ── Step 5: Send summary to Telegram ──────────────────────────
    summary = (
        f"📋 <b>Job Hunt Complete</b>\n\n"
        f"🔍 Query: {req.query}\n"
        f"📊 Jobs found: {len(jobs)}\n"
        f"✉️ Cover letters written: {len(cover_letters)}\n\n"
        f"<b>Top matches:</b>\n"
    )
    for i, job in enumerate(top_jobs, 1):
        summary += f"{i}. {job['title']} at {job['company']} ({job['location']})\n"

    summary += f"\n📁 Saved to: Desktop/GlassBox-Outputs/"
    await send_telegram(summary)

    results["steps"].append({"agent": "Atlas", "status": "done", "telegram_sent": True})
    results["success"] = True

    evt5 = make_event("Atlas", "atlas", f"Job hunt complete: {len(jobs)} jobs, {len(cover_letters)} letters", "success")
    await broadcast({"type": "activity", "event": evt5})

    return results


@app.get("/api/jobs/saved")
async def get_saved_jobs():
    """List all saved job matches and cover letters."""
    return {
        "job_files": profile_mgr.list_saved_jobs(),
        "cover_letters": profile_mgr.list_cover_letters(),
        "paths": profile_mgr.get_output_paths(),
    }


@app.post("/api/jobs/daily-digest")
async def daily_digest():
    """
    Run a daily job digest:
    1. Search for jobs matching profile preferences
    2. Send top 5 to Telegram
    3. Save full results to Desktop
    """
    prefs = profile_mgr.get_profile().get("job_preferences", {})
    roles = prefs.get("roles", ["python developer"])

    all_jobs = []
    for role in roles[:3]:  # Search top 3 preferred roles
        result = await job_tools.search_all(query=role, limit=5)
        if result.get("success"):
            all_jobs.extend(result.get("jobs", []))

    # Deduplicate by URL
    seen = set()
    unique_jobs = []
    for j in all_jobs:
        url = j.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique_jobs.append(j)

    # Sort by date
    unique_jobs.sort(key=lambda j: j.get("posted", ""), reverse=True)
    top_jobs = unique_jobs[:10]

    # Save
    filepath = profile_mgr.save_job_matches(top_jobs, query="daily-digest")

    # Send Telegram digest
    now = datetime.now()
    digest = (
        f"📰 <b>Daily Job Digest</b>\n"
        f"📅 {now.strftime('%B %d, %Y')}\n"
        f"🔍 Searched: {', '.join(roles[:3])}\n"
        f"📊 Found: {len(unique_jobs)} unique jobs\n\n"
        f"<b>Top 5 Matches:</b>\n"
    )
    for i, job in enumerate(top_jobs[:5], 1):
        digest += (
            f"\n{i}. <b>{job['title']}</b>\n"
            f"   🏢 {job['company']} | 📍 {job['location']}\n"
            f"   💰 {job['salary']}\n"
        )

    digest += f"\n\n📁 Full list: Desktop/GlassBox-Outputs/\n🤖 Reply to start cover letter pipeline"
    await send_telegram(digest)

    evt = make_event("Atlas", "atlas", f"Daily digest sent: {len(top_jobs)} jobs, {len(roles[:3])} roles", "success")
    await broadcast({"type": "activity", "event": evt})

    return {
        "success": True,
        "total_found": len(unique_jobs),
        "top_jobs": top_jobs,
        "saved_to": filepath,
        "telegram_sent": True,
    }


# ── GitHub Portfolio Endpoints ────────────────────────────────────

@app.post("/api/github/connect")
async def github_connect(req: GitHubSetupRequest):
    """Set GitHub username and fetch profile."""
    github_tools.set_username(req.username)
    profile = await github_tools.get_profile()
    if profile.get("success"):
        # Save username to user profile
        profile_mgr.update_profile({
            "portfolio_links": {
                "github": profile["profile"]["url"],
                "github_username": req.username,
            }
        })
        evt = make_event("Scout", "scout", f"GitHub connected: {req.username} ({profile['profile']['public_repos']} repos)", "success")
        await broadcast({"type": "activity", "event": evt})
    return profile


@app.get("/api/github/profile")
async def github_profile():
    """Get GitHub profile data."""
    return await github_tools.get_profile()


@app.get("/api/github/repos")
async def github_repos():
    """List GitHub repositories."""
    return await github_tools.get_repos(limit=20)


@app.get("/api/github/commits")
async def github_commits(repo: str = ""):
    """Get recent commits. Optional: ?repo=repo_name for specific repo."""
    return await github_tools.get_recent_commits(repo_name=repo, limit=20)


@app.get("/api/github/languages")
async def github_languages():
    """Get language stats across all repos."""
    return await github_tools.get_language_stats()


@app.get("/api/github/activity")
async def github_activity():
    """Get recent activity summary."""
    return await github_tools.get_activity_summary()


@app.post("/api/github/sync-profile")
async def github_sync_profile():
    """Pull GitHub data and auto-update the user profile."""
    update = await github_tools.build_profile_update()
    if not update:
        return {"success": False, "error": "No GitHub data to sync"}

    updated = profile_mgr.update_profile(update)
    evt = make_event("Atlas", "atlas", "Profile synced with GitHub portfolio data", "success")
    await broadcast({"type": "activity", "event": evt})
    return {
        "success": True,
        "synced_fields": list(update.keys()),
        "profile": updated,
    }


# ── WebSocket ─────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.add(ws)
    try:
        # Send current state on connect
        await ws.send_text(json.dumps({
            "type": "connected",
            "agents": agent_manager.get_all_states(),
            "activity": activity_feed[:15],
        }))
        # Keep alive
        while True:
            data = await ws.receive_text()
            # Client can send pings or other messages
            if data == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        ws_clients.discard(ws)
    except Exception:
        ws_clients.discard(ws)


# ── Run Server ────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
