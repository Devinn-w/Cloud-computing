from datetime import datetime, timedelta, date, timezone
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import ipywidgets as widgets
from IPython.display import display, clear_output
import api_utils
import importlib
importlib.reload(api_utils)
from api_utils import get_mastodon_posts_counts, get_extreme_mastodon_posts,get_mastodon_data
from datetime import date

KEYWORDS_TRUMP = ["donald trump", "trump", "make america great again","trumpism", "trumpian", "45th president"]
KEYWORDS_TARIFF = ["tariff", "tariffs", "us-australia trade", "trade war"]

# First Plot 
def plot_trump_tariff_bubble(trump_count: int, tariff_count: int):

    df = pd.DataFrame({
        'Category': ['Trump Related', 'Tariff Related'],
        'Post Count': [trump_count, tariff_count],
        'x': [1, 1.04], 
        'y': [1, 1],
        'Label': [str(trump_count), str(tariff_count)]
    })

    fig = px.scatter(
        df,
        x='x',
        y='y',
        size='Post Count',
        color='Category',
        text='Label',
        size_max=200,
        title='Live Trump vs Tariff Posts Count in Mastodon AU',
        color_discrete_map={
            'Trump Related': '#1f77b4',
            'Tariff Related': '#fcbf49'
        }
    )

    fig.update_traces(
        textposition='middle center',
        textfont=dict(
            family="Arial Black",
            size=22,
            color='black'
        )
    )

    fig.update_layout(
        xaxis=dict(visible=False, range=[0.95, 1.07]),
        yaxis=dict(visible=False, range=[0.8, 1.2]),
        showlegend=True,
        plot_bgcolor='white',
        height=500
    )

    fig.show()

# Second Plot
def show_sentiment_on_date():
    date_picker = widgets.DatePicker(
        description='Pick a date',
        value=date.today(),
        min=date(2025, 4, 2),
        max=date.today(),
        disabled=False
    )

    output = widgets.Output()

    def on_date_change(change):
        with output:
            clear_output(wait=True)
            selected = change["new"]
            if not selected:
                print("Please pick a date.")
                return
            
            start_str = selected.strftime("%Y-%m-%d")
            end_str = selected.strftime("%Y-%m-%d")

            print(f"Fetching data for: {start_str} (UTC full-day)")

            df = get_mastodon_posts_counts(start_date=start_str, end_date=end_str)

            if df.empty:
                print("No data available for this date.")
                return

            df["keyword"] = df["keyword"].str.lower()

            avg_sent_overall = df["avg_sentiment"].mean()
            total_count_overall = df["count"].sum()

            df_trump = df[df["keyword"].apply(lambda k: any(kw in k for kw in KEYWORDS_TRUMP))]
            avg_sent_trump = df_trump["avg_sentiment"].mean() if not df_trump.empty else None
            total_count_trump = df_trump["count"].sum() if not df_trump.empty else 0

            df_tariff = df[df["keyword"].apply(lambda k: any(kw in k for kw in KEYWORDS_TARIFF))]
            avg_sent_tariff = df_tariff["avg_sentiment"].mean() if not df_tariff.empty else None
            total_count_tariff = df_tariff["count"].sum() if not df_tariff.empty else 0

            print(f"Overall — Avg Sentiment: {avg_sent_overall:.4f}, Total Posts: {total_count_overall}")
            print(f"Trump-related — Avg Sentiment: {avg_sent_trump:.4f} Posts: {total_count_trump}" if avg_sent_trump is not None else
                  f"Trump-related — Avg Sentiment: N/A Posts: {total_count_trump}")
            print(f"Tariff-related — Avg Sentiment: {avg_sent_tariff:.4f} Posts: {total_count_tariff}" if avg_sent_tariff is not None else
                  f"Tariff-related — Avg Sentiment: N/A Posts: {total_count_tariff}")
            
    date_picker.observe(on_date_change, names='value')

    display(date_picker, output)

