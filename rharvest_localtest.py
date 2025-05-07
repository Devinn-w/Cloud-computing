from typing import List, Dict, Any
from praw import Reddit
import json
import time
import logging

KEYWORDS = ["trump", "tariff"]


try:
    from flask import current_app
    logger = current_app.logger
except RuntimeError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def contains_keywords(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)


def main() -> str:
    reddit = Reddit(
        client_id='Ku89M9J60Btb3X10HJVeaw',
        client_secret='YDdSCPyuomG0oXDBwFOKbAZa9tKwkw',
        user_agent='AU Sentiment Harvester by /u/Devinn_W'
    )

    results: List[Dict[str, Any]] = []
    try:
        submissions = reddit.subreddit('australia').search("trump tariff", sort="new", limit=30)

        for submission in submissions:
            fulltext = f"{submission.title} {submission.selftext}"
            if contains_keywords(fulltext):
                results.append({
                    "source": "reddit",
                    "user": submission.author.name if submission.author else "N/A",
                    "title": submission.title,
                    "content": submission.selftext,
                    "created_at": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(submission.created_utc))
                })

        logger.info(f"Harvested {len(results)} reddit posts with keywords")

    except Exception as e:
        logger.error(f"[Reddit ERROR] {e}")

    return json.dumps(results, default=str)

if __name__ == "__main__":
    print(main())