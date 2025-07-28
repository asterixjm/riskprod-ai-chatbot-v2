Awesome—here’s how we’ll kick off the green-field build using **repo `asterixjm/riskprod-ai-chatbot-v2`** and package name **`riskportal-ai`**.

---

## 1 Repo setup (today)

1. I’ll fork / clone the repo and create a new branch `feature/graph-engine`.
2. Commit **project skeleton**

   * `riskportal_ai/` package root (FastAPI app)
   * `graph_simulate.py` placeholder
   * `schema.graph.json` (JSON-Schema file)
   * `tests/` folder with `pytest.ini`.

> *You can add me as a collaborator or grant push rights to a branch; just let me know.*

---

## 2 Mr Whimsy scenario (graph JSON)

If you don’t already have it, I’ll craft the canonical test file (`examples/mr_whimsy.json`) in the new schema:

```jsonc
{
  "schemaVersion": "1.0",
  "metadata": { "title": "Mr Whimsy Summer Sales" },
  "nodes": [
    { "id": "season_duration", "type": "parameter",
      "distribution": { "type": "constant", "parameters": { "value": 100 } } },

    { "id": "days_lost", "type": "parameter",
      "distribution": { "type": "constant", "parameters": { "value": 0 } } },

    { "id": "daily_sales", "type": "parameter",
      "distribution": { "type": "normal",
        "parameters": { "mean": 100, "stddev": 15 } } },

    { "id": "unit_price", "type": "parameter",
      "distribution": { "type": "normal",
        "parameters": { "mean": 3, "stddev": 0.25 } } },

    { "id": "available_days", "type": "expression",
      "formula": "season_duration - days_lost" },

    { "id": "total_revenue", "type": "expression",
      "formula": "daily_sales * available_days * unit_price",
      "is_result": true }
  ],
  "edges": [
    { "id": "weather_risk", "target": "days_lost",
      "probability": 1.0, "impact_type": "absolute", "priority": 0,
      "distribution": { "type": "triangular",
        "parameters": { "min": 0, "mode": 2, "max": 7 } } },

    { "id": "council_crackdown", "target": "days_lost",
      "probability": 0.2, "impact_type": "absolute", "priority": 0,
      "distribution": { "type": "triangular",
        "parameters": { "min": 0, "mode": 5, "max": 14 } } },

    { "id": "equipment_failure", "target": "days_lost",
      "probability": 0.1, "impact_type": "absolute", "priority": 0,
      "distribution": { "type": "triangular",
        "parameters": { "min": 2, "mode": 4, "max": 14 } } },

    { "id": "van_theft", "target": "days_lost",
      "probability": 0.05, "impact_type": "absolute", "priority": 0,
      "distribution": { "type": "triangular",
        "parameters": { "min": 7, "mode": 14, "max": 21 } } },

    { "id": "demand_shift", "target": "daily_sales",
      "probability": 1.0, "impact_type": "percentage", "priority": 10,
      "distribution": { "type": "uniform",
        "parameters": { "lower": -50, "upper": 25 } } },

    { "id": "price_comp", "target": "unit_price",
      "probability": 1.0, "impact_type": "percentage", "priority": 10,
      "distribution": { "type": "uniform",
        "parameters": { "lower": -25, "upper": 10 } } }
  ]
}
```

This will be our regression-test anchor.

---

## 3 Week-1 sprint deliverables (unchanged)

| Day | Commit tag                                        | You can test via                         |
| --- | ------------------------------------------------- | ---------------------------------------- |
| D1  | Skeleton + schema + README                        | `pytest` shows placeholder pass          |
| D2  | Distribution samplers incl. lognormal + bernoulli | `tests/test_distribution.py`             |
| D3  | Secure AST evaluator (whitelist)                  | `tests/test_expression.py`               |
| D4  | Full iteration loop, priority edges, NaN handling | `tests/test_mr_whimsy.py` (<2 s runtime) |
| D5  | Claude prompt v1 + `/chat` stub                   | sample curl script                       |

Package is **`riskportal_ai`** in `pyproject.toml`.

---

### Action items for you

1. **Add me as contributor / share push token** for the repo branch.
2. Confirm the Mr Whimsy JSON above (or send tweaks).
3. Anything else before coding starts? Let me know today.

Once I have repo access I’ll push the Day-1 skeleton and tag you.
