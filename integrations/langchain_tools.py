from langchain.tools import tool
from integrations.skillevector_client import sv
import json
import logging
from integrations.github_pusher import push_code_changes
from integrations.dashboard_updater import update_dashboard_stats
from integrations.code_improver import improve_code_from_feedback

logger = logging.getLogger(__name__)


@tool
async def verify_skillevector_connection(_: str = "") -> str:
    """
    ATLAS uses this first.
    Checks SkillVector API is alive before starting daily pipeline.
    If it returns DOWN, wait 30 minutes and retry before aborting.
    """
    alive = await sv.health_check()
    if alive:
        return "SkillVector is alive and ready. Proceed with daily pipeline."
    else:
        return "SkillVector is DOWN. Do not proceed. Retry in 30 minutes."


@tool
async def push_skill_trends_to_skillevector(trends_json: str) -> str:
    """
    SCOUT uses this after researching trending ML skills via NewsAPI.
    Input must be a JSON array of skill name strings.
    Example input: '["MLOps", "LLMOps", "RAG", "RLHF", "Feature Stores"]'
    """
    try:
        skills = json.loads(trends_json)
        result = await sv.update_trends(trending_skills=skills)
        return f"Scout sent {result['skills_updated']} skill trends to SkillVector. Top: {result['trending']}"
    except Exception as e:
        return f"Trend update failed: {e}"


@tool
async def push_jobs_to_skillevector(jobs_json: str) -> str:
    """
    NEXUS uses this AFTER Sentinel has approved the job list.
    Sends validated jobs to SkillVector Pinecone index.
    Input must be a JSON array. Each job needs:
    title, company, location, apply_url, required_skills (list), description
    """
    try:
        jobs = json.loads(jobs_json)
        result = await sv.ingest_jobs(jobs=jobs, source="nexus_remotive_arbeitnow")
        return f"Nexus sent {result['jobs_indexed']} jobs to SkillVector Pinecone."
    except Exception as e:
        return f"Job ingestion failed: {e}"


@tool
async def get_insight_and_write_content(_: str = "") -> str:
    """
    SCRIBE uses this at 8AM.
    Gets today's SkillVector data and a Claude-generated LinkedIn hook.
    Scribe then writes the full post and passes to Sentinel for review.
    """
    try:
        insight = await sv.get_daily_insight()
        return f"""
SKILLEVECTOR DATA FOR TODAY'S POSTS:

LINKEDIN HOOK (expand into 150-200 word post):
{insight['linkedin_hook']}

TWEET (ready to post, under 280 chars):
{insight['tweet'].replace('[URL]', insight['app_url'])}

RAW STATS:
- Resumes analyzed: {insight['stats']['total_analyses']}
- Top skill gap: {insight['stats']['top_skill_gap']}
- Avg match score: {insight['stats']['avg_match_score']}%
- Trending roles: {', '.join(insight['stats']['trending_roles'])}
- App URL: {insight['app_url']}

INSTRUCTIONS FOR SCRIBE:
1. Expand LinkedIn hook into full 150-200 word post
2. End LinkedIn post with: Try SkillVector free at {insight['app_url']}
3. Send both posts to Sentinel for compliance review before posting
"""
    except Exception as e:
        return f"Could not get insight: {e}. Use fallback: 'Most ML engineers are 2 skills away from their target role. SkillVector shows exactly which ones.'"


@tool
async def update_dashboard(_: str = "") -> str:
    """
    Gets today's SkillVector stats, updates dashboard data,
    and pushes the changed dashboard file to GitHub.
    """
    result = await update_dashboard_stats()
    return f"Dashboard updated: {result['status']}. Stats: {result.get('stats_updated', {})}"


@tool
def improve_skillevector_from_feedback(feedback: str) -> str:
    """
    Reads user feedback, writes a code improvement,
    and pushes it to GitHub.
    """
    result = improve_code_from_feedback(feedback=feedback)
    if result["status"] == "success":
        return f"Improvement pushed: {result['improvement']}. Deployed to Render in ~2 min."
    if result["status"] == "skipped":
        return f"No code change needed: {result['reason']}"
    return f"Improvement failed: {result.get('error')}"


@tool
def push_to_github(message: str = "") -> str:
    """
    Pushes any pending changes to GitHub.
    """
    result = push_code_changes(
        files_changed=["."],
        commit_message=message or "feat: Atlas daily update",
    )
    return f"GitHub push: {result['status']} — {result.get('message', result.get('deployed', ''))}"
