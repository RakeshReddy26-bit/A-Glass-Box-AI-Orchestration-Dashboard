"""
Glass Box AI Dashboard — GitHub Integration
Connects to GitHub API (no token needed for public repos).
Shows commit activity, repos, languages, and auto-updates the profile.
"""

import httpx
from datetime import datetime, timedelta


GITHUB_API = "https://api.github.com"


class GitHubTools:
    """Fetch GitHub profile, repos, commits, and contribution data."""

    def __init__(self, username: str = ""):
        self.username = username
        self.headers = {"Accept": "application/vnd.github+json"}

    def set_username(self, username: str):
        self.username = username

    # ── User Profile ──────────────────────────────────────────────

    async def get_profile(self):
        """Fetch GitHub user profile."""
        if not self.username:
            return {"success": False, "error": "GitHub username not set"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{GITHUB_API}/users/{self.username}",
                    headers=self.headers,
                )
                if resp.status_code != 200:
                    return {"success": False, "error": f"GitHub user not found: {resp.status_code}"}
                d = resp.json()
                return {
                    "success": True,
                    "profile": {
                        "username": d.get("login", ""),
                        "name": d.get("name", ""),
                        "bio": d.get("bio", ""),
                        "avatar": d.get("avatar_url", ""),
                        "url": d.get("html_url", ""),
                        "public_repos": d.get("public_repos", 0),
                        "followers": d.get("followers", 0),
                        "following": d.get("following", 0),
                        "location": d.get("location", ""),
                        "company": d.get("company", ""),
                        "blog": d.get("blog", ""),
                        "created_at": d.get("created_at", "")[:10],
                    },
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Repositories ──────────────────────────────────────────────

    async def get_repos(self, sort="updated", limit=20):
        """Fetch user's public repositories sorted by last update."""
        if not self.username:
            return {"success": False, "error": "GitHub username not set", "repos": []}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{GITHUB_API}/users/{self.username}/repos",
                    headers=self.headers,
                    params={
                        "sort": sort,
                        "direction": "desc",
                        "per_page": min(limit, 100),
                        "type": "owner",
                    },
                )
                if resp.status_code != 200:
                    return {"success": False, "error": f"HTTP {resp.status_code}", "repos": []}

                repos = []
                for r in resp.json()[:limit]:
                    repos.append({
                        "name": r.get("name", ""),
                        "description": r.get("description", "") or "",
                        "url": r.get("html_url", ""),
                        "language": r.get("language", ""),
                        "stars": r.get("stargazers_count", 0),
                        "forks": r.get("forks_count", 0),
                        "open_issues": r.get("open_issues_count", 0),
                        "is_fork": r.get("fork", False),
                        "created": r.get("created_at", "")[:10],
                        "updated": r.get("updated_at", "")[:10],
                        "pushed": r.get("pushed_at", "")[:10] if r.get("pushed_at") else "",
                        "topics": r.get("topics", []),
                        "size_kb": r.get("size", 0),
                        "default_branch": r.get("default_branch", "main"),
                    })

                return {"success": True, "total": len(repos), "repos": repos}

        except Exception as e:
            return {"success": False, "error": str(e), "repos": []}

    # ── Recent Commits ────────────────────────────────────────────

    async def get_recent_commits(self, repo_name: str = "", limit=15):
        """Fetch recent commits. If repo_name given, from that repo. Else from all repos."""
        if not self.username:
            return {"success": False, "error": "GitHub username not set", "commits": []}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if repo_name:
                    # Commits for specific repo
                    resp = await client.get(
                        f"{GITHUB_API}/repos/{self.username}/{repo_name}/commits",
                        headers=self.headers,
                        params={"per_page": limit},
                    )
                    if resp.status_code != 200:
                        return {"success": False, "error": f"HTTP {resp.status_code}", "commits": []}

                    commits = []
                    for c in resp.json()[:limit]:
                        commit_info = c.get("commit", {})
                        author = commit_info.get("author", {})
                        commits.append({
                            "sha": c.get("sha", "")[:7],
                            "message": commit_info.get("message", "").split("\n")[0],
                            "date": author.get("date", "")[:10],
                            "time": author.get("date", "")[11:19] if len(author.get("date", "")) > 19 else "",
                            "repo": repo_name,
                            "url": c.get("html_url", ""),
                        })
                    return {"success": True, "total": len(commits), "repo": repo_name, "commits": commits}

                else:
                    # Recent events across all repos (public activity)
                    resp = await client.get(
                        f"{GITHUB_API}/users/{self.username}/events/public",
                        headers=self.headers,
                        params={"per_page": 50},
                    )
                    if resp.status_code != 200:
                        return {"success": False, "error": f"HTTP {resp.status_code}", "commits": []}

                    commits = []
                    for event in resp.json():
                        if event.get("type") == "PushEvent":
                            repo = event.get("repo", {}).get("name", "").split("/")[-1]
                            for c in event.get("payload", {}).get("commits", []):
                                commits.append({
                                    "sha": c.get("sha", "")[:7],
                                    "message": c.get("message", "").split("\n")[0],
                                    "date": event.get("created_at", "")[:10],
                                    "time": event.get("created_at", "")[11:19],
                                    "repo": repo,
                                    "url": f"https://github.com/{self.username}/{repo}/commit/{c.get('sha', '')}",
                                })
                                if len(commits) >= limit:
                                    break
                        if len(commits) >= limit:
                            break

                    return {"success": True, "total": len(commits), "commits": commits}

        except Exception as e:
            return {"success": False, "error": str(e), "commits": []}

    # ── Language Stats ────────────────────────────────────────────

    async def get_language_stats(self):
        """Aggregate language usage across all repos."""
        if not self.username:
            return {"success": False, "error": "GitHub username not set"}

        repos = await self.get_repos(limit=30)
        if not repos.get("success"):
            return repos

        lang_count = {}
        for r in repos["repos"]:
            lang = r.get("language")
            if lang:
                lang_count[lang] = lang_count.get(lang, 0) + 1

        # Sort by count
        sorted_langs = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)
        total = sum(c for _, c in sorted_langs)

        languages = []
        for lang, count in sorted_langs:
            languages.append({
                "language": lang,
                "repos": count,
                "percentage": round(count / total * 100, 1) if total > 0 else 0,
            })

        return {"success": True, "total_repos": len(repos["repos"]), "languages": languages}

    # ── Contribution Activity ─────────────────────────────────────

    async def get_activity_summary(self):
        """Get a summary of recent GitHub activity for the profile."""
        if not self.username:
            return {"success": False, "error": "GitHub username not set"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{GITHUB_API}/users/{self.username}/events/public",
                    headers=self.headers,
                    params={"per_page": 100},
                )
                if resp.status_code != 200:
                    return {"success": False, "error": f"HTTP {resp.status_code}"}

                events = resp.json()
                push_count = 0
                pr_count = 0
                issue_count = 0
                create_count = 0
                repos_active = set()
                days_active = set()

                for e in events:
                    etype = e.get("type", "")
                    date = e.get("created_at", "")[:10]
                    repo = e.get("repo", {}).get("name", "").split("/")[-1]
                    days_active.add(date)
                    repos_active.add(repo)

                    if etype == "PushEvent":
                        push_count += len(e.get("payload", {}).get("commits", []))
                    elif etype == "PullRequestEvent":
                        pr_count += 1
                    elif etype == "IssuesEvent":
                        issue_count += 1
                    elif etype == "CreateEvent":
                        create_count += 1

                return {
                    "success": True,
                    "summary": {
                        "total_events": len(events),
                        "commits": push_count,
                        "pull_requests": pr_count,
                        "issues": issue_count,
                        "repos_created": create_count,
                        "repos_active": list(repos_active)[:10],
                        "active_days": len(days_active),
                        "date_range": {
                            "from": min(days_active) if days_active else "",
                            "to": max(days_active) if days_active else "",
                        },
                    },
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Build portfolio context for agents ────────────────────────

    async def get_portfolio_text(self):
        """Generate a text summary of GitHub activity for agent prompts."""
        profile = await self.get_profile()
        repos = await self.get_repos(limit=10)
        langs = await self.get_language_stats()

        lines = ["GITHUB PORTFOLIO:\n"]

        if profile.get("success"):
            p = profile["profile"]
            lines.append(f"Username: {p['username']}")
            lines.append(f"Public Repos: {p['public_repos']}")
            lines.append(f"Followers: {p['followers']}")
            lines.append(f"Member since: {p['created_at']}\n")

        if langs.get("success"):
            top_langs = [f"{l['language']} ({l['repos']} repos)" for l in langs["languages"][:5]]
            lines.append(f"Top Languages: {', '.join(top_langs)}\n")

        if repos.get("success"):
            lines.append("Recent Projects:")
            for r in repos["repos"][:6]:
                stars = f" ⭐{r['stars']}" if r['stars'] > 0 else ""
                lines.append(f"  - {r['name']}: {r['description'][:80]}{stars} [{r['language'] or 'N/A'}]")

        return "\n".join(lines)

    # ── Build profile update data from GitHub ─────────────────────

    async def build_profile_update(self):
        """Create a dict of profile fields to update from GitHub data."""
        profile = await self.get_profile()
        repos = await self.get_repos(limit=15)
        langs = await self.get_language_stats()
        activity = await self.get_activity_summary()

        update = {}

        if profile.get("success"):
            p = profile["profile"]
            update["portfolio_links"] = {
                "github": p["url"],
            }

        if repos.get("success"):
            projects = []
            for r in repos["repos"][:8]:
                if not r["is_fork"]:
                    projects.append({
                        "name": r["name"],
                        "description": r["description"][:120] if r["description"] else "",
                        "language": r["language"] or "N/A",
                        "url": r["url"],
                        "stars": r["stars"],
                        "updated": r["updated"],
                    })
            update["github_projects"] = projects

        if langs.get("success"):
            update["github_languages"] = [
                {"language": l["language"], "repos": l["repos"], "pct": l["percentage"]}
                for l in langs["languages"]
            ]

        if activity.get("success"):
            update["github_activity"] = activity["summary"]

        return update
