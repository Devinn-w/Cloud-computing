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
YouTube Video: https://www.youtube.com/watch?v=8p3OrnrJdpY 

### Structure
```
.
├── backend/                  # Application back-end source code
├── frontend/                 # Source code of the client part of the application
│   └── trump_tariff_analysis.ipynb  
├── test                      # On-premise back-end testing of the harvester code
├── data                      # Reference data
├── docs                      # Documentation
│   └── CCC_A2_Report.pdf
├── .gitlab-ci.yml            # CI Pipeline
└── README.md                 # This file
```

## Installation

This project builds upon the standard COMP90024 workshop setup provided by teaching staff.

Including:
- Kubernetes cluster 
- Fission serverless platform installed
- Elasticsearch deployed and accessible at `elasticsearch-master.elastic.svc.cluster.local:9200`
- Basic authentication credentials stored via ConfigMap `shared-data`

 We followed the instructor-provided setup and specifications from the practical labs.
 [comp90024 Gitlab Repository – Installation](https://gitlab.unimelb.edu.au/feit-comp90024/comp90024/-/tree/master/installation)

### Environment Requirements to run our Jupyter notebook
Make sure you have Python 3.8 or above installed on your computer.

### Install necessary Python modules

Run the following command in the terminal to install the modules required for running (Success FOR `WINDOWS`):

#### Jupyter notebook
```bash
pip install notebook
```

#### pandas (for data processing)
```bash
pip install pandas
```

#### plotly (for visualization)
```bash
pip install plotly
```

#### folium (for map visualization)
```bash
pip install folium
```

#### ipywidgets (for interactive controls)
```bash
pip install ipywidgets
```

### Place Frontend Files

Make sure you place these files `mastodon_thinking_swinging_question.gif`, `api_utils.py`, `plot_utils.py` and `trump_tariff_analysis.ipynb` in the same directory.


## Instructions
This system uses Fission functions running on a Kubernetes cluster. You can access the system through HTTP API calls after setting up a local port forwarding.

This guide shows how to run the application, query data, and see results, **even if you’re new to Kubernetes or Fission**.

---
### Before You Start

Make sure you have:

- A running Kubernetes cluster
- Fission already installed and functions deployed
- Elasticsearch running inside the cluster
- Your environment variables (Elasticsearch username, Elasticsearch password) stored in the `shared-data` ConfigMap

---

### Step 1: Port Forward Fission Router
Start a port forward from the Fission router in different shell

```bash
kubectl port-forward svc/router -n fission 9090:80
```

Keep this terminal open during testing.

### Step 2: Use in Jupyter Notebook

Start Jupyter Notebook:
```bash
jupyter notebook
```

### Step 3: View Frontend Service
Open `frontend/trump_tariff_analysis.ipynb` and run each cell to view our frontend visualization dashboard:
	-	Visualize analysis result
	-	Verify response shape and keywords
  - Query both Mastodon and Reddit

## Tesing
### Query the Sentiment API
You can query the Mastodon and Reddit sentiment endpoints using curl, Jupyter Notebook, or Python.

### Mastodon Sentiment analysis Functions
These routes would return a JSON array of keyword-based sentiment stats.

### Supported endpoints
- `GET /analysis/mastodon`
  - Requires headers: `X-Fission-Params-Start`, `X-Fission-Params-End`, and `X-Fission-Params-Keyword`
- `GET /analysis/mastodon/content`
  - Requires headers: `X-Fission-Params-Start`, `X-Fission-Params-End`, and `X-Fission-Params-Keyword`
- `GET /analysis/timestats`
  - Requires headers: `X-Fission-Params-Start`, `X-Fission-Params-End`, and `X-Fission-Params-Keyword`
- `GET /subreddit/date/{start:[0-9]{4}-[0-9]{2}-[0-9]{2}}/to/{end:[0-9]{4}-[0-9]{2}-[0-9]{2}}`

#### Example requests:
```bash
curl -X GET http://localhost:9090/analysis/mastodon \
  -H "X-Fission-Params-Start: 2025-05-01" \
  -H "X-Fission-Params-End: 2025-05-12" \
  -H "X-Fission-Params-Keyword: trump"
```

#### Example Response:
[{"avg_sentiment":-0.077,"count":40157,"keyword":"trump"},{"avg_sentiment":-0.076,"count":4707,"keyword":"tariff"},{"avg_sentiment":-0.073,"count":3715,"keyword":"tariffs"},{"avg_sentiment":-0.047,"count":3397,"keyword":"donald trump"},{"avg_sentiment":-0.452,"count":447,"keyword":"trade war"},{"avg_sentiment":-0.026,"count":201,"keyword":"trumpism"},{"avg_sentiment":-0.13,"count":71,"keyword":"trumpian"},{"avg_sentiment":-0.218,"count":15,"keyword":"maga"},{"avg_sentiment":0.431,"count":11,"keyword":"make america great again"},{"avg_sentiment":0.0,"count":3,"keyword":"potus"}]

### Reddit Sentiment Analysis Fuctions

These endpoints return a **JSON objects** with a `statusCode` and a `body` field. The `body` is a JSON-encoded string containing an array of sentiment results.

### Supported endpoints:
- `GET /analysis/reddit`
  - Requires headers: `X-Fission-Params-Start`, `X-Fission-Params-End`, and `X-Fission-Params-Keyword`

#### Example requests:
```bash
curl -X GET http://localhost:9090/analysis/reddit \
  -H "X-Fission-Params-Start: 2025-05-01" \
  -H "X-Fission-Params-End: 2025-05-12" \
  -H "X-Fission-Params-Keyword: trump"
```

#### Example Response:
{"body":"[{\"keyword\": \"trump\", \"count\": 5, \"avg_sentiment\": 0.115}, {\"keyword\": \"tariff\", \"count\": 2, \"avg_sentiment\": -0.211}, {\"keyword\": \"tariffs\", \"count\": 2, \"avg_sentiment\": -0.211}, {\"keyword\": \"maga\", \"count\": 1, \"avg_sentiment\": 0.966}, {\"keyword\": \"make america great again\", \"count\": 1, \"avg_sentiment\": 0.966}]","statusCode":200}

### System Testing Instructions
Here’s how to verify it works as expected:

#### Make sure data is indexed
Run the mharvest and rharvest functions to ensure data is present in Elasticsearch, run the following command in the cloud.
```bash
kubectl exec -it elasticsearch-master-0 -n elastic -- curl -u elastic:elastic https://elasticsearch-master:9200/mastodon-posts/_count --insecure
```

```bash
kubectl exec -it elasticsearch-master-0 -n elastic -- curl -u elastic:elastic https://elasticsearch-master:9200/reddit-posts/_count --insecure
```

Or In a new terminal, start a port forward from ElasticSearch:
```bash
kubectl port-forward service/elasticsearch-master -n elastic 9200:9200
```

View all indexes containing `mastodon` in ElasticSearch:
```bash
curl -u elastic:elastic -k https://localhost:9200/_cat/indices?v | grep mastodon
```

View all indexes containing `reddit` in ElasticSearch:
```bash
curl -u elastic:elastic -k https://localhost:9200/_cat/indices?v | grep reddit
```

####  Test Mastodon Query
```bash
curl -X GET http://localhost:9090/analysis/mastodon \
  -H "X-Fission-Params-Start: 2025-05-01" \
  -H "X-Fission-Params-End: 2025-05-12" \
  -H "X-Fission-Params-Keyword: trump"
```
Output is shown above in [Example Response]

#### Test Reddit Query
```bash
curl -X GET http://localhost:9090/analysis/reddit \
  -H "X-Fission-Params-Start: 2025-05-01" \
  -H "X-Fission-Params-End: 2025-05-12" \
  -H "X-Fission-Params-Keyword: trump"
```
Output is shown above in [Example Response]

## Note on Git History
During development, the Git history of this repository was unintentionally overwritten due to a forced push (`git push --force`) while trying to upload the `specs/` directory for Fission deployment.  
Although I have manually restored all the original files, please note that the previous commit history has been lost. As a result, individual commit records are no longer available.  
I will make sure to acknowledge everyone's contributions in the final report.  
— Zijing Li, 7 May 2025
