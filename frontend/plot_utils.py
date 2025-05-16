from datetime import datetime, timezone
import pandas as pd
import plotly.graph_objects as go
from api_utils import get_summary_stats
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from plotly.subplots import make_subplots

def plot_sentiment_trend_with_events(keyword: str, start_date_str: str, get_summary_stats_func):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.now(timezone.utc).date()

    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    avg_sentiments = []

    for date in date_range:
        date_str = date.strftime("%Y-%m-%d")
        df_day = get_summary_stats_func(date_str, date_str)

        if df_day.empty or "avg_sentiment" not in df_day.columns:
            print(f"No valid data on {date_str}")
            avg_sentiments.append(None)
        else:
            avg_sentiments.append(df_day.at[0, "avg_sentiment"])

    df_plot = pd.DataFrame({
        "date": date_range,
        "avg_sentiment": avg_sentiments
    })

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_plot['date'],
        y=df_plot['avg_sentiment'],
        mode='lines+markers',
        name='Avg Sentiment',
        line=dict(color='royalblue', width=3),
        marker=dict(size=8)
    ))

    events = [
        ("2025-04-02", "Tariff Announced (Apr 2)", "red", 0),
        ("2025-04-09", "90-Day Tariff Delay (Apr 9)", "blue", -15),
        ("2025-05-12", "Trump Agreed to Cut Tariffs (May 12)", "purple", -30)
    ]

    for date_str, label, color, yshift in events:
        event_date = datetime.strptime(date_str, "%Y-%m-%d")
        fig.add_shape(
            type="line",
            x0=event_date,
            x1=event_date,
            y0=0,
            y1=1,
            xref="x",
            yref="paper",
            line=dict(color=color, width=2, dash="dash")
        )
        fig.add_annotation(
            x=event_date,
            y=1,
            xref="x",
            yref="paper",
            text=label,
            showarrow=False,
            font=dict(color=color),
            yshift=yshift
        )

    fig.update_layout(
        title=f"Live Mastodon Sentiment Trend on '{keyword.title()}' Among Australians Since Tariff",
        xaxis_title="Date",
        yaxis_title="Avg Sentiment Score",
        template="plotly_white",
        hovermode="x unified",
        width=1000,
        height=500
    )

    return fig

def plot_animated_sentiment_trend(df_plot, event_list):


    fig = go.Figure(
        data=[go.Scatter(x=[], y=[], mode='lines+markers', name='Avg Sentiment')],
        frames=[
            go.Frame(
                data=[go.Scatter(x=df_plot['date'][:k], y=df_plot['avg_sentiment'][:k])],
                name=str(k)
            )
            for k in range(2, len(df_plot))
        ]
    )

    for date_str, label, color, yshift in event_list:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        fig.add_shape(type="line", x0=d, x1=d, y0=0, y1=1, xref='x', yref='paper',
                      line=dict(color=color, width=2, dash="dash"))
        fig.add_annotation(x=d, y=1, xref='x', yref='paper', text=label,
                           showarrow=False, font=dict(color=color), yshift=yshift)

    fig.update_layout(
        title="Live Mastodon Sentiment Trend on Trump Among Australians Since Tariff",
        xaxis_title="Date",
        yaxis_title="Avg Sentiment Score",
        template="plotly_white",
        width=1000,
        height=500,
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 100}}]},
                {"label": "Pause", "method": "animate", "args": [[None], {"mode": "immediate", "frame": {"duration": 0}}]}
            ]
        }]
    )

    return fig

