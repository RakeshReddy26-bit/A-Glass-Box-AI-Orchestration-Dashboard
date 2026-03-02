import asyncio
import schedule
import time
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)
logger = logging.getLogger(__name__)


async def run():
    from agents.atlas import AtlasAgent
    from agents.scout import ScoutAgent
    from agents.nexus import NexusAgent
    from agents.cipher import CipherAgent
    from agents.scribe import ScribeAgent
    from agents.sentinel import SentinelAgent
    from integrations.langchain_tools import (
        check_current_plan,
        complete_task,
        verify_skillevector_connection,
        plan_daily_pipeline,
        push_skill_trends_to_skillevector,
        push_jobs_to_skillevector,
        record_lesson,
        get_insight_and_write_content,
        update_dashboard,
        update_pipeline_review,
        improve_skillevector_from_feedback,
        push_to_github,
    )
    from integrations.daily_pipeline import run_full_pipeline

    atlas = AtlasAgent(extra_tools=[
        plan_daily_pipeline,
        verify_skillevector_connection,
        complete_task,
        record_lesson,
        check_current_plan,
        update_pipeline_review,
        update_dashboard,
        improve_skillevector_from_feedback,
        push_to_github,
    ])
    scout = ScoutAgent(extra_tools=[
        push_skill_trends_to_skillevector,
        complete_task,
    ])
    nexus = NexusAgent(extra_tools=[
        push_jobs_to_skillevector,
        complete_task,
    ])
    cipher = CipherAgent(extra_tools=[complete_task])
    scribe = ScribeAgent(extra_tools=[
        get_insight_and_write_content,
        complete_task,
    ])
    sentinel = SentinelAgent(extra_tools=[complete_task])

    await run_full_pipeline(atlas, scout, nexus, cipher, scribe, sentinel)


def trigger():
    asyncio.create_task(run())


async def main():
    schedule.every().day.at("06:00").do(trigger)

    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("Atlas Scheduler is running")
    logger.info("Pipeline runs every day at 06:00 AM")
    logger.info("Press Ctrl+C to stop")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    while True:
        schedule.run_pending()
        await asyncio.sleep(60)


if __name__ == "__main__":
    if "--test-connection" in sys.argv:
        async def test():
            from integrations.skillevector_client import sv
            alive = await sv.health_check()
            print(f"SkillVector connection: {'OK' if alive else 'FAILED'}")
        asyncio.run(test())
    else:
        asyncio.run(main())
