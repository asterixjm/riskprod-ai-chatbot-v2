"""
graph_simulate.py
Day-1 stub: holds the public `simulate_graph()` signature.
Implementation will be added in subsequent commits.
"""

from typing import Dict, Any

def simulate_graph(scenario: Dict[str, Any], iterations: int = 10_000, seed: int | None = None) -> Dict[str, Any]:
    """
    Placeholder Monte-Carlo driver.

    Parameters
    ----------
    scenario : dict
        Graph-schema JSON from the client.
    iterations : int
        Number of Monte-Carlo iterations (default 10 000).
    seed : int | None
        RNG seed for reproducibility.

    Returns
    -------
    dict
        Dummy payload until engine is coded.
    """
    return {
        "results": {},
        "metadata": {
            "iterations": iterations,
            "seed": seed,
            "engine": "stub"
        }
    }
