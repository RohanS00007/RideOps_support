import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "favicon.png")

st.set_page_config(page_title="RideOps Support Triage Console", page_icon=ICON, layout="wide", initial_sidebar_state="collapsed")
# Palette: Cream #F3EEE3, Ink #111111, Burnt Orange #D9541E (theme is set in .streamlit/config.toml)
INK, CREAM, ORANGE = "#111111", "#F3EEE3", "#D9541E"
GRID, GREY = "#DFD7CA", "#9A948A"

st.set_page_config(page_title="RideOps Support Triage Console", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@1&family=Inter:wght@400;500;600;700;800&display=swap');
#MainMenu, footer, .stDeployButton, [data-testid="stToolbar"], [data-testid="stDecoration"], header[data-testid="stHeader"] { display: none !important; }
.block-container { padding-top: 1.25rem !important; padding-bottom: 3rem !important; max-width: 1280px !important; }
html, body, .stApp { font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif !important; background-color: #F3EEE3 !important; }

/* Global Text Colors */
p, span, label, div, [data-testid="stMarkdownContainer"] p { color: #111111; }
h1, h2, h3, h4 { font-family: 'Inter', sans-serif !important; font-weight: 700 !important; letter-spacing: -0.02em !important; color: #111111 !important; }
.emph { font-family: 'Instrument Serif', Georgia, serif !important; font-style: italic !important; font-weight: 400 !important; color: #D9541E !important; }

/* Clean Cards */
.card { background: #FAF7F2; border: 1px solid #DFD7CA; border-radius: 12px; padding: 1.1rem 1.3rem; margin-bottom: 1rem; }
.card-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #555555 !important; }
.card-value { font-size: 2rem; font-weight: 800; color: #111111 !important; line-height: 1.15; letter-spacing: -0.03em; }
.card-value.orange { color: #D9541E !important; }
.card-value small { font-size: 1rem; font-weight: 500; color: #555555 !important; }
.card-sub { font-size: 0.8rem; color: #333333 !important; margin-top: 0.3rem; }

/* Callout Box */
.sowhat { background: #FAF7F2; border-left: 3px solid #D9541E; padding: 0.65rem 0.9rem; border-radius: 0 8px 8px 0; font-size: 0.85rem; margin: 0.4rem 0 1.1rem 0; color: #111111 !important; }
.sowhat b { color: #D9541E !important; }
.note { font-size: 0.85rem; color: #555555 !important; margin-top: 0.35rem; }

/* Tab Bar Styling (Crisp, High Contrast, No Glitches) */
div[data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 2px solid #DFD7CA !important;
    gap: 1.5rem !important;
    padding-bottom: 0px !important;
    margin-bottom: 1.5rem !important;
}

button[data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    padding: 0.6rem 0.2rem !important;
    height: auto !important;
}

button[data-baseweb="tab"] p, button[data-baseweb="tab"] div, button[data-baseweb="tab"] span {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    color: #111111 !important;
    opacity: 0.8 !important;
}

button[data-baseweb="tab"]:hover p {
    color: #D9541E !important;
    opacity: 1 !important;
}

button[data-baseweb="tab"][aria-selected="true"] p {
    color: #D9541E !important;
    font-weight: 800 !important;
    opacity: 1 !important;
}

div[data-baseweb="tab-highlight"] {
    background-color: #D9541E !important;
    height: 3px !important;
    border-radius: 3px 3px 0 0 !important;
}

div[data-baseweb="tab-border"] {
    display: none !important;
}

/* Button & Form Elements */
.stDownloadButton button { background: #111111 !important; color: #F3EEE3 !important; border: 1px solid #111111 !important; border-radius: 8px !important; }
.stDownloadButton button p { color: #F3EEE3 !important; font-weight: 600 !important; }
.stDownloadButton button:hover { background: #D9541E !important; border-color: #D9541E !important; }

/* Table styling */
[data-testid="stDataFrame"] { background-color: #FAF7F2 !important; border: 1px solid #DFD7CA !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data
# -----------------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "rideops_support_tickets.csv")
NOW = pd.Timestamp("2026-09-30 23:59:59")   # data pull date = "today" for all ages
RETURNED = ["Insufficient info - returned to L1", "Config issue - returned to L1"]
NO_INV = ["Duplicate of known issue", "Not a bug - how-to", "Not reproducible"]
MONTHS = {7: "Jul", 8: "Aug", 9: "Sep"}


@st.cache_data
def load_data():
    d = pd.read_csv(DATA_PATH)
    for c in ["created_at", "first_response_at", "first_closed_at", "final_closed_at"]:
        d[c] = pd.to_datetime(d[c], errors="coerce")
    d["hours"] = (d["final_closed_at"] - d["created_at"]).dt.total_seconds() / 3600.0
    d["first_resp_h"] = (d["first_response_at"] - d["created_at"]).dt.total_seconds() / 3600.0
    d["is_esc"] = d["escalated_to_eng"].eq("Yes")
    d["is_closed"] = d["status"].eq("Closed")
    d["returned"] = d["eng_outcome"].isin(RETURNED)
    d["no_inv"] = d["eng_outcome"].isin(NO_INV)
    d["reopened"] = d["reopen_count"] > 0
    d["month"] = d["created_at"].dt.month
    d["week_start"] = d["created_at"].dt.to_period("W-SUN").dt.start_time
    return d


df = load_data()


def open_series(frame):
    """Open tickets at the end of each day (reopen-aware: open until final_closed_at)."""
    days = pd.date_range("2026-07-02", "2026-09-30")
    out = []
    for day in days:
        t = day + pd.Timedelta(hours=23, minutes=59, seconds=59)
        out.append(int(((frame["created_at"] <= t) & (frame["final_closed_at"].isna() | (frame["final_closed_at"] > t))).sum()))
    return pd.Series(out, index=days)


def card(label, value, sub="", orange=False):
    cls = "card-value orange" if orange else "card-value"
    return f'<div class="card"><div class="card-label">{label}</div><div class="{cls}">{value}</div><div class="card-sub">{sub}</div></div>'


def sowhat(text):
    st.markdown(f'<div class="sowhat"><b>So what:</b> {text}</div>', unsafe_allow_html=True)


def style(fig, height=340):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=height,
        margin=dict(l=10, r=10, t=30, b=10), font=dict(family="Inter", color=INK),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=INK)
    fig.update_yaxes(gridcolor=GRID, linecolor=INK)
    return fig


# -----------------------------------------------------------------------------
# Numbers used across tabs (all computed from the CSV)
# -----------------------------------------------------------------------------
total = len(df)
esc_df = df[df["is_esc"]]
esc_n = len(esc_df)
open_df = df[~df["is_closed"]].copy()
open_n = len(open_df)
open_l1 = int((open_df["status"] == "Open - with L1").sum())
open_eng = int((open_df["status"] == "Open - with Engineering").sum())
ret_n, noinv_n = int(df["returned"].sum()), int(df["no_inv"].sum())
fixed_n = int((df["eng_outcome"] == "Fixed").sum())
closed = df[df["is_closed"]]
med_l1 = closed.loc[~closed["is_esc"], "hours"].median()
med_esc = closed.loc[closed["is_esc"], "hours"].median()
csat_rated = int(df["csat_score"].notna().sum())
csat_resp = csat_rated / total * 100

daily_open = open_series(df)
avg_open = daily_open.groupby(daily_open.index.month).mean()
inflow_m = df.groupby("month").size()
esc_rate_m = df.groupby("month")["is_esc"].mean() * 100
open_jul31, open_sep30 = int(daily_open[pd.Timestamp("2026-07-31")]), int(daily_open[pd.Timestamp("2026-09-30")])
infl_growth = (inflow_m[9] / inflow_m[7] - 1) * 100
open_growth_avg = (avg_open[9] / avg_open[7] - 1) * 100
open_growth_pt = (open_sep30 / open_jul31 - 1) * 100

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown(f"""
<div style="margin-bottom: 1.25rem;">
    <h1 style="font-size: 2.2rem; font-weight: 800; margin: 0; line-height: 1.15; letter-spacing: -0.03em;">
        RideOps <span class="emph">Support</span> Triage Console
    </h1>
    <div style="font-size: 0.85rem; color: #555555; margin-top: 0.35rem;">
        Role: <strong>Meera (Support Lead)</strong> · Dataset: {total:,} tickets (2 Jul – 30 Sep 2026) · Time Anchor: 30 Sep 2026 23:59
    </div>
</div>
""", unsafe_allow_html=True)

tab_health, tab_act, tab_quality, tab_agents, tab_sim = st.tabs(
    ["Overview", f"Act now ({open_n} open)", "Escalation quality", "Agents", "What-if"])

# -----------------------------------------------------------------------------
# TAB 1: OVERVIEW
# -----------------------------------------------------------------------------
with tab_health:
    st.markdown("### Where the backlog <span class='emph'>comes</span> from", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(card("Open tickets at 30 Sep", open_n, f"{open_l1} with L1 / {open_eng} with Engineering", True), unsafe_allow_html=True)
    k2.markdown(card("Bounced back to L1", ret_n, f"{ret_n / esc_n * 100:.1f}% of {esc_n} escalations (info missing or config)"), unsafe_allow_html=True)
    k3.markdown(card("Did not need new investigation", noinv_n, f"{noinv_n / esc_n * 100:.1f}% of escalations (duplicate, how-to, not reproducible)"), unsafe_allow_html=True)
    k4.markdown(card("Median time to close", f"{med_l1:.1f}h <small>vs {med_esc:.1f}h</small>", "L1 only vs escalated (closed tickets only)"), unsafe_allow_html=True)

    # Weekly flow
    created_w = df.groupby("week_start").size()
    closed_w = df.dropna(subset=["final_closed_at"]).assign(w=lambda d: d["final_closed_at"].dt.to_period("W-SUN").dt.start_time).groupby("w").size()
    flow = pd.DataFrame({"created": created_w, "closed": closed_w}).fillna(0).astype(int).sort_index()
    labels = [d.strftime("%d %b") for d in flow.index]
    labels[0] += "*"
    labels[-1] += "*"

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Tickets created vs closed, per week")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=labels, y=flow["created"], name="Created", marker_color=INK))
        fig.add_trace(go.Bar(x=labels, y=flow["closed"], name="Closed", marker_color=ORANGE))
        fig.update_layout(barmode="group")
        st.plotly_chart(style(fig))
        peak = flow["created"].idxmax()
        sowhat(f"Intake peaked in the week of {peak.strftime('%d %b')}: {flow.loc[peak, 'created']} created vs {flow.loc[peak, 'closed']} closed. "
               f"In surge weeks closures lag intake, and the gap shows up as backlog. (* = partial week at the start or end of the data.)")
    with c2:
        st.markdown("#### Open tickets at the end of each day")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_open.index, y=daily_open.values, mode="lines", name="Open tickets", line=dict(color=ORANGE, width=3)))
        st.plotly_chart(style(fig))
        sowhat(f"Average open tickets per day went from {avg_open[7]:.0f} (Jul) to {avg_open[9]:.0f} (Sep), up {open_growth_avg:.0f}%, "
               f"while monthly intake grew {infl_growth:.0f}%. The backlog grew about {open_growth_avg / infl_growth:.1f}x faster than intake, so closing capacity did not keep up. "
               f"The brief's 'about 60%' matches 31 Jul ({open_jul31}) vs 30 Sep ({open_sep30}) = +{open_growth_pt:.0f}%.")

    st.markdown("#### Month by month")
    mt = pd.DataFrame({
        "Month": [MONTHS[m] for m in (7, 8, 9)],
        "Tickets created": [int(inflow_m[m]) for m in (7, 8, 9)],
        "Average open per day": [round(avg_open[m], 1) for m in (7, 8, 9)],
        "Escalated to engineering %": [round(esc_rate_m[m], 1) for m in (7, 8, 9)],
    })
    st.dataframe(mt, hide_index=True)

    st.markdown("#### By priority (the data has no SLA targets, so these are our own yardsticks)")
    pr = df.groupby("priority").agg(Tickets=("ticket_id", "count"), first=("first_resp_h", "median"), close=("hours", "median"),
                                    Open=("is_closed", lambda s: int((~s).sum()))).reset_index()
    pr = pr.rename(columns={"priority": "Priority", "first": "Median first response (h)", "close": "Median time to close (h)", "Open": "Still open"})
    pr[["Median first response (h)", "Median time to close (h)"]] = pr[["Median first response (h)", "Median time to close (h)"]].round(1)
    st.dataframe(pr, hide_index=True)
    st.markdown("#### Which categories grew, and which ones escalate")
    cat = df.pivot_table(index="category", columns="month", values="ticket_id", aggfunc="count", fill_value=0).rename(columns=MONTHS)
    cat["Added (Jul to Sep)"] = cat["Sep"] - cat["Jul"]
    cat["Growth %"] = ((cat["Sep"] / cat["Jul"] - 1) * 100).round(0)
    cat["Total"] = df.groupby("category").size()
    cat["Escalated"] = esc_df.groupby("category").size().reindex(cat.index).fillna(0).astype(int)
    cat["Escalation rate %"] = (cat["Escalated"] / cat["Total"] * 100).round(1)
    cat.columns.name = None
    cat = cat.sort_values("Added (Jul to Sep)", ascending=False).reset_index().rename(columns={"category": "Category"})
    st.dataframe(cat[["Category", "Jul", "Aug", "Sep", "Added (Jul to Sep)", "Growth %", "Total", "Escalated", "Escalation rate %"]], hide_index=True)
    top_add = cat.head(3)
    top_esc_cat = cat.sort_values("Escalation rate %", ascending=False).head(2)
    sowhat("Volume growth and escalations are different problems. The biggest additions were "
           + ", ".join(f"{r['Category']} (+{r['Added (Jul to Sep)']})" for r in top_add.to_dict("records"))
           + ". The categories that escalate most are "
           + " and ".join(f"{r['Category']} ({r['Escalation rate %']:.0f}%)" for r in top_esc_cat.to_dict("records")) + ".")

# -----------------------------------------------------------------------------
# TAB 2: ACT NOW
# -----------------------------------------------------------------------------
with tab_act:
    st.markdown("### Open tickets, <span class='emph'>ranked</span> for today", unsafe_allow_html=True)
    weights = {"P1": 4.0, "P2": 3.0, "P3": 2.0, "P4": 1.0}
    open_df["age_days"] = ((NOW - open_df["created_at"]).dt.total_seconds() / 86400).round(2)
    open_df["score"] = (open_df["priority"].map(weights) * open_df["age_days"]
                        * np.where(open_df["status"].eq("Open - with Engineering"), 1.5, 1.0)
                        * np.where(open_df["reopened"], 1.5, 1.0)).round(2)
    st.caption("Score = priority weight (P1=4, P2=3, P3=2, P4=1) x age in days x 1.5 if waiting on Engineering x 1.5 if the client reopened it. "
               "Higher means act sooner. Age is counted from the 30 Sep data pull.")

    f1, f2, f3, f4, f5 = st.columns(5)
    sel = {
        "assigned_agent": f1.selectbox("Agent", ["All"] + sorted(open_df["assigned_agent"].unique())),
        "client_name": f2.selectbox("Client", ["All"] + sorted(open_df["client_name"].unique())),
        "category": f3.selectbox("Category", ["All"] + sorted(open_df["category"].unique())),
        "priority": f4.selectbox("Priority", ["All"] + sorted(open_df["priority"].unique())),
        "status": f5.selectbox("Status", ["All"] + sorted(open_df["status"].unique())),
    }
    view = open_df.copy()
    for col, val in sel.items():
        if val != "All":
            view = view[view[col] == val]
    view = view.sort_values("score", ascending=False)
    cols = ["ticket_id", "priority", "status", "category", "client_name", "assigned_agent", "age_days", "reopen_count", "score", "description"]
    st.caption(f"Showing {len(view)} of {open_n} open tickets.")
    st.dataframe(view[cols], hide_index=True)
    st.download_button("Download this list (CSV)", view[cols].to_csv(index=False).encode("utf-8"), "rideops_open_tickets_ranked.csv", "text/csv")

    st.markdown("---")
    st.markdown("#### Escalation packet")
    insuff_n = int((df["eng_outcome"] == "Insufficient info - returned to L1").sum())
    st.markdown(
        f'<div class="note">Why this exists: {insuff_n} of {esc_n} escalations ({insuff_n / esc_n * 100:.1f}%) came back from engineering as '
        f'"insufficient info". Pick a ticket, tick what has been collected, and copy the packet into the message to engineering. '
        f'The checklist is a proposal to validate with the engineering manager. It is not an existing RideOps rule.</div>', unsafe_allow_html=True)

    if len(view) == 0:
        st.info("No tickets match the filters above.")
    else:
        tid = st.selectbox("Ticket", view["ticket_id"].tolist())
        t = view[view["ticket_id"] == tid].iloc[0]
        items = [("client", "Client name and ID recorded"), ("ids", "Trip / roster / booking ID attached"),
                 ("time", "Exact time of the issue recorded"), ("proof", "Screenshot or exact error message captured"),
                 ("repro", "Agent tried to reproduce the issue"), ("dup", "Checked for a recent duplicate report")]
        left, right = st.columns([1, 2])
        with left:
            ticked = {k: st.checkbox(label, key=f"chk_{tid}_{k}") for k, label in items}
        missing = [label for k, label in items if not ticked[k]]
        title = "FOLLOW-UP PACKET (chase engineering)" if t["status"] == "Open - with Engineering" else "ESCALATION PACKET"
        lines = [title,
                 f"Ticket: {t['ticket_id']}  |  Priority: {t['priority']}  |  Status: {t['status']}",
                 f"Client: {t['client_name']} ({t['client_tier']})  |  Channel: {t['channel']}",
                 f"Category: {t['category']}",
                 f"Raised: {t['created_at']:%d %b %Y %H:%M}  |  Age: {t['age_days']} days (as of 30 Sep 2026)",
                 f"Agent: {t['assigned_agent']}  |  Engineering handoffs so far: {t['eng_handoffs']}  |  Reopens: {t['reopen_count']}",
                 f"Issue: {t['description']}", "", "Checklist:"]
        lines += [f"  [{'x' if ticked[k] else ' '}] {label}" for k, label in items]
        lines.append("")
        lines.append("Ready to send: YES" if not missing else f"Ready to send: NO. Still missing: {len(missing)} item(s)")
        with right:
            st.code("\n".join(lines), language="text")

# -----------------------------------------------------------------------------
# TAB 3: ESCALATION QUALITY
# -----------------------------------------------------------------------------
with tab_quality:
    st.markdown("### What engineering <span class='emph'>says</span> about our escalations", unsafe_allow_html=True)
    q1, q2 = st.columns(2)
    with q1:
        st.markdown(f"#### Engineering's verdict on {esc_n} escalated tickets")
        g = esc_df.assign(Group=np.where(esc_df["returned"], "Returned to L1", np.where(esc_df["no_inv"], "Did not need new investigation", "Real fix")))
        ov = g.groupby(["eng_outcome", "Group"]).agg(Tickets=("ticket_id", "count"), med=("hours", "median")).reset_index()
        ov["Share of escalations %"] = (ov["Tickets"] / esc_n * 100).round(1)
        ov["Median hours to close"] = ov["med"].round(1)
        ov = ov.sort_values("Tickets", ascending=False).rename(columns={"eng_outcome": "Outcome"})
        st.dataframe(ov[["Outcome", "Group", "Tickets", "Share of escalations %", "Median hours to close"]], hide_index=True)
        sowhat(f"{ret_n} tickets ({ret_n / esc_n * 100:.1f}%) bounced back to L1, which a pre-escalation check can fix. "
               f"Another {noinv_n} ({noinv_n / esc_n * 100:.1f}%) did not need new investigation and need a known-issues list instead. "
               f"Only {fixed_n} ({fixed_n / esc_n * 100:.1f}%) were real fixes, and even those took {closed.loc[closed['eng_outcome'] == 'Fixed', 'hours'].median():.0f}h (median).")
    with q2:
        st.markdown("#### More handoffs to engineering, slower and unhappier")
        h = df.groupby("eng_handoffs").agg(Tickets=("ticket_id", "count"), med=("hours", "median"), csat=("csat_score", "mean"), n=("csat_score", "count")).reset_index()
        hs = pd.DataFrame({"Handoffs": h["eng_handoffs"], "Tickets": h["Tickets"], "Median hours to close": h["med"].round(1),
                           "Average CSAT": h["csat"].round(2), "Tickets with CSAT": h["n"]})
        st.dataframe(hs, hide_index=True)
        sowhat("Median closing time goes " + " > ".join(f"{v:.0f}h" for v in h["med"]) + " and CSAT goes "
               + " > ".join(f"{v:.2f}" for v in h["csat"]) + f" as handoffs go from {int(h['eng_handoffs'].min())} to {int(h['eng_handoffs'].max())}. "
               f"CSAT exists for only {csat_resp:.0f}% of tickets, so treat it as a signal, not a measurement.")

    st.markdown("---")
    st.markdown("#### Look inside a category")
    top_cats = esc_df["category"].value_counts().head(3).index.tolist()
    pick = st.radio("Category", top_cats, horizontal=True)
    sub = df[df["category"] == pick].copy()
    s_esc = int(sub["is_esc"].sum())
    s_ret, s_noinv = int(sub["returned"].sum()), int(sub["no_inv"].sum())
    m1, m2, m3 = st.columns(3)
    m1.markdown(card("Tickets in category", len(sub), f"{s_esc} escalated ({s_esc / len(sub) * 100:.1f}%)"), unsafe_allow_html=True)
    m2.markdown(card("Bounced back to L1", s_ret, f"{s_ret / s_esc * 100:.1f}% of its escalations"), unsafe_allow_html=True)
    m3.markdown(card("Did not need investigation", s_noinv, f"{s_noinv / s_esc * 100:.1f}% of its escalations"), unsafe_allow_html=True)

    sub["Issue pattern"] = sub["description"].str.replace(r"\d+", "N", regex=True)
    pat = sub.groupby("Issue pattern").agg(Tickets=("ticket_id", "count"), Escalated=("is_esc", "sum"),
                                           Bounced=("returned", "sum"), NoInv=("no_inv", "sum")).reset_index()
    pat["Escalations that were avoidable %"] = (((pat["Bounced"] + pat["NoInv"]) / pat["Escalated"].replace(0, np.nan)) * 100).round(1)
    pat = pat.sort_values("Tickets", ascending=False).head(6).rename(columns={"Bounced": "Bounced to L1", "NoInv": "No investigation needed"})
    st.dataframe(pat, hide_index=True)
    sowhat("Numbers in descriptions are grouped as N so similar tickets count together. Small groups mean small samples, "
           "so use this to pick where to write a known-issue note first, not as proof.")

# -----------------------------------------------------------------------------
# TAB 4: AGENTS
# -----------------------------------------------------------------------------
with tab_agents:
    st.markdown("### Speed and quality, <span class='emph'>side</span> by side", unsafe_allow_html=True)
    st.caption("For coaching conversations, not blame. Speed and reopen rate are measured on tickets the agent closed without engineering, so agents are compared like for like.")
    rows = []
    for ag, grp in df.groupby("assigned_agent"):
        ne = grp[(~grp["is_esc"]) & grp["is_closed"]]
        e = grp[grp["is_esc"]]
        rated = grp["csat_score"].dropna()
        rows.append({
            "Agent": ag, "Tickets": len(grp), "Escalation rate %": round(len(e) / len(grp) * 100, 1),
            "Bounced to L1 % of escalations": round(e["returned"].sum() / len(e) * 100, 1) if len(e) else 0.0,
            "Median close, no escalation (h)": round(ne["hours"].median(), 1),
            "Reopened % (no escalation)": round(ne["reopened"].mean() * 100, 1),
            "Reopen events": int(grp["reopen_count"].sum()),
            "Average CSAT": round(rated.mean(), 2), "CSAT response %": round(len(rated) / len(grp) * 100, 1),
            "CSAT (no escalation)": round(ne["csat_score"].mean(), 2),
            "_esc_n": len(e), "_ret_n": int(e["returned"].sum()), "_noinv_n": int(e["no_inv"].sum()),
        })
    ag = pd.DataFrame(rows)
    fast = ag.loc[ag["Median close, no escalation (h)"].idxmin()]
    topesc = ag.loc[ag["Escalation rate %"].idxmax()]
    ag["Group"] = np.where(ag["Agent"] == fast["Agent"], "Fastest closer", np.where(ag["Agent"] == topesc["Agent"], "Highest escalation rate", "Other agents"))
    fig = px.scatter(ag, x="Median close, no escalation (h)", y="Reopened % (no escalation)", size="Tickets", text="Agent", color="Group",
                     color_discrete_map={"Fastest closer": ORANGE, "Highest escalation rate": INK, "Other agents": GREY})
    fig.update_traces(textposition="top center")
    fig.update_xaxes(title="Median hours to close (no escalation)")
    fig.update_yaxes(title="Tickets reopened by the client (%)")
    st.plotly_chart(style(fig, 380))

    others = ag[ag["Agent"] != fast["Agent"]]
    others2 = ag[ag["Agent"] != topesc["Agent"]]
    sowhat(f"{fast['Agent']} is the fastest closer ({fast['Median close, no escalation (h)']}h median) but {fast['Reopened % (no escalation)']}% of those tickets are reopened, "
           f"against {others['Reopened % (no escalation)'].min()}% to {others['Reopened % (no escalation)'].max()}% for the others, and their CSAT is {fast['CSAT (no escalation)']} "
           f"against {others['CSAT (no escalation)'].min()} to {others['CSAT (no escalation)'].max()}. Fast closing is not the same as solving. "
           f"{topesc['Agent']} escalates {topesc['Escalation rate %']}% of tickets against {others2['Escalation rate %'].min()}% to {others2['Escalation rate %'].max()}% for the others.")
    show_cols = [c for c in ag.columns if not c.startswith("_") and c != "Group"]
    st.dataframe(ag[show_cols], hide_index=True)

    st.markdown("#### Coaching focus")
    cc1, cc2 = st.columns(2)
    cc1.markdown(
        f'<div class="card"><div class="card-label">{fast["Agent"]}: quick to close, often reopened</div>'
        f'<div class="card-sub"><b>What the data shows:</b> {fast["Median close, no escalation (h)"]}h median close, {fast["Reopened % (no escalation)"]}% reopened, '
        f'{int(fast["Reopen events"])} of {int(df["reopen_count"].sum())} reopen events in the whole team ({fast["Reopen events"] / df["reopen_count"].sum() * 100:.0f}%).<br>'
        f'<b>Suggested focus:</b> confirm the fix with the client before marking a ticket closed.</div></div>', unsafe_allow_html=True)
    cc2.markdown(
        f'<div class="card"><div class="card-label">{topesc["Agent"]}: high escalation, many bounces</div>'
        f'<div class="card-sub"><b>What the data shows:</b> {int(topesc["_esc_n"])} of {int(topesc["Tickets"])} tickets escalated ({topesc["Escalation rate %"]}%); '
        f'{int(topesc["_ret_n"])} came back to L1 and {int(topesc["_noinv_n"])} did not need investigation.<br>'
        f'<b>Suggested focus:</b> run the pre-escalation checklist (Act now tab) before sending to engineering.</div></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 5: WHAT-IF
# -----------------------------------------------------------------------------
with tab_sim:
    st.markdown("### What if bounced tickets were <span class='emph'>solved</span> at L1?", unsafe_allow_html=True)
    st.caption(f"Takes the {ret_n} tickets that engineering returned to L1 and asks: if a share of them had been solved by L1 at the usual L1 speed, how many hours and open tickets would that save? A scenario, not a forecast.")
    pct = st.slider("Share of bounced tickets solved at L1 instead", 0, 100, 50, 5, format="%d%%")

    idx = df.index[df["returned"]].to_numpy()
    k = int(round(len(idx) * pct / 100))
    chosen = np.random.RandomState(42).choice(idx, size=k, replace=False) if k else np.array([], dtype=int)

    sim = df[["created_at", "final_closed_at"]].copy()
    actual_h = ((sim["final_closed_at"].fillna(NOW) - sim["created_at"]).dt.total_seconds() / 3600.0)
    new_close = sim["created_at"] + pd.to_timedelta(int(round(med_l1 * 3600)), unit="s")
    keep_orig = sim["final_closed_at"].notna() & (sim["final_closed_at"] < new_close)
    new_close = new_close.where(~keep_orig, sim["final_closed_at"])
    sim["final_closed_at"] = sim["final_closed_at"].where(~sim.index.isin(chosen), new_close)
    hours_saved = float((actual_h.loc[chosen] - med_l1).clip(lower=0).sum())
    sim_daily = open_series(sim)
    sim_sep30 = int(sim_daily.iloc[-1])

    s1, s2, s3 = st.columns(3)
    s1.markdown(card("Tickets solved at L1", k, f"of {len(idx)} bounced tickets"), unsafe_allow_html=True)
    s2.markdown(card("Customer wait time saved", f"{hours_saved:,.0f}h", f"actual hours minus the {med_l1:.1f}h L1 median", True), unsafe_allow_html=True)
    s3.markdown(card("Open tickets at 30 Sep", f"{sim_sep30} <small>(was {open_sep30})</small>", f"{open_sep30 - sim_sep30} fewer open"), unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_open.index, y=daily_open.values, name="Actual", line=dict(color=INK, width=3)))
    fig.add_trace(go.Scatter(x=sim_daily.index, y=sim_daily.values, name="With the scenario", line=dict(color=ORANGE, width=3, dash="dot")))
    st.plotly_chart(style(fig))
    sowhat(f"Solving {pct}% of bounced tickets at L1 would save about {hours_saved:,.0f} hours of customer waiting and cut the open count at 30 Sep from {open_sep30} to {sim_sep30}. "
           f"Average open per day in September would go from {daily_open[daily_open.index.month == 9].mean():.1f} to {sim_daily[sim_daily.index.month == 9].mean():.1f}.")
    with st.expander("How this is calculated"):
        st.markdown(
            f"1. Take the {len(idx)} tickets whose engineering outcome was 'Insufficient info' or 'Config issue' (returned to L1).\n"
            f"2. Pick {pct}% of them at random with a fixed seed (42), so the same slider value always gives the same result.\n"
            f"3. Give each a close time of created time + {med_l1:.1f}h (the median for closed L1-only tickets). Tickets already faster than that keep their real time.\n"
            f"4. Hours saved = sum of (actual hours, or hours open so far if still open, minus {med_l1:.1f}h).\n"
            f"5. Recount open tickets for every day and compare.")