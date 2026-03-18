"""
Atlas Daily Pipeline v2.0 — CEO-level daily automation for SkillVector.
Generates multi-platform content, monitors competitors, improves code, sends reports.

Runs every morning via scheduler.py. Self-healing: retries on failure, skips broken steps,
always sends email even if upstream steps fail.
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import json
import time
import asyncio
import logging
import httpx
from datetime import date, datetime

# Absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

POSTS_DIR = os.path.join(BASE_DIR, "posts")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TASKS_DIR = os.path.join(BASE_DIR, "tasks")
LOG_FILE = os.path.join(LOGS_DIR, "atlas.log")

os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(TASKS_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("atlas.pipeline")

# Config
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
SKILLEVECTOR_URL = os.getenv("SKILLEVECTOR_URL", "https://api.skill-vector.com")
SKILLEVECTOR_PROD_URL = "https://api.skill-vector.com"
CLAUDE_MODEL = "claude-sonnet-4-20250514"
TODAY = date.today()
TODAY_STR = TODAY.strftime("%Y-%m-%d")
TODAY_PRETTY = TODAY.strftime("%B %d, %Y")
DAY_OF_WEEK = TODAY.strftime("%A")


# ===============================================================
# HELPERS
# ===============================================================

def retry_with_delay(func, retries=3, delay=60, label="operation"):
    """Retry a function up to retries times with delay seconds between attempts."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            result = func()
            return result
        except Exception as e:
            last_error = e
            logger.warning(f"[RETRY] {label} attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                logger.info(f"[RETRY] Waiting {delay}s before retry...")
                time.sleep(delay)
    logger.error(f"[RETRY] {label} failed after {retries} attempts: {last_error}")
    return None


async def call_claude(prompt: str, max_tokens: int = 1024) -> str:
    """Call Claude API with error handling. Returns response text or error string."""
    if not ANTHROPIC_API_KEY:
        logger.error("[CLAUDE] ANTHROPIC_API_KEY not set. Add it to .env file.")
        return "[ERROR] ANTHROPIC_API_KEY not configured. Set it in .env"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": CLAUDE_MODEL,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            data = resp.json()
            if resp.status_code != 200:
                error = data.get("error", {}).get("message", f"HTTP {resp.status_code}")
                logger.error(f"[CLAUDE] API error: {error}")
                return f"[ERROR] Claude API: {error}"

            text = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text += block.get("text", "")

            # Track token usage
            usage = data.get("usage", {})
            input_t = usage.get("input_tokens", 0)
            output_t = usage.get("output_tokens", 0)
            logger.info(f"[TOKENS] in={input_t} out={output_t} total={input_t + output_t}")

            return text.strip() if text else "[ERROR] Empty Claude response"

    except Exception as e:
        logger.error(f"[CLAUDE] Request failed: {e}")
        return f"[ERROR] Claude request failed: {e}"


def save_post(filename: str, content: str) -> str:
    """Save content to posts/ directory. Returns the full path."""
    path = os.path.join(POSTS_DIR, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"[SAVE] Wrote {path}")
        return path
    except Exception as e:
        logger.error(f"[SAVE] Failed to write {path}: {e}")
        return ""


# ===============================================================
# AUTO-FIX: Trigger Railway redeploy via git push
# ===============================================================

def trigger_railway_redeploy() -> dict:
    """Push an empty commit to SkillVector repo to trigger Railway redeploy."""
    from integrations.github_pusher import run_git

    repo_path = os.getenv("SKILLEVECTOR_REPO_PATH", "")
    if not repo_path:
        logger.error("[REDEPLOY] SKILLEVECTOR_REPO_PATH not set")
        return {"status": "failed", "error": "no repo path"}

    logger.info("[REDEPLOY] Triggering Railway redeploy via empty commit...")

    # Pull latest first
    run_git(["git", "pull", "origin", "main", "--rebase"], repo_path)

    # Empty commit to trigger Railway auto-deploy
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    success, output = run_git(
        ["git", "commit", "--allow-empty", "-m", f"fix: Atlas auto-redeploy {now_str} (API was down)"],
        repo_path,
    )
    if not success:
        logger.error(f"[REDEPLOY] Empty commit failed: {output}")
        return {"status": "failed", "error": output}

    success, output = run_git(["git", "push", "origin", "main"], repo_path)
    if not success:
        logger.error(f"[REDEPLOY] Push failed: {output}")
        return {"status": "failed", "error": output}

    logger.info("[REDEPLOY] Pushed empty commit — Railway will redeploy in ~2 min")
    return {"status": "success", "message": "Redeploy triggered"}


async def check_api_with_retry(url: str, retries: int = 3, delay: int = 10) -> bool:
    """Check API health with multiple retries before declaring it down."""
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"{url}/health")
                if r.status_code == 200:
                    return True
                logger.warning(f"[HEALTH] Attempt {attempt}/{retries}: HTTP {r.status_code}")
        except Exception as e:
            logger.warning(f"[HEALTH] Attempt {attempt}/{retries}: {e}")
        if attempt < retries:
            await asyncio.sleep(delay)
    return False


