import json, pathlib
from riskportalai.graph_simulate import simulate_graph

SCENARIO = pathlib.Path(__file__).with_suffix(".json").read_text()
whimsy = json.loads(SCENARIO)

def test_whimsy_runs():
    res = simulate_graph(whimsy, iterations=20, seed=123)
    assert res["metadata"]["discarded"] == 0
    rev = res["results"]["total_revenue"]["mean"]
    assert rev > 0
