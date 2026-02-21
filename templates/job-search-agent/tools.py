"""
AI Job Search Agent — Tools
Multi-source job search: Remotive (worldwide) + Arbeitnow (Europe).
All free, no API keys needed for job data.
"""

import httpx
from datetime import datetime


class JobTools:
    """Search multiple free job APIs and merge results."""

    async def search_remotive(self, query="software developer", limit=20):
        """Search remote jobs via Remotive.com API. Free, no key needed."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://remotive.com/api/remote-jobs",
                    params={"category": "software-dev", "search": query, "limit": limit},
                )
                data = resp.json()
                jobs = []
                for j in data.get("jobs", [])[:limit]:
                    jobs.append({
                        "title": j.get("title", ""),
                        "company": j.get("company_name", ""),
                        "location": j.get("candidate_required_location", "Worldwide"),
                        "type": j.get("job_type", "full_time"),
                        "salary": j.get("salary", "Not specified"),
                        "posted": j.get("publication_date", "")[:10],
                        "url": j.get("url", ""),
                        "tags": j.get("tags", []),
                        "description": (j.get("description", "")[:500] + "...") if j.get("description") else "",
                        "source": "Remotive",
                    })
                return {"success": True, "source": "Remotive", "total": len(jobs), "jobs": jobs}
        except Exception as e:
            return {"success": False, "error": str(e), "source": "Remotive", "jobs": []}

    async def search_arbeitnow(self, query="software", page=1):
        """Search European jobs via Arbeitnow.com API. Free, no key needed."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://www.arbeitnow.com/api/job-board-api",
                    params={"page": page},
                )
                data = resp.json()
                all_jobs = data.get("data", [])
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
                        "description": (j.get("description", "")[:500] + "...") if j.get("description") else "",
                        "source": "Arbeitnow",
                    })
                return {"success": True, "source": "Arbeitnow", "total": len(jobs), "jobs": jobs}
        except Exception as e:
            return {"success": False, "error": str(e), "source": "Arbeitnow", "jobs": []}

    async def search_all(self, query="software developer", limit=10):
        """Search all sources and merge results."""
        all_jobs = []
        sources = []
        errors = []

        remotive = await self.search_remotive(query=query, limit=limit)
        if remotive["success"]:
            all_jobs.extend(remotive["jobs"])
            sources.append("Remotive")
        else:
            errors.append(f"Remotive: {remotive.get('error')}")

        arbeitnow = await self.search_arbeitnow(query=query)
        if arbeitnow["success"]:
            all_jobs.extend(arbeitnow["jobs"])
            sources.append("Arbeitnow")
        else:
            errors.append(f"Arbeitnow: {arbeitnow.get('error')}")

        all_jobs.sort(key=lambda j: j.get("posted", ""), reverse=True)
        return {
            "success": len(all_jobs) > 0,
            "sources": sources,
            "total": len(all_jobs),
            "query": query,
            "jobs": all_jobs[:limit * 2],
            "errors": errors if errors else None,
        }

    def format_for_agent(self, data):
        """Format job results as context string for the AI agent."""
        if not data.get("success"):
            return f"[Job search failed: {data.get('error', 'No results')}]"
        lines = [f"Found {data['total']} jobs for '{data['query']}':\n"]
        for i, j in enumerate(data.get("jobs", [])[:10], 1):
            lines.append(
                f"{i}. {j['title']} at {j['company']}\n"
                f"   Location: {j['location']} | Type: {j['type']} | Salary: {j['salary']}\n"
                f"   Posted: {j['posted']} | Source: {j['source']}\n"
                f"   URL: {j['url']}\n"
            )
        return "\n".join(lines)
