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
    start = req.headers.get("X-Fission-Params-Start")
    end   = req.headers.get("X-Fission-Params-End")
    keyword = req.headers.get("X-Fission-Params-Keyword", "")
    exclude = req.headers.get("X-Fission-Params-Exclude", "")
    index = req.headers.get("X-Fission-Params-Source", "mastodon-posts")

    if not start or not end:
        return jsonify({"error": "X-Fission-Params-Start AND X-Fission-Params-End Provided At same time"}), 400
    
    filters = [
        {"range": {"created_at": {"gte": f"{start} 00:00:00", "lte": f"{end} 23:59:59"}}},
        {"range": {"sentiment_score": {"gte": -1.0, "lte": 1.0}}}
    ]
    if keyword:
        filters.append({"match": {"matched_keywords": keyword}})
    if exclude:
        exs = [e.strip() for e in exclude.split(",") if e.strip()]
        filters.append({
            "bool": {
                "must_not": [
                    {"term": {"matched_keywords": e}} for e in exs
                ]
            }
        })
    elif keyword:
        filters.append({"match": {"matched_keywords": keyword}})

    # Build dynamic query based on parameters
    query_body = {
        "query": {
            "bool": {
                "filter": filters
            }
        },
        "aggs": {
            "by_date": {
                "date_histogram": {
                    "field": "created_at",
                    "calendar_interval": "day",
                    "format": "yyyy-MM-dd"
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
    
    try:
        res = es_client.search(index=index, body=query_body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    buckets = res["aggregations"]["by_date"]["buckets"]
    result = []
    for b in buckets:
        date = b["key_as_string"]
        avg = b["avg_sentiment"]["value"]
        result.append({
            "created_at": date,
            "avg_sentiment": round(avg, 4)
        })
    return jsonify(result)