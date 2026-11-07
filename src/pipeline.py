"""Career Progression & Promotion Gap Analysis - core pipeline.

Steps: feature engineering -> preprocessing -> K-Means clustering
(validated with hierarchical clustering) -> cluster labelling ->
promotion gap scoring -> retention opportunity identification.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "palo_alto_networks.csv"
N_CLUSTERS = 5
SEED = 42

CLUSTER_FEATURES = [
    "YearsAtCompany", "YearsSinceLastPromotion", "YearsInCurrentRole",
    "PromotionGapRatio", "RoleStagnationIndex", "TrainingIntensityScore",
    "ManagerStabilityIndicator", "JobLevel", "TotalWorkingYears",
]


def load_data(path=DATA_PATH):
    return pd.read_csv(path)


# ---------------------------------------------------------------- 1. features
def engineer_features(df):
    df = df.copy()
    tenure = df["YearsAtCompany"]
    safe_tenure = tenure.replace(0, 1)  # new joiners: avoid divide-by-zero

    df["PromotionGapRatio"] = np.where(tenure == 0, 0, df["YearsSinceLastPromotion"] / safe_tenure)
    df["RoleStagnationIndex"] = np.where(tenure == 0, 0, df["YearsInCurrentRole"] / safe_tenure)
    df["TrainingIntensityScore"] = df["TrainingTimesLastYear"] / safe_tenure
    df["ManagerStabilityIndicator"] = np.where(tenure == 0, 0, df["YearsWithCurrManager"] / safe_tenure)

    # Engagement = average of the four satisfaction / involvement scores (1-4)
    df["EngagementScore"] = df[["EnvironmentSatisfaction", "JobSatisfaction",
                                "JobInvolvement", "WorkLifeBalance"]].mean(axis=1)

    df["CareerStage"] = pd.cut(df["TotalWorkingYears"], bins=[-1, 5, 15, 100],
                               labels=["Early Career (0-5y)", "Mid Career (6-15y)", "Late Career (16y+)"])
    df["ManagerTenureBand"] = pd.cut(df["YearsWithCurrManager"], bins=[-1, 1, 4, 8, 100],
                                     labels=["0-1 yrs", "2-4 yrs", "5-8 yrs", "9+ yrs"])
    return df


# ----------------------------------------------------------- 2. preprocessing
def remove_outliers(df):
    """Drop extreme late-career edge cases (very long tenure / experience)."""
    mask = (df["YearsAtCompany"] <= 30) & (df["TotalWorkingYears"] <= 35)
    return df[mask].reset_index(drop=True)


def scale_features(df):
    scaler = StandardScaler()
    return scaler.fit_transform(df[CLUSTER_FEATURES])


def encode_categoricals(df):
    """One-hot encode categorical fields (used by the attrition-risk model)."""
    cats = ["Department", "JobRole", "BusinessTravel", "OverTime", "MaritalStatus"]
    return pd.get_dummies(df[cats], drop_first=True).astype(int)


# --------------------------------------------------------------- 3. clustering
def run_clustering(X):
    kmeans = KMeans(n_clusters=N_CLUSTERS, n_init=20, random_state=SEED)
    km_labels = kmeans.fit_predict(X)
    hc_labels = fcluster(linkage(X, method="ward"), N_CLUSTERS, criterion="maxclust") - 1

    k_scan = {}
    for k in range(2, 9):
        model = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(X)
        k_scan[k] = {"inertia": model.inertia_, "silhouette": silhouette_score(X, model.labels_)}

    metrics = {
        "silhouette_kmeans": silhouette_score(X, km_labels),
        "silhouette_hierarchical": silhouette_score(X, hc_labels),
        "adjusted_rand_index": adjusted_rand_score(km_labels, hc_labels),
        "k_scan": k_scan,
    }
    return km_labels, hc_labels, metrics


def label_clusters(df):
    """Name each K-Means cluster from its profile (promotion, role, training, manager)."""
    prof = df.groupby("ClusterId")[CLUSTER_FEATURES + ["Age"]].mean()
    names = {}
    remaining = list(prof.index)

    def take(cid, name):
        names[cid] = name
        remaining.remove(cid)

    # Longest gap since promotion -> high-risk stagnation
    take(prof.loc[remaining, "YearsSinceLastPromotion"].idxmax(), "High-Risk Stagnation")
    # Shortest tenure -> early-career explorers
    take(prof.loc[remaining, "YearsAtCompany"].idxmin(), "Early-Career Explorers")
    # Highest promotion-gap ratio among the rest -> promotion-stalled
    take(prof.loc[remaining, "PromotionGapRatio"].idxmax(), "Promotion-Stalled")
    # Longest tenure among the rest -> stable long-term contributors
    take(prof.loc[remaining, "YearsAtCompany"].idxmax(), "Stable Long-Term Contributors")
    take(remaining[0], "Fast-Track Performers")
    return df["ClusterId"].map(names)


# ------------------------------------------------------------ 4. risk scoring
def pct_rank(s):
    return s.rank(pct=True)


def promotion_gap_scoring(df):
    cluster_weight = {"High-Risk Stagnation": 1.0, "Promotion-Stalled": 0.8,
                      "Stable Long-Term Contributors": 0.5, "Early-Career Explorers": 0.2,
                      "Fast-Track Performers": 0.1}
    raw = (0.35 * pct_rank(df["YearsSinceLastPromotion"])
           + 0.25 * pct_rank(df["PromotionGapRatio"])
           + 0.20 * pct_rank(df["RoleStagnationIndex"])
           + 0.20 * df["CareerCluster"].map(cluster_weight))
    score = (raw - raw.min()) / (raw.max() - raw.min()) * 100
    band = pd.cut(score, bins=[-0.1, 40, 70, 100.1], labels=["Low", "Medium", "High"])
    return score.round(1), band


def attrition_risk(df):
    """Simple logistic-regression attrition probability (context, not the goal)."""
    num = ["Age", "MonthlyIncome", "JobLevel", "DistanceFromHome", "NumCompaniesWorked",
           "TotalWorkingYears", "YearsAtCompany", "StockOptionLevel", "EngagementScore",
           "PercentSalaryHike", "RelationshipSatisfaction"]
    X = pd.concat([df[num], encode_categoricals(df)], axis=1)
    X = StandardScaler().fit_transform(X)
    model = LogisticRegression(max_iter=2000, class_weight="balanced")
    model.fit(X, df["Attrition"])
    return model.predict_proba(X)[:, 1]


# --------------------------------------------------- 5. retention opportunity
def suggest_action(row):
    actions = []
    if row["YearsSinceLastPromotion"] >= 4 or row["PromotionGapRatio"] >= 0.5:
        actions.append("Promotion review")
    if row["RoleStagnationIndex"] >= 0.7 and row["YearsInCurrentRole"] >= 4:
        actions.append("Internal role rotation")
    if row["TrainingNeed"] == "Yes":
        actions.append("Upskilling / training plan")
    if row["ManagerStabilityIndicator"] >= 0.8 and row["YearsWithCurrManager"] >= 5:
        actions.append("Mentor / manager change")
    return ", ".join(actions) if actions else "Career conversation"


def build():
    raw = load_data()
    df = remove_outliers(engineer_features(raw))
    X = scale_features(df)

    km, hc, metrics = run_clustering(X)
    df["ClusterId"] = km
    df["HierarchicalCluster"] = hc
    df["CareerCluster"] = label_clusters(df)

    df["PromotionGapScore"], df["PromotionGapBand"] = promotion_gap_scoring(df)
    df["AttritionRiskProb"] = attrition_risk(df).round(3)
    df["TrainingNeed"] = np.where((df["TrainingTimesLastYear"] <= 1) |
                                  (df["TrainingIntensityScore"] < 0.25), "Yes", "No")

    not_disengaged = df["EngagementScore"] >= 2.5
    low_risk = df["AttritionRiskProb"] < 0.5
    stagnating = df["PromotionGapBand"].isin(["Medium", "High"])
    df["RetentionOpportunity"] = (df["Attrition"] == 0) & not_disengaged & low_risk & stagnating

    # Retention Opportunity Index (0-100): stagnation x engagement x (1 - risk)
    roi = (df["PromotionGapScore"] / 100) * (df["EngagementScore"] / 4) * (1 - df["AttritionRiskProb"])
    df["RetentionOpportunityIndex"] = (roi / roi.max() * 100).round(1)
    df["SuggestedAction"] = df.apply(suggest_action, axis=1)
    df.insert(0, "EmployeeID", [f"PAN-{i:04d}" for i in range(1, len(df) + 1)])

    metrics["rows_raw"] = len(raw)
    metrics["rows_clean"] = len(df)
    return df, metrics


if __name__ == "__main__":
    data, m = build()
    print({k: v for k, v in m.items() if k != "k_scan"})
    print(data["CareerCluster"].value_counts())
    print(data["PromotionGapBand"].value_counts())
    print("Retention opportunities:", data["RetentionOpportunity"].sum())
