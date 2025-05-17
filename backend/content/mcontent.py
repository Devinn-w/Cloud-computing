from elasticsearch8 import Elasticsearch
from flask import request, jsonify, current_app
import json

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
    keyword_str = request.headers.get("X-Fission-Params-Keyword")
    
    if not start or not end:
        return {"error": "Missing X-Fission-Params-Start or End"}
    
    query_filter = [
        {
            "range": {
                "created_at": {
                    "gte": f"{start} 00:00:00",
                    "lte": f"{end} 23:59:59"
                }
            }
        }
    ]

    
    if keyword_str:
        keyword_list = [kw.strip() for kw in keyword_str.split(",") if kw.strip()]
        print("Keyword list received:", keyword_list)
        if keyword_list:
            query_filter.append({"terms": {"matched_keywords": keyword_list}})

    base_query = {
        "query": {
            "bool": {
                "must": query_filter
            }
        },
        "size": 1
    }

    try:
        
        es = Elasticsearch(
            "https://elasticsearch-master.elastic.svc.cluster.local:9200",
            verify_certs=False,
            ssl_show_warn=False,
            basic_auth=(es_user, es_pass)
        )

        index = "mastodon-posts"
        
        query_pos = json.loads(json.dumps(base_query))
        query_pos["sort"] = [{"sentiment_score": "desc"}]

        query_neg = json.loads(json.dumps(base_query))
        query_neg["sort"] = [{"sentiment_score": "asc"}]

        res_pos = es.search(index=index, body=query_pos)
        res_neg = es.search(index=index, body=query_neg)

        def extract_doc(hit):
            if not hit:
                return None
            src = hit[0].get("_source", {})
            return {
                "user": src.get("user", "unknown"),
                "content": src.get("content", "[No content]"),
                "sentiment_score": round(src.get("sentiment_score", 0), 4),
                "matched_keywords": src.get("matched_keywords", [])
            }

        most_pos = extract_doc(res_pos["hits"]["hits"])
        most_neg = extract_doc(res_neg["hits"]["hits"])

        if not most_pos and not most_neg:
            return jsonify({"message": "No matching posts found for this day."}), 404

        return jsonify({
            "most_positive": most_pos,
            "most_negative": most_neg
        })

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify({"error": str(e)}), 500