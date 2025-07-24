"""
graph_simulate.py – Day-4
• samples parameter nodes
• applies risk edges in priority order
• evaluates expression / result nodes with SafeEvaluator
• discards iterations that raise math errors (NaN)
• returns P5, P50, P95, mean + count of discarded iterations
"""

from __future__ import annotations
from typing import Dict, Any

import numpy as np
from .expression_eval import SafeEvaluator, ExpressionEvaluationError
from .graph_utils import topological_sort  # helper added below
from .graph_utils import RESULT_KEYS

# ---------- RNG helper (unchanged) ----------
_rng: np.random.Generator | None = None
def _get_rng(seed: int | None) -> np.random.Generator:
    global _rng
    if _rng is None or seed is not None:
        _rng = np.random.default_rng(seed)
    return _rng

# --- Distribution sampling --------------------------------
def sample_distribution(dist: Dict[str, Any],
                        size: int,
                        rng: np.random.Generator) -> np.ndarray:
    dtype = float
    d_type = dist["type"].lower()
    p = dist["parameters"]

    if d_type == "constant":
        return np.full(size, p["value"], dtype=dtype)
    if d_type == "normal":
        return rng.normal(p["mean"], p["stddev"], size=size)
    if d_type == "uniform":
        return rng.uniform(p["lower"], p["upper"], size=size)
    if d_type == "triangular":
        return rng.triangular(p["min"], p["mode"], p["max"], size=size)
    if d_type == "discrete":
        vals = np.array(p["values"])
        idx = rng.integers(0, len(vals), size=size)
        return vals[idx].astype(dtype)
    if d_type == "lognormal":
        return rng.lognormal(p["mean"], p["sigma"], size=size)
    if d_type == "bernoulli":
        return (rng.random(size) < p["p"]).astype(dtype)
    raise ValueError(f"Unsupported distribution: {d_type}")


# ---------- core driver ----------
def simulate_graph(scenario: Dict[str, Any],
                   iterations: int = 10_000,
                   seed: int | None = None) -> Dict[str, Any]:
    rng = _get_rng(seed)

    nodes = {n["id"]: n for n in scenario["nodes"]}
    edges = sorted(scenario["edges"],
                   key=lambda e: e.get("priority", 0))

    # Build evaluation order for expressions/results
    expr_order = topological_sort(nodes)

    # Pre-allocate samples dict
    samples = {nid: np.empty(iterations) for nid in nodes if nodes[nid].get("is_result")}

    discarded = 0

    # ------------ Monte-Carlo loop ------------
    for idx in range(iterations):
        values: Dict[str, Any] = {}

        # 1. sample parameter nodes
        for n in nodes.values():
            if n["type"] == "parameter":
                values[n["id"]] = sample_distribution(n["distribution"], 1, rng)[0]

        # 2. apply risk edges in priority order
        for e in edges:
            if rng.random() > e["probability"]:
                continue  # edge did not fire
            target = e["target"]
            impact = sample_distribution(e["distribution"], 1, rng)[0]
            if e["impact_type"] == "absolute":
                values[target] += impact
            else:  # percentage
                values[target] += values[target] * (impact / 100.0)

        # 3. evaluate expression / result nodes
        success = True
        try:
            for nid in expr_order:
                n = nodes[nid]
                evaluator = SafeEvaluator(values)
                values[nid] = evaluator.evaluate(n["formula"])
        except ExpressionEvaluationError:
            success = False

        if not success or any(np.isnan(v).any() for v in values.values()):
            discarded += 1
            continue

        # 4. store result samples
        for res_id in samples:
            samples[res_id][idx] = values[res_id]

    effective_n = iterations - discarded

    results = {}
    for nid, arr in samples.items():
        valid = arr[:effective_n]  # ignore unfilled / discarded tail
        results[nid] = {
            "p5": float(np.percentile(valid, 5)),
            "p50": float(np.percentile(valid, 50)),
            "p95": float(np.percentile(valid, 95)),
            "mean": float(valid.mean())
        }

    return {
        "results": results,
        "metadata": {
            "iterations": iterations,
            "discarded": discarded,
            "seed": seed
        }
    }
