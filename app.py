# simple_calculator_v3/app.py
"""Advanced CLI calculator:
- Operators: +, -, *, /, %, ** (exponent), parentheses, unary +/- with precedence
- Functions: sqrt(x), max(a,b), min(a,b)
- Session history commands:
    :history  -> show history
    :save     -> save history to history.txt
    :clear    -> clear history
    :q        -> quit
- One-shot mode: python app.py "sqrt(9) + 2**3 % 5"
"""

import ast
import operator as _op
import sys
import math
from typing import Any, List

_bin_ops = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    ast.Mod: _op.mod,
    ast.Pow: _op.pow,
}
_unary_ops = {
    ast.UAdd: lambda x: x,
    ast.USub: lambda x: -x,
}
_funcs = {
    "sqrt": lambda x: math.sqrt(float(x)),
    "max": lambda a, b: max(float(a), float(b)),
    "min": lambda a, b: min(float(a), float(b)),
}

class SafeEvaluator(ast.NodeVisitor):
    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type not in _bin_ops:
            raise ValueError("Unsupported binary operator")
        if op_type is ast.Div and right == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return _bin_ops[op_type](left, right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type not in _unary_ops:
            raise ValueError("Unsupported unary operator")
        return _unary_ops[op_type](operand)

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function names are allowed")
        name = node.func.id
        if name not in _funcs:
            raise ValueError(f"Unsupported function '{name}'")
        # Disallow keywords, starargs
        if node.keywords:
            raise ValueError("No keyword arguments allowed")
        args = [self.visit(arg) for arg in node.args]
        # Arity checks
        if name == "sqrt" and len(args) != 1:
            raise ValueError("sqrt() takes exactly 1 argument")
        if name in ("max", "min") and len(args) != 2:
            raise ValueError(f"{name}() takes exactly 2 arguments")
        return _funcs[name](*args)

    def visit_Num(self, node: ast.Num) -> Any:  # for Python <3.8
        return float(node.n)

    def visit_Constant(self, node: ast.Constant) -> Any:  # Python 3.8+
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Only numeric literals are allowed")

    def visit_Name(self, node: ast.Name) -> Any:
        # Only allow function names in Call nodes; bare names are forbidden
        raise ValueError("Bare names are not allowed")

    # Disallow everything else
    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression: {type(node).__name__}")

def evaluate_expr(expr: str) -> float:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError("Invalid expression syntax") from e
    evaluator = SafeEvaluator()
    return evaluator.visit(tree)

def main():
    history: List[str] = []

    if len(sys.argv) > 1:
        expr = sys.argv[1]
        try:
            res = evaluate_expr(expr)
            print(f"= {res}")
            return
        except Exception as e:
            print("Error:", e)
            return

    print("Advanced Calculator (':q' quit, ':history', ':save', ':clear')")
    while True:
        raw = input(">>> ").strip()
        if raw in ("q", ":q", "quit", "exit"):
            print("Bye!")
            break
        if raw in (":history", ":h"):
            print("\n".join(history) if history else "(empty)")
            continue
        if raw == ":clear":
            history.clear()
            print("History cleared")
            continue
        if raw == ":save":
            with open("history.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(history))
            print("Saved to history.txt")
            continue

        try:
            res = evaluate_expr(raw)
            line = f"{raw} = {res}"
            history.append(line)
            print("= {}".format(res))
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
