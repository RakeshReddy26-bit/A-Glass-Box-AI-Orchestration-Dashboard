"""
Atlas Workflow Manager
Handles: planning, task tracking, lessons learning, verification.
Atlas calls this at start and end of every task.
"""

import logging
from datetime import date, datetime
from pathlib import Path
from typing import Callable

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TASKS_DIR = Path("tasks")
TODO_FILE = TASKS_DIR / "todo.md"
LESSONS_FILE = TASKS_DIR / "lessons.md"


def ensure_tasks_dir():
    TASKS_DIR.mkdir(exist_ok=True)


def write_plan(tasks: list[str], context: str = "") -> str:
    """
    Atlas writes a plan before starting any non-trivial work.
    Call this FIRST before doing anything with 3+ steps.
    """
    ensure_tasks_dir()
    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M")

    content = f"""# Atlas Task Plan
Date: {today} {now}
Context: {context}

## Tasks
"""
    for task in tasks:
        content += f"- [ ] {task}\n"

    content += f"\n## Review\n- Started: {now}\n- Completed: \n- Errors: none\n"

    with TODO_FILE.open("w", encoding="utf-8") as f:
        f.write(content)

    logger.info("[ATLAS] Plan written with %s tasks", len(tasks))
    return f"Plan written to tasks/todo.md with {len(tasks)} tasks"


def mark_task_complete(task_name: str) -> str:
    """Atlas calls this after completing each task."""
    ensure_tasks_dir()

    if not TODO_FILE.exists():
        return "No todo.md found"

    content = TODO_FILE.read_text(encoding="utf-8")
    updated = content.replace(f"- [ ] {task_name}", f"- [x] {task_name}")

    if updated == content:
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if task_name.lower() in line.lower() and "- [ ]" in line:
                lines[i] = line.replace("- [ ]", "- [x]")
                break
        updated = "\n".join(lines)

    TODO_FILE.write_text(updated, encoding="utf-8")
    logger.info("[ATLAS] Task complete: %s", task_name)
    return f"Marked complete: {task_name}"


def update_review(key: str, value: str) -> str:
    """Updates the review section of todo.md with results."""
    ensure_tasks_dir()

    if not TODO_FILE.exists():
        return "No todo.md found"

    content = TODO_FILE.read_text(encoding="utf-8")
    old = f"- {key}:"
    new = f"- {key}: {value}"
    updated = content.replace(old, new, 1)
    TODO_FILE.write_text(updated, encoding="utf-8")
    return f"Review updated: {key} = {value}"


def add_lesson(pattern: str, fix: str) -> str:
    """
    Atlas calls this when a mistake happens.
    Writes the lesson so it never happens again.
    """
    ensure_tasks_dir()

    if not LESSONS_FILE.exists():
        LESSONS_FILE.write_text("# Atlas Lessons Learned\n\n", encoding="utf-8")

    content = LESSONS_FILE.read_text(encoding="utf-8")
    lesson_count = content.count("## Lesson")
    lesson_num = str(lesson_count + 1).zfill(3)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    new_lesson = f"""
## Lesson {lesson_num} — {now}
Pattern: {pattern}
Fix: {fix}
"""
    LESSONS_FILE.write_text(content + new_lesson, encoding="utf-8")
    logger.info("[ATLAS] Lesson %s recorded", lesson_num)
    return f"Lesson {lesson_num} saved: {pattern}"


def read_lessons() -> str:
    """Atlas reads this at start of every session."""
    ensure_tasks_dir()

    if not LESSONS_FILE.exists():
        return "No lessons yet."

    return LESSONS_FILE.read_text(encoding="utf-8")


def verify_task_complete(
    task_name: str,
    verification_check: Callable[[], bool],
    expected_result: str,
) -> dict:
    """
    Atlas never marks a task done without proving it works.
    verification_check: function that returns True/False
    expected_result: what success looks like
    """
    try:
        result = verification_check()
        if result:
            mark_task_complete(task_name)
            return {
                "verified": True,
                "task": task_name,
                "result": expected_result,
            }
        add_lesson(
            pattern=f"Task '{task_name}' appeared complete but verification failed",
            fix=f"Always run verification_check() before marking {task_name} done",
        )
        return {
            "verified": False,
            "task": task_name,
            "error": f"Verification failed. Expected: {expected_result}",
        }
    except Exception as e:
        return {
            "verified": False,
            "task": task_name,
            "error": str(e),
        }


def get_current_plan() -> str:
    """Returns current todo.md content."""
    if not TODO_FILE.exists():
        return "No plan written yet."
    return TODO_FILE.read_text(encoding="utf-8")
