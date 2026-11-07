# Career Progression & Promotion Gap Analysis for Retention Optimization — Palo Alto Networks

**Author:** Thota Sathwika · B.Tech CSE, B V Raju Institute of Technology · Unified Mentor Internship (2026-27)

Traditional attrition models tell HR *who* might leave. This project explains *why* — by finding
employees stuck in **promotion gaps**, **role stagnation**, **low training** and **weak manager continuity**,
and flagging them **before** they disengage.

## What it does
| Step | Method |
|---|---|
| Feature engineering | Promotion Gap Ratio, Role Stagnation Index, Training Intensity Score, Manager Stability Indicator, Engagement Score, Career Stage |
| Preprocessing | StandardScaler normalisation, one-hot encoding (department, role, …), removal of 24 late-career outliers (tenure > 30 y or experience > 35 y) |
| Clustering | K-Means, k = 5 (primary) validated with Ward hierarchical clustering (ARI = 0.74) |
| Cluster labels | Early-Career Explorers · Fast-Track Performers · Stable Long-Term Contributors · Promotion-Stalled · High-Risk Stagnation |
| Promotion Gap Score | 0–100 score → Low / Medium / High, combining stagnation indicators with cluster membership |
| Retention opportunities | Still employed + engaged (≥ 2.5/4) + low attrition risk (logistic regression, AUC 0.86) + Medium/High gap → **408 employees** with a suggested action |

## KPIs
Career Cluster · Promotion Gap Score · Retention Opportunity Index · Training Need Indicator · Manager Stability Impact

## Streamlit dashboard
Five tabs — **Career Clusters**, **Promotion Gap Monitor**, **Retention Opportunities**, **Managerial Insights**, **Cluster Explorer** —
with department & role filters, a career-stage selector, a promotion-gap threshold slider and a downloadable intervention list.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure
```
├── app.py                  # Streamlit dashboard
├── src/pipeline.py         # feature engineering, clustering, scoring
├── data/palo_alto_networks.csv
├── outputs/                # scored employees, retention list, model metrics
├── requirements.txt
└── .streamlit/config.toml
```

## Key findings
- **25 %** of employees fall in the High promotion-gap band; Managers and Research Directors stagnate the most.
- The **Promotion-Stalled** cluster (avg 4.3 yrs since promotion, gap ratio 0.86) has **19 %** attrition vs **6 %** for Stable Long-Term Contributors.
- Employees with a manager of **0–1 yrs** leave at **28 %** vs **7 %** for 9+ yrs — but long manager tenure goes with long promotion gaps (5.3 yrs), a hidden stagnation signal.
- **408** current, engaged, low-risk employees show stagnation — top actions: promotion review (267), role rotation (219), training plan (170).
