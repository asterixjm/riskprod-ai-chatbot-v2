"""
graph_simulate.py
Day-2: distribution samplers + RNG helper.
Simulation loop remains stubbed (Day-3).

Supported distributions
  constant • normal • uniform • triangular • discrete • lognormal • bernoulli
"""

from typing import Dict, Any
import numpy as np

# Corrected relative import
from .expression_eval import SafeEvaluator, ExpressionEvaluationError


# --------------------------------------------------------------------------- #
# RNG helper (single global generator, seedable from simulate_graph)
# --------------------------------------------------------------------------- #
_rng: np.random.Generator | None = None


def _get_rng(seed: int | None) -> np.random.Generator:
    global _rng
    if _rng is None or seed is not None:
        _rng = np.random.default_rng(seed)
    return _rng


# --------------------------------------------------------------------------- #
# Distribution sampling
# --------------------------------------------------------------------------- #
def sample_distribution(dist: Dict[str, Any],
                        size: int,
                        rng: np.random.Generator) -> np.ndarray:
    """Return NumPy array of samples for a single distribution dict."""
    dtype = float  # default output dtype
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
        # values: list[int|float]  – choose with equal probability
        values = np.array(p["values"])
        idx = rng.integers(0, len(values), size=size)
        return values[idx].astype(dtype)

    if d_type == "lognormal":
        # parameters are mean & sigma in log-space (same as NumPy)
        return rng.lognormal(p["mean"], p["sigma"], size=size)

    if d_type == "bernoulli":
        samples = (rng.random(size) < p["p"]).astype(dtype)
        return samples

    raise ValueError(f"Unsupported distribution type: {d_type!r}")


# --------------------------------------------------------------------------- #
# Public stub – simulation loop arrives Day-3/4
# --------------------------------------------------------------------------- #
def simulate_graph(scenario: Dict[str, Any],
                   iterations: int = 10_000,
                   seed: int | None = None) -> Dict[str, Any]:
    """Stub: returns metadata only until Day-3."""
    _get_rng(seed)  # ensure deterministic even in stub
    return {
        "results": {},
        "metadata": {
            "iterations": iterations,
            "seed": seed,
            "engine": "stub-sampler-ready"
        }
    }
