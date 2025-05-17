from io import StringIO
import pandas as pd
import requests
from datetime import datetime, timezone, date
from typing import Optional
import json

def get_mastodon_sentiment_timeseries_trump(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    keyword:    Optional[str] = None,

) -> pd.DataFrame:

    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    url = f"http://localhost:9090/analysis/timestats"
    headers = {
        "X-Fission-Params-Source":  "mastodon-posts",
        "X-Fission-Params-Start":   start_date or "",
        "X-Fission-Params-End":     end_date or "",
        "X-Fission-Params-Keyword": keyword    or "",
        "X-Fission-Params-Exclude": "tariff,tariffs,trade war,us-australia trade"
    }
 
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
  
    df = pd.DataFrame(data)

    if "created_at" in df:
        df["created_at"] = pd.to_datetime(df["created_at"], format="%Y-%m-%d")
    return df

def get_mastodon_posts_counts_tariff(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    keyword:    Optional[str] = None
) -> pd.DataFrame:

    url = f"http://localhost:9090/analysis/mastodon"
    headers = {
        "X-Fission-Params-Source":  "mastodon-posts",
        "X-Fission-Params-Start":   start_date or "",
        "X-Fission-Params-End":     end_date   or "",
        "X-Fission-Params-Keyword": keyword    or "",
        "X-Fission-Params-Exclude": "donald trump, trump, make america great again,trumpism, trumpian, 45th president, maga"
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
    
def get_mastodon_posts_counts_trump(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    keyword:    Optional[str] = None
) -> pd.DataFrame:

    url = f"http://localhost:9090/analysis/mastodon"
    headers = {
        "X-Fission-Params-Source":  "mastodon-posts",
        "X-Fission-Params-Start":   start_date or "",
        "X-Fission-Params-End":     end_date   or "",
        "X-Fission-Params-Keyword": keyword    or "",
        "X-Fission-Params-Exclude": "tariff,tariffs,trade war,us-australia trade"
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
    
def get_mastodon_posts_counts_all(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    keyword:    Optional[str] = None
) -> pd.DataFrame:

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

def get_summary_stats(start_date, end_date):

    url = "http://localhost:9090/analysis/range"
    headers = {
        "X-Fission-Params-Source": "mastodon-posts",
        "X-Fission-Params-Start": start_date,
        "X-Fission-Params-End": end_date
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


def merge_keywords(df: pd.DataFrame, merge_map: dict) -> pd.DataFrame:
    df = df.copy()

    df["merged_keyword"] = df["keyword"].apply(lambda x: merge_map.get(x, x))

    df_merged = (
        df.groupby("merged_keyword")
        .apply(lambda group: pd.Series({
            "count": group["count"].sum(),
            "avg_sentiment": (group["avg_sentiment"] * group["count"]).sum() / group["count"].sum()
        }))
        .reset_index()
        .rename(columns={"merged_keyword": "keyword"})
    )

    return df_merged

def merge_keywords_over_time(df, merge_map):
    df = df.copy()
    df["keyword"] = df["keyword"].replace(merge_map)
    return df.groupby(["keyword", "date"], as_index=False).agg({
        "avg_sentiment": "mean",
        "count": "sum"
    })

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


def get_keyword_stats_over_time_reddit(start_date_str: str, end_date_str: str = None, keyword: str = "") -> pd.DataFrame:
    """Pull Reddit keyword sentiment+count day by day and combine"""
    if end_date_str is None:
        end_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    all_data = []

    for day in pd.date_range(start=start_date, end=end_date):
        date_str = day.strftime("%Y-%m-%d")
        df = get_reddit_data(date_str, date_str, keyword=keyword)

        if not df.empty and {"keyword", "count", "avg_sentiment"}.issubset(df.columns):
            df = df.copy()
            df["date"] = date_str
            all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame(columns=["keyword", "avg_sentiment", "count", "date"])
