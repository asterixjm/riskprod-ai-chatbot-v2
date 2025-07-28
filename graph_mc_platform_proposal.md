# Graph‑Based Monte‑Carlo Simulation Platform

*Draft v0.2 – expanded for executive & technical circulation*

---

## 1 Vision & Concept

**Goal**   Deliver a conversational, AI‑assisted risk‑analysis workspace where non‑technical users type a scenario in plain language and instantly receive a fully quantified picture of upside and downside.  Under the hood the engine is a **directed risk graph**: every business quantity (cash flow, throughput, days lost) is a **node**; every uncertainty or causal rule is an **edge**.  The graph is executed thousands of times to reveal probability bands, stress points, and risk contributions.

**Why Now?**

- Legacy *parameter + assessment* model cannot layer several risks on the same variable – analysts patch with spreadsheets and lose auditability.
- Board‑level pressure for transparent “explainable AI” outputs – graph diagrams communicate logic at a glance.
- Large‑language models (Claude) natively produce structured JSON via tool‑calling – perfect for filling a node/edge blueprint.
- Cloud costs for Monte‑Carlo (NumPy on Cloud Run) are now trivial; tokens, not compute, dominate marginal cost.

**Strategic Fit** The product sits between spreadsheet Monte‑Carlo and heavyweight GRC suites: lightweight, chat‑first, visually compelling.

**Success Metrics**

- **Accuracy**  Pilot (Mr Whimsy) median revenue within ±1 % of analytic solution.
- **Speed**  P95 latency < 2 s for a 1 000‑node, 10 k‑iteration run.
- **Adoption**  ≥ 5 paying clients in first 12 months; ≥ 60 % monthly active power‑user rate.

---

## 2 Business Proposal

| Item             | Detail                                                                                                                                                   |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Problem**      | Current tool cannot model multiple risks per parameter; analysts maintain 4‑5 disconnected artefacts (chat log, JSON, spreadsheet results, diagram).     |
| **Opportunity**  | First SaaS that merges natural‑language modelling, interactive graph, and rigorous Monte‑Carlo in one screen. Upsell premium support & white‑labelling.  |
| **Benefits**     | • 40 % analyst modelling time saved  • 2× client workshop engagement (visual storytelling)  • New €20 k p.a. licence tier + €5 k onboarding per customer |
| **Costs (est.)** | Dev €45 k, UX €10 k, Cloud €5 k (year 1) → total €60 k.                                                                                                  |
| **ROI**          | Break‑even after **three** enterprise clients; IRR ≈ 68 % over 3 years.                                                                                  |
| **Risks**        | Scope creep; numerical validation; Claude quota overspend; client data‑privacy fears.                                                                    |
| **Mitigations**  | Fixed MVP schema, regression test pack, token budget guardrails, optional on‑premise runner.                                                             |

**Market Comparison (qualitative)**

| Vendor                | Natural‑language input | Visual graph  | Multi‑risk layering | Price band |   |
| --------------------- | ---------------------- | ------------- | ------------------- | ---------- | - |
| *Legacy spreadsheets* | ✗                      | ✗             | limited             | N/A        |   |
| Crystal Ball / @Risk  | ✗ macro‑based          | Formula tree  | manual              | \$         |   |
| Big‑3 GRC suites      | Form‑based             | Process maps  | ✔︎                  | \$\$\$\$   |   |
| **Proposed**          | ✔︎ chat                | ✔︎ auto‑graph | ✔︎ native           | \$\$       |   |

---

## 3 Scope & Objectives

### 3.1 In‑Scope (MVP)

- **Conversational modelling** via Claude tool‑calls producing `graph.json`.
- **Graph review & edit sidebar** so users can inspect and tweak nodes/edges before running the simulation.
- **Monte‑Carlo graph engine** supporting five base distributions (constant, normal, uniform, triangular, discrete) and two impact types (absolute, percentage).
- **Result analytics**  P5/Mean/Median/P95, sample histogram, and risk‑contribution tornado chart (stretch goal).
- **Visual layers**  Existing D3 component reused; colour‑code node types; hover tooltips show distribution parameters.
- **Export**  CSV of raw samples + PNG of graph for reports.
- **Security & audit**  Every run stamps scenario JSON, seed, timestamp.

