"""
AI Content Writer Agent — Claude AI Integration
Generates blog posts, social media content, and SEO-optimized articles.
"""

import os
import httpx

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ── Prompts ───────────────────────────────────────────────────────

BLOG_PROMPT = (
    "You are a professional content writer. Generate high-quality blog posts.\n"
    "Structure: Compelling title → Hook intro (2-3 sentences) → Clear headings → "
    "Actionable body paragraphs → Strong conclusion with CTA.\n"
    "Use Markdown formatting. Include relevant examples and data points.\n"
    "Write naturally — avoid AI-sounding phrases like 'dive into' or 'let's explore'."
)

SOCIAL_PROMPT = (
    "You are a social media content expert. Convert content into platform-specific posts.\n"
    "Twitter: Max 280 chars, punchy, use relevant hashtags (2-3 max).\n"
    "LinkedIn: Professional tone, 150-300 words, storytelling format, end with question.\n"
    "Instagram: Visual-focused caption, emoji-friendly, 5-10 relevant hashtags at end.\n"
    "Return each platform's post clearly labeled."
)

SEO_PROMPT = (
    "You are an SEO content analyst. Analyze content for search engine optimization.\n"
    "Score each category 0-100:\n"
    "- Keyword density & placement\n"
    "- Readability (Flesch-Kincaid level)\n"
    "- Header structure (H1, H2, H3 usage)\n"
    "- Meta description quality\n"
    "- Internal linking opportunities\n"
    "Provide specific, actionable improvements. Return JSON with scores and suggestions."
)

REWRITE_PROMPT = (
    "You are a content editor. Rewrite the given text in the requested tone.\n"
    "Preserve all key information and arguments. Adjust vocabulary, sentence structure, "
    "and style to match the target tone. Keep the same approximate length."
)

TONES = {
    "professional": "Formal, authoritative, data-driven. Use industry terminology.",
    "casual": "Conversational, friendly, relatable. Use contractions and simple words.",
    "technical": "Precise, detailed, code-aware. Include technical specifics.",
    "storytelling": "Narrative-driven, engaging, uses analogies and personal anecdotes.",
    "persuasive": "Compelling, benefit-focused, uses social proof and urgency.",
    "witty": "Clever, humorous, memorable. Use wordplay and unexpected angles.",
}


class ContentAgent:
    """Claude-powered content generation engine."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    def is_configured(self):
        return bool(self.api_key) and self.api_key != "sk-ant-api03-YOUR_KEY_HERE"

    async def _call_claude(self, system_prompt, user_message, max_tokens=1500):
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

    async def write_blog(self, topic, tone="professional", word_count=800, keywords=None, outline=None):
        """Generate a complete blog post."""
        tone_desc = TONES.get(tone, TONES["professional"])
        prompt = f"Write a blog post about: {topic}\n\nTone: {tone} — {tone_desc}\nTarget length: ~{word_count} words\n"
        if keywords:
            prompt += f"SEO Keywords to include naturally: {', '.join(keywords)}\n"
        if outline:
            prompt += f"Follow this outline:\n{outline}\n"
        prompt += "\nReturn the complete blog post in Markdown format."
        return await self._call_claude(BLOG_PROMPT, prompt, max_tokens=max(1500, word_count * 2))

    async def generate_social(self, text, platforms=None):
        """Generate social media posts from content."""
        if platforms is None:
            platforms = ["twitter", "linkedin", "instagram"]
        prompt = f"Convert this content into social media posts for: {', '.join(platforms)}\n\nContent:\n{text[:3000]}"
        return await self._call_claude(SOCIAL_PROMPT, prompt, max_tokens=1000)

    async def analyze_seo(self, content, keywords=None):
        """Analyze content for SEO quality."""
        prompt = f"Analyze this content for SEO:\n\n{content[:4000]}\n"
        if keywords:
            prompt += f"\nTarget keywords: {', '.join(keywords)}"
        return await self._call_claude(SEO_PROMPT, prompt, max_tokens=800)

    async def rewrite(self, text, target_tone="casual"):
        """Rewrite content in a different tone."""
        tone_desc = TONES.get(target_tone, TONES["casual"])
        prompt = f"Rewrite this text in a {target_tone} tone ({tone_desc}):\n\n{text[:4000]}"
        return await self._call_claude(REWRITE_PROMPT, prompt, max_tokens=1500)
