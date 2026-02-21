"""
AI Job Search Agent — Claude AI Integration
Scores jobs against your profile and generates tailored cover letters.
"""

import os
import httpx

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ── Prompts ───────────────────────────────────────────────────────

SCORER_PROMPT = (
    "You are a job-matching AI. Score each job 0-100 against the candidate profile.\n"
    "Scoring weights: Skills Match 40%, Location Fit 20%, Role Relevance 20%, Growth Potential 20%.\n"
    "Return JSON array: [{\"title\": ..., \"company\": ..., \"score\": N, \"reason\": \"...\"}]\n"
    "Be strict — only high-quality matches should score above 70."
)

COVER_LETTER_PROMPT = (
    "You are a professional cover letter writer. Write a 250-400 word cover letter.\n"
    "Structure: Why this company → 2-3 specific skill matches → Notable project → Enthusiastic close.\n"
    "Professional but warm. Never use generic phrases. Tailor to the company's mission."
)


class JobAgent:
    """Claude-powered job scoring and cover letter generation."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    def is_configured(self):
        return bool(self.api_key) and self.api_key != "sk-ant-api03-YOUR_KEY_HERE"

    async def _call_claude(self, system_prompt, user_message, max_tokens=512):
        """Make a Claude API call."""
        if not self.is_configured():
            return "[Error: ANTHROPIC_API_KEY not configured in .env]"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    CLAUDE_API_URL,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": CLAUDE_MODEL,
                        "max_tokens": max_tokens,
                        "system": system_prompt,
                        "messages": [{"role": "user", "content": user_message}],
                    },
                )
                data = resp.json()
                if "content" in data and data["content"]:
                    return data["content"][0].get("text", "")
                return f"[API error: {data.get('error', {}).get('message', 'Unknown')}]"
        except Exception as e:
            return f"[Error: {str(e)}]"

    async def score_jobs(self, jobs_text, profile_text):
        """Score jobs against candidate profile."""
        prompt = f"{profile_text}\n\n---\n\nJOBS TO SCORE:\n{jobs_text}\n\nScore each job 0-100. Return JSON array."
        return await self._call_claude(SCORER_PROMPT, prompt, max_tokens=800)

    async def write_cover_letter(self, company, role, job_description, profile_text):
        """Generate a tailored cover letter."""
        prompt = (
            f"Write a cover letter for:\n"
            f"Company: {company}\nRole: {role}\n"
            f"Job Description: {job_description}\n\n"
            f"Candidate:\n{profile_text}"
        )
        return await self._call_claude(COVER_LETTER_PROMPT, prompt, max_tokens=800)
