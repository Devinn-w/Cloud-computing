from io import StringIO
import pandas as pd
import requests
from datetime import datetime, timezone, date
import json
from typing import Union, List, Optional

TRUMP_KEYWORDS = ["trump", "donald trump", "maga", "make america great again", "trumpism", "trumpian", "potus"]
TARIFF_KEYWORDS = ["tariff", "tariffs", "import tax", "trade war"]

# Second Used
def get_mastodon_sentiment_timeseries_trump(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    keyword:    Optional[str] = None,) -> pd.DataFrame:

    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    url = f"http://localhost:9090/analysis/timestats"
    headers = {
        "X-Fission-Params-Source": "mastodon-posts",
        "X-Fission-Params-Exclude": "tariff,tariffs,trade war,us-australia trade"
    }

    if start_date and end_date:
        headers["X-Fission-Params-Start"] = start_date
        headers["X-Fission-Params-End"] = end_date

    if keyword:
        headers["X-Fission-Params-Keyword"] = keyword
 
    resp = requests.get(url, headers=headers)
    #resp.raise_for_status()
    data = resp.json()
  
    df = pd.DataFrame(data)

    if "created_at" in df:
        df["created_at"] = pd.to_datetime(df["created_at"], format="%Y-%m-%d")
    return df

# First Used
def get_mastodon_posts_counts(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    keyword: Union[str, List[str], None] = None
) -> pd.DataFrame:
    
    if isinstance(keyword, list):
        keyword = ",".join(keyword)

    url = f"http://localhost:9090/analysis/mastodon"
    headers = {
        "X-Fission-Params-Source":  "mastodon-posts",
        "X-Fission-Params-Start":   start_date or "",
        "X-Fission-Params-End":     end_date   or "",
        "X-Fission-Params-Keyword": keyword    or ""
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

# Third Used
def get_trump_post_volume_on_day(start: str, end: str) -> pd.DataFrame:
 
    df = get_mastodon_posts_counts(start, end, keyword=",".join(TRUMP_KEYWORDS))

    if df.empty or "keyword" not in df.columns or "count" not in df.columns:
        return pd.DataFrame(columns=["keyword", "count"])
    def match_trump(k: str):
        return any(kw in k for kw in TRUMP_KEYWORDS)

    df = df[df["keyword"].apply(match_trump)]
    return pd.DataFrame([{
        "date": start,
        "count": df["count"].sum()
    }])

# Fourth Used
def get_daily_sentiment_count(start_date: str, end_date: str, keywords: List[str]) -> pd.DataFrame:
    df = get_mastodon_posts_counts(start_date, end_date, keyword=keywords)

    if df.empty:
        return pd.DataFrame([{
            "keyword": ",".join(keywords),
            "count": 0,
            "avg_sentiment": None
        }])


    filtered_df = df[df["keyword"].isin(keywords)]

    if filtered_df.empty:
        return pd.DataFrame([{
            "keyword": ",".join(keywords),
            "count": 0,
            "avg_sentiment": None
        }])

    total_count = filtered_df["count"].sum()
    weighted_avg_sentiment = (
        (filtered_df["count"] * filtered_df["avg_sentiment"]).sum() / total_count
        if total_count > 0 else None
    )

    return pd.DataFrame([{
        "keyword": ",".join(keywords),
        "count": total_count,
        "avg_sentiment": weighted_avg_sentiment
    }])

# Fifth Used
def get_keyword_stats_over_time(start_date_str: str, end_date_str: str = None, keyword: str = "") -> pd.DataFrame:

    if end_date_str is None:
        end_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    all_data = []

    for day in pd.date_range(start=start_date, end=end_date):
        date_str = day.strftime("%Y-%m-%d")
        df = get_mastodon_data(date_str, date_str, keyword=keyword)
        if not df.empty and {"keyword", "count", "avg_sentiment"}.issubset(df.columns):
            df = df.copy()
            df["date"] = date_str
            all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame(columns=["keyword", "avg_sentiment", "count", "date"])

# Sixth Used
def fetch_subreddit_stats(start: str, end: str = None) -> pd.DataFrame:
    if end is None:
        end = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    url = f"http://localhost:9090/subreddit/date/{start}/to/{end}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        json_string = response.json().get("body", "[]")
        df = pd.read_json(StringIO(json_string))
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame(columns=["subreddit", "count", "avg_sentiment"])

# Seventh Used
def get_mastodon_data(start_date, end_date, keyword=""):
    """Fetch daily keyword-level sentiment data from Mastodon."""
    url = "http://localhost:9090/analysis/mastodon"

    headers = {
        "X-Fission-Params-Source":  "mastodon-posts",
        "X-Fission-Params-Start":   start_date,
        "X-Fission-Params-End":     end_date,
        "X-Fission-Params-Keyword": keyword
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        try:
            data = response.json()
        except Exception as json_error:
            print("Failed to parse JSON from response.")
            print("Raw response text (first 200 chars):", response.text[:200])
            raise json_error

        df = pd.DataFrame(data)

        return df

    except Exception as e:
        print(f"Error occurred while retrieving data for {start_date}: {e}")
        return pd.DataFrame()

# Eighth Used
def get_reddit_data(start_date, end_date, keyword=""):
    """Fetch daily keyword-level sentiment data from Reddit."""
    url = "http://localhost:9090/analysis/reddit"

    headers = {
        "X-Fission-Params-Source":  "reddit-posts",
        "X-Fission-Params-Start":   start_date,
        "X-Fission-Params-End":     end_date,
        "X-Fission-Params-Keyword": keyword
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        raw_body = data.get("body", [])

        if isinstance(raw_body, str):
            try:
                body = json.loads(raw_body)
            except Exception as e:
                print("Failed to parse Reddit body JSON:", e)
                print("Raw body:", repr(raw_body)[:200])
                return pd.DataFrame()
        else:
            body = raw_body

        if isinstance(body, list):
            df = pd.DataFrame(body)
        elif isinstance(body, dict):
            df = pd.DataFrame([body])
        else:
            print(f"Unexpected body format from Reddit API on {start_date}")
            return pd.DataFrame()

        return df

    except Exception as e:
        print(f"Error retrieving Reddit data for {start_date}: {e}")
        return pd.DataFrame()

# Need
def get_extreme_mastodon_posts(date_str, keyword_list=None):
    url = "http://localhost:9090/analysis/mastodon/content"
    headers = {
        "X-Fission-Params-Start": date_str,
        "X-Fission-Params-End": date_str
    }
    if keyword_list:
        keyword_str = ",".join(keyword_list)
        headers["X-Fission-Params-Keyword"] = keyword_str
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 404:
            return {"message": "No matching posts"}
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error: {e}")
        return {}
