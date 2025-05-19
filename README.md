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
This project publishes multiple analysis functions as HTTP routes exposed by Fission. Any HTTP client (e.g., curl, Python requests, or Jupyter Notebook) can be used to interact with them. The endpoints enable querying of Mastodon and Reddit posts in Elasticsearch along with their corresponding sentiment scores.

### Mastodon Sentiment analysis
The following routes return **a JSON objects** with each keyword's sentiment score and post count.

### Supported endpoints
- `GET /analysis/mastodon`
  - Requires headers: `X-Fission-Params-Start`, `X-Fission-Params-End`, and `X-Fission-Params-Keyword`
- `GET /analysis/mastodon/keyword/{keyword}`
- `GET /analysis/mastodon/date/{start}/end/{end}`
- `GET /analysis/mastodon/date/{start}/end/{end}/keyword/{keyword}`

#### Example Response:
```json
[
  {"keyword": "trump", "count": 40156, "avg_sentiment": -0.077},
  {"keyword": "tariff", "count": 4049, "avg_sentiment": -0.075}
]
```
---

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

#### Example Response:
```json
{
  "statusCode": 200,
  "body": "[{\"keyword\": \"trump\", \"count\": 5, \"avg_sentiment\": 0.115}]"
}
```

## Note on Git History
During development, the Git history of this repository was unintentionally overwritten due to a forced push (`git push --force`) while trying to upload the `specs/` directory for Fission deployment.  
Although I have manually restored all the original files, please note that the previous commit history has been lost. As a result, individual commit records are no longer available.  
I will make sure to acknowledge everyone's contributions in the final report.  
— Zijing Li, 7 May 2025
