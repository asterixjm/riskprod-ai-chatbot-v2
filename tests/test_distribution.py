import numpy as np
from riskportalai.graph_simulate import sample_distribution, _get_rng

rng = _get_rng(42)


def test_constant():
    dist = {"type": "constant", "parameters": {"value": 7}}
    arr = sample_distribution(dist, 5, rng)
    assert (arr == 7).all()


def test_normal_shape():
    dist = {"type": "normal", "parameters": {"mean": 0, "stddev": 1}}
    arr = sample_distribution(dist, 1_000, rng)
    assert abs(arr.mean()) < 0.1


def test_uniform_bounds():
    dist = {"type": "uniform", "parameters": {"lower": 10, "upper": 12}}
    arr = sample_distribution(dist, 500, rng)
    assert arr.min() >= 10 and arr.max() <= 12


def test_triangular_mode():
    dist = {"type": "triangular", "parameters": {"min": 0, "mode": 5, "max": 10}}
    arr = sample_distribution(dist, 1_000, rng)
    assert 4 <= arr.mean() <= 6


def test_discrete_values():
    dist = {"type": "discrete", "parameters": {"values": [1, 2, 3]}}
    arr = sample_distribution(dist, 100, rng)
    assert set(arr).issubset({1, 2, 3})


def test_lognormal_positive():
    dist = {"type": "lognormal", "parameters": {"mean": 0, "sigma": 0.5}}
    arr = sample_distribution(dist, 100, rng)
    assert (arr > 0).all()


def test_bernoulli_mean():
    dist = {"type": "bernoulli", "parameters": {"p": 0.3}}
    arr = sample_distribution(dist, 10_000, rng)
    assert 0.28 < arr.mean() < 0.32
