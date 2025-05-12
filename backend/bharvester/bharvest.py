import logging
from atproto import Client
from analyzer.sentiment import analyze_sentiment
from elasticsearch8 import Elasticsearch


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


KEYWORDS = ["Donald Trump", "Trump", "tariff", "tariffs"]
AU_KEYWORDS = [
    "australia", "australian", "aussie",
    "melbourne", "sydney", "brisbane", "perth", "adelaide",
    "canberra", "tasmania", "darwin", "down under"
]
ES_INDEX = "bluesky-posts"
MAX_PAGES = 100  

def contains_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in KEYWORDS)

def is_au_related(text: str) -> bool:
    text_lower = text.lower()
    return any(au_kw in text_lower for au_kw in AU_KEYWORDS)

def main():
    # Initialize Elasticsearch
    es_client: Elasticsearch = Elasticsearch(
        'https://elasticsearch-master.elastic.svc.cluster.local:9200', 
        verify_certs=False,
        ssl_show_warn=False,
        basic_auth=('elastic', 'elastic')
    )

    # Initialize Bluesky client
    client = Client()
    handle = "devinn12.bsky.social"
    app_password = "evhp-3gto-kj6g-ewal"

    try:
        profile = client.login(handle, app_password)
        logger.info(f"Logged in to Bluesky as @{profile.handle}")
    except Exception as e:
        logger.error(f"Failed to log in to Bluesky: {e}")
        return

    total_indexed = 0

    for keyword in KEYWORDS:
        logger.info(f"Searching posts for keyword: '{keyword}'")
        seen_cursors = set()
        page_count = 0
        cursor = None

        while page_count < MAX_PAGES:
            try:
                params = {"q": keyword, "limit": 100}
                if cursor:
                    params["cursor"] = cursor
                response = client.app.bsky.feed.search_posts(params)
            except Exception as e:
                logger.error(f"Search error for '{keyword}' (cursor={cursor}): {e}")
                break

            posts = response.posts or []
            if not posts:
                logger.info("No posts returned, ending search.")
                break

            logger.info(f"Fetched {len(posts)} posts for '{keyword}' (page {page_count + 1})")

            for post in posts:
                text = post.record.text or ""
                created_at = post.record.created_at
                author_handle = post.author.handle if post.author and post.author.handle else None
                uri = post.uri

                # It must simultaneously meet the following requirements: Keywords related to Australia
                if not (contains_keywords(text) and is_au_related(text)):
                    continue

                sentiment_score = analyze_sentiment(text)

                doc = {
                    "id": uri,
                    "user": author_handle,
                    "content": text,
                    "created_at": created_at,
                    "source": "bluesky-au",
                    "sentiment_score": sentiment_score
                }

                try:
                    es_client.index(index=ES_INDEX, id=uri, document=doc)
                    total_indexed += 1
                    logger.info(f"Indexed AU post {uri}")
                except Exception as e:
                    logger.error(f"Failed to index post {uri}: {e}")

            new_cursor = response.cursor
            if not new_cursor or new_cursor in seen_cursors:
                logger.info("No new cursor or repeated cursor. Stopping pagination.")
                break

            seen_cursors.add(new_cursor)
            cursor = new_cursor
            page_count += 1

    logger.info(f"Done. Total indexed AU documents: {total_indexed}")

