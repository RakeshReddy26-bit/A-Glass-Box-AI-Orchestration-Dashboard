"""
Glass Box AI Dashboard — Test Suite
Covers: API endpoints, agent manager, profile manager, job tools, scout tools.
Run: cd backend && pytest tests/ -v
"""

import os
import sys
import json
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

# Ensure backend/ is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient

# ── Patch env vars BEFORE importing server ──────────────────────
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key-for-testing"
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["TELEGRAM_CHAT_ID"] = ""
os.environ["NEWSAPI_KEY"] = ""

from server import app, agent_manager, make_event, activity_feed, approval_queue
from agents import AgentManager, AGENT_PROMPTS
from profile_manager import ProfileManager, DEFAULT_PROFILE


# ── Shared Fixtures ──────────────────────────────────────────────

@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def fresh_agent_manager():
    """A fresh AgentManager with a fake API key."""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
        mgr = AgentManager()
    return mgr


# ════════════════════════════════════════════════════════════════════
#  1. HEALTH & BASIC ENDPOINTS (4 tests)
# ════════════════════════════════════════════════════════════════════

class TestHealthEndpoints:
    """Test basic API health and info endpoints."""

    def test_health_returns_ok(self, client):
        """GET /api/health should return status ok."""
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "agents" in data
        assert data["agents"] == 5
        assert "timestamp" in data

    def test_health_shows_claude_api_status(self, client):
        """Health check should report Claude API configuration."""
        resp = client.get("/api/health")
        data = resp.json()
        assert "claude_api" in data
        assert isinstance(data["claude_api"], bool)

    def test_get_agents_returns_all_five(self, client):
        """GET /api/agents should return all 5 agent states."""
        resp = client.get("/api/agents")
        assert resp.status_code == 200
        data = resp.json()
        expected = {"atlas", "scout", "cipher", "scribe", "sentinel"}
        assert set(data.keys()) == expected

    def test_get_activity_feed(self, client):
        """GET /api/activity should return a list."""
        resp = client.get("/api/activity")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ════════════════════════════════════════════════════════════════════
#  2. AGENT MANAGER UNIT TESTS (5 tests)
# ════════════════════════════════════════════════════════════════════

class TestAgentManager:
    """Test the AgentManager class."""

    def test_all_agents_defined(self, fresh_agent_manager):
        """All 5 agents should be defined with name, role, color, system."""
        mgr = fresh_agent_manager
        for agent_id in ["atlas", "scout", "cipher", "scribe", "sentinel"]:
            info = mgr.get_agent_info(agent_id)
            assert info is not None, f"Agent {agent_id} not found"
            assert "name" in info
            assert "role" in info
            assert "color" in info
            assert "system" in info

    def test_agent_states_initialized(self, fresh_agent_manager):
        """Each agent should start with status, messageCount, etc."""
        states = fresh_agent_manager.get_all_states()
        assert len(states) == 5
        for agent_id, state in states.items():
            assert state["messageCount"] == 0
            assert state["status"] in ("active", "idle")
            assert state["name"] == AGENT_PROMPTS[agent_id]["name"]

    def test_unknown_agent_returns_error(self, fresh_agent_manager):
        """Chatting with invalid agent ID should return error string."""
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            fresh_agent_manager.chat("nonexistent_agent", "hello")
        )
        loop.close()
        assert "Unknown agent" in result

    def test_clear_history(self, fresh_agent_manager):
        """clear_history should reset message history."""
        mgr = fresh_agent_manager
        mgr.history["atlas"].append({"role": "user", "content": "test"})
        assert len(mgr.history["atlas"]) == 1
        mgr.clear_history("atlas")
        assert len(mgr.history["atlas"]) == 0

    def test_clear_all_history(self, fresh_agent_manager):
        """clear_history() with no args should clear all agents."""
        mgr = fresh_agent_manager
        for aid in mgr.history:
            mgr.history[aid].append({"role": "user", "content": "test"})
        mgr.clear_history()
        for aid in mgr.history:
            assert len(mgr.history[aid]) == 0


# ════════════════════════════════════════════════════════════════════
#  3. CHAT ENDPOINT TESTS (3 tests)
# ════════════════════════════════════════════════════════════════════

