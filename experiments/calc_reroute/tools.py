"""The `calc` tool — genuine (not simulated) arithmetic capability.

A worker holding this tool can offload multi-step arithmetic and get exact
answers; a worker without it must compute in-head and errs on compounding
tasks. This is the competence source for the calc-reroute experiment.
"""

import ast
import operator

from agents import function_tool

_BIN = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def safe_eval(expr: str) -> float:
    """Evaluate an arithmetic expression: numbers, + - * / ** %, parens, unary.

    Rejects names, calls, attributes — no arbitrary code.
    """
    def _ev(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
            return _BIN[type(node.op)](_ev(node.left), _ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
            return _UNARY[type(node.op)](_ev(node.operand))
        raise ValueError(f"unsupported expression element: {ast.dump(node)}")

    return _ev(ast.parse(expr.strip(), mode="eval"))


@function_tool
def calc(expression: str) -> str:
    """Evaluate an arithmetic expression and return the exact numeric result.

    Supports + - * / ** % and parentheses, e.g. '100/1.09 + 120/1.09**2'.
    Use this for any non-trivial calculation to avoid arithmetic mistakes.
    """
    try:
        return str(safe_eval(expression))
    except Exception as e:  # noqa: BLE001
        return f"calc error: {e}"
