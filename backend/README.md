## Backend System Overview

### Structure
```
.
├── backend/                  # Application back-end source code
│   ├── rharvester/           # Reddit data collector
│   ├── mharvester/           # Mastodon data collector
│   ├── bharvester/           # Bluesky data collector
│   ├── pharvester/           # Past data collector        
│   ├── specs/                # YAML specifications
│   ├── stats_demo/           # Base route query 
│   ├── stats_mastodon/       # Mastodon route query
│   ├── stats_reddit/         # Reddit route query
│   └── README.md             # Instructions on how to run

```