import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def run_full_pipeline(atlas, scout, nexus, cipher, scribe, sentinel):
    """
    Complete daily pipeline with planning, tracking and lessons.
    """

    def log(msg):
        logger.info(f"[{datetime.now().strftime('%H:%M')}] {msg}")

    log("=== ATLAS DAILY PIPELINE STARTED ===")

    # STEP 0 — Read lessons + write plan
    log("Step 0: Atlas planning today's pipeline...")
    await atlas.arun(
        "Call plan_daily_pipeline to write today's task plan "
        "and read lessons from past mistakes. "
        "Then confirm you are ready to start."
    )

    # STEP 1 — Verify connection
    log("Step 1: Verifying SkillVector connection...")
    health = await atlas.arun(
        "Call verify_skillevector_connection. "
        "If OK, call complete_task with 'Verify SkillVector connection'. "
        "If FAILED, call record_lesson with the error pattern and fix, "
        "then wait 30 seconds and retry once."
    )
    if "DOWN" in health:
        log("SkillVector down. Aborting.")
        return

    # STEP 2 — Scout trends
    log("Step 2: Scout researching trending skills...")
    await scout.arun(
        "Search NewsAPI for top 10 trending ML skills this week. "
        "Call push_skill_trends_to_skillevector with results. "
        "Then call complete_task with 'Scout: research trending ML skills via NewsAPI'."
    )

    # STEP 3 — Nexus finds jobs
    log("Step 3: Nexus finding new jobs...")
    raw_jobs = await nexus.arun(
        "Search Remotive and Arbeitnow for 20 ML jobs from last 48 hours. "
        "Return as JSON array. Do NOT push yet. "
        "Call complete_task with 'Nexus: find 20 new job postings from Remotive + Arbeitnow'."
    )

    # STEP 4 — Cipher scores
    log("Step 4: Cipher scoring jobs...")
    ranked = await cipher.arun(
        f"Score these jobs 0-100 for quality: {raw_jobs}. "
        "Remove anything below 60. Return filtered JSON. "
        "Call complete_task with 'Cipher: score and rank job quality'."
    )

    # STEP 5 — Sentinel validates
    log("Step 5: Sentinel validating jobs...")
    approved = await sentinel.arun(
        f"Review for compliance: {ranked}. "
        "Remove scams and fake listings. Return approved JSON. "
        "Call complete_task with 'Sentinel: validate job listings for compliance'."
    )

    # STEP 6 — Push jobs
    log("Step 6: Pushing approved jobs to SkillVector...")
    await nexus.arun(
        f"Call push_jobs_to_skillevector with: {approved}. "
        "Then call complete_task with 'Push validated jobs to SkillVector Pinecone'."
    )

    # STEP 7 — Dashboard update
    log("Step 7: Updating dashboard...")
    await atlas.arun(
        "Call update_dashboard to update stats and push to GitHub. "
        "Then call complete_task with 'Update dashboard stats + push to GitHub'."
    )

    # STEP 8 — Content creation
    log("Step 8: Scribe creating content...")
    draft = await scribe.arun(
        "Call get_insight_and_write_content. "
        "Write full LinkedIn post 150-200 words. "
        "Write Indie Hackers post 200-300 words. "
        "Call complete_task with 'Scribe: get daily insight from SkillVector'."
    )

    # STEP 9 — Sentinel reviews
    log("Step 9: Sentinel reviewing content...")
    reviewed = await sentinel.arun(
        f"Review this content: {draft}. "
        "Check compliance. Return APPROVED or REVISED content. "
        "Call complete_task with 'Sentinel: review LinkedIn post'."
    )

    # STEP 10 — Post content
    if "APPROVED" in str(reviewed) or "REVISED" in str(reviewed):
        log("Step 10: Posting content...")
        await scribe.arun(
            f"Post to LinkedIn via Zapier: {reviewed}. "
            "Save Indie Hackers post to posts/ folder. "
            "Call complete_task with 'Post to LinkedIn via Zapier'. "
            "Call complete_task with 'Save Indie Hackers post to posts/ folder'."
        )

    # STEP 11 — Final review
    log("Step 11: Recording pipeline results...")
    await atlas.arun(
        "Call update_pipeline_review with jobs added count. "
        "Call update_pipeline_review with LinkedIn post URL. "
        "Call check_current_plan to confirm all tasks complete."
    )

    log("=== ATLAS DAILY PIPELINE COMPLETE ===")


async def run_pipeline(atlas, scout, nexus, cipher, scribe, sentinel):
    """
    Backward-compatible alias for callers expecting run_pipeline.
    """
    return await run_full_pipeline(atlas, scout, nexus, cipher, scribe, sentinel)
