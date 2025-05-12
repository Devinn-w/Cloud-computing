import logging
import json
from typing import List, Optional, Dict, Any
from flask import current_app, request, jsonify
from elasticsearch8 import Elasticsearch
from collections import defaultdict
from string import Template

date_expr = Template('''{
  "range": {
    "created_at": {
      "gte": "${date} 00:00:00",
      "lte": "${date} 23:59:59"
    }
  }
}''')

keyword_expr = Template('''{
  "match": {
    "matched_keywords": "${keyword}"
  }
}''')

def read_credential(name: str) -> str:
    path = f"/configs/default/shared-data/{name}"
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        current_app.logger.error(f"Credential file {path} not found")
        return ""
    
def main() -> Dict[str, Any]:

    es_user = read_credential("ES_USERNAME")
    es_pass = read_credential("ES_PASSWORD")

    # Initialize Elasticsearch client with type annotation
    es_client: Elasticsearch = Elasticsearch(
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs=False,
        ssl_show_warn=False,
        basic_auth=(es_user, es_pass)
    )

    req = request
    date: Optional[str] = req.headers.get("X-Fission-Params-Date")
    keyword: Optional[str] = req.headers.get("X-Fission-Params-Keyword")

    filters = []
    if date:
        filters.append(json.loads(date_expr.substitute(date=date)))
    if keyword:
        filters.append(json.loads(keyword_expr.substitute(keyword=keyword)))

    # Eliminate abnormal sentiment values （score = 2.0）
    filters.append({
        "range": {
            "sentiment_score": {
                "lte": 1.0
            }
        }
    })

    if not filters:
        return {"error": "Must specify at least one of 'date' or 'keyword'"}, 400


    # Build dynamic query based on parameters
    query_body = {
        "query": {
            "bool": {
                "filter": filters
            }
        },
        "aggs": {
            "keywords": {
                "terms": {
                    "field": "matched_keywords",
                },
                "aggs": {
                    "avg_sentiment": {
                        "avg": {
                            "field": "sentiment_score"
                        }
                    }
                }
            }
        }
    }

    current_app.logger.info(
        f'Executing keyword aggregation for '
        f'Date: {date}' +
        (f' Keyword: {keyword}' if keyword else ''))
    
    try:
        res: Dict[str, Any] = es_client.search(
            index='mastodon-posts',
            body=query_body
        )

        agg_data: Dict[str, Any] = res.get('aggregations', {})
        keywords_agg: Dict[str, Any] = agg_data.get('keywords', {})
        buckets: List[Dict[str, Any]] = keywords_agg.get('buckets', [])

        result = []
        for bucket in buckets:
            result.append({
                "keyword": bucket["key"],
                "count": bucket["doc_count"],
                "avg_sentiment": round(bucket["avg_sentiment"]["value"] or 0.0, 3)
            })

        return jsonify(result)

    except Exception as e:
        current_app.logger.error(f"Aggregation failed: {e}")
        return {"error": str(e)}, 500