"""Streamlit dashboard: Career Progression & Promotion Gap Analysis."""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).parent / "src"))
from pipeline import build  # noqa: E402

st.set_page_config(page_title="Career Progression Intelligence | Palo Alto Networks",
                   page_icon="📈", layout="wide")

CLUSTER_ORDER = ["Early-Career Explorers", "Fast-Track Performers", "Stable Long-Term Contributors",
                 "Promotion-Stalled", "High-Risk Stagnation"]
CLUSTER_COLORS = dict(zip(CLUSTER_ORDER, ["#4C78A8", "#54A24B", "#9D755D", "#F58518", "#E45756"]))
BAND_COLORS = {"Low": "#54A24B", "Medium": "#F2B701", "High": "#E45756"}


@st.cache_data
def get_data():
    return build()


df, metrics = get_data()

# ------------------------------------------------------------------ sidebar
st.sidebar.title("Filters")
dept = st.sidebar.multiselect("Department", sorted(df["Department"].unique()))
role_options = sorted(df[df["Department"].isin(dept)]["JobRole"].unique()) if dept else sorted(df["JobRole"].unique())
roles = st.sidebar.multiselect("Job Role", role_options)
stages = st.sidebar.multiselect("Career Stage", list(df["CareerStage"].cat.categories))
gap_threshold = st.sidebar.slider("Promotion gap threshold (years since last promotion)", 0, 15, 4)
include_left = st.sidebar.checkbox("Include employees who already left", value=True)

f = df.copy()
if dept:
    f = f[f["Department"].isin(dept)]
if roles:
    f = f[f["JobRole"].isin(roles)]
if stages:
    f = f[f["CareerStage"].isin(stages)]
if not include_left:
    f = f[f["Attrition"] == 0]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(f):,}** of {len(df):,} employees "
                   f"({metrics['rows_raw'] - metrics['rows_clean']} late-career outliers removed).")

if f.empty:
    st.warning("No employees match these filters.")
    st.stop()

# ------------------------------------------------------------------ header
st.title("📈 Career Progression & Promotion Gap Intelligence")
st.caption("Palo Alto Networks · explaining *why* employees may disengage, before they do")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Employees", f"{len(f):,}")
k2.metric("High promotion gap", f"{(f['PromotionGapBand'] == 'High').mean():.0%}")
k3.metric("Retention opportunities", f"{int(f['RetentionOpportunity'].sum()):,}")
k4.metric("Training need", f"{(f['TrainingNeed'] == 'Yes').mean():.0%}")
k5.metric("Attrition rate", f"{f['Attrition'].mean():.1%}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧭 Career Clusters", "⏳ Promotion Gap Monitor",
                                        "🎯 Retention Opportunities", "👥 Managerial Insights",
                                        "🔍 Cluster Explorer"])

# ------------------------------------------------------- 1. cluster dashboard
with tab1:
    c1, c2 = st.columns(2)
    counts = f["CareerCluster"].value_counts().reindex(CLUSTER_ORDER).fillna(0).reset_index()
    counts.columns = ["CareerCluster", "Employees"]
    c1.plotly_chart(px.bar(counts, x="CareerCluster", y="Employees", color="CareerCluster",
                           color_discrete_map=CLUSTER_COLORS, title="Cluster distribution")
                    .update_layout(showlegend=False, xaxis_title=None), width="stretch")
    c2.plotly_chart(px.scatter(f, x="YearsAtCompany", y="YearsSinceLastPromotion", color="CareerCluster",
                               color_discrete_map=CLUSTER_COLORS, category_orders={"CareerCluster": CLUSTER_ORDER},
                               opacity=0.6, title="Tenure vs years since last promotion",
                               hover_data=["EmployeeID", "JobRole", "JobLevel"]), width="stretch")

    st.subheader("Career pattern summaries")
    summary = (f.groupby("CareerCluster")
               .agg(Employees=("EmployeeID", "count"), AvgTenure=("YearsAtCompany", "mean"),
                    YrsSincePromotion=("YearsSinceLastPromotion", "mean"),
                    PromotionGapRatio=("PromotionGapRatio", "mean"),
                    RoleStagnation=("RoleStagnationIndex", "mean"),
                    TrainingsLastYear=("TrainingTimesLastYear", "mean"),
                    ManagerStability=("ManagerStabilityIndicator", "mean"),
                    AttritionRate=("Attrition", "mean"))
               .reindex([c for c in CLUSTER_ORDER if c in f["CareerCluster"].unique()]).round(2))
    st.dataframe(summary, width="stretch")
    st.caption(f"K-Means (k=5) silhouette = {metrics['silhouette_kmeans']:.3f}; validated against Ward "
               f"hierarchical clustering (Adjusted Rand Index = {metrics['adjusted_rand_index']:.2f}).")

