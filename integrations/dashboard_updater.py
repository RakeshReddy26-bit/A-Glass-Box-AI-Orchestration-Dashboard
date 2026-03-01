"""
Updates SkillVector dashboard with daily stats.
Writes a JSON file that the frontend reads.
"""

import json
import logging
import os
from datetime import date, datetime

from integrations.skillevector_client import sv

logger = logging.getLogger(__name__)

SKILLEVECTOR_PATH = os.getenv("SKILLEVECTOR_REPO_PATH")
DASHBOARD_FILE = "frontend/public/daily_stats.json"


async def update_dashboard_stats() -> dict:
    """
    Get today's stats from SkillVector API and write dashboard JSON.
    """
    if not SKILLEVECTOR_PATH:
        return {"status": "failed", "error": "SKILLEVECTOR_REPO_PATH not set in .env"}

    try:
        insight = await sv.get_daily_insight()
        stats = insight["stats"]
        dashboard_data = {
            "last_updated": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "total_analyses": stats["total_analyses"],
            "top_skill_gap": stats["top_skill_gap"],
            "avg_match_score": stats["avg_match_score"],
            "trending_roles": stats["trending_roles"],
            "skill_gap_distribution": stats["skill_gap_distribution"],
            "linkedin_hook": insight["linkedin_hook"],
            "app_url": insight["app_url"],
        }

        full_path = os.path.join(SKILLEVECTOR_PATH, DASHBOARD_FILE)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(dashboard_data, f, indent=2)

        logger.info(
            "[ATLAS] Dashboard stats updated: %s analyses today",
            stats["total_analyses"],
        )

        from integrations.github_pusher import push_code_changes

        result = push_code_changes(
            files_changed=[DASHBOARD_FILE],
            commit_message=f"data: daily stats update {date.today().isoformat()}",
        )

        return {
            "status": "success",
            "stats_updated": dashboard_data,
            "github_push": result["status"],
        }
    except Exception as e:
        logger.error("Dashboard update failed: %s", e)
        return {"status": "failed", "error": str(e)}
