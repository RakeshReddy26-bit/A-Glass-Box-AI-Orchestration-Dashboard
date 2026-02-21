"""
Glass Box AI Dashboard — Scout Tools
Real data fetching: NewsAPI, SEC EDGAR, Yahoo Finance.
Each method returns structured data matching the dashboard's format.
"""

import os
import httpx
from datetime import datetime


class ScoutTools:
    """Real data sources for the Scout research agent."""

    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")

    async def search_news(self, query, page_size=5):
        """
        Search news articles via NewsAPI.org.
        Free tier: 100 requests/day.
        Returns list of article dicts.
        """
        if not self.newsapi_key or self.newsapi_key == "PASTE_YOUR_NEWSAPI_KEY_HERE":
            return {
                "success": False,
                "error": "NewsAPI key not configured. Add NEWSAPI_KEY to .env",
                "articles": [],
            }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": query,
                        "pageSize": page_size,
                        "sortBy": "publishedAt",
                        "language": "en",
                        "apiKey": self.newsapi_key,
                    },
                )
                data = resp.json()

                if data.get("status") != "ok":
                    return {
                        "success": False,
                        "error": data.get("message", "NewsAPI error"),
                        "articles": [],
                    }

                articles = []
                for a in data.get("articles", []):
                    articles.append({
                        "title": a.get("title", ""),
                        "source": a.get("source", {}).get("name", "Unknown"),
                        "publishedAt": a.get("publishedAt", ""),
                        "description": a.get("description", ""),
                        "url": a.get("url", ""),
                    })

                return {
                    "success": True,
                    "totalResults": data.get("totalResults", 0),
                    "articles": articles,
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "articles": [],
            }

    async def search_sec_filings(self, ticker, filing_type="10-K"):
        """
        Search SEC EDGAR for company filings.
        Free API, no key needed. Rate limit: 10 requests/second.
        """
        try:
            headers = {
                "User-Agent": "GlassBoxDashboard research@glassbox.dev",
                "Accept": "application/json",
            }

            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                resp = await client.get(
                    "https://efts.sec.gov/LATEST/search-index",
                    params={
                        "q": f'"{ticker}" AND "{filing_type}"',
                        "dateRange": "custom",
                        "startdt": "2023-01-01",
                        "enddt": datetime.now().strftime("%Y-%m-%d"),
                        "forms": filing_type,
                    },
                )

                if resp.status_code != 200:
                    # Try the full-text search endpoint instead
                    resp = await client.get(
                        f"https://efts.sec.gov/LATEST/search-index?q={ticker}&forms={filing_type}",
                    )

                data = resp.json()
                hits = data.get("hits", {}).get("hits", [])

                filings = []
                for hit in hits[:5]:
                    source = hit.get("_source", {})
                    filings.append({
                        "filingDate": source.get("file_date", ""),
                        "form": source.get("form_type", filing_type),
                        "company": source.get("entity_name", ticker),
                        "description": source.get("display_names", [""])[0] if source.get("display_names") else "",
                    })

                return {
                    "success": True,
                    "ticker": ticker,
                    "filingType": filing_type,
                    "total": len(filings),
                    "filings": filings,
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "ticker": ticker,
                "filings": [],
            }

    async def get_stock_price(self, ticker):
        """
        Get current stock price and summary via yfinance.
        Free, no API key needed.
        """
        try:
            import yfinance as yf

            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                "success": True,
                "ticker": ticker,
                "name": info.get("longName", ticker),
                "price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
                "previousClose": info.get("previousClose", 0),
                "marketCap": info.get("marketCap", 0),
                "peRatio": info.get("trailingPE", 0),
                "week52High": info.get("fiftyTwoWeekHigh", 0),
                "week52Low": info.get("fiftyTwoWeekLow", 0),
                "volume": info.get("volume", 0),
                "avgVolume": info.get("averageVolume", 0),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "ticker": ticker,
            }

    async def get_stock_history(self, ticker, period="6mo"):
        """
        Get historical price data via yfinance.
        """
        try:
            import yfinance as yf

            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            data_points = []
            for date, row in hist.iterrows():
                data_points.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"]),
                })

            return {
                "success": True,
                "ticker": ticker,
                "period": period,
                "dataPoints": len(data_points),
                "data": data_points[-10:],  # Last 10 for brevity
                "priceRange": {
                    "low": round(hist["Low"].min(), 2) if len(hist) > 0 else 0,
                    "high": round(hist["High"].max(), 2) if len(hist) > 0 else 0,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "ticker": ticker,
            }

    def format_for_agent(self, data, data_type="news"):
        """Format tool results as context for agent prompts."""
        if not data.get("success"):
            return f"[Data fetch failed: {data.get('error', 'Unknown error')}]"

        if data_type == "news":
            lines = [f"Found {data['totalResults']} articles:"]
            for a in data.get("articles", []):
                lines.append(f"- {a['title']} ({a['source']}, {a['publishedAt'][:10]})")
            return "\n".join(lines)

        elif data_type == "stock":
            return (
                f"{data['name']} ({data['ticker']}): "
                f"${data['price']:.2f} | "
                f"Market Cap: ${data['marketCap']:,.0f} | "
                f"P/E: {data['peRatio']:.1f} | "
                f"52w Range: ${data['week52Low']:.2f}-${data['week52High']:.2f}"
            )

        elif data_type == "filings":
            lines = [f"SEC filings for {data['ticker']} ({data['total']} found):"]
            for f in data.get("filings", []):
                lines.append(f"- {f['form']} filed {f['filingDate']} by {f['company']}")
            return "\n".join(lines)

        return str(data)
