from elasticsearch8 import Elasticsearch
from flask import request, jsonify

def read_credential(name: str) -> str:
    path = f"/configs/default/shared-data/{name}"
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        current_app.logger.error(f"Credential file {path} not found")
        return ""

def main():
    es_user = read_credential("ES_USERNAME")
    es_pass = read_credential("ES_PASSWORD")

    req = request
    start = request.headers.get("X-Fission-Params-Start")
    end   = request.headers.get("X-Fission-Params-End")
    
    if not start or not end:
        return {"error": "Missing X-Fission-Params-Start or End"}

    try:
        es = Elasticsearch(
            "https://elasticsearch-master.elastic.svc.cluster.local:9200",
            verify_certs=False,
            ssl_show_warn=False,
            basic_auth=("elastic", "elastic")
        )

        index = "mastodon-posts"

        # Shared base query for time range
        base_query = {
            "query": {
                "range": {
                    "created_at": {
                        "gte": f"{start} 00:00:00",
                        "lte": f"{end} 23:59:59"
                    }
                }
            },
            "size": 1
        }

        # Most positive
        query_pos = base_query.copy()
        query_pos["sort"] = [{"sentiment_score": "desc"}]
        res_pos = es.search(index=index, body=query_pos)

        # Most negative
        query_neg = base_query.copy()
        query_neg["sort"] = [{"sentiment_score": "asc"}]
        res_neg = es.search(index=index, body=query_neg)

        def extract_doc(hit):
            if not hit:
                return None
            src = hit[0]["_source"]
            return {
                "user": src.get("user", "unknown"),
                "content": src.get("content", "[No content]"),
                "sentiment_score": round(src.get("sentiment_score", 0), 4),
                "matched_keywords": src.get("matched_keywords", [])
            }

        most_pos = extract_doc(res_pos["hits"]["hits"])
        most_neg = extract_doc(res_neg["hits"]["hits"])

        result = {
            "most_positive": most_pos,
            "most_negative": most_neg
        }

        return jsonify(result)

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify({"error": str(e)}), 500