# Third Plot
def show_content_on_date_trump():
    date_picker = widgets.DatePicker(
        description='Pick a date',
        value=date.today(),
        min=date(2025, 4, 2),
        max=date.today()
    )

    output = widgets.Output()

    def on_date_change(change):
        with output:
            clear_output(wait=True)
            selected = change["new"]
            if not selected:
                print("Please pick a valid date.")
                return
            day_str = selected.strftime("%Y-%m-%d")
            print(f"Fetching most extreme posts for {day_str}...\n")

            result = get_extreme_mastodon_posts(day_str,KEYWORDS_TRUMP)
            if result.get("message") == "No matching posts":
                print("No relevant posts found for this date and topic.")
                return

            if not result or ("most_positive" not in result and "most_negative" not in result):
                print("No data available.")
                return

            if result.get("most_positive"):
                pos = result["most_positive"]
                print("【Most Positive Post】")
                print(f"User: {pos['user']}")
                print(f"Score: {pos['sentiment_score']:.4f}")
                print(f"Keywords: {', '.join(pos.get('matched_keywords', []))}")
                print(f"Content:\n{pos['content']}\n")
                print("-" * 80)

            if result.get("most_negative"):
                neg = result["most_negative"]
                print("\n【Most Negative Post】")
                print(f"User: {neg['user']}")
                print(f"Score: {neg['sentiment_score']:.4f}")
                print(f"Keywords: {', '.join(pos.get('matched_keywords', []))}")
                print(f"Content:\n{neg['content']}")

    date_picker.observe(on_date_change, names='value')
    display(date_picker, output)

# Forth Plot
def show_content_on_date_tariff():
    date_picker = widgets.DatePicker(
        description='Pick a date',
        value=date.today(),
        min=date(2025, 4, 2),
        max=date.today()
    )

    output = widgets.Output()

    def on_date_change(change):
        with output:
            clear_output(wait=True)
            selected = change["new"]
            if not selected:
                print("Please pick a valid date.")
                return
            day_str = selected.strftime("%Y-%m-%d")
            print(f"Fetching most extreme posts for {day_str}...\n")

            result = get_extreme_mastodon_posts(day_str,KEYWORDS_TARIFF)
            if result.get("message") == "No matching posts":
                print("No relevant posts found for this date and topic.")
                return

            if not result or ("most_positive" not in result and "most_negative" not in result):
                print("No data available.")
                return

            if result.get("most_positive"):
                pos = result["most_positive"]
                print("【Most Positive Post】")
                print(f"User: {pos['user']}")
                print(f"Score: {pos['sentiment_score']:.4f}")
                print(f"Keywords: {', '.join(pos.get('matched_keywords', []))}")
                print(f"Content:\n{pos['content']}\n")
                print("-" * 80)

            if result.get("most_negative"):
                neg = result["most_negative"]
                print("\n【Most Negative Post】")
                print(f"User: {neg['user']}")
                print(f"Score: {neg['sentiment_score']:.4f}")
                print(f"Keywords: {', '.join(pos.get('matched_keywords', []))}")
                print(f"Content:\n{neg['content']}")

    date_picker.observe(on_date_change, names='value')
    display(date_picker, output)

# Fifth Plot
def plot_trump_sentiment_trend(df_plot, event_list):
    import plotly.graph_objects as go
    from datetime import datetime

    df_plot = df_plot.sort_values("created_at")

    frames = []
    for k in range(3, len(df_plot) + 1):
        #max_date = df_plot['created_at'][:k].max()
        #print(f"Frame {k}: max_date = {max_date}")
        frames.append(
            go.Frame(
                data=[go.Scatter(
                    x=df_plot['created_at'][:k],
                    y=df_plot['avg_sentiment'][:k]
                )],
                name=str(k)
            )
        )

    fig = go.Figure(
        data=[go.Scatter(
            x=df_plot['created_at'][:2],
            y=df_plot['avg_sentiment'][:2],
            mode='lines+markers',
            name='Avg Sentiment')],
        frames=frames
    )

    for date_str, label, color, yshift in event_list:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        fig.add_shape(type="line", x0=d, x1=d, y0=0, y1=1, xref='x', yref='paper',
                      line=dict(color=color, width=2, dash="dash"))
        fig.add_annotation(x=d, y=1, xref='x', yref='paper', text=label,
                           showarrow=False, font=dict(color=color), yshift=yshift)

    fig.update_layout(
        title="Live Sentiment Trend on Trump Among Australians Since Tariff (Mastodon AU)",
        xaxis=dict(
            title="Date",
            range=[df_plot["created_at"].min(), df_plot["created_at"].max()]
        ),
        yaxis=dict(
            title="Avg Sentiment Score",
            range=[df_plot["avg_sentiment"].min() - 0.01, df_plot["avg_sentiment"].max() + 0.01]),
        template="plotly_white",
        width=1000,
        height=500,
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [None, {
                        "frame": {"duration": 100, "redraw": True},
                        "fromcurrent": True,
                        "mode": "immediate"
                    }]
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [[None], {
                        "mode": "immediate",
                        "frame": {"duration": 0}
                    }]
                }
            ]
        }],
        sliders=[{
            "steps": [
                {
                    "method": "animate",
                    "label": str(k),
                    "args": [[str(k)], {
                        "mode": "immediate",
                        "frame": {"duration": 0, "redraw": True}
                        }]
                    } for k in range(3, len(df_plot) + 1)
                ],
                "active": len(df_plot) - 3
            }]
        )

    return fig

