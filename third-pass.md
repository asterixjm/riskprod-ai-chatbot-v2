Below is a **plain-English “executive + developer” overview** of the proposed overhaul. It keeps the existing HTML/CSS look-and-feel but replaces everything under the hood with a **graph-based Monte Carlo engine** that handles multiple risks per parameter (Mr Whimsy’s days-lost example).

---

## 1 . What Exactly Are We Building?

| Layer                 | Old App                                                              | New Graph-Based App                                                                                                                                                |
| --------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **UI**                | Chat interface + D3 diagram (keep)                                   | *Unchanged* – same chat, same graph visual                                                                                                                         |
| **Model Schema**      | `parameters + assessments + expressions` (one-risk-per-parameter)    | `nodes + edges` where:<br>• **nodes** = quantities (parameters, expressions, KPI)<br>• **edges** = influences/risks (probability + impact)                         |
| **Simulation Engine** | Samples each parameter once → applies single risk → runs expressions | For **every iteration**:<br>1 . sample all parameter nodes<br>2 . evaluate each risk-edge (may or may not fire)<br>3 . recalc expression nodes in dependency order |
| **AI Prompt**         | Explains parameter/assessment schema                                 | Explains node/edge schema (with examples)                                                                                                                          |
| **Backend Routes**    | `/api/simulate`                                                      | `/api/graph_simulate` (new)                                                                                                                                        |

---

## 2 . How Does Mr Whimsy Fit?

### Graph view

```
orange nodes  = season_duration, days_lost, daily_sales, unit_price
green node    = available_days  (season_duration – days_lost)
pink node     = total_revenue   (daily_sales × available_days × unit_price)
grey arrows   = ordinary maths dependencies
red arrows    = risks impacting days_lost / daily_sales / unit_price
```

**Risks on `days_lost`**

| Risk arrow        | Probability | Impact distribution (days) | Type     |
| ----------------- | ----------- | -------------------------- | -------- |
| weather           | 1.0         | triangular 0–2–7           | absolute |
| council crackdown | 0.2         | triangular 0–5–14          | absolute |
| equipment failure | 0.1         | triangular 2–4–14          | absolute |
| theft / damage    | 0.05        | triangular 7–14–21         | absolute |

**Risks on % change**

| Risk arrow    | Target       | Probability | Impact distribution   | Type       |
| ------------- | ------------ | ----------- | --------------------- | ---------- |
| demand\_shift | daily\_sales | 1.0         | uniform -50 % … +25 % | percentage |
| price\_comp   | unit\_price  | 1.0         | uniform -25 % … +10 % | percentage |

During each Monte-Carlo run (say 10 000 iterations):

1. Sample base values.
2. For every red arrow, decide “does it fire?” (Bernoulli).
3. If fired, sample impact and add (absolute) or scale (percentage).
4. Recalculate `available_days`, then `total_revenue`.
5. Save `total_revenue` for the histogram.

After 10 000 passes you get P5 / Median / P95 etc. exactly as before—just correctly layered.

---

## 3 . Why Is This Better?

* **Multiple risks per parameter** = natural; just add more arrows.
* **Clear causal picture** for non-technical stakeholders (graph is self-documenting).
* **Easier AI generation** – Claude only fills nodes and arrows.
* **Extensible** – timelines, conditional probabilities, feedback loops can be added later without schema rewrite.

---

## 4 . Minimal Technical Roadmap

| Phase                    | Tasks                                                                                                    | Effort (dev-days) |
| ------------------------ | -------------------------------------------------------------------------------------------------------- | ----------------- |
| **1. Engine prototype**  | • Add `graph_simulate()` in Python (≈150 LOC)<br>• Unit-test discrete + percentage risks                 | 2 – 3             |
| **2. Schema & Prompt**   | • Draft JSON schema (nodes/edges)<br>• Update Claude system prompt examples                              | 1                 |
| **3. API plumbing**      | • New POST `/api/graph_simulate` route<br>• Keep old route for backward-compat                           | 0.5               |
| **4. Front-end hook-up** | • Detect `type:\"graph\"` response → call new endpoint<br>• Feed returned samples to existing chart code | 1                 |
| **5. Migration / demo**  | • Convert Mr Whimsy scenario to new schema<br>• Show results + graph to stakeholders                     | 0.5               |

**Total** ≈ 5 – 6 developer-days for a working pilot; no design/UX change.

---

## 5 . Explaining to the Boss

> > *“We’re keeping the same chat front-end you like, but the engine underneath now uses a simple cause-and-effect graph. Every box is a number we care about, every arrow is a risk. The computer runs that graph thousands of times, so instead of guessing averages we see a full probability curve—including when several bad things happen at once.”*

---

## 6 . Next Actions

1. **Approve** the graph schema (table above).
2. **Green-light** engine prototype.
3. **Schedule** the five-day sprint.

I can supply the exact JSON schema, updated Claude prompt, and starter Python code as soon as you say “go”.