### 3.2 Out of Scope (Phase 1) Out of Scope (Phase 1)

- **Multi‑scenario batch comparisons & optimisation** (deferred—see Phase 2 roadmap).
- Mobile‑first UI redesign.

## 3.3 Phase‑2 Roadmap (Planned, **not** in MVP)

| Feature                             | What it delivers                                                     | Est. dev‑days | Notes                                     |
| ----------------------------------- | -------------------------------------------------------------------- | ------------- | ----------------------------------------- |
| **Multi‑scenario batch comparison** | Run 5–20 scenarios in one click, side‑by‑side stats & plots.         | 8–10          | Engine orchestration + comparison UI.     |
| **Sensitivity / Tornado analysis**  | One‑at‑a‑time perturbation; bar chart showing top drivers of spread. | 6–8           | Advanced Sobol method + 5 days.           |
| **Basic optimisation**              | Grid / random search to maximise KPI under constraints.              | 12–15         | Later upgrade to Bayesian adds \~10 days. |

> Phase‑2 work will commence only after MVP is validated in production.

### Permanently Out of Scope

**MCMC (Markov‑Chain Monte‑Carlo)** is intentionally excluded from both MVP and Phase 2. Switching to MCMC would require a chain‑state engine, convergence diagnostics, and would break our sub‑2‑second speed target. Forward Monte‑Carlo has been deemed sufficient by stakeholders.

- Time‑stepped event simulation (Markov chains).
- Multi‑scenario batch comparisons & optimisation.
- Mobile‑first UI redesign.

---

## 4 Functional Requirements

| Ref      | Requirement                                                     | Rationale                             |
| -------- | --------------------------------------------------------------- | ------------------------------------- |
| F‑1      | User types scenario; Claude returns valid graph JSON.           | Natural‑language ease.                |
| F‑2      | System renders graph with nodes, maths edges, risk edges.       | Explainability.                       |
| F‑3      | ≥10 k iterations, ≤2 s, 1 000 nodes, 50 edges/node worst‑case.  | Performance SLA.                      |
| F‑4      | Outputs stats & histogram; user can download CSV.               | Analyst workflow.                     |
| F‑5      | Parameter can receive unlimited absolute & % risk edges.        | Core capability.                      |
| F‑6      | Risk edges fire independently via Bernoulli sampling.           | Statistical correctness.              |
| F‑7      | Chat history stores scenario + seed for rerun.                  | Audit trail.                          |
| F‑8      | Front‑end warns if Claude proposes unsupported distribution.    | Data quality.                         |
| F‑9      | Health‑check endpoint returns build SHA + Claude quota.         | DevOps.                               |
| **F‑10** | Review & Edit sidebar lets user adjust graph before simulation. | Prevents AI mis‑interpretation loops. |

---

## 5 Non‑Functional Requirements Requirements

- **Performance**  ≤200 ms per 1 000 iterations on 16‑core Cloud Run; auto‑scales to 100 k iterations under 5 s.
- **Scalability**  Horizontal‑scale graph jobs; memory O(nodes + edges).
- **Availability**  99.5 % (SLA) with two regional Cloud Run revisions.
- **Explainability**  Store risk‑edge sample per iteration → drill‑down.
- **Security**  SOC 2 controls; encrypt Claude prompts; erase prompts after 30 d.
- **Cost Control**  Per‑organisation Claude token cap; fail‑fast if exceeded.

---

## 6 Mid‑Level Technical Specification

### 6.1 High‑Level Architecture

```
Browser
  │
  ├─ /chat    → FastAPI endpoint → Claude API (tool‑call)
  │
  ├─ /graph_simulate → Python engine (NumPy + AST evaluator)
  │                      │
  │                      ├─ Topological sort
  │                      ├─ Node sampler
  │                      └─ Edge applicator (absolute & %)
  │
  └─ /results → returns statistics, 100 samples, seed, metadata
```

### 6.2 Key Code Modules

