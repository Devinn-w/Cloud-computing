from flask import request, jsonify
from elasticsearch8 import Elasticsearch
from datetime import datetime

def read_credential(name: str) -> str:
    try:
        with open(f"/configs/default/shared-data/{name}", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def main():
    req = request
    headers = req.headers

    date: str = headers.get("X-Fission-Params-Date")
    index: str = headers.get("X-Fission-Params-Source", "mastodon-posts")

    if not date:
        return jsonify({"error": "Missing X-Fission-Params-Date"}), 400

    es_user = read_credential("ES_USERNAME")
    es_pass = read_credential("ES_PASSWORD")

    es = Elasticsearch(
        "https://elasticsearch-master.elastic.svc.cluster.local:9200",
        verify_certs=False,
        ssl_show_warn=False,
        basic_auth=(es_user, es_pass)
    )

    query = {
        "query": {
            "range": {
                "created_at": {
                    "gte": f"{date} 00:00:00",
                    "lte": f"{date} 23:59:59"
                }
            }
        },
        "aggs": {
            "per_minute": {
                "date_histogram": {
                    "field": "created_at",
                    "fixed_interval": "1m",
                    "format": "HH:mm"
                }
            }
        },
        "size": 0
    }

    try:
        res = es.search(index=index, body=query)
        buckets = res["aggregations"]["per_minute"]["buckets"]
        result = [{"time": b["key_as_string"], "count": b["doc_count"]} for b in buckets]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
