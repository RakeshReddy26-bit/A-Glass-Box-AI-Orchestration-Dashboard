import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def run_pipeline(atlas, scout, nexus, cipher, scribe, sentinel):
    """
    Master daily pipeline. Atlas calls this every morning at 6AM.
    All 6 agents work in sequence. Zero human input needed.
    """

    def log(msg):
        logger.info(f"[{datetime.now().strftime('%H:%M')}] {msg}")

    log("=== ATLAS DAILY PIPELINE STARTED ===")

    # STEP 1 — Atlas checks SkillVector is alive
    log("Step 1: Atlas checking SkillVector connection...")
    health = await atlas.arun("Call verify_skillevector_connection")
    if "DOWN" in health:
        log("SkillVector down. Waiting 30 minutes...")
        await asyncio.sleep(1800)
        health = await atlas.arun("Call verify_skillevector_connection")
        if "DOWN" in health:
            log("Still down. Aborting pipeline.")
            return

    # STEP 2 — Scout researches trending ML skills
    log("Step 2: Scout researching trending skills via NewsAPI...")
    await scout.arun(
        "Search NewsAPI for the top 10 trending ML engineering skills "
        "mentioned in job postings this week at companies like Stripe, "
        "Google, Anthropic, OpenAI. Return as JSON array of skill strings. "
        "Then call push_skill_trends_to_skillevector with your findings."
    )

    # STEP 3 — Nexus scrapes new jobs
    log("Step 3: Nexus scraping Remotive + Arbeitnow...")
    raw_jobs = await nexus.arun(
        "Search Remotive and Arbeitnow for ML engineering jobs posted "
        "in the last 48 hours. Find 20 jobs. For each collect: "
        "title, company, location, apply_url, required_skills (list), "
        "description (first 300 chars), salary if shown. "
        "Return as JSON array. Do NOT call push_jobs_to_skillevector yet."
    )

    # STEP 4 — Cipher scores job quality
    log("Step 4: Cipher scoring job quality...")
    ranked_jobs = await cipher.arun(
        f"Score each job listing 0-100 for quality and legitimacy: {raw_jobs}. "
        "Remove anything scoring below 60. "
        "Return filtered list as JSON array."
    )

    # STEP 5 — Sentinel validates compliance
    log("Step 5: Sentinel validating jobs...")
    approved_jobs = await sentinel.arun(
        f"Review these job listings for compliance: {ranked_jobs}. "
        "Remove any scams, duplicates, or suspicious URLs. "
        "Return only approved jobs as JSON array."
    )

    # STEP 6 — Nexus sends approved jobs to SkillVector
    log("Step 6: Nexus pushing approved jobs to SkillVector...")
    await nexus.arun(
        f"Call push_jobs_to_skillevector with this list: {approved_jobs}"
    )

    # STEP 7 — Wait until 8AM then Scribe creates content
    log("Step 7: Waiting until 8AM for content creation...")
    now = datetime.now()
    seconds_to_8am = max(0, (8 - now.hour) * 3600 - now.minute * 60)
    if seconds_to_8am > 0:
        await asyncio.sleep(seconds_to_8am)

    log("Step 7: Scribe getting daily insight and writing content...")
    draft = await scribe.arun(
        "Call get_insight_and_write_content to get today's SkillVector data. "
        "Write a full LinkedIn post (150-200 words, founder voice). "
        "Write a tweet (under 280 chars). "
        "Label them clearly as LINKEDIN: and TWEET:"
    )

    # STEP 8 — Sentinel reviews content
    log("Step 8: Sentinel reviewing content...")
    reviewed = await sentinel.arun(
        f"Review this content for compliance before posting: {draft}. "
        "No false claims. No competitor names. "
        "If approved respond with APPROVED followed by the content. "
        "If changes needed respond with REVISED followed by fixed content."
    )

    # STEP 9 — Post approved content
    if "APPROVED" in reviewed or "REVISED" in reviewed:
        log("Step 9: Scribe posting to LinkedIn and Twitter...")
        await scribe.arun(
            f"Post this content to LinkedIn and Twitter now: {reviewed}. "
            "Post LinkedIn first then Twitter. Confirm both posted."
        )
        log("Content posted successfully.")
    else:
        log("Sentinel blocked content. Not posted.")

    log("=== ATLAS DAILY PIPELINE COMPLETE ===")


async def run_full_pipeline(atlas, scout, nexus, cipher, scribe, sentinel):
    """
    Backward-compatible alias for callers expecting run_full_pipeline.
    """
    return await run_pipeline(atlas, scout, nexus, cipher, scribe, sentinel)
