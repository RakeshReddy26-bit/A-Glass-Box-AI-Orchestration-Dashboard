"""
Glass Box AI Dashboard — Job Hunter Tools
Fetches real job listings from free APIs.
Sources: Adzuna API (free tier), Remotive API (free), Arbeitnow API (free).
"""

import os
import httpx
from datetime import datetime, timedelta


class JobTools:
    """Real job search APIs for the Job Hunter pipeline."""

    def __init__(self):
        # Adzuna is optional (needs free signup at developer.adzuna.com)
        self.adzuna_app_id = os.getenv("ADZUNA_APP_ID", "")
        self.adzuna_api_key = os.getenv("ADZUNA_API_KEY", "")

    # ── Remotive (100% free, no key needed) ───────────────────────

    async def search_remotive(self, query="software developer", category="software-dev", limit=20):
        """
        Search remote jobs via Remotive.com API.
        Free, no API key needed. Returns remote-friendly jobs worldwide.
        Categories: software-dev, data, devops, design, product, marketing, etc.
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://remotive.com/api/remote-jobs",
                    params={
                        "category": category,
                        "search": query,
                        "limit": limit,
                    },
                )
                data = resp.json()
                jobs_raw = data.get("jobs", [])

                jobs = []
                for j in jobs_raw[:limit]:
                    jobs.append({
                        "title": j.get("title", ""),
                        "company": j.get("company_name", ""),
                        "location": j.get("candidate_required_location", "Worldwide"),
                        "type": j.get("job_type", "full_time"),
                        "salary": j.get("salary", "Not specified"),
                        "posted": j.get("publication_date", "")[:10],
                        "url": j.get("url", ""),
                        "tags": j.get("tags", []),
                        "description_snippet": (j.get("description", "")[:300] + "...")
                            if j.get("description") else "",
                        "source": "Remotive",
                    })

                return {
                    "success": True,
                    "source": "Remotive",
                    "total": len(jobs),
                    "query": query,
                    "jobs": jobs,
                }

        except Exception as e:
            return {"success": False, "error": str(e), "source": "Remotive", "jobs": []}

    # ── Arbeitnow (free, no key, Europe-focused) ──────────────────

    async def search_arbeitnow(self, query="software", page=1):
        """
        Search European jobs via Arbeitnow.com API.
        Free, no API key needed. Focused on Europe/Germany.
        Great for EU-based job seekers.
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://www.arbeitnow.com/api/job-board-api",
                    params={"page": page},
                )
                data = resp.json()
                all_jobs = data.get("data", [])

                # Filter by query keyword
                query_lower = query.lower()
                filtered = [
                    j for j in all_jobs
                    if query_lower in j.get("title", "").lower()
                    or query_lower in j.get("description", "").lower()
                    or query_lower in j.get("company_name", "").lower()
                    or any(query_lower in tag.lower() for tag in j.get("tags", []))
                ]

                jobs = []
                for j in filtered[:20]:
                    # created_at is a Unix timestamp (int), convert to date string
                    created = j.get("created_at")
                    if isinstance(created, (int, float)):
                        posted = datetime.fromtimestamp(created).strftime("%Y-%m-%d")
                    elif isinstance(created, str):
                        posted = created[:10]
                    else:
                        posted = ""

                    jobs.append({
                        "title": j.get("title", ""),
                        "company": j.get("company_name", ""),
                        "location": j.get("location", "Europe"),
                        "type": "remote" if j.get("remote", False) else "on-site",
                        "salary": "Not specified",
                        "posted": posted,
                        "url": j.get("url", ""),
                        "tags": j.get("tags", []),
                        "description_snippet": (j.get("description", "")[:300] + "...")
                            if j.get("description") else "",
                        "source": "Arbeitnow",
                    })

                return {
                    "success": True,
                    "source": "Arbeitnow (Europe)",
                    "total": len(jobs),
                    "query": query,
                    "jobs": jobs,
                }

        except Exception as e:
            return {"success": False, "error": str(e), "source": "Arbeitnow", "jobs": []}

    # ── Adzuna (free tier: 250 calls/day, needs signup) ───────────

    async def search_adzuna(self, query="python developer", location="europa", country="de", page=1):
        """
        Search jobs via Adzuna API. Free tier: 250 requests/day.
        Signup at developer.adzuna.com to get app_id and api_key.
        Supports: gb, de, fr, nl, at, ch, us, au, etc.
        """
        if not self.adzuna_app_id or not self.adzuna_api_key:
            return {
                "success": False,
                "error": "Adzuna API not configured. Free signup at developer.adzuna.com, then add ADZUNA_APP_ID and ADZUNA_API_KEY to .env",
                "source": "Adzuna",
                "jobs": [],
            }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}",
                    params={
                        "app_id": self.adzuna_app_id,
                        "app_key": self.adzuna_api_key,
                        "what": query,
                        "where": location,
                        "results_per_page": 20,
                        "content-type": "application/json",
                        "sort_by": "date",
                    },
                )
                data = resp.json()
                results = data.get("results", [])

                jobs = []
                for j in results:
                    salary_min = j.get("salary_min")
                    salary_max = j.get("salary_max")
                    salary_str = "Not specified"
                    if salary_min and salary_max:
                        salary_str = f"€{int(salary_min):,} - €{int(salary_max):,}"
                    elif salary_min:
                        salary_str = f"From €{int(salary_min):,}"

                    jobs.append({
                        "title": j.get("title", ""),
                        "company": j.get("company", {}).get("display_name", ""),
                        "location": j.get("location", {}).get("display_name", ""),
                        "type": "full_time",
                        "salary": salary_str,
                        "posted": j.get("created", "")[:10],
                        "url": j.get("redirect_url", ""),
                        "tags": j.get("category", {}).get("tag", "").split("/") if j.get("category") else [],
                        "description_snippet": (j.get("description", "")[:300] + "...")
                            if j.get("description") else "",
                        "source": "Adzuna",
                    })

                return {
                    "success": True,
                    "source": "Adzuna",
                    "total": data.get("count", len(jobs)),
                    "query": query,
                    "jobs": jobs,
                }

        except Exception as e:
            return {"success": False, "error": str(e), "source": "Adzuna", "jobs": []}

    # ── Search all sources at once ────────────────────────────────

    async def search_all(self, query="software developer", limit=10):
        """Search all available job sources and merge results."""
        all_jobs = []
        sources_used = []
        errors = []

        # Always search free sources
        remotive = await self.search_remotive(query=query, limit=limit)
        if remotive["success"]:
            all_jobs.extend(remotive["jobs"])
            sources_used.append("Remotive")
        else:
            errors.append(f"Remotive: {remotive.get('error')}")

        arbeitnow = await self.search_arbeitnow(query=query)
        if arbeitnow["success"]:
            all_jobs.extend(arbeitnow["jobs"])
            sources_used.append("Arbeitnow")
        else:
            errors.append(f"Arbeitnow: {arbeitnow.get('error')}")

        # Search Adzuna if configured
        if self.adzuna_app_id and self.adzuna_api_key:
            adzuna = await self.search_adzuna(query=query)
            if adzuna["success"]:
                all_jobs.extend(adzuna["jobs"])
                sources_used.append("Adzuna")
            else:
                errors.append(f"Adzuna: {adzuna.get('error')}")

        # Sort by date (most recent first)
        all_jobs.sort(key=lambda j: j.get("posted", ""), reverse=True)

        return {
            "success": len(all_jobs) > 0,
            "sources": sources_used,
            "total": len(all_jobs),
            "query": query,
            "jobs": all_jobs[:limit * 2],  # return up to 2x limit from merged
            "errors": errors if errors else None,
        }

    # ── Format for agent context ──────────────────────────────────

    def format_for_agent(self, data):
        """Format job search results as context string for agents."""
        if not data.get("success"):
            return f"[Job search failed: {data.get('error', 'No results')}]"

        lines = [f"Found {data['total']} jobs for '{data['query']}' from {', '.join(data.get('sources', [data.get('source', 'unknown')]))}:\n"]
        for i, j in enumerate(data.get("jobs", [])[:10], 1):
            lines.append(
                f"{i}. {j['title']} at {j['company']}\n"
                f"   Location: {j['location']} | Type: {j['type']} | Salary: {j['salary']}\n"
                f"   Posted: {j['posted']} | Source: {j['source']}\n"
                f"   URL: {j['url']}\n"
            )
        return "\n".join(lines)