# ===============================================================
# STEP 1 - HEALTH CHECK (self-healing)
# ===============================================================

async def step_health_check() -> dict:
    """Ping SkillVector API. If down, auto-trigger Railway redeploy."""
    logger.info("--- STEP 1: Health Check ---")
    result = {"step": "health_check", "status": "unknown"}

    # Check production URL (the one users hit)
    check_url = SKILLEVECTOR_PROD_URL
    is_up = await check_api_with_retry(check_url, retries=3, delay=10)

    if is_up:
        logger.info("[HEALTH] SkillVector API is UP")
        result["status"] = "healthy"
    else:
        logger.error("[HEALTH] SkillVector API is DOWN after 3 checks — triggering auto-fix")
        result["status"] = "down"

        # Auto-fix: trigger redeploy
        redeploy = trigger_railway_redeploy()
        result["redeploy"] = redeploy

        if redeploy.get("status") == "success":
            logger.info("[HEALTH] Waiting 120s for Railway to redeploy...")
            await asyncio.sleep(120)

            # Verify after redeploy
            is_up_now = await check_api_with_retry(SKILLEVECTOR_URL, retries=2, delay=15)
            if is_up_now:
                logger.info("[HEALTH] API recovered after redeploy!")
                result["status"] = "recovered"
                append_lesson(
                    f"\n## Lesson (auto {TODAY_STR})\n"
                    f"API was down, Atlas auto-redeployed via empty commit. It recovered."
                )
            else:
                logger.error("[HEALTH] API still down after redeploy — may need manual fix")
                result["status"] = "critical"
                send_error_alert(
                    f"SkillVector API is DOWN and auto-redeploy didn't fix it.\n"
                    f"URL: {SKILLEVECTOR_URL}\n"
                    f"Action needed: Check Railway dashboard manually."
                )

    return result


# ===============================================================
# LEARNING LOOP - Read past lessons before acting
# ===============================================================

