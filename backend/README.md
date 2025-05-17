## Backend System Overview

### Structure
```
.
├── backend/                  # Application back-end source code
│   ├── rharvester/           # Reddit data collector
│   ├── mharvester/           # Mastodon data collector
│   ├── pharvester/           # Past data collector        
│   ├── specs/                # YAML specifications
│   ├── stats_mastodon/       # Mastodon route query
│   ├── stats_reddit/         # Reddit route query
│   ├── bharvester/           # Bluesky data collector
│   ├── stats_demo/           # Base route query 
│   └── README.md             # Instructions on how to run

```

Note: We initially developed a `bharvest` function for harvesting Bluesky data, but later decided to consolidate into `mharvest`. The code is retained here to demonstrate exploration and modularity.
Note: `stats_demo` was built as an example for teammates who is responsible for frontend system, to know how to write code. `stats_mastodon` and `stats_reddit` are what we used for frontend