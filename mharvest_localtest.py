from mastodon import Mastodon, MastodonError
from html import unescape
from typing import List, Dict, Any
import json
import time
import re
import logging


try:
    from flask import current_app
    logger = current_app.logger
except RuntimeError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

KEYWORDS = ["trump", "tariff"]

def remove_html_tags(text: str) -> str:
    clean = re.compile('<.*?>')
    return unescape(re.sub(clean, '', text))

def contains_keywords(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)

def main() -> str:
    """Harvest recent public posts from Mastodon timeline matching keywords."""

    mastodon: Mastodon = Mastodon(
        access_token='468XGrkU6y2GYVnmTXF_VlxeJGF2GwXw8uOKLMFz7zY',
        api_base_url='https://mastodon.au',
        request_timeout=10
    )

    results: List[Dict[str, Any]] = []
    try:
        anchor_post = mastodon.timeline(timeline='public', limit=1, remote=True)[0]
        lastid = anchor_post['id']
        time.sleep(5) 

        # # posts = mastodon.timeline(timeline='public', since_id=lastid, remote=True)
        # For the local test, I did not follow the sinceid=lastid that was commented out above. Instead, I used sinceid=lastid in the file used for fission.
        posts = mastodon.timeline(timeline='public', limit=100)
        for post in posts:
            content = remove_html_tags(post.get('content', ''))
            if contains_keywords(content):
                results.append({
                    "source": "mastodon",
                    "user": post["account"]["acct"],
                    "content": content,
                    "created_at": post["created_at"]
                })

        logger.info(f"Harvested {len(results)} mastodon posts with keywords")

    except MastodonError as e:
        logger.error(f"[Mastodon ERROR] {e}")

    return json.dumps(results, default=str)


if __name__ == "__main__":
    print(main())