def plot_post_volume_with_events(start_date_str: str, get_summary_stats_func):

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.now(timezone.utc).date()

    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    counts = []

    for date in date_range:
        date_str = date.strftime("%Y-%m-%d")
        df_day = get_summary_stats_func(date_str, date_str)

        if df_day.empty or "count" not in df_day.columns:
            counts.append(0)
        else:
            counts.append(df_day.at[0, "count"])

    df_count = pd.DataFrame({
        "date": date_range,
        "post_count": counts
    })

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_count["date"],
        y=df_count["post_count"],
        mode="lines+markers",
        name="Post Count",
        line=dict(color="orange", width=3),
        marker=dict(size=8)
    ))

    events = [
        ("2025-04-02", "Tariff Announced (Apr 2)", "red", 0),
        ("2025-04-09", "90-Day Tariff Delay", "blue", -15),
        ("2025-05-12", "Trump Agreed to Cut Tariffs", "purple", -30)
    ]

    for date_str, label, color, yshift in events:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        fig.add_shape(
            type="line",
            x0=d,
            x1=d,
            y0=0,
            y1=1,
            xref="x",
            yref="paper",
            line=dict(color=color, width=2, dash="dash")
        )
        fig.add_annotation(
            x=d,
            y=1,
            xref="x",
            yref="paper",
            text=label,
            showarrow=False,
            font=dict(color=color),
            yshift=yshift
        )

    fig.update_layout(
        title=f"Live Daily Trump Post Volume on Mastodon Among Australians",
        xaxis_title="Date",
        yaxis_title="Post Count",
        template="plotly_white",
        hovermode="x unified",
        width=1000,
        height=500
    )

    return fig

def plot_combined_sentiment_volume(start_date_str: str, get_summary_stats_func):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.now(timezone.utc).date()

    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    sentiments = []
    counts = []

    for date in date_range:
        date_str = date.strftime("%Y-%m-%d")
        df_day = get_summary_stats_func(date_str, date_str)

        if df_day.empty or "avg_sentiment" not in df_day.columns:
            sentiments.append(None)
        else:
            sentiments.append(df_day.at[0, "avg_sentiment"])

        if df_day.empty or "count" not in df_day.columns:
            counts.append(0)
        else:
            counts.append(df_day.at[0, "count"])

    df = pd.DataFrame({
        "date": date_range,
        "avg_sentiment": sentiments,
        "post_count": counts
    })

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["avg_sentiment"],
        name="Avg Sentiment",
        mode="lines+markers",
        line=dict(color="royalblue", width=3),
        marker=dict(size=6),
        yaxis="y1"
    ))

    fig.add_trace(go.Bar(
        x=df["date"],
        y=df["post_count"],
        name="Post Count",
        marker_color="orange",
        yaxis="y2",
        opacity=0.5
    ))

    events = [
        ("2025-04-02", "Tariff Announced", "red", 0),
        ("2025-04-09", "90-Day Delay", "blue", -15),
        ("2025-05-12", "Tariff Cut Agreed", "purple", -30)
    ]
    for date_str, label, color, yshift in events:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        fig.add_shape(
            type="line", x0=d, x1=d, y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(color=color, width=2, dash="dash")
        )
        fig.add_annotation(
            x=d, y=1,
            xref="x", yref="paper",
            text=label,
            showarrow=False,
            font=dict(color=color),
            yshift=yshift
        )

    fig.update_layout(
        title=f"Live Daily Trump Sentiment and Post Volume on Mastodon Among Australians",
        xaxis_title="Date",
        yaxis=dict(
            title="Avg Sentiment",
            side="left",
            range=[-1, 1]
        ),
        yaxis2=dict(
            title="Post Count",
            overlaying="y",
            side="right"
        ),
        template="plotly_white",
        hovermode="x unified",
        width=1000,
        height=500
    )

    return fig


def plot_keyword_sentiment_bubble(df):
    fig = px.scatter(
        df,
        x="avg_sentiment",
        y="count",
        size="count",
        color="keyword",
        text="keyword",
        range_x=[-1, 1],
        title=" Today Keyword Sentiment Trend on Mastodon Among Australians",
        height=600
    )
    fig.update_traces(textposition='top center', marker=dict(opacity=0.7, line=dict(width=1)))
    fig.update_layout(template="plotly_white", hovermode="closest")
    return fig



def plot_keyword_sentiment_trend(df: pd.DataFrame):
    if df.empty:
        print("Empty DataFrame provided.")
        return None

    fig = px.line(
        df,
        x="date",
        y="avg_sentiment",
        color="keyword",
        markers=True,
        title="Live Keyword Sentiment Trend on Mastodon Among Australians Since the Tariff",
        labels={
            "avg_sentiment": "Average Sentiment",
            "date": "Date",
            "keyword": "Keyword"
        }
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        width=1000,
        height=500,
        legend_title="Keyword"
    )

    return fig

import plotly.express as px

