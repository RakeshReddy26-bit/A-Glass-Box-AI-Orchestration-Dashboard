
import tweepy
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def post_to_twitter(tweet: str) -> dict:
    try:
        client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
        )
        
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        
        response = client.create_tweet(text=tweet)
        tweet_id = response.data["id"]
        logger.info(f"Tweet posted: {tweet_id}")
        
        return {
            "status": "success",
            "tweet_id": tweet_id,
            "url": f"https://twitter.com/reddyk_rakesh/status/{tweet_id}"
        }
        
    except Exception as e:
        logger.error(f"Tweet failed: {e}")
        return {"status": "failed", "error": str(e)}