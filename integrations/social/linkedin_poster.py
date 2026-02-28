import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def get_access_token():
    response = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "client_credentials",
            "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
            "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET")
        }
    )
    return response.json().get("access_token")

def post_to_linkedin(content: str) -> dict:
    try:
        token = get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "author": f"urn:li:organization:{os.getenv('LINKEDIN_ORG_ID')}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        logger.info("LinkedIn post published")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"LinkedIn failed: {e}")
        return {"status": "failed", "error": str(e)}