import json
import inspect
from typing import get_type_hints


def get_type_info(param, type_hints):
    """Helper function to determine parameter type information"""
    if param.name in type_hints:
        typ = type_hints[param.name]
        if typ == str:
            return {"type": "string"}
        elif typ == int:
            return {"type": "integer"}
        elif typ == float:
            return {"type": "number"}
        elif typ == bool:
            return {"type": "boolean"}
        elif typ == dict:
            return {"type": "object"}
        elif typ == list:
            return {"type": "array"}
    return {"type": "string"}


def func_to_json(func, description=None):
    """Convert a function to a JSON function schema.

    Args:
        func: The function to convert
        description: Optional description of what the function does

    Returns:
        str: JSON string representing the function schema
    """
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue

        type_info = get_type_info(param, type_hints)
        properties[name] = {**type_info, "description": name}

        if param.default == param.empty:
            required.append(name)

    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description or func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
            "strict": True,
        },
    }

    return schema


def encode_func_call_result(result):
    """Encode a function call result into a JSON string.

    Args:
        result: The result to encode

    Returns:
        str: JSON string representing the function call result
    """
    try:
        # Try to directly serialize the result
        json_result = json.dumps(result)
        return json_result
    except (TypeError, OverflowError):
        # If the result is not JSON serializable (like a DataFrame)
        if hasattr(result, "to_json"):
            # If it has a to_json method (like pandas DataFrame)
            json_result = result.to_json(orient="records")
            return json_result
        elif hasattr(result, "__dict__"):
            # For custom objects, try to serialize their __dict__
            json_result = json.dumps(result.__dict__)
            return json_result
        else:
            # Last resort: convert to string
            json_result = json.dumps(str(result))
            return json_result


def invoke_tool_for_llm(func, args):
    """Invoke a function and return the result as a JSON string.

    Args:
        func: The function to invoke
        args: Arguments to pass to the function
    """
    args_dict = json.loads(args)
    result = func(**args_dict)
    return result

