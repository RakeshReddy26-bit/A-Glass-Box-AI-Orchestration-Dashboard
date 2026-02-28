from dotenv import load_dotenv
load_dotenv()
import httpx
import os
import logging

logger = logging.getLogger(__name__)

SKILLEVECTOR_URL = os.getenv("SKILLEVECTOR_URL")
ATLAS_KEY = os.getenv("AUTOMATION_API_KEY")
HEADERS = {
    "x-atlas-key": ATLAS_KEY,
    "Content-Type": "application/json"
}


class SkillVectorClient:

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(
                    f"{SKILLEVECTOR_URL}/automation/health-atlas",
                    headers=HEADERS
                )
                return r.status_code == 200
        except Exception as e:
            logger.error(f"SkillVector health check failed: {e}")
            return False

    async def ingest_jobs(self, jobs: list, source: str = "nexus_agent") -> dict:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"{SKILLEVECTOR_URL}/automation/ingest-jobs",
                json={
                    "jobs": jobs,
                    "source": source,
                    "ingested_by": "nexus_agent"
                },
                headers=HEADERS
            )
            r.raise_for_status()
            return r.json()

    async def update_trends(self, trending_skills: list) -> dict:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.post(
                f"{SKILLEVECTOR_URL}/automation/trend-update",
                json={
                    "trending_skills": trending_skills,
                    "market_data": {},
                    "source": "scout_agent"
                },
                headers=HEADERS
            )
            r.raise_for_status()
            return r.json()

    async def get_daily_insight(self) -> dict:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(
                f"{SKILLEVECTOR_URL}/automation/daily-insight",
                headers=HEADERS
            )
            r.raise_for_status()
            return r.json()


sv = SkillVectorClient()
