import json
from elasticsearch8 import Elasticsearch
from string import Template
from typing import Dict, Any, Optional, List

date_range_expr = Template("{\"range\": {\"created_at\": {\"gte\": \"${start} 00:00:00\", \"lte\": \"${end} 23:59:59\"}}}")
keyword_expr = Template("{\"match\": {\"matched_keywords\": \"${keyword}\"}}")

def read_credential(name: str) -> str:
    try:
        with open(f"/configs/default/shared-data/{name}", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Credential file {name} not found")
        return ""

from flask import request

def main():
    req = request
    es_user = read_credential("ES_USERNAME")
    es_pass = read_credential("ES_PASSWORD")

    es_client: Elasticsearch = Elasticsearch(
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs=False,
        ssl_show_warn=False,
        basic_auth=(es_user, es_pass)
    )

    headers = req.headers
    start: Optional[str] = headers.get("X-Fission-Params-Start")
    end: Optional[str] = headers.get("X-Fission-Params-End")
    keyword: Optional[str] = headers.get("X-Fission-Params-Keyword")
    index: str = headers.get("X-Fission-Params-Source", "mastodon-posts")

    filters = []
    if start and end:
        filters.append(json.loads(date_range_expr.substitute(start=start, end=end)))
    if keyword:
        filters.append(json.loads(keyword_expr.substitute(keyword=keyword)))
    filters.append({"range": {"sentiment_score": {"lte": 1.0}}})

    if not filters:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Must specify at least start+end or keyword"})
        }

    query_body = {
    "query": {"bool": {"filter": filters}},
    "aggs": {
        "keywords": {
            "terms": {"field": "matched_keywords.keyword"},
            "aggs": {
                "avg_sentiment": {
                    "avg": {
                        "script": {
                            "source": "Double.parseDouble(doc['sentiment_score'].value)"
                        }
                    }
                }
            }
        }
    }
}

    print(f"Querying {index} from {start} to {end}, keyword={keyword}")

    try:
        res = es_client.search(index=index, body=query_body)
        buckets: List[Dict[str, Any]] = res.get("aggregations", {}).get("keywords", {}).get("buckets", [])
        return {
            "statusCode": 200,
            "body": json.dumps([
                {
                    "keyword": b["key"],
                    "count": b["doc_count"],
                    "avg_sentiment": round(b["avg_sentiment"]["value"] or 0.0, 3)
                } for b in buckets
            ])
        }
    except Exception as e:
        print(f"Aggregation failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }