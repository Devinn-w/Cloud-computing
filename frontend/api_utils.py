import requests
import pandas as pd

def get_mastodon_data(start_date, end_date, keyword="trump") -> pd.DataFrame:
    """
    Fetch Mastodon posts from Fission API between given dates with a specific keyword.
    """
    url = "http://localhost:9090/analysis/range"
    headers = {
        "X-Fission-Params-Source": "mastodon-posts",
        "X-Fission-Params-Start": start_date,
        "X-Fission-Params-End": end_date,
        "X-Fission-Params-Keyword": keyword
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            print("✅ No posts found in the given range.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df["created_at"] = pd.to_datetime(df["created_at"])
        return df

    except Exception as e:
        print(f"❌ Error fetching data from Fission API: {e}")
        return pd.DataFrame()