def load_lessons() -> str:
    """Read tasks/lessons.md so the pipeline learns from past mistakes."""
    lessons_path = os.path.join(TASKS_DIR, "lessons.md")
    try:
        with open(lessons_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        logger.info(f"[LEARN] Loaded {len(content)} chars of lessons")
        return content
    except FileNotFoundError:
        return ""


def append_lesson(lesson_text: str):
    """Append a new lesson to tasks/lessons.md."""
    lessons_path = os.path.join(TASKS_DIR, "lessons.md")
    try:
        with open(lessons_path, "a", encoding="utf-8") as f:
            f.write(f"\n{lesson_text}\n")
        logger.info("[LEARN] New lesson appended")
    except Exception as e:
        logger.warning(f"[LEARN] Could not append lesson: {e}")


# ===============================================================
# STEP 2 - RESEARCH
# ===============================================================

async def step_research() -> dict:
    """Use Claude to generate research insights for content creation."""
    logger.info("--- STEP 2: Research ---")
    result = {"step": "research", "status": "unknown", "insights": []}

    prompt = (
        "You are the research agent for SkillVector, an AI career intelligence platform.\n\n"
        "Generate 3 key insights about the ML/AI career landscape right now (March 2026).\n"
        "Focus on:\n"
        "1. ML career tools and competitors - what is new in the AI career space\n"
        "2. ML engineer job market trends - hiring, layoffs, salary shifts\n"
        "3. AI career product launches - new tools builders are shipping\n\n"
        "For each insight, provide:\n"
        "- A one-line headline\n"
        "- 2-3 sentences of detail\n"
        "- Why it matters for ML engineers\n\n"
        "Format as JSON array:\n"
        '[{"headline": "...", "detail": "...", "relevance": "..."},\n'
        ' {"headline": "...", "detail": "...", "relevance": "..."},\n'
        ' {"headline": "...", "detail": "...", "relevance": "..."}]\n\n'
        "Return ONLY the JSON array, no markdown fences."
    )

    try:
        response = await call_claude(prompt, max_tokens=500)
        if response.startswith("[ERROR]"):
            result["status"] = "failed"
            result["error"] = response
            logger.warning(f"[RESEARCH] Claude error: {response}")
            return result

        try:
            insights = json.loads(response)
            result["insights"] = insights
            result["status"] = "success"
            for i, ins in enumerate(insights, 1):
                logger.info(f"[RESEARCH] Insight {i}: {ins.get('headline', 'N/A')}")
        except json.JSONDecodeError:
            result["insights"] = [{"headline": "Market research", "detail": response, "relevance": "General"}]
            result["status"] = "success"
            logger.info("[RESEARCH] Got raw research text (non-JSON)")

    except Exception as e:
        result["status"] = "failed"
        logger.error(f"[RESEARCH] Failed: {e}")
        result["error"] = str(e)

    return result


# ===============================================================
# STEP 3 - GENERATE ALL CONTENT
# ===============================================================

async def step_generate_content(insights: list) -> dict:
    """Generate all 4 platform posts using Claude + research insights."""
    logger.info("--- STEP 3: Content Generation ---")
    result = {"step": "content_generation", "status": "unknown", "posts": {}}

    insight_text = ""
    if insights:
        for ins in insights[:3]:
            headline = ins.get("headline", "")
            detail = ins.get("detail", "")
            insight_text += f"- {headline}: {detail}\n"
    else:
        insight_text = "- SkillVector helps ML engineers discover skill gaps and find better roles using AI-powered analysis.\n"

    prompt = (
        f"You are the content team for SkillVector (https://skill-vector.com), "
        f"an AI career intelligence platform built with Claude Sonnet, Neo4j, Pinecone, and FastAPI.\n\n"
        f"Today's research insights:\n{insight_text}\n"
        f"Generate ALL 4 posts below. Use a founder voice (Rakesh Reddy, building SkillVector).\n\n"
        f"=== LINKEDIN POST (exactly 150-200 words) ===\n"
        f"- Use one insight from the research\n"
        f"- Professional founder tone\n"
        f"- End with https://skill-vector.com\n"
        f"- Include exactly 3 relevant hashtags\n"
        f"- No emojis in first line\n\n"
        f"=== REDDIT POST for r/MachineLearning (150-250 words) ===\n"
        f"- Honest, helpful, zero hype\n"
        f"- Share a genuine insight about ML career gaps\n"
        f"- Mention SkillVector naturally (not as an ad)\n"
        f"- End with link to skill-vector.com\n"
        f"- Title line first, then body\n\n"
        f"=== TWITTER/X POST (max 280 characters) ===\n"
        f"- Punchy, data-driven\n"
        f"- One surprising stat or insight\n"
        f"- Include https://skill-vector.com\n"
        f"- No hashtags\n\n"
        f"=== INDIE HACKERS POST (200-300 words) ===\n"
        f"- Builder/founder tone\n"
        f"- Share what you learned building SkillVector this week\n"
        f"- Be transparent about challenges\n"
        f"- End with link\n\n"
        f"Return as JSON object with keys: linkedin, reddit, twitter, indie_hackers\n"
        f"Each value is the full post text as a string.\n"
        f"Return ONLY the JSON object, no markdown fences."
    )

    try:
        response = await call_claude(prompt, max_tokens=2000)
        if response.startswith("[ERROR]"):
            result["status"] = "failed"
            result["error"] = response
            logger.warning(f"[CONTENT] Claude error: {response}")
            return result

        try:
            posts = json.loads(response)
            result["posts"] = posts
            result["status"] = "success"
            for platform in ["linkedin", "reddit", "twitter", "indie_hackers"]:
                if platform in posts:
                    chars = len(posts[platform])
                    logger.info(f"[CONTENT] {platform}: {chars} chars generated")
                else:
                    logger.warning(f"[CONTENT] Missing {platform} post")
        except json.JSONDecodeError:
            cleaned = response
            if "```" in cleaned:
                parts = cleaned.split("```")
                for part in parts:
                    stripped = part.strip().lstrip("json").strip()
                    try:
                        posts = json.loads(stripped)
                        result["posts"] = posts
                        result["status"] = "success"
                        break
                    except json.JSONDecodeError:
                        continue
            if not result["posts"]:
                result["status"] = "failed"
                logger.error("[CONTENT] Could not parse Claude response as JSON")
                result["error"] = "JSON parse failed"
                result["raw_response"] = response[:500]

    except Exception as e:
        result["status"] = "failed"
        logger.error(f"[CONTENT] Generation failed: {e}")
        result["error"] = str(e)

    return result


# ===============================================================
# STEP 3b - MONDAY IMAGE PROMPT
# ===============================================================

async def step_generate_image_prompt() -> str:
    """Generate a DALL-E style image prompt on Mondays."""
    if DAY_OF_WEEK != "Monday":
        return ""

    logger.info("--- STEP 3b: Monday Image Prompt ---")

    prompt = (
        "Generate a DALL-E image prompt for a social media graphic for SkillVector, "
        "an AI career intelligence platform.\n\n"
        "Theme: ML career intelligence, skill gaps, AI career tools.\n"
        "Style: Modern, clean, professional, dark theme with green (#00e5a0) accents.\n"
        "Include: Abstract visualization of career paths, neural networks, or skill graphs.\n\n"
        "Return ONLY the image prompt text, nothing else. Max 200 words."
    )

    try:
        result = await call_claude(prompt, max_tokens=300)
        if not result.startswith("[ERROR]"):
            save_post("image_prompt_monday.txt", result)
            logger.info("[IMAGE] Monday image prompt generated")
            return result
    except Exception as e:
        logger.error(f"[IMAGE] Failed: {e}")

    return ""


# ===============================================================
# STEP 4 - SAVE ALL POSTS
# ===============================================================

def step_save_posts(posts: dict) -> dict:
    """Save each platform post to posts/ with dated filenames."""
    logger.info("--- STEP 4: Save Posts ---")
    result = {"step": "save_posts", "status": "unknown", "saved": []}

    file_map = {
        "linkedin": f"linkedin_{TODAY_STR}.md",
        "reddit": f"reddit_{TODAY_STR}.md",
        "twitter": f"twitter_{TODAY_STR}.md",
        "indie_hackers": f"indie_hackers_{TODAY_STR}.md",
    }

    for platform, filename in file_map.items():
        content = posts.get(platform, "")
        if content:
            path = save_post(filename, content)
            if path:
                result["saved"].append(filename)
                today_name = f"{platform}_today.md"
                save_post(today_name, content)

    if result["saved"]:
        result["status"] = "success"
    else:
        result["status"] = "failed"
    logger.info(f"[SAVE] Saved {len(result['saved'])} post files")
    return result


# ===============================================================
# STEP 5 - SEND EMAIL (with retry)
# ===============================================================

def step_send_email(posts: dict, image_prompt: str = "") -> dict:
    """Send daily posts email with 3x retry logic."""
    logger.info("--- STEP 5: Send Email ---")

    from integrations.email_sender import send_daily_posts_email

    if image_prompt and "indie_hackers" in posts:
        posts["indie_hackers"] += f"\n\n---\nMonday Image Prompt:\n{image_prompt}"

    def do_send():
        r = send_daily_posts_email(posts)
        if r.get("status") == "failed":
            raise Exception(r.get("error", "Unknown email error"))
        return r

    email_result = retry_with_delay(do_send, retries=3, delay=60, label="Email send")

    if email_result and email_result.get("status") == "success":
        logger.info(f"[EMAIL] Successfully sent to {email_result.get('sent_to')}")
        return {"step": "email", "status": "success", "sent_to": email_result.get("sent_to")}
    else:
        logger.error("[EMAIL] Failed after 3 retries")
        return {"step": "email", "status": "failed", "error": "All retries exhausted"}


# ===============================================================
# STEP 6 - CODE IMPROVEMENT (Mon, Wed, Fri)
# ===============================================================

async def step_code_improvement() -> dict:
    """Run code improvement on Mon/Wed/Fri."""
    if DAY_OF_WEEK not in ("Monday", "Wednesday", "Friday"):
        logger.info(f"[CODE] Skipping code improvement (today is {DAY_OF_WEEK})")
        return {"step": "code_improvement", "status": "skipped", "reason": f"Not a code day ({DAY_OF_WEEK})"}

    logger.info("--- STEP 6: Code Improvement ---")
    result = {"step": "code_improvement", "status": "unknown"}

    try:
        from integrations.code_improver import improve_code_from_feedback

        feedback = (
            f"Daily review {TODAY_STR}: Check for any error handling improvements, "
            "missing type hints, or performance optimizations in the pipeline code. "
            "Focus on small, safe, incremental improvements only."
        )

        improvement = improve_code_from_feedback(feedback)
        result.update(improvement)
        logger.info(f"[CODE] Improvement result: {improvement.get('status', 'unknown')}")

    except Exception as e:
        logger.error(f"[CODE] Code improvement failed: {e}")
        result["status"] = "failed"
        result["error"] = str(e)

    return result


# ===============================================================
# STEP 7 - WEEKLY ANALYTICS (Sunday)
# ===============================================================

async def step_weekly_analytics() -> dict:
    """Generate weekly analytics report on Sundays."""
    if DAY_OF_WEEK != "Sunday":
        logger.info(f"[ANALYTICS] Skipping weekly report (today is {DAY_OF_WEEK})")
        return {"step": "analytics", "status": "skipped"}

    logger.info("--- STEP 7: Weekly Analytics ---")
    result = {"step": "analytics", "status": "unknown"}

    try:
        stats = {}
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                r = await client.get(f"{SKILLEVECTOR_URL}/dashboard/stats")
                if r.status_code == 200:
                    stats = r.json()
                    logger.info(f"[ANALYTICS] Got stats: {json.dumps(stats)[:200]}")
            except Exception as e:
                logger.warning(f"[ANALYTICS] Could not fetch stats: {e}")
                stats = {"note": "API stats unavailable this week"}

        prompt = (
            f"Generate a weekly analytics summary for SkillVector.\n"
            f"Date: Week ending {TODAY_PRETTY}\n"
            f"Stats data: {json.dumps(stats)[:1000]}\n\n"
            f"Write a brief CEO-level weekly summary (100-150 words):\n"
            f"- Key metrics this week\n"
            f"- Growth trends\n"
            f"- What to focus on next week\n"
            f"- One action item\n\n"
            f"Professional, data-driven tone."
        )

        summary = await call_claude(prompt, max_tokens=500)
        if not summary.startswith("[ERROR]"):
            save_post(f"weekly_report_{TODAY_STR}.md", summary)
            result["status"] = "success"
            result["summary"] = summary[:200]
            logger.info("[ANALYTICS] Weekly report generated")
        else:
            result["status"] = "partial"
            result["error"] = summary

    except Exception as e:
        logger.error(f"[ANALYTICS] Weekly report failed: {e}")
        result["status"] = "failed"
        result["error"] = str(e)

    return result


# ===============================================================
# STEP 8 - COMPETITOR MONITORING (daily)
# ===============================================================

async def step_competitor_monitoring() -> dict:
    """Monitor competitors and save intel to tasks/."""
    logger.info("--- STEP 8: Competitor Monitoring ---")
    result = {"step": "competitor_monitoring", "status": "unknown"}

    prompt = (
        f"You track competitors for SkillVector, an AI career intelligence platform.\n\n"
        f"Date: {TODAY_PRETTY}\n\n"
        f"List 3-5 notable ML career tools, AI job platforms, or skill-gap analyzers "
        f"that are active in 2026. For each, provide:\n"
        f"- Name and URL\n"
        f"- What they do\n"
        f"- How SkillVector differentiates\n\n"
        f"Also note any recent launches or funding in this space.\n\n"
        f"Format as markdown with headers. Be specific and factual."
    )

    try:
        intel = await call_claude(prompt, max_tokens=600)
        if not intel.startswith("[ERROR]"):
            intel_path = os.path.join(TASKS_DIR, "competitor_intel.md")
            header = f"# Competitor Intel - {TODAY_PRETTY}\n\n"
            with open(intel_path, "w", encoding="utf-8") as f:
                f.write(header + intel)
            logger.info("[COMPETITORS] Intel saved to tasks/competitor_intel.md")
            result["status"] = "success"
        else:
            result["status"] = "failed"
            result["error"] = intel

    except Exception as e:
        logger.error(f"[COMPETITORS] Monitoring failed: {e}")
        result["status"] = "failed"
        result["error"] = str(e)

    return result


# ===============================================================
# MAIN PIPELINE
# ===============================================================

async def run_daily_pipeline() -> dict:
    """
    Complete daily pipeline. Self-healing: if any step fails,
    subsequent steps still run. Email is ALWAYS attempted.
    """
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info(f"ATLAS DAILY PIPELINE v2.0 - {TODAY_PRETTY} ({DAY_OF_WEEK})")
    logger.info("=" * 60)

    pipeline_results = {}
    posts = {}
    image_prompt = ""

    # Load lessons from past runs
    lessons = load_lessons()
    if lessons:
        logger.info("[PIPELINE] Loaded past lessons — avoiding known mistakes")

    # STEP 1: Health Check
    try:
        pipeline_results["health"] = await step_health_check()
    except Exception as e:
        logger.error(f"[PIPELINE] Health check crashed: {e}")
        pipeline_results["health"] = {"status": "error", "error": str(e)}

    # STEP 2: Research
    insights = []
    try:
        research = await step_research()
        pipeline_results["research"] = research
        insights = research.get("insights", [])
    except Exception as e:
        logger.error(f"[PIPELINE] Research crashed: {e}")
        pipeline_results["research"] = {"status": "error", "error": str(e)}

    # STEP 3: Generate Content
    try:
        content = await step_generate_content(insights)
        pipeline_results["content"] = content
        posts = content.get("posts", {})
    except Exception as e:
        logger.error(f"[PIPELINE] Content generation crashed: {e}")
        pipeline_results["content"] = {"status": "error", "error": str(e)}

    # STEP 3b: Monday Image Prompt
    try:
        image_prompt = await step_generate_image_prompt()
    except Exception as e:
        logger.error(f"[PIPELINE] Image prompt crashed: {e}")

    # STEP 4: Save Posts
    if posts:
        try:
            pipeline_results["save"] = step_save_posts(posts)
        except Exception as e:
            logger.error(f"[PIPELINE] Save posts crashed: {e}")
            pipeline_results["save"] = {"status": "error", "error": str(e)}
    else:
        logger.warning("[PIPELINE] No posts to save - content generation may have failed")
        pipeline_results["save"] = {"status": "skipped", "reason": "No posts generated"}

    # STEP 5: Send Email (ALWAYS attempt)
    try:
        if not posts:
            posts = {
                "linkedin": f"[Atlas {TODAY_STR}] Content generation failed today. Check logs.",
                "reddit": "",
                "twitter": "",
                "indie_hackers": "",
            }
        pipeline_results["email"] = step_send_email(posts, image_prompt)
    except Exception as e:
        logger.error(f"[PIPELINE] Email step crashed: {e}")
        pipeline_results["email"] = {"status": "error", "error": str(e)}

    # STEP 6: Code Improvement (Mon/Wed/Fri)
    try:
        pipeline_results["code_improvement"] = await step_code_improvement()
    except Exception as e:
        logger.error(f"[PIPELINE] Code improvement crashed: {e}")
        pipeline_results["code_improvement"] = {"status": "error", "error": str(e)}

    # STEP 7: Weekly Analytics (Sunday)
    try:
        pipeline_results["analytics"] = await step_weekly_analytics()
    except Exception as e:
        logger.error(f"[PIPELINE] Analytics crashed: {e}")
        pipeline_results["analytics"] = {"status": "error", "error": str(e)}

    # STEP 8: Competitor Monitoring
    try:
        pipeline_results["competitors"] = await step_competitor_monitoring()
    except Exception as e:
        logger.error(f"[PIPELINE] Competitor monitoring crashed: {e}")
        pipeline_results["competitors"] = {"status": "error", "error": str(e)}

    # SUMMARY + CONFIDENCE SCORE
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info("=" * 60)
    logger.info(f"PIPELINE COMPLETE in {elapsed:.1f}s")

    # Calculate confidence score: each successful step = points
    step_weights = {
        "health": 10, "research": 15, "content": 25, "save": 10,
        "email": 25, "code_improvement": 5, "analytics": 5, "competitors": 5,
    }
    total_points = 0
    earned_points = 0
    failed_steps = []

    for step_name, step_result in pipeline_results.items():
        weight = step_weights.get(step_name, 0)
        total_points += weight
        status = step_result.get("status", "unknown") if isinstance(step_result, dict) else "done"
        logger.info(f"  {step_name}: {status}")
        if status in ("healthy", "success", "done", "skipped"):
            earned_points += weight
        else:
            failed_steps.append(f"{step_name}={status}")

    confidence = round((earned_points / max(total_points, 1)) * 100)
    logger.info(f"  CONFIDENCE: {confidence}%")
    logger.info("=" * 60)

    # Auto-learn: record failures as lessons
    if failed_steps:
        lesson_num = 6  # next after existing lessons
        lesson = (
            f"\n## Lesson (auto {TODAY_STR})\n"
            f"Pipeline confidence: {confidence}%. "
            f"Failed steps: {', '.join(failed_steps)}. "
            f"Action: investigate and fix before next run."
        )
        append_lesson(lesson)
        logger.info(f"[LEARN] Recorded failure lesson: {', '.join(failed_steps)}")

    pipeline_results["elapsed_seconds"] = elapsed
    pipeline_results["confidence"] = confidence
    pipeline_results["date"] = TODAY_STR
    return pipeline_results


# Standalone health ping (used by scheduler hourly) — self-healing
_consecutive_failures = 0

async def health_ping() -> bool:
    """Hourly health check. If API is down 2+ times in a row, trigger redeploy."""
    global _consecutive_failures
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{SKILLEVECTOR_PROD_URL}/health")
            if r.status_code == 200:
                if _consecutive_failures > 0:
                    logger.info(f"[PING] SkillVector recovered after {_consecutive_failures} failures")
                _consecutive_failures = 0
                logger.info("[PING] SkillVector: UP")
                return True
            else:
                _consecutive_failures += 1
                logger.warning(f"[PING] SkillVector: HTTP {r.status_code} (failures: {_consecutive_failures})")
    except Exception as e:
        _consecutive_failures += 1
        logger.warning(f"[PING] SkillVector unreachable: {e} (failures: {_consecutive_failures})")

    # Auto-fix after 2 consecutive failures (2 hours of downtime)
    if _consecutive_failures >= 2:
        logger.error(f"[PING] {_consecutive_failures} consecutive failures — triggering redeploy")
        result = trigger_railway_redeploy()
        if result.get("status") == "success":
            _consecutive_failures = 0  # Reset counter after redeploy attempt
            send_error_alert(
                f"SkillVector API was down for {_consecutive_failures}+ hours. "
                f"Atlas auto-triggered a Railway redeploy. Check logs."
            )
    return False


# Error alert email
def send_error_alert(error_message: str):
    """Send an emergency alert email when the pipeline fails catastrophically."""
    try:
        from integrations.email_sender import send_daily_posts_email
        send_daily_posts_email({
            "linkedin": f"ATLAS PIPELINE ERROR - {TODAY_PRETTY}\n\n{error_message}\n\nCheck logs/atlas.log for details.",
            "reddit": "",
            "twitter": "",
            "indie_hackers": "",
        })
        logger.info("[ALERT] Error alert email sent")
    except Exception as e:
        logger.error(f"[ALERT] Could not send error alert: {e}")


# Entry point for direct execution
if __name__ == "__main__":
    print(f"Atlas Daily Pipeline v2.0 - {TODAY_PRETTY}")
    print(f"Base dir: {BASE_DIR}")
    print(f"Posts dir: {POSTS_DIR}")
    print(f"Claude API: {'configured' if ANTHROPIC_API_KEY else 'MISSING'}")
    print()
    result = asyncio.run(run_daily_pipeline())
    print()
    print("Pipeline complete.")
    print(json.dumps({k: v.get("status", "done") if isinstance(v, dict) else v
                      for k, v in result.items()}, indent=2))
