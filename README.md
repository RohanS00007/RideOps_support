# RideOps Support Triage & Decision Console (v0)

An operational decision-support tool and case study analysis built for **Meera (Support Lead)** to diagnose RideOps' support ticket backlog, eliminate the 56.6% avoidable engineering escalation loop, and cut active open tickets without hiring additional staff.

---

## Live Demo & Quickstart

### Local Setup
```bash
# 1. Clone the repository
git clone https://github.com/your-username/rideops-support-triage.git
cd rideops-support-triage

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Streamlit app
streamlit run app.py
```
App will open automatically in your browser at `http://localhost:8501`.

### Deploy to Streamlit Cloud
1. Fork or push this repository to GitHub.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Connect your repository, select `app.py` as the entrypoint, and deploy.

---

## Design System & Color Palette
The user interface strictly adheres to an editorial, high-contrast palette:
* **Cream (`#F3EEE3`):** Canvas background & warm card surfaces
* **Ink Black (`#111111`):** Headers, high-contrast borders, body text, and dark button elements
* **Burnt Orange (`#D9541E`):** Single accent hue for highlights, active tab states, and callout badges

---

## Key Diagnostic Findings (Computed from 1,444 Tickets)

* **Intake Surge vs. Backlog Growth:** Ticket inflow grew **+51.8%** from July (390) to September (592). Open tickets grew by **+60%** (30 at 31 Jul $\to$ 48 at 30 Sep). However, normalized backlog remained stable at ~0.35x weekly inflow.
* **Escalation Turnaround Chasm:** Closed tickets resolved at L1 have a median turnaround of **12.6 hours** (CSAT: **4.01**), whereas escalated tickets take **86.8 hours (~3.6 days)** (CSAT: **3.22**) — a **6.9x slowdown**.
* **Two Avoidable Escalation Groups (56.6% of all 486 escalations):**
  1. **Returned to L1 (173 tickets / 35.6%):** 89 Insufficient info + 84 Config issues. Median turnaround explodes to **121.1h – 128.6h (>5 days)**.
  2. **Didn't Need New Investigation (102 tickets / 21.0%):** 56 Duplicates (30 in Report export alone) + 24 How-tos + 22 Not reproducible.
* **Handoff Friction:** Every additional handoff between L1 and Engineering doubles median closed turnaround time and degrades CSAT:
  * 0 Handoffs: **12.6h** | CSAT **4.01**
  * 1 Handoff: **58.7h** | CSAT **3.56**
  * 2 Handoffs: **110.4h** | CSAT **2.80**
  * 3 Handoffs: **169.9h** | CSAT **2.10**
* **Agent Variance:**
  * **Karan B:** Fast non-escalated median close (9.6h), but a **28.0% non-escalated reopen rate** (78 total reopen events, **46.2% of company total**) and 3.27 CSAT.
  * **Rahul T:** Escalates **61.6%** of his caseload (93 tickets), with **46.2% returned to L1**.

---

## What the App Does (5 Core Tabs)

1. **Health Overview:** Top-line operational KPIs, weekly inflow vs. closure flow, raw vs. normalized week-end open backlog trend, and category inflow growth vs. escalation propensity.
2. **Act Now (Open 48 Tickets):** Prioritizes the active September open backlog using a mathematically grounded Action Score:
   $$\text{Action Score} = \text{Priority Weight} \times \text{Age (Days)} \times (\times 1.5\text{ if with Eng}) \times (\times 1.5\text{ if Reopened})$$
   Includes interactive filters, CSV export, and a copyable **Escalation Packet** generator for engineering syncs.
3. **Escalation Quality:** Breakdown of engineering final verdicts, multi-handoff turnaround penalties, top recurring issue descriptions with sample size $n$, and a generic pre-escalation intake checklist (*"proposed — to validate with engineering"*).
4. **Agent Coaching:** Speed vs. Quality scatter plot (`Non-Escalated Median Close Hours` vs. `Tickets Reopened %`, bubble size = volume) with structured coaching profiles for Karan B and Rahul T.
5. **What-If Simulation:** Sensitivity slider testing the impact of resolving returned-to-L1 tickets at L1. Recomputes historical backlog and turnaround hours saved using a reproducible fixed seed (`seed=42`).

---

## Repository Structure

```
├── .streamlit/
│   └── config.toml                  # Enforces light theme with Cream & Ink palette
├── data/
│   ├── rideops_support_tickets.csv  # 1,444 tickets (2 Jul – 30 Sep 2026)
│   └── rideops_data_dictionary.csv  # Schema and field definitions
├── app.py                           # Full Streamlit decision-support application
├── DOCS.md                          # Comprehensive submission write-up & methodology
├── README.md                        # Project documentation for GitHub
└── requirements.txt                 # Dependencies: streamlit, pandas, plotly
```

---

## Documentation
For the complete 4-page submission write-up covering problem framing, balanced stakeholder verdicts, metric derivations, non-goals, and the 4-week rollout roadmap, refer to [DOCS.md](DOCS.md).
