"""
expression_eval.py
Day-3: Safe evaluation of arithmetic expressions used by expression nodes.
Whitelist only the MVP math functions.
"""

from __future__ import annotations
import ast
import operator
from typing import Any, Dict

import numpy as np

# --------------------------------------------------------------------------- #
# Allowed operators and helper functions
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

_SAFE_FUNCS = {
    "abs": abs,
    "min": np.minimum,
    "max": np.maximum,
    "round": np.round,
    "floor": np.floor,
    "ceil": np.ceil,
    "log": np.log,
    "exp": np.exp,
    # conditional helper: where(cond, a, b)
    "where": np.where
}


class ExpressionEvaluationError(Exception):
    """Raised for any unsafe or invalid expression."""


class SafeEvaluator:
    """Evaluate arithmetic expressions using only whitelisted tokens."""

    def __init__(self, variables: Dict[str, Any]):
        self.vars = variables  # name → NumPy array or scalar

    # --------------- public API --------------- #
    def evaluate(self, expr: str) -> Any:
        try:
            tree = ast.parse(expr, mode="eval")
            return self._eval_node(tree.body)
        except ExpressionEvaluationError:
            raise
        except Exception as exc:
            raise ExpressionEvaluationError(str(exc)) from exc

    # --------------- private helpers ---------- #
    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id not in self.vars:
                raise ExpressionEvaluationError(f"Unknown variable '{node.id}'")
            return self.vars[node.id]

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in _SAFE_BIN_OPS:
                raise ExpressionEvaluationError("Operator not allowed")
            return _SAFE_BIN_OPS[op_type](self._eval_node(node.left),
                                          self._eval_node(node.right))

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in _SAFE_UNARY_OPS:
                raise ExpressionEvaluationError("Unary operator not allowed")
            return _SAFE_UNARY_OPS[op_type](self._eval_node(node.operand))

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in _SAFE_FUNCS:
                raise ExpressionEvaluationError(f"Function '{func_name}' not allowed")
            args = [self._eval_node(arg) for arg in node.args]
            return _SAFE_FUNCS[func_name](*args)

        raise ExpressionEvaluationError(f"Unsupported syntax: {ast.dump(node)}")
