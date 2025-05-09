from mastodon import Mastodon, MastodonError
from html import unescape
from typing import List, Dict, Any
import json
import time
import re
import logging
from analyzer.sentiment import analyze_sentiment
from elasticsearch8 import Elasticsearch

try:
    from flask import current_app
    logger = current_app.logger
except RuntimeError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

KEYWORDS = ["donald trump", "maga", "trump", "make america great again", "trumpism","trumpian","45th president"]

def remove_html_tags(text: str) -> str:
    clean = re.compile('<.*?>')
    return unescape(re.sub(clean, '', text))

def contains_keywords(text: str) -> bool:
    text = text.lower()
    return any(re.search(rf'\\b{re.escape(kw)}\\b', text) for kw in KEYWORDS)

def extract_matched_keywords(text: str) -> List[str]:
    text = text.lower()
    return [kw for kw in KEYWORDS if re.search(rf'\\b{re.escape(kw)}\\b', text)]

def load_last_post_id(es_client):
    try:
        resp = es_client.search(
            index="mastodon-posts",
            size=1,
            sort="created_at:desc",
            _source=["id"]
        )
        hits = resp["hits"]["hits"]
        return hits[0]["_source"]["id"] if hits else None
    except Exception as e:
        logger.warning(f"Failed to load last post ID: {e}")
        return None

def main():
    matches = 0
    """Harvest recent public posts from Mastodon timeline matching keywords."""
    
    # Initialize Elasticsearch client
    es_client: Elasticsearch = Elasticsearch(
        'https://elasticsearch-master.elastic.svc.cluster.local:9200', # local test
        verify_certs=False,
        ssl_show_warn=False,
        basic_auth=('elastic', 'elastic')
    )
    
    # Initialize Mastodon client with type annotation
    mastodon: Mastodon = Mastodon(
        access_token='468XGrkU6y2GYVnmTXF_VlxeJGF2GwXw8uOKLMFz7zY',
        api_base_url='https://mastodon.au',
        request_timeout=10
    )

    try:
        lastid = load_last_post_id(es_client)

        if not lastid:
            anchor_post = mastodon.timeline(timeline='public', limit=1, remote=True)[0]
            lastid = anchor_post['id']
            logger.info(f"Initial run — using anchor post ID: {lastid}")
        else:
            logger.info(f"Using last known post ID: {lastid}")

        posts = mastodon.timeline(timeline='public', since_id=lastid, limit=40, remote=True)

        for post in posts:
            content = remove_html_tags(post.get('content', ''))
            matched = extract_matched_keywords(content)
            created_at = post['created_at']

            if contains_keywords(content):
                matches += 1
                logger.info(f"Found {len(posts)} new posts since last_id: {lastid}")
                
                doc = {
                    'id': post['id'],
                    'source': 'mastodon',
                    'user': post['account']['acct'],
                    'content': content,
                    'created_at': created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'sentiment_score': analyze_sentiment(content),
                    'matched_keywords': matched
                }

                doc_id = str(post["id"])

                try:
                    index_response: Dict[str, Any] = es_client.index(
                        index='mastodon-posts',
                        id=doc_id,
                        document=doc
                    )
                    logger.info(f"Indexed {doc_id} — Version: {index_response['_version']}")
                except Exception as e:
                    logger.error(f"Failed to write doc {doc_id}: {e}")
                    logger.error(f"Doc content: {json.dumps(doc)}")

        logger.info(f"Indexed {matches} posts (matched keywords) from Mastodon since_id: {lastid}") 

    except MastodonError as e:
        logger.error(f"[Mastodon ERROR] {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "ok", "found_posts": len(posts), "indexed_posts": matches}

