"""CareerPulse - Career Progression & Promotion Gap Intelligence (Streamlit)."""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(str(Path(__file__).parent / "src"))
from pipeline import build  # noqa: E402

st.set_page_config(page_title="CareerPulse · Palo Alto Networks", page_icon="🚀",
                   layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------ design tokens
ACCENT = "#FA582D"
CLUSTERS = {
    "Early-Career Explorers": ("#38BDF8", "🧭", "New joiners still finding their footing"),
    "Fast-Track Performers": ("#34D399", "🚀", "Recently promoted and moving fast"),
    "Stable Long-Term Contributors": ("#A78BFA", "🏛️", "Loyal, but long in one role"),
    "Promotion-Stalled": ("#FBBF24", "⏸️", "Mid-tenure, waiting for the next step"),
    "High-Risk Stagnation": ("#FB4F6F", "🔥", "Senior and long overdue for growth"),
}
ORDER = list(CLUSTERS)
COLORS = {k: v[0] for k, v in CLUSTERS.items()}
BAND_COLORS = {"Low": "#34D399", "Medium": "#FBBF24", "High": "#FB4F6F"}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, .stText {font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;}
.stApp {background: radial-gradient(circle at 10% 0%, #1a1f4d 0%, transparent 40%),
                    radial-gradient(circle at 90% 10%, #3b1230 0%, transparent 35%), #070B1A;}
.block-container {padding-top: 3.2rem; max-width: 1400px;}
h1, h2, h3 {font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif, sans-serif !important; letter-spacing: -0.02em;}

/* hero */
.hero {position: relative; padding: 34px 38px; border-radius: 24px; overflow: hidden;
       background: linear-gradient(120deg, rgba(250,88,45,.22), rgba(167,139,250,.18), rgba(56,189,248,.18));
       border: 1px solid rgba(255,255,255,.08); margin-bottom: 22px;}
.hero:before {content: ""; position: absolute; inset: -60%; z-index: 0;
       background: conic-gradient(from 0deg, transparent, rgba(250,88,45,.35), transparent 30%);
       animation: spin 9s linear infinite;}
.hero > * {position: relative; z-index: 1;}
.hero-inner {position: absolute; inset: 2px; border-radius: 22px; background: rgba(9,13,32,.86); z-index: 0;}
@keyframes spin {to {transform: rotate(360deg);}}
.hero .eyebrow {color: #FDBA74; font-weight: 600; letter-spacing: .18em; font-size: .75rem; text-transform: uppercase;}
.hero h1 {font-size: 2.6rem; margin: 6px 0 4px; padding: 0 !important; line-height: 1.1;
          background: linear-gradient(90deg, #fff 0%, #FDBA74 45%, #F472B6 75%, #A78BFA 100%);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.hero p {color: #B8C0DD; font-size: 1.02rem; margin: 0 0 14px; max-width: 760px;}
.chip {display: inline-block; padding: 5px 12px; margin: 0 6px 6px 0; border-radius: 999px; font-size: .78rem;
       background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.12); color: #E6EAF7;}

/* KPI cards */
.kpi {padding: 18px 20px; border-radius: 18px; background: rgba(17,24,51,.75);
      border: 1px solid rgba(255,255,255,.07); backdrop-filter: blur(10px);
      transition: transform .25s ease, box-shadow .25s ease; animation: rise .6s ease both; height: 100%;}
.kpi:hover {transform: translateY(-4px); box-shadow: 0 14px 34px -12px var(--c);}
.kpi .top {display: flex; justify-content: space-between; align-items: center; color: #9AA3C7; font-size: .82rem;}
.kpi .icon {width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center;
            background: color-mix(in srgb, var(--c) 22%, transparent); font-size: 1.05rem;}
.kpi .val {font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; font-size: 2.1rem; font-weight: 700; color: #fff; margin-top: 6px;}
.kpi .sub {font-size: .78rem; color: var(--c);}
.kpi .bar {height: 4px; border-radius: 4px; margin-top: 10px; background: rgba(255,255,255,.07);}
.kpi .bar > div {height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--c), #fff0);}
@keyframes rise {from {opacity: 0; transform: translateY(14px);} to {opacity: 1; transform: none;}}

/* persona cards */
.persona {padding: 16px; border-radius: 16px; background: rgba(17,24,51,.7); height: 100%;
          border: 1px solid rgba(255,255,255,.06); border-top: 3px solid var(--c); animation: rise .7s ease both;}
.persona .n {font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; font-size: 1.7rem; font-weight: 700; color: var(--c);}
.persona .t {font-weight: 600; color: #fff; font-size: .92rem;}
.persona .d {color: #9AA3C7; font-size: .78rem; margin: 2px 0 8px;}
.persona .s {font-size: .78rem; color: #CBD2EE;}

/* section header & insight */
.sec {margin: 18px 0 6px;} .sec h3 {margin: 0; font-size: 1.25rem; color: #fff;}
.sec span {color: #8E97BC; font-size: .85rem;}
.insight {padding: 14px 18px; border-radius: 14px; margin: 8px 0 14px; color: #E6EAF7; font-size: .92rem;
          background: linear-gradient(90deg, rgba(250,88,45,.16), rgba(250,88,45,.02));
          border-left: 4px solid #FA582D;}

/* tabs as pills */
.stTabs [data-baseweb="tab-list"] {gap: 8px; background: rgba(17,24,51,.6); padding: 6px;
       border-radius: 16px; border: 1px solid rgba(255,255,255,.06);}
.stTabs [data-baseweb="tab"] {height: 44px; border-radius: 12px; padding: 0 18px; color: #AAB2D5; font-weight: 600;}
.stTabs [aria-selected="true"] {background: linear-gradient(120deg, #FA582D, #E0457B) !important; color: #fff !important;
       box-shadow: 0 8px 22px -8px #FA582D;}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {display: none;}

/* sidebar, charts, tables */
section[data-testid="stSidebar"] {background: linear-gradient(180deg, #0E1430 0%, #0A0F24 100%);
       border-right: 1px solid rgba(255,255,255,.06);}
.brand {font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; font-size: 1.45rem; font-weight: 700; color: #fff;}
.brand b {color: #FA582D;}
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {background: rgba(17,24,51,.55); border-radius: 18px;
       border: 1px solid rgba(255,255,255,.06); padding: 6px;}
.profile {padding: 22px; border-radius: 20px; background: linear-gradient(140deg, rgba(17,24,51,.95), rgba(40,20,60,.85));
          border: 1px solid rgba(255,255,255,.08);}
.profile h2 {margin: 0; color: #fff;} .profile .role {color: #9AA3C7; margin-bottom: 12px;}
.tag {display: inline-block; padding: 4px 11px; margin: 4px 6px 0 0; border-radius: 999px; font-size: .78rem;
      font-weight: 600; background: color-mix(in srgb, var(--c) 20%, transparent); color: var(--c);
      border: 1px solid color-mix(in srgb, var(--c) 45%, transparent);}
#MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ helpers
def style(fig, height=380, legend=True):
    fig.update_layout(template="plotly_dark", height=height, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#CBD2EE", size=12),
                      title_font=dict(family="Space Grotesk, Inter, sans-serif", size=16, color="#fff"),
                      margin=dict(l=10, r=10, t=50, b=10), showlegend=legend,
                      legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.15),
                      hoverlabel=dict(bgcolor="#111833", font_family="Inter"))
    fig.update_xaxes(gridcolor="rgba(255,255,255,.06)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.06)", zeroline=False)
    return fig


def kpi(col, icon, label, value, sub, color, pct):
    col.markdown(f"""<div class="kpi" style="--c:{color}"><div class="top"><span>{label}</span>
        <span class="icon">{icon}</span></div><div class="val">{value}</div><div class="sub">{sub}</div>
        <div class="bar"><div style="width:{min(pct, 100):.0f}%"></div></div></div>""", unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f'<div class="sec"><h3>{title}</h3><span>{sub}</span></div>', unsafe_allow_html=True)


def insight(text):
    st.markdown(f'<div class="insight">💡 {text}</div>', unsafe_allow_html=True)


@st.cache_data
def get_data():
    return build()


df, metrics = get_data()

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown('<div class="brand">Career<b>Pulse</b></div>', unsafe_allow_html=True)
    st.caption("Career trajectory intelligence · Palo Alto Networks")
    st.markdown("---")
    dept = st.multiselect("🏢 Department", sorted(df["Department"].unique()))
    pool = df[df["Department"].isin(dept)] if dept else df
    roles = st.multiselect("💼 Job role", sorted(pool["JobRole"].unique()))
    stages = st.multiselect("🎓 Career stage", list(df["CareerStage"].cat.categories))
    gap_threshold = st.slider("⏳ Promotion gap threshold (years)", 0, 15, 4)
    include_left = st.toggle("Include employees who left", value=True)
    st.markdown("---")
    st.caption(f"🧠 K-Means k=5 · silhouette {metrics['silhouette_kmeans']:.2f}  \n"
               f"🔗 Hierarchical agreement (ARI) {metrics['adjusted_rand_index']:.2f}  \n"
               f"🧹 {metrics['rows_raw'] - metrics['rows_clean']} late-career outliers removed")

f = df.copy()
if dept:
    f = f[f["Department"].isin(dept)]
if roles:
    f = f[f["JobRole"].isin(roles)]
if stages:
    f = f[f["CareerStage"].isin(stages)]
if not include_left:
    f = f[f["Attrition"] == 0]
if f.empty:
    st.warning("No employees match these filters — try widening them.")
    st.stop()

# ------------------------------------------------------------------ hero + KPIs
st.markdown(f"""<div class="hero"><div class="hero-inner"></div>
  <div class="eyebrow">Palo Alto Networks · People Analytics</div>
  <h1>Career Progression &amp; Promotion Gap Intelligence</h1>
  <p>Don't just predict who leaves — see <b>why</b> careers stall, and act while employees are still engaged.</p>
  <span class="chip">👥 {len(f):,} employees in view</span><span class="chip">🧩 5 career clusters</span>
  <span class="chip">🎯 K-Means + Ward validation</span><span class="chip">⚡ Live filters</span></div>""",
            unsafe_allow_html=True)

n = len(f)
high = (f["PromotionGapBand"] == "High").mean() * 100
opp = int(f["RetentionOpportunity"].sum())
train = (f["TrainingNeed"] == "Yes").mean() * 100
attr = f["Attrition"].mean() * 100
c = st.columns(5)
kpi(c[0], "👥", "Employees", f"{n:,}", f"{n / len(df):.0%} of workforce", "#38BDF8", n / len(df) * 100)
kpi(c[1], "⏳", "High promotion gap", f"{high:.0f}%", "stagnation risk", "#FB4F6F", high)
kpi(c[2], "🎯", "Retention opportunities", f"{opp:,}", "engaged · low risk · stalled", "#FA582D", opp / n * 100)
kpi(c[3], "📚", "Training need", f"{train:.0f}%", "≤1 training or low intensity", "#A78BFA", train)
kpi(c[4], "🚪", "Attrition rate", f"{attr:.1f}%", "already left", "#FBBF24", attr)
st.write("")

tabs = st.tabs(["🧭 Career Clusters", "⏳ Promotion Gap", "🎯 Retention Panel", "👥 Manager Insights",
                "🔍 Cluster Explorer", "🪪 Employee Spotlight"])

# ================================================================== 1. clusters
with tabs[0]:
    section("Five career trajectories", "Who is moving, who is waiting, who is stuck")
    cols = st.columns(5)
    for col, name in zip(cols, ORDER):
        sub = f[f["CareerCluster"] == name]
        color, icon, desc = CLUSTERS[name]
        yrs = sub["YearsSinceLastPromotion"].mean() if len(sub) else 0
        col.markdown(f"""<div class="persona" style="--c:{color}"><div class="n">{icon} {len(sub)}</div>
            <div class="t">{name}</div><div class="d">{desc}</div>
            <div class="s">⏳ {yrs:.1f} yrs since promotion<br>🚪 {sub['Attrition'].mean() if len(sub) else 0:.0%} attrition</div>
            </div>""", unsafe_allow_html=True)
    st.write("")

    a, b = st.columns([1, 1.4])
    counts = f["CareerCluster"].value_counts().reindex(ORDER).fillna(0)
    donut = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=.68, sort=False,
                             marker=dict(colors=[COLORS[k] for k in counts.index], line=dict(color="#070B1A", width=3))))
    donut.add_annotation(text=f"<b>{n:,}</b><br>employees", showarrow=False, font=dict(size=20, color="#fff"))
    a.plotly_chart(style(donut.update_layout(title="Cluster distribution"), 420), width="stretch")

    s3d = px.scatter_3d(f, x="YearsAtCompany", y="YearsSinceLastPromotion", z="YearsInCurrentRole",
                        color="CareerCluster", color_discrete_map=COLORS, category_orders={"CareerCluster": ORDER},
                        opacity=.75, hover_data=["EmployeeID", "JobRole"], title="Career space in 3D — drag to rotate")
    s3d.update_traces(marker=dict(size=3))
    s3d.update_layout(scene=dict(bgcolor="rgba(0,0,0,0)", xaxis_title="Tenure", yaxis_title="Yrs since promo",
                                 zaxis_title="Yrs in role"))
    b.plotly_chart(style(s3d, 420), width="stretch")

    feats = {"PromotionGapRatio": "Promotion gap", "RoleStagnationIndex": "Role stagnation",
             "ManagerStabilityIndicator": "Manager stability", "TrainingIntensityScore": "Training intensity",
             "YearsSinceLastPromotion": "Yrs since promo"}
    prof = f.groupby("CareerCluster")[list(feats)].mean().reindex(ORDER).dropna()
    norm = prof / prof.max()
    radar = go.Figure()
    for name, row in norm.iterrows():
        radar.add_trace(go.Scatterpolar(r=list(row) + [row.iloc[0]], theta=list(feats.values()) + [list(feats.values())[0]],
                                        name=name, fill="toself", opacity=.55, line=dict(color=COLORS[name], width=2)))
    radar.update_layout(title="Cluster DNA (scaled 0–1)", polar=dict(bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,.1)", showticklabels=False),
                        angularaxis=dict(gridcolor="rgba(255,255,255,.1)")))
    a, b = st.columns([1.1, 1])
    a.plotly_chart(style(radar, 440), width="stretch")
    with b:
        section("Career pattern summary")
        summary = (f.groupby("CareerCluster").agg(Employees=("EmployeeID", "count"),
                   Tenure=("YearsAtCompany", "mean"), YrsSincePromo=("YearsSinceLastPromotion", "mean"),
                   GapRatio=("PromotionGapRatio", "mean"), Attrition=("Attrition", "mean"))
                   .reindex([o for o in ORDER if o in f["CareerCluster"].unique()]))
        st.dataframe(summary, width="stretch", column_config={
            "Tenure": st.column_config.NumberColumn(format="%.1f yrs"),
            "YrsSincePromo": st.column_config.NumberColumn("Yrs since promo", format="%.1f"),
            "GapRatio": st.column_config.ProgressColumn("Gap ratio", min_value=0, max_value=1, format="%.2f"),
            "Attrition": st.column_config.ProgressColumn(min_value=0, max_value=.5, format="percent")})
        insight("<b>Promotion-Stalled</b> employees leave at ~3× the rate of Stable Long-Term Contributors "
                "despite similar engagement — the gap, not the job, is the push factor.")

# ================================================================== 2. promotion gap
with tabs[1]:
    high_gap = f[f["YearsSinceLastPromotion"] >= gap_threshold]
    share = len(high_gap) / n * 100
    a, b = st.columns([1, 1.6])
    gauge = go.Figure(go.Indicator(mode="gauge+number", value=share, number=dict(suffix="%", font=dict(size=46)),
                      title=dict(text=f"Waiting {gap_threshold}+ yrs for promotion"),
                      gauge=dict(axis=dict(range=[0, 100], tickcolor="#555"), bar=dict(color=ACCENT, thickness=.3),
                                 bgcolor="rgba(255,255,255,.04)", borderwidth=0,
                                 steps=[dict(range=[0, 15], color="rgba(52,211,153,.18)"),
                                        dict(range=[15, 35], color="rgba(251,191,36,.18)"),
                                        dict(range=[35, 100], color="rgba(251,79,111,.18)")])))
    gauge.update_layout(margin=dict(l=40, r=40, t=80, b=10))
    a.plotly_chart(style(gauge, 340, legend=False).update_layout(margin=dict(l=40, r=40, t=80, b=10)), width="stretch")
    heat = f.pivot_table(index="Department", columns="JobLevel", values="PromotionGapScore", aggfunc="mean")
    hm = px.imshow(heat.round(0), text_auto=True, aspect="auto", color_continuous_scale=["#111833", "#7C3AED", "#FA582D", "#FDE68A"],
                   title="Stagnation heatmap · avg gap score by department × job level")
    b.plotly_chart(style(hm, 340), width="stretch")

    role = (f.groupby("JobRole").agg(Score=("PromotionGapScore", "mean"),
            Share=("YearsSinceLastPromotion", lambda s: (s >= gap_threshold).mean() * 100)).sort_values("Score").reset_index())
    bars = px.bar(role, x="Score", y="JobRole", orientation="h", color="Score", text=role["Score"].round(1),
                  color_continuous_scale=["#38BDF8", "#A78BFA", "#FA582D"], hover_data={"Share": ":.0f"},
                  title="Role-level stagnation · avg Promotion Gap Score")
    bars.update_traces(marker_line_width=0, textposition="outside")
    bars.update_layout(coloraxis_showscale=False, yaxis_title=None)
    st.plotly_chart(style(bars, 420), width="stretch")
    insight(f"<b>{len(high_gap):,}</b> employees ({share:.0f}%) have gone {gap_threshold}+ years without a promotion. "
            "Managers and Research Directors carry the highest stagnation scores.")

    section("High-gap employees", f"Sorted by Promotion Gap Score · threshold {gap_threshold}+ yrs")
    st.dataframe(high_gap.sort_values("PromotionGapScore", ascending=False)[
        ["EmployeeID", "Department", "JobRole", "JobLevel", "YearsAtCompany", "YearsSinceLastPromotion",
         "PromotionGapScore", "PromotionGapBand", "CareerCluster"]], width="stretch", hide_index=True, height=360,
        column_config={"PromotionGapScore": st.column_config.ProgressColumn("Gap score", min_value=0, max_value=100,
                                                                           format="%.0f")})

# ================================================================== 3. retention
with tabs[2]:
    opp_df = f[f["RetentionOpportunity"]].sort_values("RetentionOpportunityIndex", ascending=False)
    insight("Retention opportunities = <b>still employed</b> · <b>engaged</b> (≥ 2.5/4) · "
            "<b>low attrition risk</b> (&lt; 0.5) · <b>Medium/High</b> promotion gap. "
            "The cheapest people to keep — and nobody else is flagging them.")
    if opp_df.empty:
        st.info("No retention opportunities in this selection.")
    else:
        acts = opp_df["SuggestedAction"].str.split(", ").explode().value_counts()
        icons = {"Promotion review": "🏆", "Internal role rotation": "🔄", "Upskilling / training plan": "📚",
                 "Mentor / manager change": "🤝", "Career conversation": "💬"}
        cols = st.columns(len(acts))
        palette = ["#FA582D", "#A78BFA", "#38BDF8", "#34D399", "#FBBF24"]
        for i, (col, (act, cnt)) in enumerate(zip(cols, acts.items())):
            kpi(col, icons.get(act, "✨"), act, f"{cnt}", "employees", palette[i % 5], cnt / len(opp_df) * 100)
        st.write("")
        a, b = st.columns(2)
        sun = px.sunburst(opp_df, path=["Department", "CareerCluster"], color="CareerCluster",
                          color_discrete_map={**COLORS, "(?)": "#1E2547"}, title="Where the opportunities sit")
        sun.update_traces(marker_line_color="#070B1A", marker_line_width=2)
        a.plotly_chart(style(sun, 430, legend=False), width="stretch")
        hist = px.histogram(opp_df, x="RetentionOpportunityIndex", nbins=25, color="CareerCluster",
                            color_discrete_map=COLORS, title="Retention Opportunity Index · intervention priority")
        hist.update_layout(bargap=.08, yaxis_title="Employees")
        b.plotly_chart(style(hist, 430), width="stretch")

        section("Intervention list", "Highest priority first")
        cols_ = ["EmployeeID", "Department", "JobRole", "CareerCluster", "YearsSinceLastPromotion", "EngagementScore",
                 "AttritionRiskProb", "RetentionOpportunityIndex", "SuggestedAction"]
        st.dataframe(opp_df[cols_], width="stretch", hide_index=True, height=380, column_config={
            "RetentionOpportunityIndex": st.column_config.ProgressColumn("Priority", min_value=0, max_value=100, format="%.0f"),
            "EngagementScore": st.column_config.NumberColumn("Engagement", format="%.2f / 4"),
            "AttritionRiskProb": st.column_config.NumberColumn("Risk", format="%.2f")})
        st.download_button("⬇️ Download intervention list (CSV)", opp_df[cols_].to_csv(index=False),
                           "retention_opportunities.csv", "text/csv", type="primary")

# ================================================================== 4. managers
with tabs[3]:
    mgr = (f.groupby("ManagerTenureBand", observed=True).agg(Employees=("EmployeeID", "count"),
           Promo=("YearsSinceLastPromotion", "mean"), Attrition=("Attrition", "mean")).reset_index())
    combo = go.Figure()
    combo.add_bar(x=mgr["ManagerTenureBand"].astype(str), y=mgr["Promo"], name="Yrs since promotion",
                  marker=dict(color=mgr["Promo"], colorscale=[[0, "#38BDF8"], [1, "#A78BFA"]]),
                  text=mgr["Promo"].round(1), textposition="outside")
    combo.add_scatter(x=mgr["ManagerTenureBand"].astype(str), y=mgr["Attrition"] * 100, name="Attrition %", yaxis="y2",
                      mode="lines+markers+text", text=(mgr["Attrition"] * 100).round(0).astype(int).astype(str) + "%",
                      textposition="top center", line=dict(color=ACCENT, width=4), marker=dict(size=12))
    combo.update_layout(title="Manager tenure vs career growth & attrition", xaxis_title="Years with current manager",
                        yaxis=dict(title="Yrs since promotion"),
                        yaxis2=dict(title="Attrition %", overlaying="y", side="right", showgrid=False, tickformat=".0f", ticksuffix="%"))
    st.plotly_chart(style(combo, 420), width="stretch")
    insight("A <b>new manager</b> is the riskiest moment for attrition — yet the <b>longest pairings</b> carry the "
            "longest promotion gaps. Stability can quietly mask stagnation.")

    team = (f.groupby(["Department", "JobRole"]).agg(Employees=("EmployeeID", "count"),
            MgrTenure=("YearsWithCurrManager", "mean"), GapScore=("PromotionGapScore", "mean"),
            HighGap=("PromotionGapBand", lambda s: (s == "High").mean()), Attrition=("Attrition", "mean"))
            .reset_index().sort_values("GapScore", ascending=False))
    bub = px.scatter(team, x="MgrTenure", y="GapScore", size="Employees", color="Department", hover_name="JobRole",
                     size_max=55, title="Team-level stagnation signals · bubble = team size",
                     color_discrete_sequence=["#FA582D", "#38BDF8", "#A78BFA"])
    bub.update_traces(marker=dict(line=dict(width=1, color="#fff"), opacity=.85))
    bub.update_layout(xaxis_title="Avg years with manager", yaxis_title="Avg Promotion Gap Score")
    st.plotly_chart(style(bub, 440), width="stretch")
    st.dataframe(team, width="stretch", hide_index=True, column_config={
        "MgrTenure": st.column_config.NumberColumn("Mgr tenure", format="%.1f yrs"),
        "GapScore": st.column_config.ProgressColumn("Gap score", min_value=0, max_value=100, format="%.0f"),
        "HighGap": st.column_config.ProgressColumn("High-gap share", min_value=0, max_value=1, format="percent"),
        "Attrition": st.column_config.NumberColumn(format="percent")})

# ================================================================== 5. cluster explorer
with tabs[4]:
    present = [o for o in ORDER if o in f["CareerCluster"].unique()]
    chosen = st.radio("Pick a cluster", present, horizontal=True,
                      format_func=lambda x: f"{CLUSTERS[x][1]} {x}")
    sub = f[f["CareerCluster"] == chosen]
    color = COLORS[chosen]
    c = st.columns(4)
    kpi(c[0], "👥", "Employees", f"{len(sub)}", f"{len(sub) / n:.0%} of view", color, len(sub) / n * 100)
    kpi(c[1], "⏳", "Avg yrs since promotion", f"{sub['YearsSinceLastPromotion'].mean():.1f}", "years", color,
        sub["YearsSinceLastPromotion"].mean() / 15 * 100)
    kpi(c[2], "📈", "Avg gap score", f"{sub['PromotionGapScore'].mean():.0f}", "out of 100", color,
        sub["PromotionGapScore"].mean())
    kpi(c[3], "🎯", "Retention opportunities", f"{int(sub['RetentionOpportunity'].sum())}", "to act on", color,
        sub["RetentionOpportunity"].mean() * 100)
    st.write("")
    a, b = st.columns(2)
    cmp_feats = ["PromotionGapRatio", "RoleStagnationIndex", "ManagerStabilityIndicator"]
    cmp = pd.DataFrame({"Metric": ["Promotion gap", "Role stagnation", "Manager stability"],
                        chosen: sub[cmp_feats].mean().values, "Company": f[cmp_feats].mean().values})
    gb = px.bar(cmp.melt(id_vars="Metric", var_name="Group"), x="Metric", y="value", color="Group", barmode="group",
                color_discrete_map={chosen: color, "Company": "#475073"}, title="vs company average")
    gb.update_layout(yaxis_title="Ratio of tenure", xaxis_title=None)
    a.plotly_chart(style(gb, 380), width="stretch")
    tm = px.treemap(sub, path=["Department", "JobRole"], title="Where this cluster works",
                    color_discrete_sequence=[color])
    tm.update_traces(marker_line_color="#070B1A", marker_line_width=2)
    b.plotly_chart(style(tm, 380, legend=False), width="stretch")
    st.dataframe(sub[["EmployeeID", "Department", "JobRole", "Age", "YearsAtCompany", "YearsSinceLastPromotion",
                      "PromotionGapScore", "SuggestedAction"]], width="stretch", hide_index=True, height=320,
                 column_config={"PromotionGapScore": st.column_config.ProgressColumn("Gap score", min_value=0,
                                                                                    max_value=100, format="%.0f")})

# ================================================================== 6. employee spotlight
with tabs[5]:
    section("Employee spotlight", "A one-page career health card for any employee")
    default = f.sort_values("RetentionOpportunityIndex", ascending=False)["EmployeeID"].iloc[0]
    ids = list(f["EmployeeID"])
    emp_id = st.selectbox("Search employee ID", ids, index=ids.index(default))
    e = f[f["EmployeeID"] == emp_id].iloc[0]
    color = COLORS[e["CareerCluster"]]
    band_c = BAND_COLORS[e["PromotionGapBand"]]
    a, b = st.columns([1, 1.2])
    with a:
        tags = "".join(f'<span class="tag" style="--c:{ACCENT}">{t}</span>' for t in e["SuggestedAction"].split(", "))
        status = ("🎯 Retention opportunity" if e["RetentionOpportunity"] else
                  "🚪 Has left" if e["Attrition"] else "✅ No urgent action")
        st.markdown(f"""<div class="profile"><h2>{e['EmployeeID']}</h2>
            <div class="role">{e['JobRole']} · {e['Department']} · Level {e['JobLevel']} · Age {e['Age']}</div>
            <span class="tag" style="--c:{color}">{CLUSTERS[e['CareerCluster']][1]} {e['CareerCluster']}</span>
            <span class="tag" style="--c:{band_c}">Gap: {e['PromotionGapBand']} ({e['PromotionGapScore']:.0f})</span>
            <span class="tag" style="--c:#38BDF8">{status}</span>
            <p style="margin:16px 0 4px;color:#9AA3C7;font-size:.82rem">SUGGESTED ACTIONS</p>{tags}
            <p style="margin:16px 0 0;color:#CBD2EE;font-size:.88rem">
            🏢 {e['YearsAtCompany']} yrs at company · 💼 {e['YearsInCurrentRole']} yrs in role ·
            ⏳ {e['YearsSinceLastPromotion']} yrs since promotion · 🤝 {e['YearsWithCurrManager']} yrs with manager ·
            📚 {e['TrainingTimesLastYear']} trainings last year · 💚 engagement {e['EngagementScore']:.2f}/4 ·
            ⚠️ risk {e['AttritionRiskProb']:.2f}</p></div>""", unsafe_allow_html=True)
    with b:
        dims = ["PromotionGapRatio", "RoleStagnationIndex", "ManagerStabilityIndicator"]
        labels = ["Promotion gap", "Role stagnation", "Manager stability", "Engagement", "Risk"]
        me = [e[d] for d in dims] + [e["EngagementScore"] / 4, e["AttritionRiskProb"]]
        avg = list(f[dims].mean()) + [f["EngagementScore"].mean() / 4, f["AttritionRiskProb"].mean()]
        pol = go.Figure()
        pol.add_scatterpolar(r=avg + [avg[0]], theta=labels + [labels[0]], name="Company avg", fill="toself",
                             line=dict(color="#64748B"), opacity=.5)
        pol.add_scatterpolar(r=me + [me[0]], theta=labels + [labels[0]], name=e["EmployeeID"], fill="toself",
                             line=dict(color=color, width=3), opacity=.75)
        pol.update_layout(title="Career fingerprint vs company", polar=dict(bgcolor="rgba(0,0,0,0)",
                          radialaxis=dict(range=[0, 1], gridcolor="rgba(255,255,255,.1)", showticklabels=False),
                          angularaxis=dict(gridcolor="rgba(255,255,255,.1)")))
        st.plotly_chart(style(pol, 400), width="stretch")

st.markdown('<p style="text-align:center;color:#5B6488;font-size:.8rem;margin-top:28px">'
            'CareerPulse · built with Streamlit, scikit-learn &amp; Plotly · Thota Sathwika, BVRIT · Unified Mentor 2026-27</p>',
            unsafe_allow_html=True)
