import json
from typing import List, Optional, Dict, Any
from flask import current_app, request, jsonify
from elasticsearch8 import Elasticsearch
from string import Template

#date_range_expr = Template("{\"range\": {\"created_at\": {\"gte\": \"${start} 00:00:00\", \"lte\": \"${end} 23:59:59\"}}}")
#keyword_expr = Template("{\"match\": {\"matched_keywords\": \"${keyword}\"}}")

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

    es_client: Elasticsearch = Elasticsearch(
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs=False,
        ssl_show_warn=False,
        basic_auth=(es_user, es_pass)
    )

    req = request

    start: Optional[str] = req.headers.get("X-Fission-Params-Start")
    end: Optional[str] = req.headers.get("X-Fission-Params-End")
    keyword: Optional[str] = req.headers.get("X-Fission-Params-Keyword")
    exclude: Optional[str] = req.headers.get("X-Fission-Params-Exclude", "")
    
    index: str = req.headers.get("X-Fission-Params-Source", "mastodon-posts")

    filters = []
    if start and end:
        filters.append({
            "range": {
                "created_at": {
                    "gte": f"{start} 00:00:00",
                    "lte": f"{end} 23:59:59"
                }
            }
        })

    if keyword:
        keywords = [k.strip() for k in keyword.split(",") if k.strip()]
        filters.append({
            "bool": {
                "should": [{"match": {"matched_keywords": k}} for k in keywords],
                "minimum_should_match": 1
            }
        })

    if exclude:
        exs = [e.strip() for e in exclude.split(",") if e.strip()]
        filters.append({
            "bool": {
                "must_not": [
                    {"term": {"matched_keywords": e}} for e in exs
                ]
            }
        })

    filters.append({
        "range": {
            "sentiment_score": {
                "lte": 1.0
            }
        }
    })

    if not (start and end) and not keyword:
        return jsonify({"error": "Please Provide X-Fission-Params-Start+X-Fission-Params-End OR X-Fission-Params-Keyword in Headers"}), 400

    query_body = {
        "query": {
            "bool": {
                "filter": filters
            }
        },
        "aggs": {
            "keywords": {
                "terms": {"field": "matched_keywords"},
                "aggs": {
                    "avg_sentiment": {
                        "avg": {"field": "sentiment_score"}
                    }
                }
            }
        },
        "size": 0
    }

    current_app.logger.info(f"Querying index: {index}, from {start} to {end}, keyword={keyword}")
    
    try:
        res: Dict[str, Any] = es_client.search(index=index, body=query_body)
        buckets: List[Dict[str, Any]] = res.get("aggregations", {}).get("keywords", {}).get("buckets", [])
        return jsonify([
            {
                "keyword": b["key"],
                "count": b["doc_count"],
                "avg_sentiment": round(b["avg_sentiment"]["value"] or 0.0, 3)
            } for b in buckets
        ])
    except Exception as e:
        current_app.logger.error(f"Aggregation failed: {e}")
        return jsonify({"error": str(e)}), 500