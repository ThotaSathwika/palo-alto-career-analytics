# Submission Guide — links, deployment steps and video scripts

## Step 1 · GitHub Repository Link (≈5 min)
1. Go to https://github.com/new → Repository name: `palo-alto-career-analytics` → **Public** → *Create repository* (do NOT add a README).
2. Unzip `palo-alto-career-analytics.zip`, open a terminal inside the folder and run:
   ```bash
   git remote add origin https://github.com/ThotaSathwika/palo-alto-career-analytics.git
   git push -u origin main
   ```
   (No terminal? On the empty repo page click **uploading an existing file** and drag in every file/folder.)
3. **Link:** `https://github.com/ThotaSathwika/palo-alto-career-analytics`

## Step 2 · Deployed Project Link (≈5 min)
1. Go to https://share.streamlit.io → *Sign in with GitHub*.
2. **Create app** → *Deploy a public app from GitHub* → Repository `ThotaSathwika/palo-alto-career-analytics`, Branch `main`, Main file `app.py`.
3. App URL (custom subdomain): `palo-alto-career-analytics` → **Deploy**. First build takes 2–3 minutes.
4. **Link:** `https://palo-alto-career-analytics.streamlit.app`

## Step 3 · Research Paper Link
Open the research-paper doc in Claude → **Share** → set link access to *anyone with the link* → copy the link.
Alternative: **Export → Word/PDF**, upload to Google Drive, set *Anyone with the link → Viewer*, copy that link.

## Step 4 & 5 · Videos
Record with OBS Studio, Loom or Google Meet (screen + webcam). Upload to **YouTube as Unlisted** (or Google Drive with
*Anyone with the link*). Copy the `https://youtu.be/...` link.

---

## Video 1 — Project Explanation (target 5–7 min)

**[0:00 – 0:30] Intro (webcam)**
"Hi, I'm Thota Sathwika, a final-year B.Tech CSE student at BVRIT Narsapur. In this video I'll walk you through my
Unified Mentor internship project: Career Progression and Promotion Gap Analysis for Retention Optimization at Palo Alto Networks."

**[0:30 – 1:15] Problem**
"Most attrition models tell HR *who* might leave. They don't explain *why*. Very often people leave because their career
stalls — long gaps between promotions, staying in the same role, little training, or manager issues. My goal was to
find those employees early, while they are still engaged, so HR can act before they decide to leave."

**[1:15 – 2:00] Data & features (show README / pipeline.py)**
"The dataset has 1,470 employees and 31 columns, no missing values, 16% attrition. I created four career metrics:
Promotion Gap Ratio, Role Stagnation Index, Training Intensity Score and Manager Stability Indicator — each one divides a
tenure field by years at the company. I also built an Engagement Score from the four satisfaction ratings, removed 24
extreme late-career outliers, scaled the features and one-hot encoded the categorical columns."

**[2:00 – 3:00] Clustering & scoring (show pipeline.py)**
"I used K-Means with five clusters and validated it with Ward hierarchical clustering — the Adjusted Rand Index is 0.74,
so both methods agree. From the cluster centres I labelled them: Early-Career Explorers, Fast-Track Performers, Stable
Long-Term Contributors, Promotion-Stalled, and High-Risk Stagnation. Then each employee gets a Promotion Gap Score from
0 to 100 — Low, Medium or High. A logistic-regression model with AUC 0.86 gives attrition risk, used only as context.
A retention opportunity is someone still here, engaged, low-risk, but with a Medium or High gap."

**[3:00 – 5:30] Dashboard demo (screen share the live app)**
- KPI row: "1,446 employees, 25% with a high promotion gap, 408 retention opportunities."
- *Career Clusters* tab: "Here's the cluster distribution and the tenure-vs-promotion scatter; the summary table shows Promotion-Stalled employees leave at 19% vs 6% for stable ones."
- Sidebar: pick *Sales*, move the gap slider to 5 — "everything updates."
- *Promotion Gap Monitor*: "Managers and Research Directors have the highest stagnation."
- *Retention Opportunities*: "Each person gets a suggested action — promotion review, role rotation, training or mentor change — and HR can download this list as CSV."
- *Managerial Insights*: "New manager relationships have 28% attrition, but very long ones go with the longest promotion gaps."
- *Cluster Explorer*: pick *High-Risk Stagnation* — "90% of this group need training."

**[5:30 – 6:15] Recommendations & close**
"My recommendations: promotion reviews for 267 employees, rotation for 219, training plans for 170 and a review of
long manager pairings. The research paper and code are linked in my submission. Thank you!"

---

## Video 2 — Internship Experience & Feedback (target 2–3 min)

**Intro:** "Hi, I'm Thota Sathwika from BVRIT Narsapur, and this is my experience of the Unified Mentor data-science internship."

**What I worked on:** "My project analysed career progression at Palo Alto Networks to find employees whose careers are
stalling before they disengage."

**What I learned** (pick what's true for you):
- "Feature engineering — turning raw tenure columns into ratios that actually explain stagnation."
- "Unsupervised learning — K-Means, hierarchical clustering, and validating clusters with silhouette and Adjusted Rand Index."
- "Building and deploying an interactive Streamlit dashboard and managing code on GitHub."
- "Thinking like a business analyst — turning model output into actions HR can take."

**Challenges:** "The hardest part was labelling clusters in a way that makes business sense, and handling new joiners
with zero tenure when calculating ratios."

**Feedback:** "The project brief was clear and realistic. [Add your honest feedback — e.g. mentor support, timelines,
what you'd improve.]"

**Close:** "This internship strengthened my Python, machine learning and storytelling skills, and I'm grateful to the
Unified Mentor team. Thank you."

---

## Final checklist (all must start with https://)
| Field | Link |
|---|---|
| GitHub Repository | https://github.com/ThotaSathwika/palo-alto-career-analytics |
| Research Paper | (your shared doc / Google Drive link) |
| Deployed Project | https://palo-alto-career-analytics.streamlit.app |
| Project Explanation Video | https://youtu.be/… |
| Internship Experience Video | https://youtu.be/… |
