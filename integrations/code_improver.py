"""
Reads user feedback and improves SkillVector code automatically.
Uses Claude to propose a minimal safe patch and pushes it via GitHub helper.
"""

import json
import logging
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SKILLEVECTOR_PATH = os.getenv("SKILLEVECTOR_REPO_PATH")


def read_current_file(file_path: str) -> str:
    """Read current version of a SkillVector file."""
    if not SKILLEVECTOR_PATH:
        return ""
    try:
        full_path = os.path.join(SKILLEVECTOR_PATH, file_path)
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def improve_code_from_feedback(
    feedback: str,
    file_to_improve: str = "src/pipeline/full_pipeline.py",
) -> dict:
    """
    Read user feedback and improve code in the selected file.
    """
    if not SKILLEVECTOR_PATH:
        return {"status": "failed", "error": "SKILLEVECTOR_REPO_PATH not set in .env"}

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    current_code = read_current_file(file_to_improve)

    prompt = f"""You are improving SkillVector — a FastAPI-based AI career intelligence platform.

USER FEEDBACK RECEIVED:
{feedback}

CURRENT FILE ({file_to_improve}):
{current_code[:3000]}

Based on the user feedback, write an improvement to this file.

Rules:
- Only fix what the feedback specifically mentions
- Do NOT change the /analyze endpoint contract
- Do NOT break existing functionality
- Keep all existing tests passing
- Make the smallest possible change that fixes the issue

Return ONLY this JSON:
{{
    "should_improve": true/false,
    "reason": "one sentence explaining the improvement",
    "improved_code": "complete new file content here",
    "commit_message": "feat: one line description of change"
}}

If the feedback doesn't require a code change, set should_improve to false."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()

        result = json.loads(raw)
        if not result.get("should_improve"):
            return {
                "status": "skipped",
                "reason": result.get("reason", "No code change needed"),
            }

        from integrations.github_pusher import write_and_push_improvement

        push_result = write_and_push_improvement(
            file_path=file_to_improve,
            new_content=result["improved_code"],
            reason=result["commit_message"],
        )

        return {
            "status": "success",
            "improvement": result["reason"],
            "commit": result["commit_message"],
            "github": push_result["status"],
        }
    except Exception as e:
        logger.error("Code improvement failed: %s", e)
        return {"status": "failed", "error": str(e)}
