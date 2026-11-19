# RideOps Support: Diagnosis, Success Measure, v0 and 4-Week Plan

*Built for Meera (Support Lead). Data: 1,444 tickets, 2 Jul to 30 Sep 2026. "Now" = 30 Sep 2026 23:59, the date of the data pull. Every number below is computed from the CSV by `app.py`.*

## 1. The problem and what each leader believes

Open tickets rose about 60% since July and leadership wants that number down with no hiring budget.
- **Meera:** engineering is the bottleneck, escalated tickets vanish for days, some agents close in hours. Wants more people and faster engineering.
- **Sandeep:** support escalates things that should never reach engineering and skips basic checks.
- **Ritika:** the open-ticket number must fall this quarter, no new hires.

## 2. Data and assumptions

- **Open ticket:** at time T, `created_at <= T` and (`final_closed_at > T` or blank). A ticket the client reopened therefore counts as open until its final close.
- **Resolution times** use closed tickets only. The 48 open tickets are the slowest ones, so all medians are biased low.
- **CSAT** exists on only 648 of 1,444 tickets (45%). Treat it as a signal, not a measurement.
- **No SLA targets** exist in the data. I do not claim SLA breaches. First response and time to close by priority are used as yardsticks (P1: 0.3h / 14.6h, P2: 1.0h / 20.4h, P3: 2.9h / 19.9h, P4: 6.1h / 28.9h, median first response / median time to close).
- No rows were dropped or edited. Dates parse cleanly, ticket IDs are unique, and escalation fields are consistent (every escalated ticket has an engineering ID and outcome).
- I invented **no** RideOps rules (no cutoff hours, app versions, limits). The checklist below is a generic proposal to validate with engineering.

## 3. Diagnosis

**3.1 The backlog grew about twice as fast as intake.**
Monthly intake went 390 / 462 / 592 (+52% Jul to Sep). Average open tickets per day went 20.8 / 29.2 / 42.9 (+106%). The "about 60%" in the brief reproduces exactly as 30 open on 31 Jul vs 48 on 30 Sep, but that compares two single days. On monthly averages the backlog doubled while intake grew by half, so closing capacity did not keep pace. Normalised by weekly intake (open at week end / tickets created that week), the load was about 0.20x in Jul to Aug and about 0.30x in September.

**3.2 Growth and escalation are different problems.**
The biggest additions Jul to Sep were Cab delay (+43), Report export (+33) and Address change (+26), none of which escalate much except Report export (37%). The categories that escalate most are Live tracking (55.7%) and Roster sync (50.9%), together 302 of 486 escalations (62.1%).

**3.3 Escalation is the expensive path.**
486 of 1,444 tickets (33.7%) were escalated. Closed median: 12.6h at L1 vs 86.8h escalated (6.9x). CSAT 4.01 vs 3.11.

**3.4 What engineering concluded on the 486 escalations:**

| Outcome | Tickets | Share | Median close |
|---|---|---|---|
| Real fix | 211 | 43.4% | 64.8h |
| Returned to L1: insufficient info | 89 | 18.3% | 121.1h |
| Returned to L1: config issue | 84 | 17.3% | 128.6h |
| Duplicate of known issue | 56 | 11.5% | 67.5h |
| Not a bug / how-to | 24 | 4.9% | 68.7h |
| Not reproducible | 22 | 4.5% | 62.3h |

Two different failure modes: **173 (35.6%) bounced back to L1**, fixable by a pre-escalation check; **102 (21.0%) needed no new investigation**, fixable by a known-issues list (30 of the 56 duplicates are Report export).

**3.5 Each engineering handoff costs time and satisfaction.**
0 / 1 / 2 / 3 handoffs: median 12.6h / 58.7h / 110.4h / 169.9h; CSAT 4.01 / 3.56 / 2.80 / 2.10.

**3.6 Fast is not the same as good.**
Karan B closes non-escalated tickets fastest (9.6h median, peers 11.7h to 15.4h) but 27.2% of them are reopened (peers 3.6% to 7.3%) and CSAT on them is 3.27 (peers 4.12 to 4.30). He has 78 of the team's 169 reopen events (46%). Tickets that were reopened have CSAT 2.35 vs 3.84 for the rest. Rahul T escalates 61.6% of tickets (93 of 151; peers 16.1% to 40.2%); 43 came back to L1 and 27 needed no investigation.

**3.7 Verdicts**
- **Meera is partly right.** Even real fixes take 64.8h, so engineering is slow. But hiring does not touch the 173 bounces or the 102 non-investigations.
- **Sandeep is partly right.** 56.6% of escalations (275 of 486) did not need a fresh investigation. But real fixes still take almost three days, and a shared known-issues list is something engineering must help build.
- **Ritika's metric can be gamed.** Closing early lowers the open count and raises reopens. Karan B shows exactly this.

