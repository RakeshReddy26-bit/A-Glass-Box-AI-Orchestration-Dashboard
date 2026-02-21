"""
AI Research Agent — News & Data Tools
Fetches real-time news via NewsAPI for market research and trend analysis.
"""

import os
import httpx
from datetime import datetime, timedelta


class ResearchTools:
    """Real data sources for market research."""

    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")

    def is_configured(self):
        return bool(self.newsapi_key) and self.newsapi_key != "YOUR_NEWSAPI_KEY_HERE"

    async def search_news(self, query, page_size=10, days_back=30):
        """Search news articles via NewsAPI. Free tier: 100 requests/day."""
        if not self.is_configured():
            return {"success": False, "error": "NewsAPI key not configured. Add NEWSAPI_KEY to .env", "articles": []}

        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": query,
                        "pageSize": page_size,
                        "sortBy": "relevancy",
                        "language": "en",
                        "from": from_date,
                        "apiKey": self.newsapi_key,
                    },
                )
                data = resp.json()
                if data.get("status") != "ok":
                    return {"success": False, "error": data.get("message", "NewsAPI error"), "articles": []}

                articles = []
                for a in data.get("articles", [])[:page_size]:
                    articles.append({
                        "title": a.get("title", ""),
                        "source": a.get("source", {}).get("name", "Unknown"),
                        "author": a.get("author", ""),
                        "description": a.get("description", ""),
                        "url": a.get("url", ""),
                        "published": a.get("publishedAt", "")[:10],
                        "content": (a.get("content", "") or "")[:500],
                    })
                return {"success": True, "total": len(articles), "query": query, "articles": articles}
        except Exception as e:
            return {"success": False, "error": str(e), "articles": []}

    async def get_headlines(self, category="technology", country="us", page_size=10):
        """Fetch top headlines by category."""
        if not self.is_configured():
            return {"success": False, "error": "NewsAPI key not configured", "articles": []}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={
                        "category": category,
                        "country": country,
                        "pageSize": page_size,
                        "apiKey": self.newsapi_key,
                    },
                )
                data = resp.json()
                if data.get("status") != "ok":
                    return {"success": False, "error": data.get("message", "Error"), "articles": []}

                articles = []
                for a in data.get("articles", [])[:page_size]:
                    articles.append({
                        "title": a.get("title", ""),
                        "source": a.get("source", {}).get("name", ""),
                        "description": a.get("description", ""),
                        "url": a.get("url", ""),
                        "published": a.get("publishedAt", "")[:10],
                    })
                return {"success": True, "category": category, "total": len(articles), "articles": articles}
        except Exception as e:
            return {"success": False, "error": str(e), "articles": []}

    def format_articles(self, data):
        """Format articles as context string for AI analysis."""
        if not data.get("success"):
            return f"[News search failed: {data.get('error')}]"
        lines = [f"NEWS DATA — {data.get('total', 0)} articles for '{data.get('query', 'topic')}':\n"]
        for i, a in enumerate(data.get("articles", []), 1):
            lines.append(
                f"{i}. {a['title']}\n"
                f"   Source: {a['source']} | Published: {a['published']}\n"
                f"   {a.get('description', '')}\n"
            )
        return "\n".join(lines)
