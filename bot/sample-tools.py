from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage
from typing import Annotated


@tool
def add(a: int, b: int) -> int:
    """Add two numbers.
    Args:
        a (int): First number.
        b (int): Second number.
    Returns:
        int: Sum of the two numbers."""
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers.
    Args:
        a (int): First number.
        b (int): Second number.
    Returns:
        int: Difference of the two numbers."""
    return a - b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.
    Args:
        a (int): First number.
        b (int): Second number.
    Returns:
        int: Product of the two numbers."""
    return a * b

@tool
def divide(a: int, b: int) -> int:
    """Divide two numbers.
    Args:
        a (int): First number.
        b (int): Second number.
    Returns:
        int: Quotient of the two numbers.
    """
    return a / b


from langchain_core.runnables import RunnableConfig

@tool
def special_add(a: int,  b: int, 
                config: RunnableConfig) -> int:
    """Add two numbers and then multiply the result with the user fav number.
    Args:
        a (int): First number.
        b (int): Second number.
    Returns:
        int: Sum of the two numbers multiplied by the user fav number."""
    
    user_fav_num = config["configurable"].get("user_num", 1)
    res = (a+b) * user_fav_num
    return res


@tool
def special_subtract(a: int, b: int, 
                     state: Annotated[dict, InjectedState],
                     config: RunnableConfig,
                     ) -> int:
    """Subtract two numbers and then multiply the result with the user fav number.
    Args:
        a (int): First number.
        b (int): Second number.
    Returns:
        int: Difference of the two numbers multiplied by the user fav number."""
    
    user_fav_num = config["configurable"].get("user_num", 1)
    from_state = state.get("procedure_ctx", {}).get("phone_number")
    res = (a-b) * user_fav_num
    return res