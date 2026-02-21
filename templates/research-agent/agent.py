"""
AI Research Agent — Claude AI Integration
Market research, competitor analysis, trend reports, and SWOT analysis.
"""

import os
import httpx

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ── Prompts ───────────────────────────────────────────────────────

RESEARCH_PROMPT = (
    "You are a senior market research analyst. Produce structured, data-driven reports.\n"
    "Format: Executive Summary → Key Findings (numbered) → Market Size/Trends → "
    "Competitive Landscape → Opportunities → Risks → Recommendations.\n"
    "Use Markdown. Cite the news articles provided as sources. Be specific with numbers."
)

COMPETITOR_PROMPT = (
    "You are a competitive intelligence analyst. Compare companies objectively.\n"
    "Format: Overview table (features/pricing/positioning) → Strengths per company → "
    "Weaknesses → Market positioning map → Key differentiators → Winner assessment.\n"
    "Use Markdown tables. Be specific and data-driven."
)

TREND_PROMPT = (
    "You are a trend analyst. Identify emerging patterns from news data.\n"
    "Format: Top 5 Trends (ranked by impact) → Evidence for each (cite articles) → "
    "Timeline/velocity → Who's affected → Actionable implications.\n"
    "Distinguish signal from noise. Rate confidence for each trend."
)

SWOT_PROMPT = (
    "You are a strategic analyst. Create a thorough SWOT analysis.\n"
    "Format: 2x2 matrix with 4-6 items per quadrant.\n"
    "Strengths: Internal advantages and assets.\n"
    "Weaknesses: Internal limitations and gaps.\n"
    "Opportunities: External favorable conditions.\n"
    "Threats: External risks and challenges.\n"
    "End with 3 strategic recommendations. Use Markdown."
)

SUMMARY_PROMPT = (
    "You are an executive briefing writer. Distill raw research into a clear summary.\n"
    "Format: One-paragraph TL;DR → 5 key takeaways (bullet points) → "
    "Implications for decision-makers → Recommended next steps.\n"
    "Max 400 words. Every sentence must add value."
)


class ResearchAgent:
    """Claude-powered research and analysis engine."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    def is_configured(self):
        return bool(self.api_key) and self.api_key != "sk-ant-api03-YOUR_KEY_HERE"

    async def _call_claude(self, system_prompt, user_message, max_tokens=2000):
        """Make a Claude API call."""
        if not self.is_configured():
            return "[Error: ANTHROPIC_API_KEY not configured in .env]"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
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

    async def research(self, topic, news_context, depth="detailed"):
        """Generate a market research report."""
        prompt = (
            f"Research topic: {topic}\nDepth: {depth}\n\n"
            f"NEWS DATA:\n{news_context}\n\n"
            f"Using the news data above plus your knowledge, produce a comprehensive market research report."
        )
        return await self._call_claude(RESEARCH_PROMPT, prompt, max_tokens=2500)

    async def competitor_analysis(self, companies, focus, news_context=""):
        """Compare competitors side-by-side."""
        prompt = (
            f"Companies to analyze: {', '.join(companies)}\n"
            f"Focus area: {focus}\n\n"
            f"{'NEWS CONTEXT:' + chr(10) + news_context + chr(10) + chr(10) if news_context else ''}"
            f"Create a detailed competitive analysis comparing these companies."
        )
        return await self._call_claude(COMPETITOR_PROMPT, prompt, max_tokens=2000)

    async def trend_report(self, topic, news_context):
        """Identify and analyze trends from news data."""
        prompt = (
            f"Topic area: {topic}\n\n"
            f"NEWS ARTICLES:\n{news_context}\n\n"
            f"Identify the top emerging trends from these articles. Rank by impact."
        )
        return await self._call_claude(TREND_PROMPT, prompt, max_tokens=2000)

    async def swot_analysis(self, subject, context=""):
        """Generate a SWOT analysis."""
        prompt = f"Subject: {subject}\n"
        if context:
            prompt += f"Context: {context}\n"
        prompt += "\nCreate a comprehensive SWOT analysis."
        return await self._call_claude(SWOT_PROMPT, prompt, max_tokens=1500)

    async def executive_summary(self, raw_text):
        """Distill raw research into an executive summary."""
        prompt = f"Summarize this research into an executive briefing:\n\n{raw_text[:5000]}"
        return await self._call_claude(SUMMARY_PROMPT, prompt, max_tokens=800)
