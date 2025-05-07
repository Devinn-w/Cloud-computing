import logging
import re
import json
import time
from typing import List, Dict, Any
from praw import Reddit
from elasticsearch8 import Elasticsearch
from analyzer.sentiment import analyze_sentiment
from html import unescape

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


KEYWORDS = ["Donald Trump", "Trump", "tariff", "tariffs"]


def remove_html_tags(text: str) -> str:
    clean = re.compile('<.*?>')
    return unescape(re.sub(clean, '', text))

def contains_keywords(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)

#Last Time via Elasticsearch 
def load_last_created_time(es_client) -> float:
    try:
        doc = es_client.get(index="reddit-lasttime", id="australia")
        return float(doc["_source"]["last_time"])
    except Exception:
        return 0.0

def save_last_created_time(es_client, new_time: float):
    try:
        es_client.index(
            index="reddit-lasttime",
            id="australia",
            document={"last_time": new_time}
        )
    except Exception as e:
        logger.error(f"Failed to write last_time to Elasticsearch: {e}")


def main():
    matches = 0


    es_client: Elasticsearch = Elasticsearch(
        "https://elasticsearch-master.elastic.svc.cluster.local:9200",
        verify_certs=False,
        ssl_show_warn=False,
        basic_auth=("elastic", "elastic")
    )


    reddit = Reddit(
        client_id="Ku89M9J60Btb3X10HJVeaw",
        client_secret="YDdSCPyuomG0oXDBwFOKbAZa9tKwkw",
        user_agent="AU Sentiment Harvester by /u/Devinn_W"
    )

    last_time = load_last_created_time(es_client)
    logger.info(f"Last known timestamp: {last_time}")
    new_max_time = last_time

    try:
        submissions = reddit.subreddit("australia").new(limit=50)

        for post in submissions:
            if post.created_utc <= last_time:
                continue

            content = f"{post.title} {post.selftext or ''}"
            content = remove_html_tags(content)

            if contains_keywords(content):
                matches += 1
                created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(post.created_utc))
                doc = {
                    'id': post.id,
                    'source': 'reddit',
                    'user': post.author.name if post.author else 'N/A',
                    'content': content,
                    'created_at': created_at,
                    'sentiment_score': analyze_sentiment(content)
                }

                timestamp = created_at.replace(":", "-").replace(".", "-")
                doc_id: str = f"{post.id}-{timestamp}"

                try:
                    es_client.index(
                        index='reddit-posts',
                        id=doc_id,
                        document=doc
                    )
                    logger.info(f"Indexed Reddit post {doc_id}")
                except Exception as e:
                    logger.error(f"Failed to write doc {doc_id}: {e}")
                    logger.error(f"Doc content: {json.dumps(doc)}")

            new_max_time = max(new_max_time, post.created_utc)

        save_last_created_time(es_client, new_max_time)
        logger.info(f"Updated last timestamp to: {new_max_time}")
        logger.info(f"Indexed {matches} new Reddit posts")

    except Exception as e:
        logger.error(f"[Reddit ERROR] {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "ok", "indexed_posts": matches}

