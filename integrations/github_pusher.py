"""
GitHub automation for Atlas to push code changes automatically.
Uses git commands via subprocess.
"""

import logging
import os
import subprocess
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SKILLEVECTOR_PATH = os.getenv("SKILLEVECTOR_REPO_PATH")


def run_git(command: list[str], cwd: str) -> tuple[bool, str]:
    """Run a git command and return (success, output)."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr
        return success, output
    except Exception as e:
        return False, str(e)


def push_code_changes(files_changed: list[str], commit_message: str | None = None) -> dict:
    """
    Push code changes to GitHub.
    Render auto-deploys after every push to main.
    """
    if not SKILLEVECTOR_PATH:
        return {"status": "failed", "error": "SKILLEVECTOR_REPO_PATH not set in .env"}

    try:
        today = datetime.now().strftime("%Y-%m-%d")
        message = commit_message or f"feat: Atlas daily improvements {today}"

        # Stage selected files; "." stages all pending changes.
        for file_path in files_changed:
            success, output = run_git(["git", "add", file_path], SKILLEVECTOR_PATH)
            if not success:
                logger.warning("Could not stage %s: %s", file_path, output)

        success, status = run_git(["git", "status", "--porcelain"], SKILLEVECTOR_PATH)
        if not success:
            return {"status": "failed", "error": f"Could not read git status: {status}"}
        if not status.strip():
            return {"status": "skipped", "message": "No changes to commit"}

        success, output = run_git(["git", "commit", "-m", message], SKILLEVECTOR_PATH)
        if not success:
            return {"status": "failed", "error": f"Commit failed: {output}"}

        # Pull latest first to reduce push conflicts.
        run_git(["git", "pull", "origin", "main", "--rebase"], SKILLEVECTOR_PATH)

        success, output = run_git(["git", "push", "origin", "main"], SKILLEVECTOR_PATH)
        if not success:
            return {"status": "failed", "error": f"Push failed: {output}"}

        logger.info("[ATLAS] Pushed to GitHub: %s", message)
        return {
            "status": "success",
            "commit_message": message,
            "files_changed": files_changed,
            "deployed": "Render will auto-deploy in ~2 minutes",
        }
    except Exception as e:
        logger.error("GitHub push failed: %s", e)
        return {"status": "failed", "error": str(e)}


def write_and_push_improvement(file_path: str, new_content: str, reason: str) -> dict:
    """
    Write a code improvement and push it.
    file_path is relative from SkillVector root.
    """
    if not SKILLEVECTOR_PATH:
        return {"status": "failed", "error": "SKILLEVECTOR_REPO_PATH not set in .env"}

    try:
        full_path = os.path.join(SKILLEVECTOR_PATH, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        logger.info("[ATLAS] Wrote improvement to %s", file_path)
        return push_code_changes(
            files_changed=[file_path],
            commit_message=f"feat: {reason}",
        )
    except Exception as e:
        return {"status": "failed", "error": str(e)}
