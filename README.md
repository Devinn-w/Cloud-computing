# COMP90024 Team35 - Big Data Analytics on the Cloud

## Project Topic
**What do Australians think of Donald Trump and the use of tariffs in Mastodon?**

This project collects, stores, analyzes and visualizes public sentiment from Reddit and Mastodon posts related to Donald Trump and tariffs, specifically focusing on content from Australian users or communities.

## System Overview
This application is deployed on the NeCTAR Research Cloud using a **Kubernetes** cluster. It uses:

- **Fission** (Serverless Functions) to harvest and process Reddit & Mastodon data
- **Elasticsearch** to store and index data
- **Kibana** for log and index inspection
- **Jupyter Notebook** for frontend analytics and visualization

### Project presentation link
Gitlab Repository: https://gitlab.unimelb.edu.au/HENGJIN/comp90024-2025-35  
YouTube Video: https://youtu.be/yourvideo  

### Structure
```
.
├── backend/                  # Application back-end source code
├── frontend/                 # Source code of the client part of the application
│   └── trump_tariff_analysis.ipynb  
├── test                      # On-premise back-end testing of the harvester code
├── data                      # Reference data
├── docs                      # Documentation
│   └── Report.pdf
├── .gitlab-ci.yml            # CICD
└── README.md                 # This file
```

## Installation
excluding the stanrdard seyup covered in the workshop

## Instructions
This system uses Fission functions running on a Kubernetes cluster. You can access the system through HTTP API calls after setting up a local port forwarding.

This guide shows how to run the application, query data, and see results, **even if you’re new to Kubernetes or Fission**.

---
### Before You Start

Make sure you have:

- A running Kubernetes cluster
- Fission already installed and functions deployed
- Elasticsearch running inside the cluster
- Your environment variables (username, password) stored in the `shared-data` ConfigMap

---

### Step 1: Port Forward Fission Router
You must expose the Fission router to your local machine. In a terminal window, run:

```bash
kubectl port-forward -n fission svc/router 30451:80

Keep this terminal open during testing. All HTTP requests use localhost:30451.
```

### Step 2: Query the Sentiment API
You can query the Mastodon and Reddit sentiment endpoints using curl, Jupyter Notebook, or Python.


### Mastodon Sentiment analysis
These routes return a JSON array of keyword-based sentiment stats.

### Supported endpoints
- `GET /analysis/mastodon`
  - Requires headers: `X-Fission-Params-Start`, `X-Fission-Params-End`, and `X-Fission-Params-Keyword`
- `GET /analysis/mastodon/keyword/{keyword}`
- `GET /analysis/mastodon/date/{start}/end/{end}`
- `GET /analysis/mastodon/date/{start}/end/{end}/keyword/{keyword}`

#### Example requests:
curl -X GET http://localhost:30451/analysis/mastodon \
  -H "X-Fission-Params-Start: 2025-05-01" \
  -H "X-Fission-Params-End: 2025-05-12" \
  -H "X-Fission-Params-Keyword: trump"

#### Example Response:
 { [
  { "keyword": "trump", "count": 40157, "avg_sentiment": -0.077 },
  { "keyword": "tariff", "count": 4707, "avg_sentiment": -0.076 },
  { "keyword": "tariffs", "count": 3715, "avg_sentiment": -0.073 },
  { "keyword": "donald trump", "count": 3397, "avg_sentiment": -0.047 },
  { "keyword": "trade war", "count": 447, "avg_sentiment": -0.452 },
  { "keyword": "trumpism", "count": 201, "avg_sentiment": -0.026 },
  { "keyword": "trumpian", "count": 71, "avg_sentiment": -0.130 },
  { "keyword": "maga", "count": 15, "avg_sentiment": -0.218 },
  { "keyword": "make america great again", "count": 11, "avg_sentiment": 0.431 },
  { "keyword": "potus", "count": 3, "avg_sentiment": 0.000 }
]
 }

### Reddit Sentiment Analysis

These endpoints return a **JSON objects** with a `statusCode` and a `body` field. The `body` is a JSON-encoded string containing an array of sentiment results.

#### Supported endpoints:

- `GET /analysis/reddit`
  - Requires headers:
    - `X-Fission-Params-Start`
    - `X-Fission-Params-End`
    - `X-Fission-Params-Keyword`
- `GET /analysis/reddit/keyword/{keyword}`
- `GET /analysis/reddit/date/{start}/end/{end}`
- `GET /analysis/reddit/date/{start}/end/{end}/keyword/{keyword}`

#### Example requests:
curl -X GET http://localhost:30451/analysis/reddit \
  -H "X-Fission-Params-Start: 2025-05-01" \
  -H "X-Fission-Params-End: 2025-05-12" \
  -H "X-Fission-Params-Keyword: trump"


#### Example Response:
{
  "statusCode": 200,
  "body": [
    { "keyword": "trump", "count": 5, "avg_sentiment": 0.115 },
    { "keyword": "tariff", "count": 2, "avg_sentiment": -0.211 },
    { "keyword": "tariffs", "count": 2, "avg_sentiment": -0.211 },
    { "keyword": "maga", "count": 1, "avg_sentiment": 0.966 },
    { "keyword": "make america great again", "count": 1, "avg_sentiment": 0.966 }
  ]
}
### System Testing Instructions
After deploying the system, here’s how to verify it works as expected:

#### Make sure data is indexed
	Run the mharvest and rharvest functions to ensure data is present in Elasticsearch.

kubectl exec -it elasticsearch-master-0 -n elastic -- \
  curl -u elastic:elastic https://elasticsearch-master:9200/mastodon-posts/_count --insecure

kubectl exec -it elasticsearch-master-0 -n elastic -- \
  curl -u elastic:elastic https://elasticsearch-master:9200/reddit-posts/_count --insecure

####  Test Mastodon Query
curl -X GET http://localhost:30451/analysis/mastodon \
  -H "X-Fission-Params-Start: 2025-05-01" \
  -H "X-Fission-Params-End: 2025-05-12" \
  -H "X-Fission-Params-Keyword: trump"

Output should include keyword, count, and avg_sentiment.

#### Test Reddit Query
curl -X GET http://localhost:30451/analysis/reddit \
  -H "X-Fission-Params-Start: 2025-05-01" \
  -H "X-Fission-Params-End: 2025-05-12" \
  -H "X-Fission-Params-Keyword: trump"

Output should be a JSON string in the body field.

#### Test frontend
Open frontend/trump_tariff_analysis.ipynb and run the prewritten Python code to:
	•	Query both Mastodon and Reddit
	•	Visualize result using pandas & matplotlib
	•	Verify response shape and keywords

## Note on Git History
During development, the Git history of this repository was unintentionally overwritten due to a forced push (`git push --force`) while trying to upload the `specs/` directory for Fission deployment.  
Although I have manually restored all the original files, please note that the previous commit history has been lost. As a result, individual commit records are no longer available.  
I will make sure to acknowledge everyone's contributions in the final report.  
— Zijing Li, 7 May 2025
