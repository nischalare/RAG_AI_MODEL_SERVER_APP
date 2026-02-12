"""
calculator.py

This file defines a secure calculator tool for the chatbot.

Why we need this:
- Allows the LLM to perform math operations
- Demonstrates tool usage in LangChain
- Avoids hallucinated math errors

IMPORTANT:
We DO NOT use raw eval() directly (security risk).
Instead, we restrict allowed characters and operators.
"""

# =====================================================
# IMPORTS
# =====================================================

import math
import operator
import re
from langchain_classic.tools import Tool


# =====================================================
# SAFE OPERATOR MAPPING
# =====================================================

# Only allow safe mathematical operations
SAFE_OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "**": operator.pow,
    "%": operator.mod
}


# =====================================================
# SAFE CALCULATOR FUNCTION
# =====================================================

def safe_calculator(expression: str) -> str:
    """
    Safely evaluates a simple mathematical expression.

    Allowed:
    - Numbers
    - + - * / ** %
    - Parentheses

    Disallowed:
    - Variables
    - Imports
    - File access
    - System commands
    """

    try:
        # Remove spaces
        expression = expression.replace(" ", "")

        # Validate allowed characters (numbers + operators + parentheses)
        if not re.match(r"^[0-9+\-*/().%**]+$", expression):
            return "Invalid expression. Only numbers and math operators allowed."

        # Use eval in restricted environment (no builtins)
        result = eval(expression, {"__builtins__": None}, {})

        return str(result)

    except Exception:
        return "Error evaluating expression."


# =====================================================
# LANGCHAIN TOOL WRAPPER
# =====================================================

calculator_tool = Tool(
    name="Calculator",
    func=safe_calculator,
    description=(
        "Use this tool for mathematical calculations. "
        "Input should be a valid math expression like: 2+2 or 10*5"
    )
)