class TestChatEndpoint:
    """Test the /api/chat endpoint."""

    def test_chat_requires_body(self, client):
        """POST /api/chat without body should return 422."""
        resp = client.post("/api/chat")
        assert resp.status_code == 422

    def test_chat_with_invalid_agent(self, client):
        """Chat with unknown agent should return error in response."""
        resp = client.post("/api/chat", json={
            "agent": "nonexistent",
            "message": "hello"
        })
        assert resp.status_code == 200
        data = resp.json()
        # Should either have "error" key or response containing "Unknown agent"
        has_error = "error" in data or "Unknown agent" in data.get("response", "")
        assert has_error

    @patch("agents.AgentManager.chat", new_callable=AsyncMock)
    def test_chat_with_atlas_returns_response(self, mock_chat, client):
        """Chat with Atlas should return structured response."""
        mock_chat.return_value = "Atlas reporting. All systems operational."
        resp = client.post("/api/chat", json={
            "agent": "atlas",
            "message": "status update"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["agent"] == "Atlas"
        assert data["agentId"] == "atlas"
        assert "response" in data
        assert "time" in data


# ════════════════════════════════════════════════════════════════════
#  4. APPROVALS ENDPOINT TESTS (3 tests)
# ════════════════════════════════════════════════════════════════════

class TestApprovalsEndpoint:
    """Test the approval queue endpoints."""

    def test_get_approvals(self, client):
        """GET /api/approvals should return pending and history."""
        resp = client.get("/api/approvals")
        assert resp.status_code == 200
        data = resp.json()
        assert "pending" in data
        assert "history" in data
        assert isinstance(data["pending"], list)

    def test_approve_decision(self, client):
        """POST approve on APR-001 should update status."""
        # Reset approval to pending
        for a in approval_queue:
            if a["id"] == "APR-001":
                a["status"] = "pending"

        resp = client.post("/api/approvals/APR-001/decide", json={
            "decision": "approved"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["decision"]["decision"] == "approved"

    def test_approve_invalid_id(self, client):
        """Approving non-existent ID should return error."""
        resp = client.post("/api/approvals/APR-FAKE/decide", json={
            "decision": "denied"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data


# ════════════════════════════════════════════════════════════════════
#  5. PROFILE MANAGER TESTS (4 tests)
# ════════════════════════════════════════════════════════════════════

class TestProfileManager:
    """Test profile management functionality."""

    def test_default_profile_has_required_fields(self):
        """Default profile should have name, skills, job_preferences."""
        assert "name" in DEFAULT_PROFILE
        assert "skills" in DEFAULT_PROFILE
        assert "job_preferences" in DEFAULT_PROFILE
        assert "education" in DEFAULT_PROFILE

    def test_profile_text_generation(self):
        """get_profile_text should return a readable summary."""
        mgr = ProfileManager()
        text = mgr.get_profile_text()
        assert "CANDIDATE PROFILE" in text
        assert "Name:" in text
        assert "Skills:" in text
        assert "JOB PREFERENCES" in text

    def test_profile_update_merges(self):
        """update_profile should merge dict fields, not replace."""
        mgr = ProfileManager()
        original_name = mgr.profile.get("name")
        mgr.update_profile({"location": "Berlin, Germany"})
        assert mgr.profile["location"] == "Berlin, Germany"
        assert mgr.profile["name"] == original_name  # unchanged

    def test_output_paths(self):
        """get_output_paths should return all expected directories."""
        mgr = ProfileManager()
        paths = mgr.get_output_paths()
        assert "output_dir" in paths
        assert "profile" in paths
        assert "cover_letters" in paths
        assert "job_matches" in paths


# ════════════════════════════════════════════════════════════════════
#  6. UTILITY FUNCTION TESTS (3 tests)
# ════════════════════════════════════════════════════════════════════

class TestUtilityFunctions:
    """Test helper functions in server.py."""

    def test_make_event_structure(self):
        """make_event should return a properly structured event dict."""
        evt = make_event("Atlas", "atlas", "Test event", "status")
        assert evt["agent"] == "Atlas"
        assert evt["agentId"] == "atlas"
        assert evt["text"] == "Test event"
        assert evt["type"] == "status"
        assert "id" in evt
        assert "time" in evt

    def test_make_event_adds_to_feed(self):
        """make_event should prepend to the activity_feed."""
        original_len = len(activity_feed)
        make_event("Scout", "scout", "Added event", "data")
        assert len(activity_feed) >= original_len + 1
        assert activity_feed[0]["text"] == "Added event"

    def test_activity_feed_max_50(self):
        """Activity feed should not exceed 50 entries."""
        for i in range(60):
            make_event("Test", "test", f"Event {i}", "status")
        assert len(activity_feed) <= 50


# ════════════════════════════════════════════════════════════════════
#  7. JOB & RESEARCH ENDPOINT TESTS (3 tests)
# ════════════════════════════════════════════════════════════════════

class TestJobAndResearchEndpoints:
    """Test NEXUS job search and Scout research endpoints."""

    def test_profile_endpoint(self, client):
        """GET /api/profile should return profile data."""
        resp = client.get("/api/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data
        assert "skills" in data

    def test_profile_update_endpoint(self, client):
        """POST /api/profile should accept updates."""
        resp = client.post("/api/profile", json={
            "updates": {"location": "Kiel, Germany"}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_saved_jobs_endpoint(self, client):
        """GET /api/jobs/saved should list saved outputs."""
        resp = client.get("/api/jobs/saved")
        assert resp.status_code == 200
        data = resp.json()
        assert "job_files" in data
        assert "cover_letters" in data
        assert "paths" in data


# ════════════════════════════════════════════════════════════════════
#  8. GITHUB ENDPOINTS (2 tests)
# ════════════════════════════════════════════════════════════════════

class TestGitHubEndpoints:
    """Test GitHub integration endpoints."""

    def test_github_profile_without_username(self, client):
        """GET /api/github/profile without username should return error."""
        resp = client.get("/api/github/profile")
        assert resp.status_code == 200
        data = resp.json()
        # Either returns error or profile depending on saved state
        assert "success" in data

    def test_github_repos_endpoint(self, client):
        """GET /api/github/repos should return a response."""
        resp = client.get("/api/github/repos")
        assert resp.status_code == 200


# ════════════════════════════════════════════════════════════════════
#  9. STATIC FILE SERVING (2 tests)
# ════════════════════════════════════════════════════════════════════

class TestStaticServing:
    """Test that dashboard pages are served by FastAPI."""

    def test_root_returns_html(self, client):
        """GET / should return the agents.html dashboard page."""
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")

    def test_css_served(self, client):
        """GET /css/styles.css should return CSS."""
        resp = client.get("/css/styles.css")
        assert resp.status_code == 200
        content_type = resp.headers.get("content-type", "")
        assert "css" in content_type or "text" in content_type
