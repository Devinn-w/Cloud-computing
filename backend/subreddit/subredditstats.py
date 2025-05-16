import json
from elasticsearch8 import Elasticsearch
from string import Template
from typing import Dict, Any, Optional, List
from flask import request

date_range_expr = Template("""
{
  "range": {
    "created_at": {
      "gte": "${start} 00:00:00",
      "lte": "${end} 23:59:59"
    }
  }
}
""")

def read_credential(name: str) -> str:
    try:
        with open(f"/configs/default/shared-data/{name}", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Credential file {name} not found")
        return ""

def main():
    req = request
    start: Optional[str] = req.headers.get("X-Fission-Params-Start")
    end: Optional[str] = req.headers.get("X-Fission-Params-End")

    if not start or not end:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing start or end date"})
        }

    es_user = read_credential("ES_USERNAME")
    es_pass = read_credential("ES_PASSWORD")

    es = Elasticsearch(
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs=False,
        ssl_show_warn=False,
        basic_auth=(es_user, es_pass)
    )

    filters = [json.loads(date_range_expr.substitute(start=start, end=end))]

    query_body = {
        "query": {"bool": {"filter": filters}},
        "aggs": {
            "subreddits": {
                "terms": {"field": "subreddit", "size": 100},
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
        },
        "size": 0
    }

    try:
        res = es.search(index="reddit-posts", body=query_body)
        buckets = res["aggregations"]["subreddits"]["buckets"]
        result = [
            {
                "subreddit": b["key"],
                "count": b["doc_count"],
                "avg_sentiment": round(b["avg_sentiment"]["value"] or 0.0, 3)
            }
            for b in buckets
        ]
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        print(f"Query error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
