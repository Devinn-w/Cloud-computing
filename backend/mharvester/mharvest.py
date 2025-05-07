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

KEYWORDS = ["Donald Trump", "Trump", "tariff", "tariffs"] 

def remove_html_tags(text: str) -> str:
    clean = re.compile('<.*?>')
    return unescape(re.sub(clean, '', text))

def contains_keywords(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)

def main() -> str:
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
        anchor_post = mastodon.timeline(timeline='public', limit=1, remote=True)[0]
        lastid = anchor_post['id']
        time.sleep(5) # Allow time window for new posts

        posts = mastodon.timeline(timeline='public', since_id=lastid, remote=True)

        for post in posts:
            content = remove_html_tags(post.get('content', ''))

            if contains_keywords(content):
                sentiment = analyze_sentiment(content)

                doc = {
                    'id': post['id'],
                    'source': 'mastodon',
                    'user': post['account']['acct'],
                    'content': content,
                    'created_at': post['created_at'],
                    'sentiment': sentiment
                }

                timestamp = str(post["created_at"]).replace(":", "-").replace(".", "-")
                doc_id: str = f'{post["id"]}-{timestamp}'

                index_response: Dict[str, Any] = es_client.index(
                    index='mastodon-posts',
                    id=doc_id,
                    body=doc
                )

                logger.info(
                    f"Indexed Mastodon post {doc_id} - "
                    f"Version: {index_response['_version']}"
                )

        logger.info(
            f"Indexed {len(posts)} total posts from Mastodon since_id: {lastid}"
        )

    except MastodonError as e:
        logger.error(f"[Mastodon ERROR] {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "ok", "indexed_posts": len(posts)}

