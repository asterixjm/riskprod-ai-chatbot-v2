"""
graph_utils.py
• topological sort for expression nodes
"""

from typing import Dict, List, Set

RESULT_KEYS = ("p5", "p50", "p95", "mean")

def topological_sort(nodes: Dict[str, dict]) -> List[str]:
    """Return evaluation order for expression/result nodes."""
    expr_nodes = [n for n in nodes.values() if n["type"] in ("expression", "result")]
    deps: Dict[str, Set[str]] = {n["id"]: _find_deps(n["formula"], nodes) for n in expr_nodes}
    order, temp = [], set()

    def visit(nid: str):
        if nid in order:
            return
        if nid in temp:
            raise ValueError("Cycle detected in expressions")
        temp.add(nid)
        for d in deps[nid]:
            if d in deps:  # only visit other expression nodes
                visit(d)
        temp.remove(nid)
        order.append(nid)

    for n in expr_nodes:
        visit(n["id"])
    return order

def _find_deps(formula: str, nodes: Dict[str, dict]) -> Set[str]:
    return {nid for nid in nodes if nid in formula}
