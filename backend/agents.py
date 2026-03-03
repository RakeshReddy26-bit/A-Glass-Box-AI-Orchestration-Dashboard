from dotenv import load_dotenv
load_dotenv()
"""
Glass Box AI Dashboard — Agent Manager
Manages 5 AI agents, each with a unique system prompt and conversation history.
Uses Anthropic Claude API (via httpx) for intelligent responses.
"""

import os
import json
import httpx
from datetime import datetime


CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ── Agent Prompts (LEAN — optimized for low token usage) ─────────
# Each prompt is <100 tokens. Context is injected per-task, not repeated every call.
# The job hunter system is named "NEXUS" — Network EXploration & Upskill System

AGENT_PROMPTS = {
    "atlas": {
        "name": "Atlas",
        "role": "Orchestrator",
        "color": "#818cf8",
        "system": (
            "You are Atlas, orchestrator of the Glass Box AI system. "
            "Coordinate Scout, Cipher, Scribe, Sentinel. "
            "Two modes: FINANCE (AAPL analysis) and NEXUS (job hunting for Rakesh). "
            "Be concise — max 3 sentences unless asked for detail. Mission-control tone."
        ),
    },
    "scout": {
        "name": "Scout",
        "role": "Research Agent",
        "color": "#38bdf8",
        "system": (
            "You are Scout, research agent. Gather data from APIs and sources. "
            "FINANCE: market data, SEC filings, news. "
            "NEXUS: search Remotive + Arbeitnow for jobs matching Python/AI/ML/FastAPI skills. "
            "Cite sources. Be precise and data-driven. Max 3 sentences unless asked."
        ),
    },
    "cipher": {
        "name": "Cipher",
        "role": "Analysis Agent",
        "color": "#4ade80",
        "system": (
            "You are Cipher, analysis agent. Provide structured quantitative insights. "
            "NEXUS job scoring: Skills 40%, Location 20%, Role fit 20%, Growth 20%. Score 0-100. "
            "Rank jobs, flag concerns (scams, mismatch). Be precise with numbers."
        ),
    },
    "scribe": {
        "name": "Scribe",
        "role": "Writer Agent",
        "color": "#fbbf24",
        "system": (
            "You are Scribe, writer agent. Draft professional documents. "
            "NEXUS cover letters: 250-400 words, tailored to company. "
            "Structure: Why this company → 2-3 skill matches → Glass Box AI project → Close. "
            "Professional but warm tone. Adapt to company culture."
        ),
    },
    "sentinel": {
        "name": "Sentinel",
        "role": "Compliance Agent",
        "color": "#f87171",
        "system": (
            "You are Sentinel, compliance/quality agent. Review all outputs. "
            "NEXUS: check cover letters for false claims, generic language, tone issues. "
            "Flag scam jobs (no web presence, pay-to-apply, unrealistic salary). "
            "Give PASS/FAIL with specific reasons."
        ),
    },
}


class AgentManager:
    """Manages AI agents with Claude API integration and conversation history."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if self.api_key == "sk-ant-PASTE_YOUR_KEY_HERE":
            self.api_key = ""

        # Conversation history per agent (last 20 messages)
        self.history = {agent_id: [] for agent_id in AGENT_PROMPTS}

        # Agent state tracking
        self.agent_states = {}
        for agent_id, info in AGENT_PROMPTS.items():
            self.agent_states[agent_id] = {
                "id": agent_id,
                "name": info["name"],
                "role": info["role"],
                "color": info["color"],
                "status": "active" if agent_id != "scribe" else "idle",
                "lastMessage": None,
                "messageCount": 0,
            }

    def is_configured(self):
        """Check if Claude API is properly configured."""
        return bool(self.api_key)

    async def chat(self, agent_id, user_message, max_tokens=512):
        """Send a message to an agent and get a Claude-powered response.
        
        Args:
            max_tokens: Limit output length. Default 512 (saves ~50% vs 1024).
                        Use 1024 only for cover letters or long-form output.
        """
        if agent_id not in AGENT_PROMPTS:
            return f"Unknown agent: {agent_id}"

        agent = AGENT_PROMPTS[agent_id]

        # Add user message to history
        self.history[agent_id].append({
            "role": "user",
            "content": user_message,
        })

        # Trim history to last 20 messages
        if len(self.history[agent_id]) > 20:
            self.history[agent_id] = self.history[agent_id][-20:]

        # If Claude API is not configured, return a helpful fallback
        if not self.is_configured():
            fallback = (
                f"[{agent['name']}] API key not configured. "
                f"Add your ANTHROPIC_API_KEY to backend/.env to enable real AI responses."
            )
            self.history[agent_id].append({
                "role": "assistant",
                "content": fallback,
            })
            return fallback

        try:
            # Call Claude API with prompt caching (reduces input token costs by 90% on cache hits)
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    CLAUDE_API_URL,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "anthropic-beta": "prompt-caching-2024-07-31",
                        "content-type": "application/json",
                    },
                    json={
                        "model": CLAUDE_MODEL,
                        "max_tokens": max_tokens,
                        "system": [
                            {
                                "type": "text",
                                "text": agent["system"],
                                "cache_control": {"type": "ephemeral"},
                            }
                        ],
                        "messages": self.history[agent_id][-6:],  # Only last 6 messages, not 20
                    },
                )

                data = resp.json()

                if resp.status_code != 200:
                    error_msg = data.get("error", {}).get("message", f"HTTP {resp.status_code}")
                    raise Exception(error_msg)

                # Extract text from content blocks
                response_text = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        response_text += block.get("text", "")

                if not response_text:
                    response_text = f"[{agent['name']}] No response content."

            # Add assistant response to history
            self.history[agent_id].append({
                "role": "assistant",
                "content": response_text,
            })

            # Update agent state
            self.agent_states[agent_id]["lastMessage"] = response_text
            self.agent_states[agent_id]["messageCount"] += 1
            self.agent_states[agent_id]["status"] = "active"

            return response_text

        except Exception as e:
            error_msg = f"[{agent['name']}] API error: {str(e)}"
            self.history[agent_id].append({
                "role": "assistant",
                "content": error_msg,
            })
            return error_msg

    async def chat_all(self, user_message):
        """Send a message to all agents and collect responses."""
        responses = {}
        for agent_id in AGENT_PROMPTS:
            responses[agent_id] = await self.chat(agent_id, user_message)
        return responses

    def get_agent_info(self, agent_id):
        """Get agent metadata."""
        if agent_id in AGENT_PROMPTS:
            return AGENT_PROMPTS[agent_id]
        return None

    def get_all_states(self):
        """Get current state of all agents."""
        return self.agent_states

    def clear_history(self, agent_id=None):
        """Clear conversation history for one or all agents."""
        if agent_id:
            self.history[agent_id] = []
        else:
            for aid in self.history:
                self.history[aid] = []
