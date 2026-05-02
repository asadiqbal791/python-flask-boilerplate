import re
from typing import Any


def pick(source: dict, keys: list[str]) -> dict:
    """Return a new dict containing only the specified keys from source."""
    return {k: source[k] for k in keys if k in source}


def omit(source: dict, keys: list[str]) -> dict:
    """Return a new dict excluding the specified keys."""
    return {k: v for k, v in source.items() if k not in keys}


def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def snake_to_camel(name: str) -> str:
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_keys(d: dict) -> dict:
    """Recursively convert dict keys from snake_case to camelCase."""
    if not isinstance(d, dict):
        return d
    return {snake_to_camel(k): camel_keys(v) for k, v in d.items()}
