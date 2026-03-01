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
        verify_skillevector_connection,
        push_skill_trends_to_skillevector,
        push_jobs_to_skillevector,
        get_insight_and_write_content,
        update_dashboard,
        improve_skillevector_from_feedback,
        push_to_github,
    )
    from integrations.daily_pipeline import run_full_pipeline

    atlas = AtlasAgent(extra_tools=[
        verify_skillevector_connection,
        update_dashboard,
        improve_skillevector_from_feedback,
        push_to_github,
    ])
    scout    = ScoutAgent(extra_tools=[push_skill_trends_to_skillevector])
    nexus    = NexusAgent(extra_tools=[push_jobs_to_skillevector])
    cipher   = CipherAgent()
    scribe   = ScribeAgent(extra_tools=[get_insight_and_write_content])
    sentinel = SentinelAgent()

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
