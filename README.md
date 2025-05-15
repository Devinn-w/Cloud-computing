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
├── test                      # Application back-end testing of the source code
├── data                      # Reference data
├── docs                      # Documentation
│   └── Report.pdf
└── README.md                 # This file
```

## Installation
excluding the stanrdard seyup covered in the workshop

## Instructions
how to use the client

## Note on Git History
During development, the Git history of this repository was unintentionally overwritten due to a forced push (`git push --force`) while trying to upload the `specs/` directory for Fission deployment.  
Although I have manually restored all the original files, please note that the previous commit history has been lost. As a result, individual commit records are no longer available.  
I will make sure to acknowledge everyone's contributions in the final report.  
— Zijing Li, 7 May 2025