# Sixth Plot
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
        title=f"Live Daily Trump Post Volume Among Australians (Mastodon AU)",
        xaxis_title="Date",
        yaxis_title="Post Count",
        template="plotly_white",
        hovermode="x unified",
        width=1000,
        height=500
    )

    return fig

# Seventh Plot
def plot_combined_sentiment_volume(start_date_str: str, get_summary_stats_func,title: str):
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
        title=f"Live Daily {title} Sentiment and Post Volume Among Australians (Mastodon AU)",
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

# Eighth Plot
def plot_keyword_sentiment_trend(df: pd.DataFrame):
    if df.empty:
        print("Empty DataFrame provided.")
        return None

    df = df.sort_values(by="date")

    fig = px.line(
        df,
        x="date",
        y="avg_sentiment",
        color="keyword",
        markers=True,
        title="Live Sentiment Trend on Trump-Related Keywords Since Tariff (Mastodon AU)",
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
        legend_title="Keyword",
        yaxis_title="Sentiment Score",
        xaxis_title="Date",
    )

    fig.add_hline(y=0, line_dash="dot", line_color="gray", annotation_text="Neutral")

    return fig

# Ninth Plot
def plot_keyword_distribution_stacked(df: pd.DataFrame):
    fig = px.line(
        df,
        x="date",
        y="count",
        color="keyword",
        markers=True,
        title="Live Trump Keyword Post Volume Trend Since Tariff (Mastodon AU)",
        labels={"count": "Post Count", "date": "Date", "keyword": "Keyword"}
    )

    fig.update_layout(template="plotly_white", width=1000, height=500)
    return fig

# Tenth Plot
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

# Eleventh Plot
def plot_cross_platform_sentiment_comparison(df_platform1, df_platform2,
                                             name1="Reddit", name2="Mastodon"):
    trump_keywords = {"trump", "donald trump", "maga", "make america great again", "potus", "trumpism", "trumpian"}
    tariff_keywords = {"tariff", "tariffs", "import tax", "trade war"}

    data = []

    for df, platform in zip([df_platform1, df_platform2], [name1, name2]):
        trump_sent = compute_weighted_sentiment(df, trump_keywords)
        tariff_sent = compute_weighted_sentiment(df, tariff_keywords)

        data.append((platform, "Trump Related", trump_sent))
        data.append((platform, "Tariff Related", tariff_sent))

    df_plot = pd.DataFrame(data, columns=["platform", "topic", "avg_sentiment"])

    fig = px.bar(
        df_plot,
        x="topic",
        y="avg_sentiment",
        color="platform",
        barmode="group",
        title="Live Cross-Platform Sentiment: Trump vs Tariff (Reddit vs Mastodon)",
        text_auto=".2f",
        color_discrete_map={
            name1: '#636EFA',   # Reddit
            name2: '#00CC96'    # Mastodon
        }
    )

    fig.update_layout(
        yaxis_title="Avg Sentiment",
        xaxis_title="Topic",
        template="plotly_white"
    )

    fig.show()

# Needed
def compute_weighted_sentiment(df, keyword_group: set) -> float:
    filtered = df[df["keyword"].isin(keyword_group)]
    if filtered.empty:
        return 0
    total_weight = filtered["count"].sum()
    weighted_sum = (filtered["avg_sentiment"] * filtered["count"]).sum()
    return weighted_sum / total_weight if total_weight else 0