| Module                  | Core Logic                           | Unit‑Test Focus                            |
| ----------------------- | ------------------------------------ | ------------------------------------------ |
| **graph\_simulate.py**  | Iteration loop; memoised node values | Stress with 1 M iterations; variance check |
| **edge\_sampler.py**    | Bernoulli trigger + impact calc      | Boundary probs 0 & 1; % and abs combo      |
| **expression\_eval.py** | Secure AST, depth guard              | Injection attempts; nested maths           |
| **schema.graph.json**   | JSON schema validation               | Invalid field rejection                    |
| **prompt\_graph.md**    | System examples & rules              | Claude regression test via stub            |

### 6.3 Data Model

```jsonc
node  = {
  id, name, type,          // required
  distribution?,           // for parameter nodes
  formula?,                // for expression nodes
  is_result?               // marks KPI nodes
}
edge  = {
  id, target, probability, impact_type, distribution
}
```

---

## 7 Implementation Plan & Timeline

| Week | Deliverable                           | Exit Criteria                                            |
| ---- | ------------------------------------- | -------------------------------------------------------- |
| 1    | Schema freeze + prompt v1             | Claude returns valid JSON for three canned stories       |
| 2    | Engine core (node sampling, AST eval) | Pass unit tests; <150 ms per 10 k iterations (100 nodes) |
| 3    | Risk‑edge logic + discrete support    | Mr Whimsy scenario matches analytic mean ±1 %            |
| 4    | API wiring + front‑end call path      | Chat returns histogram & graph without errors            |
| 5    | Cloud deploy + load test              | 500 concurrent sims, P95 latency <3 s                    |
| 6    | Pilot demo, stakeholder sign‑off      | Go/No‑go for production hardening                        |

---

## 10 Legacy Constraints & Current Blockers

| Area                                        | Constraint                                                                                | Impact                                       |
| ------------------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------- |
| **Backend design (parameter + assessment)** | One‑risk‑per‑parameter structure baked into validation, engine, and prompt.               | Complex scenarios need hacks → erodes trust. |
| **Expression evaluator**                    | Safe‑AST supports only scalar operations; no native vector functions beyond NumPy ufuncs. | Hard to add time‑series / stateful logic.    |
| **Tech debt**                               | Mixed sync & async FastAPI routes; legacy Pydantic v1/v2 cruft; ad‑hoc logging.           | Slows onboarding; higher bug surface.        |
| **Frontend coupling**                       | Chat flow, histogram draw, and D3 graph are tightly bound in one 450‑line HTML.           | Any UI change risks breaking everything.     |
| **CI / test coverage**                      | Unit tests cover < 40 % of paths; no property‑based tests for distributions.              | Regression risk with every refactor.         |
| **Security model**                          | No per‑organisation API keys; Claude key shared via env‑var.                              | Difficult to multi‑tenant securely.          |
| **Performance knobs**                       | Iteration count hard‑coded; no adaptive sampling.                                         | Either over‑spends compute or under‑samples. |

**Remediation path**

1. Green‑field `graph_simulate` module – do *not* mutate legacy engine.
2. Side‑by‑side routes (`/simulate_legacy`, `/graph_simulate`) – staged cut‑over.
3. Incremental migration of prompt, UI, and tests.

---

## 8 Open Questions / Required Inputs

1. Default iteration budget per project?
2. Distribution wishlist (lognormal, beta, Poisson)?
3. Export formats: XLSX, PDF storyboard? Priority?
4. Authentication: Google ID or SAML?
5. Monthly Claude spend cap (€/org)?
6. How strict should audit log retention be (90 d vs 3 y)?

---

## 11 Proposed JSON Graph Schema (MVP)

Below is the **canonical JSON shape** that Claude will emit and the engine will accept. It is intentionally small enough for analysts to read yet expressive enough for layered risks, including a new `priority` field that defines the order of edge application (lower numbers first; percentages default to 10, absolutes to 0).

