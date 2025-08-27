# simple_calculator_v3/tests/test_app_v3.py
import pytest
from app import evaluate_expr

@pytest.mark.parametrize("expr, expected", [
    ("2**3", 8.0),
    ("10 % 3", 1.0),
    ("sqrt(9)", 3.0),
    ("max(2, 5)", 5.0),
    ("min(-1, 4)", -1.0),
    ("sqrt(16) + 2**3 % 5", 7.0),  # 4 + (8 % 5=3) = 7
    ("(2 + 3) * 4 - min(5, 3)", 15.0),
    ("-max(2, 3) + 10", 7.0),
])
def test_features(expr, expected):
    assert evaluate_expr(expr) == expected

def test_div_by_zero():
    with pytest.raises(ZeroDivisionError):
        evaluate_expr("1/0")

@pytest.mark.parametrize("expr", [
    "abs(2)",
    "pow(2,3)",
    "x + 1",
    "2 // 3",
])
def test_disallowed(expr):
    with pytest.raises(Exception):
        evaluate_expr(expr)