def plot_keyword_distribution_stacked(df: pd.DataFrame, merge_map: dict = None):
    if df.empty:
        print("Empty DataFrame provided.")
        return None

    df = df.copy()

    if merge_map:
        df["keyword"] = df["keyword"].apply(lambda k: merge_map.get(k, k))

        df = (
            df.groupby(["keyword", "date"], as_index=False)
            .agg({"count": "sum"})
        )

    fig = px.bar(
        df,
        x="date",
        y="count",
        color="keyword",
        title="Live Keyword Frequency on Mastodon Among Australians Since the Tariff",
        labels={"date": "Date", "count": "Post Count", "keyword": "Keyword"}
    )

    fig.update_layout(
        barmode="stack",
        template="plotly_white",
        hovermode="x unified",
        height=500,
        width=1000,
        legend_title="Keyword"
    )

    return fig



def plot_subreddit_sentiment_map(df, fixed=True):

    subreddit_locations = {
        "brisbane": (-27.4698, 153.0251),
        "perth": (-31.9505, 115.8605),
        "canberra": (-35.2809, 149.1300),
        "melbourne": (-37.8136, 144.9631),
        "sydney": (-33.8688, 151.2093),
        "australia": (-25.2744, 133.7751),
        "AustralianPolitics": (-25.2744, 133.7751),
        "AusFinance": (-25.2744, 133.7751)
    }

    m = folium.Map(
        location=[-25.3, 134.2],
        zoom_start=4,
        zoom_control=False,     
        dragging=False, 
        scrollWheelZoom=False, 
        doubleClickZoom=False,  
        touchZoom=False         
    )

    m.fit_bounds([[-44.0, 112.0], [-10.0, 154.0]])

    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        sub = row["subreddit"]
        count = row["count"]
        sentiment = row["avg_sentiment"]

        if sub not in subreddit_locations:
            continue

        lat, lon = subreddit_locations[sub]
        color = "green" if sentiment >= 0 else "red"

        folium.CircleMarker(
            location=[lat, lon],
            radius=4 + count,
            popup=folium.Popup(f"<b>{sub}</b><br>Count: {count}<br>Sentiment: {sentiment:.2f}", max_width=250),
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(marker_cluster)

    return m



def plot_platform_sentiment_only(df_masto: pd.DataFrame, df_reddit: pd.DataFrame):
    df_m = df_masto.copy()
    df_r = df_reddit.copy()

    df_m["platform"] = "Mastodon"
    df_r["platform"] = "Reddit"

    common = set(df_m["keyword"]).intersection(df_r["keyword"])
    df_m = df_m[df_m["keyword"].isin(common)]
    df_r = df_r[df_r["keyword"].isin(common)]

    df_all = pd.concat([df_m, df_r])

    fig = px.bar(
        df_all,
        x="keyword",
        y="avg_sentiment",
        color="platform",
        barmode="group",
        title="Average Sentiment Comparison: Reddit vs Mastodon (By Keyword)",
        labels={"avg_sentiment": "Avg Sentiment", "keyword": "Keyword"}
    )

    fig.update_layout(
        template="plotly_white",
        height=500,
        width=1000,
        legend_title="Platform"
    )

    return fig


import plotly.express as px
import pandas as pd

def plot_merged_keyword_trend(df: pd.DataFrame, keywords: list, label: str = "tariff"):

    df_filtered = df[df["keyword"].isin(keywords)].copy()
    df_filtered["weighted_score"] = df_filtered["avg_sentiment"] * df_filtered["count"]

    grouped = (
        df_filtered.groupby("date", as_index=False)
        .agg(
            count=("count", "sum"),
            total_score=("weighted_score", "sum")
        )
    )
    grouped["avg_sentiment"] = grouped["total_score"] / grouped["count"]
    grouped["keyword"] = label

    grouped["date"] = pd.to_datetime(grouped["date"]).dt.date

    fig = px.line(
        grouped,
        x="date",
        y="avg_sentiment",
        markers=True,
        title=f"How Have Australians Felt About '{label.title()}' on Mastodon Since the Tariff?",
        labels={"avg_sentiment": "Avg Sentiment", "date": "Date"}
    )

    fig.update_layout(
        template="plotly_white",
        height=450,
        width=950,
        xaxis=dict(tickformat="%b %d")
    )
    return fig

