"""
expression_eval.py
Safe evaluation of arithmetic + comparison expressions for graph nodes.
"""

from __future__ import annotations
import ast
import operator
from typing import Any, Dict

import numpy as np

# --------------------------------------------------------------------------- #
# Allowed operators & helper functions
# --------------------------------------------------------------------------- #
_SAFE_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod
}
_SAFE_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg
}
_SAFE_COMP_OPS = {
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne
}
_SAFE_FUNCS = {
    "abs": abs,
    "min": np.minimum,
    "max": np.maximum,
    "round": np.round,
    "floor": np.floor,
    "ceil": np.ceil,
    "log": np.log,
    "exp": np.exp,
    "where": np.where
}


class ExpressionEvaluationError(Exception):
    """Raised for unsafe or invalid expression."""


class SafeEvaluator:
    """
    Evaluate an arithmetic / comparison expression using only whitelisted
    operators and NumPy-friendly functions.
    """

    def __init__(self, variables: Dict[str, Any]):
        self.vars = variables

    # ---------- public ---------- #
    def evaluate(self, expr: str) -> Any:
        try:
            tree = ast.parse(expr, mode="eval")
            return self._eval_node(tree.body)
        except ExpressionEvaluationError:
            raise
        except Exception as exc:  # pragma: no cover
            raise ExpressionEvaluationError(str(exc)) from exc

    # ---------- private recursive ---------- #
    def _eval_node(self, node: ast.AST) -> Any:
        # literals
        if isinstance(node, ast.Constant):
            return node.value

        # variables
        if isinstance(node, ast.Name):
            if node.id not in self.vars:
                raise ExpressionEvaluationError(f"Unknown variable '{node.id}'")
            return self.vars[node.id]

        # binary operators
        if isinstance(node, ast.BinOp):
            op = _SAFE_BIN_OPS.get(type(node.op))
            if op is None:
                raise ExpressionEvaluationError("Operator not allowed")
            return op(self._eval_node(node.left),
                      self._eval_node(node.right))

        # unary operators
        if isinstance(node, ast.UnaryOp):
            op = _SAFE_UNARY_OPS.get(type(node.op))
            if op is None:
                raise ExpressionEvaluationError("Unary op not allowed")
            return op(self._eval_node(node.operand))

        # comparisons (x > y, a == b, a < b < c)
        if isinstance(node, ast.Compare):
            left_val = self._eval_node(node.left)
            results = []
            for op_node, comparator in zip(node.ops, node.comparators):
                op_func = _SAFE_COMP_OPS.get(type(op_node))
                if op_func is None:
                    raise ExpressionEvaluationError("Comparison op not allowed")
                right_val = self._eval_node(comparator)
                results.append(op_func(left_val, right_val))
                left_val = right_val  # support chained comparisons
            return np.logical_and.reduce(results)

        # function calls
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in _SAFE_FUNCS:
                raise ExpressionEvaluationError(f"Function '{func_name}' not allowed")
            args = [self._eval_node(arg) for arg in node.args]
            return _SAFE_FUNCS[func_name](*args)

        raise ExpressionEvaluationError(f"Unsupported syntax: {ast.dump(node)}")
