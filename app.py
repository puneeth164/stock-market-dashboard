import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()            # local testing only; Azure uses App Settings
except ImportError:
    pass

REFRESH = "15s"
BLUE, ORANGE, AQUA, RED, GRAY, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#e34948", "#8a8984", "#4a3aa7"
TEAM = ["Venkata Puneeth Sriramaneni", "Christopher Mavros", "Rylie Fischer"]

st.set_page_config(page_title="Live Stock Market Monitor", page_icon="📈", layout="wide")

st.markdown("""
<style>
.hero { text-align: center; padding: 0.4rem 0 0.2rem; }
.hero h1 {
    font-size: 2.9rem; font-weight: 800; margin: 0; padding: 0; letter-spacing: -0.5px;
    background: linear-gradient(90deg, #2a78d6, #1baf7a);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero .team { margin-top: 0.55rem; font-size: 0.95rem; opacity: 0.9; }
.hero .team .label {
    text-transform: uppercase; letter-spacing: 2px; font-size: 0.72rem; opacity: 0.65; margin-right: 0.6rem;
}
.hero .team .sep { opacity: 0.4; margin: 0 0.55rem; }
.hero .sub { margin-top: 0.35rem; font-size: 0.85rem; opacity: 0.6; }
.status {
    max-width: 920px; margin: 0.9rem auto 0.6rem; padding: 0.85rem 1.2rem; border-radius: 12px;
    text-align: center; border: 1px solid;
}
.status .head { font-size: 1.15rem; font-weight: 700; }
.status .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
.status .body { font-size: 0.92rem; margin-top: 0.2rem; opacity: 0.9; }
.status.open   { background: rgba(27,175,122,0.12); border-color: rgba(27,175,122,0.55); }
.status.open .dot   { background: #1baf7a; box-shadow: 0 0 0 4px rgba(27,175,122,0.25); }
.status.closed { background: rgba(42,120,214,0.12); border-color: rgba(42,120,214,0.55); }
.status.closed .dot { background: #2a78d6; }
.status .count { font-weight: 700; }
.alert {
    max-width: 920px; margin: 0.4rem auto 0.8rem; padding: 0.7rem 1.1rem; border-radius: 12px;
    background: rgba(227,73,72,0.12); border: 1px solid rgba(227,73,72,0.6); font-size: 0.92rem;
}
.alert b { color: #e34948; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1>Live Stock Market Monitor</h1>'
    '<div class="team"><span class="label">Team</span>'
    + '<span class="sep">·</span>'.join(TEAM) +
    '</div><div class="sub">Real 1-minute price bars for ~300 US stocks from Yahoo Finance, '
    'ingested every minute by an Azure Function into Azure PostgreSQL.</div></div>',
    unsafe_allow_html=True)

DB = {
    "host": os.environ.get("DATABASE_HOST"),
    "dbname": os.environ.get("DATABASE_NAME"),
    "user": os.environ.get("DATABASE_USER"),
    "password": os.environ.get("DATABASE_PASSWORD"),
    "port": os.environ.get("DATABASE_PORT", "5432"),
    "sslmode": os.environ.get("DATABASE_SSLMODE", "require"),
}


@st.cache_resource
def get_connection():
    conn = psycopg2.connect(**DB, connect_timeout=10)
    conn.autocommit = True          # every query sees the newest rows
    return conn


def q(sql, params=None):
    """Run a query and return a DataFrame; reconnect once if the connection dropped."""
    for attempt in (1, 2):
        try:
            with get_connection().cursor() as cur:
                cur.execute(sql, params)
                return pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            get_connection.clear()
            if attempt == 2:
                raise


def style(fig, height=320):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=1.08, x=0), hovermode="x unified")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.15)")
    return fig


def show(fig, height=320):
    st.plotly_chart(style(fig, height), width="stretch")


try:
    get_connection()
except Exception as e:
    st.error(f"Cannot reach the database. Check the DATABASE_* settings and the server firewall. ({e})")
    st.stop()


ET = ZoneInfo("America/New_York")


def next_market_open():
    """Next 9:30 AM ET on a weekday (US holidays are not taken into account)."""
    now = datetime.now(ET)
    day = now
    for _ in range(8):
        candidate = day.replace(hour=9, minute=30, second=0, microsecond=0)
        if candidate.weekday() < 5 and candidate > now:
            return candidate
        day = day + timedelta(days=1)
    return now


# =================================================================== 1. status + KPIs
@st.fragment(run_every=REFRESH)
def overview():
    k = q("""
        SELECT (SELECT COUNT(*) FROM stocks)                                        AS stocks,
               (SELECT COUNT(*) FROM price_bars)                                    AS bars,
               (SELECT COALESCE(SUM(bars_inserted), 0) FROM ingestion_runs
                 WHERE run_at > now() - interval '5 minutes')                       AS recent,
               (SELECT MAX(bar_time) FROM price_bars)                               AS last_bar,
               (SELECT COUNT(*) FROM outliers)                                      AS outliers,
               (SELECT accuracy FROM model_metrics ORDER BY recorded_at DESC LIMIT 1) AS acc,
               (SELECT MAX(run_at) FROM ingestion_runs)                             AS last_run
    """).iloc[0]

    last = k.last_bar
    live = last is not None and (datetime.now(timezone.utc) - last).total_seconds() < 600
    if live:
        st.markdown('<div class="status open"><div class="head"><span class="dot"></span>Market open</div>'
                    '<div class="body">Live data · new bars arrive every minute</div></div>',
                    unsafe_allow_html=True)
    else:
        nxt = next_market_open()
        left = nxt - datetime.now(ET)
        h, m = divmod(int(left.total_seconds() // 60), 60)
        when = f" Latest bar: {last:%a %b %d, %H:%M} UTC." if last is not None else ""
        st.markdown('<div class="status closed"><div class="head"><span class="dot"></span>Market closed</div>'
                    '<div class="body">US market trades 9:30 AM-4:00 PM ET, Monday-Friday. '
                    f'Showing the most recent trading session.{when}</div>'
                    f'<div class="body">Opens in <span class="count">{h} h {m:02d} min</span> '
                    f'({nxt:%a %I:%M %p} ET)</div></div>', unsafe_allow_html=True)

    alerts = q("""
        SELECT s.symbol, o.reason FROM outliers o
        JOIN price_bars p ON o.bar_id = p.bar_id JOIN stocks s ON p.stock_id = s.stock_id
        WHERE o.detected_at > now() - interval '5 minutes'
        ORDER BY ABS(o.score) DESC LIMIT 3
    """)
    if not alerts.empty:
        items = " &nbsp;|&nbsp; ".join(alerts.reason)
        st.markdown(f'<div class="alert"><b>⚠ New outliers (last 5 min):</b> {items}</div>',
                    unsafe_allow_html=True)

    c = st.columns(6)
    c[0].metric("Stocks tracked", f"{int(k.stocks):,}")
    c[1].metric("Price bars stored", f"{int(k.bars):,}")
    c[2].metric("Records / min (last 5 min)", f"{int(k.recent) / 5:,.0f}")
    c[3].metric("Outliers flagged", f"{int(k.outliers):,}")
    c[4].metric("Model accuracy", "—" if pd.isna(k.acc) else f"{k.acc:.1%}")
    c[5].metric("Last pipeline run (UTC)", "—" if k.last_run is None else f"{k.last_run:%H:%M:%S}")


overview()
st.divider()

# =================================================================== 2. the 4 dropdowns
symbols = q("SELECT symbol FROM stocks ORDER BY symbol").symbol.tolist()
if not symbols:
    st.warning("No stock data yet. Start the Azure Function and wait a minute.")
    st.stop()

WINDOWS = {"Last 30 minutes": 30, "Last 60 minutes": 60, "Last 2 hours": 120,
           "Latest full day": None, "All data (all days)": "all"}
METRICS = ["Price", "% change", "Volume", "Volatility (10-min)"]

st.subheader("Explore")
d1, d2, d3, d4 = st.columns(4)
stock_a = d1.selectbox("Stock A", symbols, index=symbols.index("AAPL") if "AAPL" in symbols else 0)
stock_b = d2.selectbox("Stock B (compare)", symbols,
                       index=symbols.index("MSFT") if "MSFT" in symbols else min(1, len(symbols) - 1))
window_label = d3.selectbox("Time window", list(WINDOWS), index=4)
metric = d4.selectbox("Metric", METRICS)
minutes = WINDOWS[window_label]


def window_start():
    """Start of the chosen window, measured back from the newest bar."""
    if minutes == "all":
        return q("SELECT MIN(bar_time) AS t FROM price_bars").t[0]
    if minutes is None:
        return q("SELECT date_trunc('day', MAX(bar_time)) AS t FROM price_bars").t[0]
    return q(f"SELECT MAX(bar_time) - interval '{int(minutes)} minutes' AS t FROM price_bars").t[0]


def stock_series(symbol, start):
    df = q("""
        SELECT p.bar_time, p.open, p.high, p.low, p.close, p.volume
        FROM price_bars p JOIN stocks s ON p.stock_id = s.stock_id
        WHERE s.symbol = %s AND p.bar_time >= %s ORDER BY p.bar_time
    """, (symbol, start))
    if df.empty:
        return df
    df["% change"] = 100 * (df.close / df.close.iloc[0] - 1)
    df["Volatility (10-min)"] = 100 * df.close.pct_change().rolling(10, min_periods=3).std()
    df["Price"] = df.close
    df["Volume"] = df.volume
    return df


# =================================================================== 3. Stock A | Stock B
@st.fragment(run_every=REFRESH)
def compare(a, b, metric):
    start = window_start()
    da, db = stock_series(a, start), stock_series(b, start)
    flagged = q("""
        SELECT s.symbol, p.bar_time, p.close, o.reason
        FROM outliers o JOIN price_bars p ON o.bar_id = p.bar_id
        JOIN stocks s ON p.stock_id = s.stock_id
        WHERE s.symbol IN (%s, %s) AND p.bar_time >= %s
    """, (a, b, start))

    left, right = st.columns(2)
    for col, sym, df, color in ((left, a, da, BLUE), (right, b, db, ORANGE)):
        with col:
            if df.empty:
                st.subheader(sym)
                st.info("No bars in this window.")
                continue
            last, first = df.close.iloc[-1], df.close.iloc[0]
            st.subheader(f"{sym} · \\${last:,.2f}")
            st.caption(f"{100 * (last / first - 1):+.2f}% in window · "
                       f"high \\${df.high.max():,.2f} · low \\${df.low.min():,.2f} · "
                       f"{int(df.volume.sum()):,} shares")
            if metric == "Volume":
                fig = px.bar(df, x="bar_time", y="Volume", color_discrete_sequence=[color],
                             labels={"bar_time": "Time (UTC)"})
            else:
                fig = go.Figure(go.Scatter(x=df.bar_time, y=df[metric], mode="lines", name=metric,
                                           line=dict(color=color, width=2)))
                if metric == "Price":
                    f = flagged[flagged.symbol == sym]
                    if not f.empty:
                        fig.add_trace(go.Scatter(x=f.bar_time, y=f.close, mode="markers", name="Outlier",
                                                 text=f.reason, hovertemplate="%{text}",
                                                 marker=dict(color=RED, size=10,
                                                             line=dict(width=2, color="white"))))
                fig.update_yaxes(title=metric)
            show(fig, 300)

    if not da.empty and not db.empty:
        st.markdown(f"**{a} vs {b}: % change on the same scale**")
        both = go.Figure()
        both.add_trace(go.Scatter(x=da.bar_time, y=da["% change"], name=a, line=dict(color=BLUE, width=2)))
        both.add_trace(go.Scatter(x=db.bar_time, y=db["% change"], name=b, line=dict(color=ORANGE, width=2)))
        both.update_yaxes(title="% change since window start", ticksuffix="%")
        show(both, 280)
        joined = da.set_index("bar_time").close.pct_change().to_frame("a").join(
            db.set_index("bar_time").close.pct_change().to_frame("b"), how="inner").dropna()
        if len(joined) > 5:
            st.caption(f"Correlation of 1-minute returns: **{joined.a.corr(joined.b):.2f}** "
                       f"(1 = move together, 0 = unrelated, −1 = opposite)")


compare(stock_a, stock_b, metric)
st.divider()


# =================================================================== 3b. candlesticks
@st.fragment(run_every=REFRESH)
def candles(a, b):
    st.subheader("Candlestick charts")
    st.caption("Each candle is one minute: body = open to close, thin line = high to low. "
               "Green = price rose in that minute, red = price fell.")
    start = window_start()
    left, right = st.columns(2)
    for col, sym in ((left, a), (right, b)):
        with col:
            df = stock_series(sym, start)
            st.markdown(f"**{sym}**")
            if df.empty:
                st.info("No bars in this window.")
                continue
            fig = go.Figure(go.Candlestick(x=df.bar_time, open=df.open, high=df.high, low=df.low,
                                           close=df.close, name=sym,
                                           increasing_line_color=AQUA, decreasing_line_color=RED))
            fig.update_layout(xaxis_rangeslider_visible=False, showlegend=False)
            fig.update_yaxes(title="Price ($)")
            show(fig, 320)


candles(stock_a, stock_b)
st.divider()


# =================================================================== 4. gainers | losers, active | volatile
def window_stats(start):
    return q("""
        WITH b AS (SELECT s.symbol, p.bar_time, p.close, p.volume
                   FROM price_bars p JOIN stocks s ON p.stock_id = s.stock_id
                   WHERE p.bar_time >= %s),
        r AS (SELECT symbol, volume, close / LAG(close) OVER (PARTITION BY symbol ORDER BY bar_time) - 1 AS ret
              FROM b)
        SELECT b.symbol,
               100 * ((array_agg(b.close ORDER BY b.bar_time DESC))[1]
                    / (array_agg(b.close ORDER BY b.bar_time))[1] - 1) AS change_pct,
               SUM(b.volume)::float8 AS volume,
               (SELECT 100 * STDDEV(r.ret) FROM r WHERE r.symbol = b.symbol) AS volatility
        FROM b GROUP BY b.symbol
    """, (start,))


def hbar(df, x, color, fmt, title):
    fig = px.bar(df, x=x, y="symbol", orientation="h", text=x, color_discrete_sequence=[color],
                 labels={x: title, "symbol": ""})
    fig.update_traces(texttemplate=fmt, textposition="inside", insidetextanchor="end",
                      textfont=dict(color="white"))
    fig.update_layout(showlegend=False, hovermode="closest")
    show(fig, 380)


@st.fragment(run_every=REFRESH)
def leaders():
    stats = window_stats(window_start())
    if stats.empty:
        st.info("Not enough data yet.")
        return
    st.subheader(f"Market leaders · {window_label.lower()}")
    l, r = st.columns(2)
    with l:
        st.markdown("**Top gainers**")
        hbar(stats.nlargest(10, "change_pct").sort_values("change_pct"), "change_pct", BLUE,
             "%{text:+.2f}%", "Change (%)")
    with r:
        st.markdown("**Top losers**")
        hbar(stats.nsmallest(10, "change_pct").sort_values("change_pct", ascending=False), "change_pct", RED,
             "%{text:+.2f}%", "Change (%)")
    l, r = st.columns(2)
    with l:
        st.markdown("**Most traded (shares)**")
        hbar(stats.nlargest(10, "volume").sort_values("volume"), "volume", AQUA,
             "%{text:.3s}", "Shares traded")
    with r:
        st.markdown("**Most volatile (std. dev. of 1-min returns)**")
        hbar(stats.dropna(subset=["volatility"]).nlargest(10, "volatility").sort_values("volatility"),
             "volatility", VIOLET, "%{text:.3f}%", "Volatility (%)")


leaders()
st.divider()


# =================================================================== 4b. heatmap
@st.fragment(run_every=REFRESH)
def heatmap():
    st.subheader(f"Market heatmap · {window_label.lower()}")
    st.caption("One tile per stock. Tile size = shares traded, color = % change "
               "(green rising, red falling). Hover a tile for details.")
    stats = window_stats(window_start())
    if stats.empty:
        st.info("Not enough data yet.")
        return
    stats = stats[stats.volume > 0].copy()
    stats["label"] = stats.symbol + "<br>" + stats.change_pct.map(lambda v: f"{v:+.2f}%")
    lim = max(0.5, float(stats.change_pct.abs().quantile(0.95)))
    fig = px.treemap(stats, path=[px.Constant("All stocks"), "label"], values="volume",
                     color="change_pct", color_continuous_scale=[[0, RED], [0.5, "#3a3a38"], [1, AQUA]],
                     range_color=[-lim, lim], custom_data=["symbol", "change_pct", "volume"])
    fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Change: %{customdata[1]:+.2f}%"
                                    "<br>Shares: %{customdata[2]:,.0f}<extra></extra>",
                      texttemplate="%{label}", textfont=dict(color="white"), root_color="rgba(0,0,0,0)")
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=0, b=0),
                      coloraxis_colorbar=dict(title="% change", ticksuffix="%"))
    st.plotly_chart(fig, width="stretch")


heatmap()
st.divider()


# =================================================================== 5. breadth | ingestion
@st.fragment(run_every=REFRESH)
def pipeline():
    l, r = st.columns(2)
    with l:
        st.subheader("Market breadth")
        st.caption("Share of stocks whose price rose in each minute (above 50% = most stocks rising).")
        br = q("""
            WITH x AS (SELECT bar_time,
                              close > LAG(close) OVER (PARTITION BY stock_id ORDER BY bar_time) AS up
                       FROM price_bars WHERE bar_time >= %s)
            SELECT bar_time, 100 * AVG(up::int) AS pct_up, COUNT(*) AS n
            FROM x WHERE up IS NOT NULL GROUP BY bar_time HAVING COUNT(*) > 20 ORDER BY bar_time
        """, (window_start(),))
        if br.empty:
            st.info("Not enough data yet.")
        else:
            fig = go.Figure(go.Scatter(x=br.bar_time, y=br.pct_up, mode="lines", name="% rising",
                                       line=dict(color=BLUE, width=2)))
            fig.add_hline(y=50, line_dash="dash", line_color=GRAY)
            fig.update_yaxes(title="% of stocks rising", ticksuffix="%", range=[0, 100])
            show(fig, 300)
    with r:
        st.subheader("Records ingested per run")
        st.caption("New rows written by the Azure Function on each 1-minute run.")
        runs = q("""SELECT run_at, bars_inserted FROM ingestion_runs
                    WHERE bars_inserted > 0 ORDER BY run_at DESC LIMIT 60""")
        if runs.empty:
            st.info("No ingestion runs with new data yet.")
        else:
            fig = px.bar(runs.sort_values("run_at"), x="run_at", y="bars_inserted",
                         labels={"run_at": "Run time (UTC)", "bars_inserted": "New records"},
                         color_discrete_sequence=[BLUE])
            show(fig, 300)


pipeline()
st.divider()


# =================================================================== 6. outliers
@st.fragment(run_every=REFRESH)
def outliers():
    st.subheader("Outlier detection")
    st.caption("Robust z-score (median and MAD) per stock over the last 90 minutes; |z| > 3.5 is flagged "
               "for 1-minute price jumps and volume spikes.")
    l, r = st.columns([3, 2])
    with l:
        out = q("""
            SELECT s.symbol, p.bar_time AS bar_minute,
                   ROUND(o.score::numeric, 1)::float8 AS z_score, o.reason, o.method
            FROM outliers o JOIN price_bars p ON o.bar_id = p.bar_id
            JOIN stocks s ON p.stock_id = s.stock_id
            ORDER BY p.bar_time DESC, ABS(o.score) DESC LIMIT 50
        """)
        if out.empty:
            st.info("No outliers flagged yet (needs about 30 minutes of history per stock).")
        else:
            st.dataframe(out, hide_index=True, width="stretch", height=380)
    with r:
        top = q("""
            SELECT s.symbol,
                   SUM((o.method = 'price_jump_robust_z')::int)   AS price_jumps,
                   SUM((o.method = 'volume_spike_robust_z')::int) AS volume_spikes
            FROM outliers o JOIN price_bars p ON o.bar_id = p.bar_id
            JOIN stocks s ON p.stock_id = s.stock_id
            GROUP BY s.symbol ORDER BY COUNT(*) DESC LIMIT 10
        """)
        if top.empty:
            st.info("Nothing to chart yet.")
        else:
            top = top.iloc[::-1]
            fig = go.Figure()
            fig.add_trace(go.Bar(y=top.symbol, x=top.price_jumps, orientation="h",
                                 name="Price jumps", marker_color=RED))
            fig.add_trace(go.Bar(y=top.symbol, x=top.volume_spikes, orientation="h",
                                 name="Volume spikes", marker_color=ORANGE))
            fig.update_layout(barmode="stack", hovermode="closest")
            fig.update_xaxes(title="Outliers flagged")
            st.markdown("**Stocks with the most outliers**")
            show(fig, 350)


outliers()
st.divider()


# =================================================================== 7. model
@st.fragment(run_every=REFRESH)
def model():
    st.subheader("Online model: will the price rise in the next minute?")
    st.caption("SGD logistic regression updated every minute with partial_fit. "
               "Each bar is predicted before the model learns from it (test-then-train).")
    l, r = st.columns([3, 2])
    with l:
        m = q("SELECT recorded_at, accuracy, f1, baseline_accuracy FROM model_metrics ORDER BY recorded_at")
        if m.empty:
            st.info("No model results yet (the model needs a few minutes of data).")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=m.recorded_at, y=m.accuracy, name="Accuracy",
                                     line=dict(color=BLUE, width=2)))
            fig.add_trace(go.Scatter(x=m.recorded_at, y=m.f1, name="F1 score",
                                     line=dict(color=AQUA, width=2)))
            fig.add_trace(go.Scatter(x=m.recorded_at, y=m.baseline_accuracy, name="Baseline (majority guess)",
                                     line=dict(color=GRAY, width=2, dash="dash")))
            fig.update_yaxes(tickformat=".0%", title="Score")
            show(fig, 320)
    with r:
        cm = q("""
            SELECT SUM((predicted_up AND actual_up)::int)         AS tp,
                   SUM((predicted_up AND NOT actual_up)::int)     AS fp,
                   SUM((NOT predicted_up AND actual_up)::int)     AS fn,
                   SUM((NOT predicted_up AND NOT actual_up)::int) AS tn
            FROM predictions WHERE predicted_up IS NOT NULL
        """).iloc[0]
        if pd.isna(cm.tp):
            st.info("No predictions yet.")
        else:
            st.markdown("**Confusion matrix**")
            z = [[int(cm.tp), int(cm.fn)], [int(cm.fp), int(cm.tn)]]
            fig = go.Figure(go.Heatmap(z=z, x=["Predicted up", "Predicted down"], y=["Actually up", "Actually down"],
                                       text=[[f"{v:,}" for v in row] for row in z], texttemplate="%{text}",
                                       colorscale=[[0, "#cde2fb"], [1, "#184f95"]], showscale=False))
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(hovermode="closest")
            show(fig, 260)
            total = sum(map(sum, z))
            st.caption(f"{total:,} predictions · precision {cm.tp / max(cm.tp + cm.fp, 1):.1%} · "
                       f"recall {cm.tp / max(cm.tp + cm.fn, 1):.1%}")


model()