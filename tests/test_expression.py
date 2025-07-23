import numpy as np
import pytest
from riskportalai.expression_eval import SafeEvaluator, ExpressionEvaluationError

def test_simple_math():
    ev = SafeEvaluator({"a": 2, "b": 3})
    assert ev.evaluate("a + b * 2") == 8

def test_numpy_array_support():
    ev = SafeEvaluator({"x": np.array([1, 2, 3])})
    out = ev.evaluate("where(x > 1, x * 10, x)")
    assert (out == np.array([1, 20, 30])).all()

def test_round_func():
    ev = SafeEvaluator({"v": 2.7})
    assert ev.evaluate("round(v)") == 3

def test_unknown_var():
    ev = SafeEvaluator({})
    with pytest.raises(ExpressionEvaluationError):
        ev.evaluate("foo + 1")

def test_disallowed_func():
    ev = SafeEvaluator({"x": 1})
    with pytest.raises(ExpressionEvaluationError):
        ev.evaluate("eval('2+2')")
