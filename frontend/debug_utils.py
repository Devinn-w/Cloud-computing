import requests

headers = {
    "X-Fission-Params-Source": "mastodon-posts",
    "X-Fission-Params-Start": "2025-05-16",
    "X-Fission-Params-End": "2025-05-17",
    "X-Fission-Params-Keyword": "trump,tariff"
}

r = requests.get("http://localhost:9090/analysis/mastodon", headers=headers)
print("STATUS:", r.status_code)
print("RAW RESPONSE:", r.text)
