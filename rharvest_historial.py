import logging
import re
import time
from datetime import datetime, timedelta, timezone
from html import unescape
from praw import Reddit
from elasticsearch8 import Elasticsearch
from analyzer.sentiment import analyze_sentiment


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


KEYWORDS = ["donald trump", "trump", "tariff", "tariffs"]
SUBREDDITS = ["worldnews", "AskReddit", "news", "politics", "trump"]
AU_SUBS = ["australia", "melbourne", "sydney", "brisbane", "perth", "adelaide"]
ES_INDEX = "reddit-trump-au"


def contains_keywords(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)

def remove_html_tags(text: str) -> str:
    clean = re.compile('<.*?>')
    return unescape(re.sub(clean, '', text))

def is_au_user(author) -> bool:
    try:
        posts = list(author.submissions.new(limit=5))
        comments = list(author.comments.new(limit=5))
        subs = set(p.subreddit.display_name.lower() for p in posts + comments)
        return any(sub in AU_SUBS for sub in subs)
    except Exception as e:
        logger.warning(f"Could not fetch user history: {e}")
        return False


def main():
    logger.info("Starting multi-subreddit harvest for last 3 months...")

    reddit = Reddit(
        client_id="Ku89M9J60Btb3X10HJVeaw",
        client_secret="YDdSCPyuomG0oXDBwFOKbAZa9tKwkw",
        user_agent="AU Sentiment Harvester by /u/Devinn_W"
    )

    es = Elasticsearch("http://localhost:9200", verify_certs=False)
    threshold = datetime.now(timezone.utc) - timedelta(days=90)
    indexed = 0

    for sub in SUBREDDITS:
        logger.info(f"Fetching from subreddit: {sub}")
        try:
            for post in reddit.subreddit(sub).new(limit=500):
                time.sleep(1)

                post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                if post_time < threshold:
                    break

                author = post.author
                if not author or not is_au_user(author):
                    continue

                content = f"{post.title} {post.selftext or ''}"
                if not contains_keywords(content):
                    continue

                clean = remove_html_tags(content)
                created = post_time.isoformat()

                doc = {
                    "id": post.id,
                    "user": author.name,
                    "subreddit": sub,
                    "content": clean,
                    "created_at": created,
                    "source": "reddit-multi-au-filtered",
                    "sentiment_score": analyze_sentiment(clean)
                }

                doc_id = f"{post.id}-{created.replace(':', '-')}"
                try:
                    es.index(index=ES_INDEX, id=doc_id, document=doc)
                    indexed += 1
                    logger.info(f"Indexed: {doc_id}")
                except Exception as e:
                    logger.warning(f"Failed to index {doc_id}: {e}")
        except Exception as e:
            logger.warning(f"Failed to fetch from subreddit {sub}: {e}")

    logger.info(f"Done. Total indexed: {indexed}")

if __name__ == "__main__":
    main()