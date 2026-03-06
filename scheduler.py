"""
Atlas Scheduler v2.0 - Production scheduler for SkillVector daily automation.

Responsibilities:
- Run full pipeline every day at 08:00 AM
- Health check ping every hour
- Log everything to logs/atlas.log with timestamps
- Send error alert email if pipeline fails
- Never crash silently - always log exceptions
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
import os
import sys
import traceback
from datetime import datetime

# Absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "atlas.log")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("atlas.scheduler")

# Config
PIPELINE_HOUR = int(os.getenv("ATLAS_PIPELINE_HOUR", "8"))
PIPELINE_MINUTE = int(os.getenv("ATLAS_PIPELINE_MINUTE", "0"))
HEALTH_INTERVAL_MINUTES = 60


async def run_pipeline():
    """Execute the full daily pipeline with error handling and alerting."""
    logger.info("=" * 60)
    logger.info("ATLAS SCHEDULER: Starting daily pipeline run")
    logger.info("=" * 60)

    try:
        from integrations.daily_pipeline import run_daily_pipeline, send_error_alert

        result = await run_daily_pipeline()

        email_status = "unknown"
        if isinstance(result, dict):
            email_info = result.get("email", {})
            email_status = email_info.get("status", "unknown") if isinstance(email_info, dict) else "unknown"

        logger.info(f"[SCHEDULER] Pipeline finished. Email status: {email_status}")
        return result

    except Exception as e:
        error_msg = f"Pipeline crashed with exception:\n{traceback.format_exc()}"
        logger.error(f"[SCHEDULER] {error_msg}")

        try:
            from integrations.daily_pipeline import send_error_alert
            send_error_alert(error_msg[:1000])
        except Exception as alert_err:
            logger.error(f"[SCHEDULER] Could not send error alert: {alert_err}")

        return {"status": "crashed", "error": str(e)}


async def run_health_ping():
    """Run a quick health check on SkillVector API."""
    try:
        from integrations.daily_pipeline import health_ping
        is_up = await health_ping()
        return is_up
    except Exception as e:
        logger.error(f"[SCHEDULER] Health ping failed: {e}")
        return False


async def main():
    """
    Main scheduler loop.
    - Runs pipeline once daily at PIPELINE_HOUR:PIPELINE_MINUTE
    - Runs health ping every HEALTH_INTERVAL_MINUTES
    - Never crashes - wraps everything in try/except
    """
    logger.info("=" * 60)
    logger.info("  ATLAS SCHEDULER v2.0")
    logger.info(f"  Pipeline runs daily at {PIPELINE_HOUR:02d}:{PIPELINE_MINUTE:02d}")
    logger.info(f"  Health ping every {HEALTH_INTERVAL_MINUTES} minutes")
    logger.info(f"  Logs: {LOG_FILE}")
    logger.info(f"  Base: {BASE_DIR}")
    logger.info("  Press Ctrl+C to stop")
    logger.info("=" * 60)

    last_health_ping = datetime.min
    last_pipeline_date = None

    while True:
        try:
            now = datetime.now()
            today_date = now.date()

            # Daily pipeline trigger
            if (now.hour == PIPELINE_HOUR
                    and now.minute >= PIPELINE_MINUTE
                    and last_pipeline_date != today_date):
                logger.info("[SCHEDULER] Pipeline trigger - starting daily run")
                last_pipeline_date = today_date
                await run_pipeline()
                logger.info("[SCHEDULER] Pipeline run complete")

            # Hourly health ping
            minutes_since_ping = (now - last_health_ping).total_seconds() / 60
            if minutes_since_ping >= HEALTH_INTERVAL_MINUTES:
                last_health_ping = now
                await run_health_ping()

            await asyncio.sleep(30)

        except KeyboardInterrupt:
            logger.info("[SCHEDULER] Stopped by user (Ctrl+C)")
            break
        except Exception as e:
            logger.error(f"[SCHEDULER] Loop error (will retry): {e}")
            logger.error(traceback.format_exc())
            await asyncio.sleep(300)


if __name__ == "__main__":
    if "--run-now" in sys.argv:
        logger.info("[SCHEDULER] --run-now: Executing pipeline immediately")
        result = asyncio.run(run_pipeline())
        logger.info(f"[SCHEDULER] Done: {result}")
    elif "--health" in sys.argv:
        asyncio.run(run_health_ping())
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("[SCHEDULER] Shut down.")
