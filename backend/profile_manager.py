"""
Glass Box AI Dashboard — Profile Manager
Stores your resume, skills, and preferences.
Agents read this to tailor job matches and cover letters.
Data saved as JSON on your Desktop for easy access.
"""

import os
import json
from datetime import datetime

# Where profiles and outputs are saved
OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "GlassBox-Outputs")
PROFILE_PATH = os.path.join(OUTPUT_DIR, "my_profile.json")
COVER_LETTERS_DIR = os.path.join(OUTPUT_DIR, "cover_letters")
JOB_MATCHES_DIR = os.path.join(OUTPUT_DIR, "job_matches")


def _ensure_dirs():
    """Create output directories if they don't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(COVER_LETTERS_DIR, exist_ok=True)
    os.makedirs(JOB_MATCHES_DIR, exist_ok=True)


# ── Default Profile (edit this to match YOUR info) ────────────────

DEFAULT_PROFILE = {
    "name": "Rakesh Reddy Kalamakuntla",
    "title": "Master's Student in Computer Science",
    "location": "Europe",
    "education": [
        {
            "degree": "Master of Science in Computer Science",
            "status": "In Progress (50% complete)",
            "focus": "AI, Machine Learning, Software Engineering",
        }
    ],
    "skills": {
        "languages": ["Python", "JavaScript", "HTML/CSS", "SQL"],
        "frameworks": ["FastAPI", "React", "Node.js", "TailwindCSS"],
        "ai_ml": ["LLM Integration", "Anthropic Claude API", "AI Agent Architecture", "Prompt Engineering"],
        "tools": ["Git", "GitHub", "VS Code", "Docker", "Linux"],
        "other": ["REST APIs", "WebSockets", "Telegram Bots", "Multi-Agent Systems"],
    },
    "experience_summary": (
        "Building multi-agent AI orchestration systems with human-in-the-loop governance. "
        "Experienced in Python backend development, API integration, and real-time dashboards. "
        "Currently developing Glass Box AI Dashboard — a transparent AI governance platform "
        "with 5 specialized agents, Telegram approval workflows, and live financial data integration."
    ),
    "job_preferences": {
        "roles": [
            "Python Developer",
            "AI/ML Engineer",
            "Backend Developer",
            "Software Engineer",
            "Full Stack Developer",
            "Data Engineer",
        ],
        "work_type": ["remote", "hybrid", "on-site"],
        "employment_type": ["part-time", "full-time", "contract", "freelance"],
        "locations": ["Germany", "Netherlands", "Europe", "Remote"],
        "min_salary_eur": 0,
        "industries": ["Technology", "AI/ML", "FinTech", "SaaS", "Startups"],
    },
    "portfolio_links": {
        "github": "",
        "linkedin": "",
        "website": "",
    },
    "updated_at": "",
}


class ProfileManager:
    """Manages user profile, saves job matches and cover letters to Desktop."""

    def __init__(self):
        _ensure_dirs()
        self.profile = self._load_or_create_profile()

    def _load_or_create_profile(self):
        """Load existing profile or create default."""
        if os.path.exists(PROFILE_PATH):
            try:
                with open(PROFILE_PATH, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        # Create default profile
        self._save_profile(DEFAULT_PROFILE)
        return DEFAULT_PROFILE.copy()

    def _save_profile(self, profile=None):
        """Save profile to disk."""
        if profile is None:
            profile = self.profile
        profile["updated_at"] = datetime.now().isoformat()
        with open(PROFILE_PATH, "w") as f:
            json.dump(profile, f, indent=2)

    def get_profile(self):
        """Return current profile."""
        return self.profile

    def update_profile(self, updates: dict):
        """Update profile fields. Merges with existing data."""
        for key, value in updates.items():
            if key in self.profile:
                if isinstance(self.profile[key], dict) and isinstance(value, dict):
                    self.profile[key].update(value)
                else:
                    self.profile[key] = value
        self._save_profile()
        return self.profile

    def get_profile_text(self):
        """Return profile as a text summary for agents to read."""
        p = self.profile
        skills_flat = []
        for category, items in p.get("skills", {}).items():
            skills_flat.extend(items)

        prefs = p.get("job_preferences", {})
        roles = ", ".join(prefs.get("roles", []))
        locations = ", ".join(prefs.get("locations", []))
        work_types = ", ".join(prefs.get("work_type", []))

        text = (
            f"CANDIDATE PROFILE:\n"
            f"Name: {p.get('name', 'Unknown')}\n"
            f"Title: {p.get('title', '')}\n"
            f"Location: {p.get('location', '')}\n"
            f"Education: {p['education'][0]['degree']} ({p['education'][0]['status']})\n"
            f"Focus: {p['education'][0].get('focus', '')}\n"
            f"Skills: {', '.join(skills_flat)}\n"
            f"Experience: {p.get('experience_summary', '')}\n\n"
            f"JOB PREFERENCES:\n"
            f"Target Roles: {roles}\n"
            f"Target Locations: {locations}\n"
            f"Work Type: {work_types}\n"
            f"Employment: {', '.join(prefs.get('employment_type', []))}\n"
        )
        return text

    # ── Save job matches ──────────────────────────────────────────

    def save_job_matches(self, jobs, query=""):
        """Save job search results to Desktop/GlassBox-Outputs/job_matches/."""
        _ensure_dirs()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"jobs_{timestamp}.json"
        filepath = os.path.join(JOB_MATCHES_DIR, filename)

        output = {
            "searched_at": datetime.now().isoformat(),
            "query": query,
            "total_jobs": len(jobs),
            "jobs": jobs,
        }

        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)

        return filepath

    # ── Save cover letter ─────────────────────────────────────────

    def save_cover_letter(self, company, role, letter_text):
        """Save a generated cover letter to Desktop/GlassBox-Outputs/cover_letters/."""
        _ensure_dirs()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        safe_company = "".join(c for c in company if c.isalnum() or c in " -_").strip().replace(" ", "_")
        filename = f"cover_letter_{safe_company}_{timestamp}.md"
        filepath = os.path.join(COVER_LETTERS_DIR, filename)

        content = (
            f"# Cover Letter\n\n"
            f"**Company:** {company}\n"
            f"**Role:** {role}\n"
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}\n\n"
            f"---\n\n"
            f"{letter_text}\n"
        )

        with open(filepath, "w") as f:
            f.write(content)

        return filepath

    # ── List saved outputs ────────────────────────────────────────

    def list_saved_jobs(self):
        """List all saved job match files."""
        _ensure_dirs()
        files = sorted(os.listdir(JOB_MATCHES_DIR), reverse=True)
        return [f for f in files if f.endswith(".json")]

    def list_cover_letters(self):
        """List all saved cover letter files."""
        _ensure_dirs()
        files = sorted(os.listdir(COVER_LETTERS_DIR), reverse=True)
        return [f for f in files if f.endswith(".md")]

    def get_output_paths(self):
        """Return all output directory paths."""
        return {
            "output_dir": OUTPUT_DIR,
            "profile": PROFILE_PATH,
            "cover_letters": COVER_LETTERS_DIR,
            "job_matches": JOB_MATCHES_DIR,
        }
