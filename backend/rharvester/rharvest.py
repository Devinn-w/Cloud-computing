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

# Keywords to match
KEYWORDS = ["donald trump", "tariff", "tariffs","trump", "make america great again","trumpism","trumpian","45th president"]

def read_credential(name: str) -> str:
    try:
        with open(f"/configs/default/shared-data/{name}", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Credential file {name} not found")
        return ""

# Simple keyword match
def contains_keywords(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)


def remove_html_tags(text: str) -> str:
    clean = re.compile('<.*?>')
    return unescape(re.sub(clean, '', text))


# Load last processed Reddit post ID from Elasticsearch
def load_last_post_id(es_client) -> str:
    try:
        doc = es_client.get(index="reddit-lastid", id="australia")
        return doc["_source"]["last_id"]
    except Exception:
        return ""

# Save the most recent post ID after each run
def save_last_post_id(es_client, last_id: str):
    try:
        es_client.index(
            index="reddit-lastid",
            id="australia",
            document={"last_id": last_id}
        )
    except Exception as e:
        logger.error(f"Failed to write last_id to Elasticsearch: {e}")

# Main function
def main():
    matches = 0
    es_user = read_credential("ES_USERNAME")
    es_pass = read_credential("ES_PASSWORD")

    # Elasticsearch client 
    es_client: Elasticsearch = Elasticsearch(
    'https://elasticsearch-master.elastic.svc.cluster.local:9200',
    verify_certs=False,
    ssl_show_warn=False,
    basic_auth=(es_user, es_pass)
    )

    # Reddit API
    reddit = Reddit(
        client_id="Ku89M9J60Btb3X10HJVeaw",
        client_secret="YDdSCPyuomG0oXDBwFOKbAZa9tKwkw",
        user_agent="AU Sentiment Harvester by /u/Devinn_W"
    )

    # Load last post ID
    last_id = load_last_post_id(es_client)
    logger.info(f"Last known post ID: {last_id}")

    newest_id = ""  # To track the newest post this run

    try:
        submissions = reddit.subreddit("australia").new(limit=50)

        for post in submissions:
            if post.id == last_id:
                logger.info(f"Reached last known post ID: {last_id}, stopping fetch.")
                continue

            if not newest_id:
                newest_id = post.id  # Save the newest post ID

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

                doc_id = f"{post.id}-{created_at.replace(':', '-')}"

                try:
                    es_client.index(
                        index='reddit-posts',
                        id=doc_id,
                        document=doc
                    )
                    logger.info(f"Indexed Reddit post {doc_id}")
                except Exception as e:
                    logger.error(f"Failed to index doc {doc_id}: {e}")

        if newest_id:
            save_last_post_id(es_client, newest_id)
            logger.info(f"Updated last known post ID to: {newest_id}")

        logger.info(f"Indexed {matches} new Reddit posts")

    except Exception as e:
        logger.error(f"[Reddit ERROR] {e}")
        return json.dumps({"status": "error", "message": str(e)})

    return json.dumps({"status": "ok", "indexed_posts": matches})