```jsonc
{
  "schemaVersion": "1.0",
  "metadata": {
    "title": "<scenario title>",
    "author": "<optional>",
    "created": "2025-07-23T12:00:00Z"
  },
  "nodes": [
    {
      "id": "season_duration",
      "name": "Season Duration",
      "type": "parameter",
      "distribution": {
        "type": "constant",
        "parameters": { "value": 100 }
      }
    },
    {
      "id": "days_lost",
      "type": "parameter",
      "distribution": { "type": "constant", "parameters": { "value": 0 } }
    },
    {
      "id": "available_days",
      "type": "expression",
      "formula": "season_duration - days_lost"
    },
    {
      "id": "total_revenue",
      "type": "expression",
      "formula": "daily_sales * available_days * unit_price",
      "is_result": true
    }
  ],
  "edges": [
    {
      "id": "weather",
      "target": "days_lost",
      "probability": 1.0,
      "impact_type": "absolute",
      "priority": 0,
      "distribution": { "type": "triangular", "parameters": { "min": 0, "mode": 2, "max": 7 } }
    },
    {
      "id": "demand_shift",
      "target": "daily_sales",
      "probability": 1.0,
      "impact_type": "percentage",
      "priority": 10,
      "distribution": { "type": "uniform", "parameters": { "lower": -50, "upper": 25 } }
    }
  ]
}
```

### Field rules

| Field          | Rule                                                                     |
| -------------- | ------------------------------------------------------------------------ |
| `id`           | snake\_case; unique within its array.                                    |
| `type` (node)  | `parameter`, `expression`, or `result` (`is_result` flag).               |
| `distribution` | Required for parameter nodes.                                            |
| `formula`      | Required for expression/result nodes; references existing node ids.      |
| `impact_type`  | `absolute` adds value; `percentage` scales value.                        |
| `probability`  | 0 – 1; Bernoulli draw per iteration.                                     |
| `priority`     | Integer; edges applied ascending. Default 0 (absolute), 10 (percentage). |

> **Execution order rule**   Engine sorts edges by `priority` each iteration, so percentages apply **after** absolute changes unless overridden.

### Validation checklist

1. Every `target` in `edges` exists in `nodes`.
2. Expression formulas reference valid node ids.
3. Expression sub‑graph is acyclic (topological sort passes).
4. At least one `is_result: true` node *or* `results[]` specified.

### Simulation error handling

If a maths error occurs in an iteration (e.g., division by zero, log of negative), that iteration’s value for the affected node becomes `NaN` and is dropped from statistics. The engine logs a count of discarded iterations so users see, e.g., “9 992 / 10 000 iterations successful.”

### MVP AST function whitelist

`+ - * / **`, `abs`, `min`, `max`, `round`, `floor`, `ceil`, `log`, `exp`, and `where(condition, a, b)`.

---

## 12 Example Scenario Mappings Example Scenario Mappings Example Scenario Mappings

Below illustrates how legacy scenario files convert into the new **nodes + edges** schema, confirming the design handles real‑world complexity.

| Legacy example                   | Contents                                                                      | Graph‑schema translation                                                                                                        |
| -------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Benoulli example**             | 2 binary repair risks, uniform commission, summed cost                        | 3 parameter nodes + 2 absolute risk edges → result node `total_cost`.                                                           |
| **ECB Banking Network**          | 14 qualitative drivers + link strengths                                       | Drivers → parameter nodes (constants or Normals); links → percentage edges; KPI node aggregates impact.                         |
| **Wildfi Re – Cedent Behaviour** | Base claim, % inflation, inclusion %, detection probability, chained formulas | Base claim & modifiers → parameter nodes; modifiers → percentage edges; detection node feeds expression; final KPI result node. |
| **Lost Socks model**             | Normal loss rate, quirky % adjustments, rounding                              | Rates → nodes; adjustments → percentage edges; expressions copy; `round()` whitelisted.                                         |
| **Critical AML Failure**         | Lognormal downtime, % mix uncertainties, cost formulas                        | Downtime edge (absolute) + percentage edges; add lognormal sampler; formulas map directly.                                      |

> **Key point:** all five examples fit without changing the core schema—only a lognormal sampler and rounding helpers are added.

---

## 9 Glossary

- **Node**  A scalar variable (parameter, calculated value, KPI).
- **Edge**  A directed influence (formula reference or risk impact).
- **Probability Edge**  Edge that only applies with certain probability.
- **Impact Type**  `absolute` adds/subtracts; `percentage` scales.
- **Monte‑Carlo**  Random resampling to approximate a distribution.
- **Topological Sort**  Ordering of nodes so dependencies are evaluated before dependents.

---

*Prepared by – GPT‑Architect (expanded draft).*  *Internal reviewers: please add comments inline or via chat.*

