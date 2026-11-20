"""Ola Ride Insights - Streamlit app
Tabs: Dashboard (interactive KPIs + charts) | SQL Insights (10 required queries + custom SQL) |
      Data Explorer (search/filter/download) | Power BI (embed published report)
Run:  streamlit run app.py
"""
import re, sqlite3
from pathlib import Path
import pandas as pd, plotly.express as px, plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).parent
# Cool "glacier" palette
INK, NAVY, INDIGO, TEAL, SKY, LAV, CORAL = "#0F1E3A", "#1B3A6B", "#4F5BD5", "#12A8A0", "#4DB6E8", "#B7BEF7", "#F2788F"
ICE, MIST, SLATE = "#EEF3F9", "#D6E2F1", "#5A6B88"
COLORWAY = [INDIGO, TEAL, SKY, LAV, NAVY, CORAL]
STATUS_COLORS = {"Success": TEAL, "Canceled by Customer": INDIGO, "Canceled by Driver": CORAL, "Driver Not Found": LAV}
VEHICLE_ORDER = ["Prime Sedan", "Prime SUV", "Prime Plus", "Mini", "Auto", "Bike", "E-Bike"]
st.set_page_config(page_title="Ola Ride Insights", page_icon="🚖", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Figtree:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Figtree', sans-serif; }
h1, h2, h3, h4 { font-family: 'Outfit', sans-serif !important; color: __INK__; letter-spacing: -0.01em; }
.stApp { background: linear-gradient(180deg, __ICE__ 0%, #E6EEF8 100%); }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.6rem; max-width: 1320px; }

/* sidebar */
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #F7FAFE 0%, __MIST__ 100%); border-right: 1px solid __MIST__; }
section[data-testid="stSidebar"] h1 { font-size: 1.35rem; }

/* hero banner: the one bold element */
.hero { background: linear-gradient(120deg, __INK__ 0%, __NAVY__ 48%, __INDIGO__ 100%); border-radius: 22px;
        padding: 30px 36px 26px; margin-bottom: 22px; color: #F4F8FF; position: relative; overflow: hidden; }
.hero:after { content: ""; position: absolute; right: -60px; top: -80px; width: 320px; height: 320px; border-radius: 50%;
        background: radial-gradient(circle, rgba(18,168,160,.55) 0%, rgba(18,168,160,0) 68%); }
.hero h1 { color: #FFFFFF !important; font-size: 2.35rem; margin: 0 0 6px; font-weight: 700; }
.hero p { color: #C9D8F2; margin: 0; font-size: 1.02rem; max-width: 62ch; line-height: 1.5; }
.hero .facts { margin-top: 16px; display: flex; gap: 28px; flex-wrap: wrap; font-size: .92rem; color: #9FC3F2; }
.hero .facts b { color: #FFFFFF; font-weight: 600; }

/* KPI cards */
.kpi { background: #FFFFFF; border: 1px solid __MIST__; border-top: 4px solid var(--accent); border-radius: 16px; padding: 14px 16px 12px; min-height: 108px; }
.kpi .lab { color: __SLATE__; font-size: .84rem; font-weight: 500; margin-bottom: 4px; }
.kpi .val { font-family: 'Outfit', sans-serif; font-size: 1.75rem; font-weight: 700; color: __INK__; line-height: 1.15; }
.kpi .note { color: __SLATE__; font-size: .78rem; margin-top: 4px; }

/* insight line under each section */
.insight { background: #FFFFFF; border: 1px solid __MIST__; border-left: 5px solid __TEAL__; border-radius: 12px;
           padding: 11px 16px; margin: 6px 0 16px; color: __INK__; font-size: .95rem; }

/* tabs as pills */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: none; }
.stTabs [data-baseweb="tab"] { background: #FFFFFF; border: 1px solid __MIST__; border-radius: 999px; padding: 6px 18px; height: auto; color: __NAVY__; font-weight: 500; }
.stTabs [aria-selected="true"] { background: __INDIGO__; color: #FFFFFF !important; border-color: __INDIGO__; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* chart panels, tables, buttons */
div[data-testid="stPlotlyChart"] { background: #FFFFFF; border: 1px solid __MIST__; border-radius: 16px; padding: 6px 8px; }
div[data-testid="stDataFrame"] { border: 1px solid __MIST__; border-radius: 12px; overflow: hidden; }
.stButton > button, .stDownloadButton > button { background: __INDIGO__; color: #FFFFFF; border: none; border-radius: 10px; padding: 8px 18px; font-weight: 500; }
.stButton > button:hover, .stDownloadButton > button:hover { background: __NAVY__; color: #FFFFFF; }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline: 3px solid __SKY__; }
@media (max-width: 700px) { .hero h1 { font-size: 1.7rem; } .hero { padding: 22px 20px; } }
</style>
"""
for k, v in {"__INK__": "#0F1E3A", "__NAVY__": "#1B3A6B", "__INDIGO__": "#4F5BD5", "__TEAL__": "#12A8A0", "__SKY__": "#4DB6E8",
             "__ICE__": "#EEF3F9", "__MIST__": "#D6E2F1", "__SLATE__": "#5A6B88"}.items():
    CSS = CSS.replace(k, v)
st.markdown(CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------ data layer
@st.cache_data(show_spinner="Loading Ola ride data...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "ola_cleaned.csv", parse_dates=["Date", "Booking_Datetime"])
    return df

@st.cache_resource
def get_connection() -> sqlite3.Connection:
    """In-memory SQLite built from the cleaned CSV (identical schema to the MySQL table)."""
    con = sqlite3.connect(":memory:", check_same_thread=False)
    d = load_data().copy()
    d["Date"] = d["Date"].dt.strftime("%Y-%m-%d"); d["Booking_Datetime"] = d["Booking_Datetime"].astype(str)
    d.to_sql("ola_rides", con, index=False)
    return con

@st.cache_data
def parse_sql_file(path: str) -> dict:
    txt = Path(path).read_text()
    return {n.strip(): q.strip() for n, q in (b.partition("\n")[::2] for b in re.split(r"-- name: ", txt)[1:])}

def run_sql(q: str) -> pd.DataFrame:
    return pd.read_sql_query(q, get_connection())

df_all = load_data()

# ------------------------------------------------------------------ sidebar filters
st.sidebar.title("Ola Ride Insights")
st.sidebar.caption("July 2024 · Bengaluru")
dmin, dmax = df_all.Date.min().date(), df_all.Date.max().date()
dr = st.sidebar.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
if isinstance(dr, tuple) and len(dr) == 2: d0, d1 = dr
else: d0 = d1 = dr[0] if isinstance(dr, tuple) else dr
vehicles = st.sidebar.multiselect("Vehicle type", VEHICLE_ORDER, default=VEHICLE_ORDER)
statuses = st.sidebar.multiselect("Booking status", sorted(df_all.Booking_Status.unique()),
                                  default=sorted(df_all.Booking_Status.unique()))
f = df_all[df_all.Date.between(pd.Timestamp(d0), pd.Timestamp(d1)) & df_all.Vehicle_Type.isin(vehicles)
           & df_all.Booking_Status.isin(statuses)]
st.sidebar.metric("Rows after filters", f"{len(f):,}")
st.sidebar.markdown("---")
st.sidebar.caption("Filters apply to the Dashboard and Data Explorer tabs. SQL Insights always queries the full dataset.")

st.markdown(f"""
<div class="hero">
  <h1>Ola Ride Insights</h1>
  <p>See where bookings succeed or fail, which vehicles and payments drive revenue, and what riders and drivers say in their ratings.</p>
  <div class="facts"><span><b>{len(f):,}</b> rides in view</span><span><b>{d0:%d %b} to {d1:%d %b %Y}</b></span><span><b>{f.Customer_ID.nunique():,}</b> customers</span></div>
</div>""", unsafe_allow_html=True)
tab_dash, tab_sql, tab_data, tab_pbi = st.tabs(["Dashboard", "SQL insights", "Data explorer", "Power BI"])

def kpi(col, label, value, note, accent):
    col.markdown(f'<div class="kpi" style="--accent:{accent}"><div class="lab">{label}</div><div class="val">{value}</div><div class="note">{note}</div></div>',
                 unsafe_allow_html=True)

def insight(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)

def style(fig, h=360):
    fig.update_layout(height=h, margin=dict(l=12, r=12, t=50, b=12), template="plotly_white", colorway=COLORWAY,
                      font=dict(family="Figtree, sans-serif", color=INK), legend_title_text="",
                      title=dict(font=dict(family="Outfit, sans-serif", size=16, color=INK)),
                      paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", hoverlabel=dict(font_family="Figtree"))
    fig.update_xaxes(gridcolor=MIST, linecolor=MIST); fig.update_yaxes(gridcolor=MIST, linecolor=MIST)
    return fig

# ================================================================== DASHBOARD
with tab_dash:
    if f.empty:
        st.warning("No rides match the current filters."); st.stop()
    succ = f[f.Is_Success == 1]
    k = st.columns(6)
    kpi(k[0], "Total bookings", f"{len(f):,}", "all statuses in view", INDIGO)
    kpi(k[1], "Success rate", f"{f.Is_Success.mean():.1%}", f"{len(succ):,} completed", TEAL)
    kpi(k[2], "Revenue", f"₹{succ.Booking_Value.sum()/1e6:.2f}M", "successful rides", SKY)
    kpi(k[3], "Average fare", f"₹{succ.Booking_Value.mean():,.0f}" if len(succ) else "-", "per successful ride", INDIGO)
    kpi(k[4], "Average distance", f"{succ.Ride_Distance.mean():.1f} km" if len(succ) else "-", "completed rides", TEAL)
    kpi(k[5], "Rating, driver / customer", f"{succ.Driver_Ratings.mean():.2f} / {succ.Customer_Ratings.mean():.2f}" if len(succ) else "-", "scale 1 to 5", LAV)
    st.write("")

    s_overall, s_vehicle, s_revenue, s_cancel, s_rating = st.tabs(["Overall", "Vehicle Type", "Revenue", "Cancellation", "Ratings"])

    with s_overall:
        insight(f"<b>{1 - f.Is_Success.mean():.1%}</b> of the bookings in this view did not complete. "
                f"Driver cancellations and unfound drivers make up <b>{(f.Booking_Status.isin(['Canceled by Driver', 'Driver Not Found'])).mean():.1%}</b>.")
        c1, c2 = st.columns([3, 2])
        daily = f.groupby(["Date", "Booking_Status"]).size().reset_index(name="Rides")
        c1.plotly_chart(style(px.line(daily, x="Date", y="Rides", color="Booking_Status", title="Ride volume over time",
                                      color_discrete_map=STATUS_COLORS)), width="stretch")
        stat = f.Booking_Status.value_counts().reset_index()
        c2.plotly_chart(style(px.pie(stat, names="Booking_Status", values="count", hole=.55, title="Booking status breakdown",
                                     color_discrete_map=STATUS_COLORS)), width="stretch")
        hourly = f.groupby("Hour").size().reset_index(name="Bookings")
        fig = px.bar(hourly, x="Hour", y="Bookings", title="Demand by hour of day (peak-hour driver allocation)", color_discrete_sequence=[TEAL])
        st.plotly_chart(style(fig, 300), width="stretch")

    with s_vehicle:
        _vd = f.groupby("Vehicle_Type").Ride_Distance.sum()
        insight(f"<b>{_vd.idxmax()}</b> covers the most distance ({_vd.max():,.0f} km). Compare Auto's average trip length with the other types in the table.")
        g = f.groupby("Vehicle_Type").agg(
            Total_Booking_Value=("Booking_Value", "sum"), Success_Booking_Value=("Success_Revenue", "sum"),
            Avg_Distance_km=("Ride_Distance", lambda s: s[s > 0].mean()), Total_Distance_km=("Ride_Distance", "sum"),
            Success_Rate=("Is_Success", "mean")).reindex([v for v in VEHICLE_ORDER if v in f.Vehicle_Type.unique()])
        st.dataframe(g.style.format({"Total_Booking_Value": "₹{:,.0f}", "Success_Booking_Value": "₹{:,.0f}",
                                     "Avg_Distance_km": "{:.1f}", "Total_Distance_km": "{:,.0f}", "Success_Rate": "{:.1%}"}),
                     width="stretch")
        top5 = g.Total_Distance_km.sort_values(ascending=False).head(5).reset_index()
        c1, c2 = st.columns(2)
        c1.plotly_chart(style(px.bar(top5, x="Total_Distance_km", y="Vehicle_Type", orientation="h",
                                     title="Top 5 vehicle types by ride distance", color_discrete_sequence=[INDIGO])
                              .update_yaxes(autorange="reversed")), width="stretch")
        c2.plotly_chart(style(px.bar(g.reset_index(), x="Vehicle_Type", y="Avg_Distance_km", title="Average distance (km, completed rides)",
                                     color_discrete_sequence=[TEAL])), width="stretch")

    with s_revenue:
        _pm = succ.groupby("Payment_Method").Booking_Value.sum()
        if len(_pm): insight(f"<b>{_pm.idxmax()}</b> brings in {_pm.max()/_pm.sum():.0%} of revenue in this view.")
        c1, c2 = st.columns(2)
        pm = succ.groupby("Payment_Method").Booking_Value.sum().reset_index()
        c1.plotly_chart(style(px.pie(pm, names="Payment_Method", values="Booking_Value", hole=.5, title="Revenue by payment method",
                                     color_discrete_sequence=COLORWAY)), width="stretch")
        top_c = succ.groupby("Customer_ID").Booking_Value.sum().nlargest(5).reset_index()
        c2.plotly_chart(style(px.bar(top_c, x="Booking_Value", y="Customer_ID", orientation="h", title="Top 5 customers by booking value",
                                     color_discrete_sequence=[TEAL]).update_yaxes(autorange="reversed")), width="stretch")
        dd = succ.groupby("Date").Ride_Distance.sum().reset_index()
        st.plotly_chart(style(px.area(dd, x="Date", y="Ride_Distance", title="Ride distance per day (km)",
                                      color_discrete_sequence=[SKY]), 300), width="stretch")

    with s_cancel:
        _cd = f[f.Booking_Status == "Canceled by Driver"].Cancel_Reason_Driver.value_counts()
        if len(_cd): insight(f"The top driver reason is <b>{_cd.index[0]}</b> with {_cd.iloc[0]:,} rides ({_cd.iloc[0]/_cd.sum():.0%} of driver cancellations).")
        c1, c2 = st.columns(2)
        cc = f[f.Booking_Status == "Canceled by Customer"].Cancel_Reason_Customer.value_counts().reset_index()
        cd = f[f.Booking_Status == "Canceled by Driver"].Cancel_Reason_Driver.value_counts().reset_index()
        c1.plotly_chart(style(px.bar(cc, x="count", y="Cancel_Reason_Customer", orientation="h", title="Customer cancellation reasons",
                                     color_discrete_sequence=[INDIGO]).update_yaxes(autorange="reversed")), width="stretch")
        c2.plotly_chart(style(px.bar(cd, x="count", y="Cancel_Reason_Driver", orientation="h", title="Driver cancellation reasons",
                                     color_discrete_sequence=[CORAL]).update_yaxes(autorange="reversed")), width="stretch")
        inc = f[f.Incomplete_Rides == "Yes"].Incomplete_Rides_Reason.value_counts().reset_index()
        if not inc.empty:
            st.plotly_chart(style(px.bar(inc, x="Incomplete_Rides_Reason", y="count", title="Incomplete rides by reason",
                                         color_discrete_sequence=[SKY]), 300), width="stretch")

    with s_rating:
        if len(succ): insight(f"Ratings sit between <b>{succ.Driver_Ratings.min():.1f}</b> and <b>{succ.Driver_Ratings.max():.1f}</b>. The average driver rating is {succ.Driver_Ratings.mean():.2f}.")
        c1, c2 = st.columns(2)
        c1.plotly_chart(style(px.histogram(succ, x="Driver_Ratings", nbins=21, title="Driver ratings distribution",
                                           color_discrete_sequence=[TEAL])), width="stretch")
        c2.plotly_chart(style(px.histogram(succ, x="Customer_Ratings", nbins=21, title="Customer ratings distribution",
                                           color_discrete_sequence=[INDIGO])), width="stretch")
        rv = succ.groupby("Vehicle_Type")[["Driver_Ratings", "Customer_Ratings"]].mean().reset_index()
        fig = go.Figure([go.Bar(name="Driver", x=rv.Vehicle_Type, y=rv.Driver_Ratings, marker_color=TEAL),
                         go.Bar(name="Customer", x=rv.Vehicle_Type, y=rv.Customer_Ratings, marker_color=INDIGO)])
        fig.update_layout(barmode="group", title="Average rating by vehicle type: customer vs driver", yaxis_range=[3, 5])
        st.plotly_chart(style(fig, 320), width="stretch")

# ================================================================== SQL INSIGHTS
with tab_sql:
    st.subheader("SQL insights")
    st.caption("Queries from `sql/02_ola_queries.sql` (the 10 required questions) and `sql/03_dashboard_support_queries.sql`. "
               "They run live against the full dataset.")
    queries = {**parse_sql_file(str(ROOT / "sql" / "02_ola_queries.sql")), **parse_sql_file(str(ROOT / "sql" / "03_dashboard_support_queries.sql"))}
    choice = st.selectbox("Choose a question", list(queries))
    st.code(queries[choice], language="sql")
    res = run_sql(queries[choice])
    st.write(f"**{len(res):,} row(s)**")
    st.dataframe(res.head(1000), width="stretch")
    st.download_button("Download result (CSV)", res.to_csv(index=False), f"{choice.split(' - ')[0]}.csv", "text/csv")
    st.markdown("#### Custom SQL (read-only)")
    custom = st.text_area("Table: `ola_rides`", "SELECT Vehicle_Type, COUNT(*) AS rides FROM ola_rides GROUP BY Vehicle_Type", height=100)
    if st.button("Run query"):
        if not re.match(r"^\s*(select|with)\b", custom, re.I) or re.search(r"\b(insert|update|delete|drop|alter|create|attach|pragma)\b", custom, re.I):
            st.error("Only read-only SELECT queries are allowed.")
        else:
            try: st.dataframe(run_sql(custom).head(2000), width="stretch")
            except Exception as e: st.error(f"SQL error: {e}")

# ================================================================== DATA EXPLORER
with tab_data:
    st.subheader("Data explorer")
    c1, c2, c3 = st.columns(3)
    q = c1.text_input("Search Booking / Customer ID")
    pay = c2.multiselect("Payment method", sorted(df_all.Payment_Method.unique()))
    loc = c3.text_input("Pickup or drop location contains")
    x = f
    if q: x = x[x.Booking_ID.str.contains(q, case=False) | x.Customer_ID.str.contains(q, case=False)]
    if pay: x = x[x.Payment_Method.isin(pay)]
    if loc: x = x[x.Pickup_Location.str.contains(loc, case=False) | x.Drop_Location.str.contains(loc, case=False)]
    st.write(f"**{len(x):,}** rides")
    st.dataframe(x.drop(columns=["Booking_Datetime"]).head(2000), width="stretch", height=450)
    st.download_button("Download filtered data (CSV)", x.to_csv(index=False), "ola_filtered.csv", "text/csv")

# ================================================================== POWER BI
with tab_pbi:
    st.subheader("Power BI dashboard")
    st.caption("Publish the report to Power BI Service → File ▸ Embed report ▸ Publish to web (public) → paste the link. "
               "Or set `POWERBI_EMBED_URL` in `.streamlit/secrets.toml`.")
    try: default = st.secrets.get("POWERBI_EMBED_URL", "")
    except Exception: default = ""      # no secrets.toml configured
    url = st.text_input("Power BI embed URL", default, placeholder="https://app.powerbi.com/view?r=...")
    if url.startswith("https://app.powerbi.com/"):
        components.iframe(url, height=720, scrolling=True)
    elif url:
        st.error("URL must start with https://app.powerbi.com/")
    else:
        st.info("No report linked yet. The **Dashboard** tab mirrors the same five Power BI pages natively.")