## 4. Success: what "better" looks like

| Metric | Formula | Baseline | Target |
|---|---|---|---|
| **Headline: open backlog at week end (reopen-aware)** | open tickets at Sunday 23:59, also shown divided by that week's intake | 48 on 30 Sep (0.30x in Sep) | at most 30, about 0.2x of current intake (Jul to Aug level) |
| **Lever: bounce rate** | (Insufficient info + Config) / escalations | 35.6% (173 of 486) | under 10% by week 4 (pilot goal, tune after week 2) |
| **Guardrail: reopen rate** | tickets with reopen_count >= 1 / tickets | 10.5% team; 7.1% excluding Karan B | at or below 7.1% |
| **Guardrail: CSAT with response rate** | average csat_score and share of tickets rated | 3.70, 45% | not below 3.70 |
| **Guardrail: escalated time to close** | median hours, closed escalated tickets | 86.8h | towards 65h (the median for real fixes, the floor once bounces are gone) |

**Why not raw open count:** it falls if tickets are closed early. The reopen and CSAT guardrails make that visible, and the headline counts reopened tickets as open. **Measured weekly** in the Overview tab from the same CSV logic.

## 5. The v0: Support Lead Triage Console (`app.py`)

**Why Meera:** she owns L1 and the engineering handoff, can enforce a checklist on day one, coaches agents, and meets Sandeep. One tool covers both sides of the problem.

- **Overview:** open tickets, bounce counts, created vs closed per week, daily open backlog, month table, priority yardsticks, category growth vs escalation rate. Each chart has a "so what" line computed from the data.
- **Act now:** all 48 open tickets ranked by score = priority weight (P1=4 ... P4=1) x age in days x 1.5 if waiting on engineering x 1.5 if reopened. Filters by agent, client, category, priority, status; CSV export. Pick a ticket, tick the checklist (client and ID, trip/roster ID, exact time, screenshot or error, tried to reproduce, checked for duplicates) and copy a ready-made escalation or follow-up packet that states what is still missing. The checklist is a proposal to validate with Sandeep.
- **Escalation quality:** engineering's verdicts, handoff penalty, and per-category issue patterns with sample sizes.
- **Agents:** speed vs reopen rate vs CSAT for coaching, not blame.
- **What-if:** slider for the share of bounced tickets solved at L1 instead. Fixed seed (42), method shown in the app. At 50%: 86 tickets, about 10,400 customer-waiting hours, 30 Sep open count 48 to 42. A scenario, not a forecast.

**Run locally:**
```
pip install -r requirements.txt
python -m streamlit run app.py
```
Files: `app.py`, `requirements.txt`, `DOCS.md`, `data/` (both CSVs), `.streamlit/config.toml` (colour theme only: Cream #F3EEE3, Ink #111111, Burnt Orange #D9541E).
**Deployed link:** [paste Streamlit Community Cloud link here]

## 6. Deliberately left out of v0

- Live ticket system integration or login: out of scope for a data-driven v0.
- A chatbot or auto-deflection: a wrong answer on a live commute problem costs more than it saves.
- Hiring: it would feed more incomplete tickets into the same loop.
- Forecasting: the what-if is a sensitivity check; I have no basis for a prediction.

## 7. Four-week plan

| Week | Do | Outcome to check |
|---|---|---|
| 1 | Meera works the Act now list daily, starting with P1/P2 tickets waiting on engineering. Agents attach the checklist fields to every escalation. | No new "insufficient info" returns; oldest P1/P2 unblocked |
| 2 | Coaching using the Agents tab: confirm fix with client before closing (Karan B), run the checklist before escalating (Rahul T). | Karan B reopen rate falling towards peers; Rahul T escalation rate falling |
| 3 | Build a known-issues list with Sandeep, Report export duplicates first (30 of 56). | Duplicate and how-to escalations falling |
| 4 | Weekly Meera and Sandeep review of bounced and stalled tickets; review the metrics with Ritika. | Bounce rate under 10%; backlog at most 30 with reopen rate not rising |

**Not doing:** hiring first, a chatbot, rewriting engineering systems, or chasing the open count alone.

## 8. Risks and limits

- CSAT is missing for 55% of tickets; check any sentiment gain with client conversations.
- Resolution medians exclude still-open tickets and so look better than reality; the Act now ranking by age counters this.
- The data has no engineering timestamps, so I cannot split "waiting in engineering" from "being worked". I would ask for them first.
- A checklist can slow genuine P1 outages; P1 incidents should keep a direct route to engineering.
- Patterns in the data show association, not proof of cause; the 4-week plan doubles as the test.