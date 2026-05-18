"""Calculator tool for arithmetic evaluation."""

import ast
import operator
from typing import Any

from src.tools.base import BaseTool

# Allowed operators for safe evaluation
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> float:
    """Recursively evaluate an AST node with only arithmetic operators."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


class CalculatorTool(BaseTool):
    """Evaluates arithmetic expressions safely (no exec/eval)."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Evaluate a mathematical expression. Supports +, -, *, /, **, %. Input: 'expression' string."

    async def execute(self, **kwargs: Any) -> str:
        expression = kwargs.get("expression", "")
        if not expression:
            return "Error: No expression provided."
        try:
            tree = ast.parse(expression, mode="eval")
            result = _safe_eval(tree)
            return str(result)
        except (ValueError, SyntaxError, ZeroDivisionError) as e:
            return f"Error: {e}"

    def _parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic expression to evaluate, e.g. '(2 + 3) * 4'",
                }
            },
            "required": ["expression"],
        }