# --------------------------------------------------- 2. promotion gap monitor
with tab2:
    high_gap = f[f["YearsSinceLastPromotion"] >= gap_threshold]
    st.markdown(f"**{len(high_gap):,} employees** have gone **{gap_threshold}+ years** without a promotion "
                f"({len(high_gap) / len(f):.0%} of the current selection).")
    c1, c2 = st.columns(2)
    band = f["PromotionGapBand"].value_counts().reindex(["Low", "Medium", "High"]).reset_index()
    band.columns = ["Band", "Employees"]
    c1.plotly_chart(px.pie(band, names="Band", values="Employees", color="Band", hole=0.5,
                           color_discrete_map=BAND_COLORS, title="Promotion Gap Score bands"),
                    width="stretch")
    role_stag = (f.groupby("JobRole")
                 .agg(AvgGapScore=("PromotionGapScore", "mean"),
                      ShareAboveThreshold=("YearsSinceLastPromotion", lambda s: (s >= gap_threshold).mean()))
                 .sort_values("AvgGapScore").reset_index())
    c2.plotly_chart(px.bar(role_stag, x="AvgGapScore", y="JobRole", orientation="h",
                           color="ShareAboveThreshold", color_continuous_scale="OrRd",
                           title="Role-level stagnation (avg Promotion Gap Score)"),
                    width="stretch")
    st.subheader("High-gap employees")
    cols = ["EmployeeID", "Department", "JobRole", "JobLevel", "YearsAtCompany", "YearsSinceLastPromotion",
            "YearsInCurrentRole", "PromotionGapScore", "PromotionGapBand", "CareerCluster"]
    st.dataframe(high_gap.sort_values("PromotionGapScore", ascending=False)[cols],
                 width="stretch", hide_index=True)

# ------------------------------------------------ 3. retention opportunities
with tab3:
    st.markdown("Employees who are **still with the company**, **not disengaged** (engagement ≥ 2.5/4), "
                "**not high attrition risk** (model probability < 0.5) but show **Medium/High promotion gap** — "
                "the best window for a proactive career intervention.")
    opp = f[f["RetentionOpportunity"]].sort_values("RetentionOpportunityIndex", ascending=False)
    c1, c2 = st.columns(2)
    actions = opp["SuggestedAction"].str.split(", ").explode().value_counts().reset_index()
    actions.columns = ["Action", "Employees"]
    c1.plotly_chart(px.bar(actions, x="Employees", y="Action", orientation="h",
                           title="Suggested interventions", color_discrete_sequence=["#4C78A8"]),
                    width="stretch")
    c2.plotly_chart(px.histogram(opp, x="RetentionOpportunityIndex", nbins=20, color="CareerCluster",
                                 color_discrete_map=CLUSTER_COLORS, title="Retention Opportunity Index"),
                    width="stretch")
    cols = ["EmployeeID", "Department", "JobRole", "CareerCluster", "YearsSinceLastPromotion",
            "PromotionGapBand", "EngagementScore", "AttritionRiskProb", "TrainingNeed",
            "RetentionOpportunityIndex", "SuggestedAction"]
    st.dataframe(opp[cols], width="stretch", hide_index=True)
    st.download_button("⬇️ Download intervention list (CSV)", opp[cols].to_csv(index=False),
                       "retention_opportunities.csv", "text/csv")

# ---------------------------------------------------- 4. managerial insights
with tab4:
    mgr = (f.groupby("ManagerTenureBand", observed=True)
           .agg(Employees=("EmployeeID", "count"), YrsSincePromotion=("YearsSinceLastPromotion", "mean"),
                PromotionGapScore=("PromotionGapScore", "mean"), AttritionRate=("Attrition", "mean"),
                JobLevel=("JobLevel", "mean")).reset_index())
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.bar(mgr, x="ManagerTenureBand", y="YrsSincePromotion",
                           title="Manager tenure vs years since last promotion",
                           color_discrete_sequence=["#F58518"]), width="stretch")
    c2.plotly_chart(px.line(mgr, x="ManagerTenureBand", y="AttritionRate", markers=True,
                            title="Manager tenure vs attrition rate"), width="stretch")
    st.subheader("Team-level stagnation signals (Department × Job Role)")
    team = (f.groupby(["Department", "JobRole"])
            .agg(Employees=("EmployeeID", "count"), AvgMgrTenure=("YearsWithCurrManager", "mean"),
                 AvgGapScore=("PromotionGapScore", "mean"),
                 HighGapShare=("PromotionGapBand", lambda s: (s == "High").mean()),
                 AttritionRate=("Attrition", "mean")).round(2).reset_index()
            .sort_values("AvgGapScore", ascending=False))
    st.plotly_chart(px.scatter(team, x="AvgMgrTenure", y="AvgGapScore", size="Employees", color="Department",
                               hover_name="JobRole", title="Teams: manager tenure vs stagnation"),
                    width="stretch")
    st.dataframe(team, width="stretch", hide_index=True)

# ---------------------------------------------------------- 5. cluster explorer
with tab5:
    chosen = st.selectbox("Choose a career cluster", [c for c in CLUSTER_ORDER if c in f["CareerCluster"].unique()])
    sub = f[f["CareerCluster"] == chosen]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Employees", len(sub))
    m2.metric("Avg years since promotion", f"{sub['YearsSinceLastPromotion'].mean():.1f}")
    m3.metric("Avg gap score", f"{sub['PromotionGapScore'].mean():.0f}")
    m4.metric("Retention opportunities", int(sub["RetentionOpportunity"].sum()))
    feats = ["PromotionGapRatio", "RoleStagnationIndex", "ManagerStabilityIndicator"]
    radar = pd.DataFrame({"Feature": feats, "Cluster": sub[feats].mean().values, "Company": f[feats].mean().values})
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.bar(radar.melt(id_vars="Feature"), x="Feature", y="value", color="variable",
                           barmode="group", title=f"{chosen} vs company average"), width="stretch")
    c2.plotly_chart(px.histogram(sub, x="Department", color="PromotionGapBand", color_discrete_map=BAND_COLORS,
                                 title="Department mix & gap band"), width="stretch")
    st.dataframe(sub[["EmployeeID", "Department", "JobRole", "Age", "YearsAtCompany", "YearsSinceLastPromotion",
                      "PromotionGapScore", "SuggestedAction"]], width="stretch", hide_index=True)
