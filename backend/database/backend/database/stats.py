# backend/analysis/stats.py

import logging
import json
import re
from flask import jsonify, request, current_app
from elasticsearch8 import Elasticsearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_credential(name: str) -> str:
    path = f"/configs/default/shared-data/{name}"
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        current_app.logger.error(f"Credential file {path} not found")
        return ""


def get_es_client() -> Elasticsearch:
    es_user = read_credential("ES_USERNAME")
    es_pass = read_credential("ES_PASSWORD")
    return Elasticsearch(
        "https://elasticsearch-master.elastic.svc.cluster.local:9200",
        basic_auth=(es_user, es_pass),
        verify_certs=False,
        ssl_show_warn=False
    )


# date range router
def stats_range():
    start = request.args.get("start")
    end   = request.args.get("end")
    if not (start and end):
        return jsonify({"error":"need ?start=YYYY-MM-DD&end=YYYY-MM-DD"}), 400

    es = get_es_client()
    body = {
      "size": 0,
      "query": {
        "range": {
          "created_at": {
            "gte": f"{start}T00:00:00",
            "lte": f"{end}T23:59:59"
          }
        }
      },
      "aggs": {
        "daily": {
          "date_histogram": {
            "field": "created_at",
            "calendar_interval": "1d",
            "format": "yyyy-MM-dd"
          },
          "aggs": {
            "avg_sentiment": {"avg": {"field": "sentiment_score"}},
            "count": {"value_count": {"field": "_id"}}
          }
        }
      }
    }
    res = es.search(index="mastodon-posts", body=body)
    buckets = res["aggregations"]["daily"]["buckets"]
    return jsonify([
      {
        "date": b["key_as_string"],
        "count": b["count"]["value"],
        "avg_sentiment": round(b["avg_sentiment"]["value"] or 0,3)
      } for b in buckets
    ])


# keyword router
def stats_keyword():
    kw = request.args.get("keyword")
    if not kw:
        return jsonify({"error":"need ?keyword=..."}), 400

    es = get_es_client()
    body = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {"match": {"content": kw}},
            {"range": {"sentiment_score": {"lte":1.0}}}
          ]
        }
      },
      "aggs": {
        "daily": {
          "date_histogram": {
            "field": "created_at",
            "calendar_interval": "1d",
            "format": "yyyy-MM-dd"
          },
          "aggs": {
            "avg_sentiment": {"avg": {"field": "sentiment_score"}},
            "count": {"value_count": {"field": "_id"}}
          }
        }
      }
    }
    res = es.search(index="mastodon-posts", body=body)
    buckets = res["aggregations"]["daily"]["buckets"]
    return jsonify([
      {
        "date": b["key_as_string"],
        "count": b["count"]["value"],
        "avg_sentiment": round(b["avg_sentiment"]["value"] or 0,3)
      } for b in buckets
    ])


# daterange + keyword router
def stats_range_keyword():
    start = request.args.get("start")
    end   = request.args.get("end")
    kw    = request.args.get("keyword")
    if not (start and end and kw):
        return jsonify({"error":"need ?start=&end=&keyword="}), 400

    es = get_es_client()
    body = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {"range": {"created_at": {"gte":f"{start}T00:00:00","lte":f"{end}T23:59:59"}}},
            {"match": {"content": kw}},
            {"range": {"sentiment_score": {"lte":1.0}}}
          ]
        }
      },
      "aggs": {
        "by_hour": {
          "date_histogram": {
            "field": "created_at",
            "fixed_interval": "1h",
            "format": "yyyy-MM-dd'T'HH"
          },
          "aggs": {
            "avg_sentiment": {"avg": {"field": "sentiment_score"}},
            "count": {"value_count": {"field": "_id"}}
          }
        }
      }
    }
    res = es.search(index="mastodon-posts", body=body)
    buckets = res["aggregations"]["by_hour"]["buckets"]
    return jsonify([
      {
        "hour": b["key_as_string"],
        "count": b["count"]["value"],
        "avg_sentiment": round(b["avg_sentiment"]["value"] or 0,3)
      } for b in buckets
    ])


