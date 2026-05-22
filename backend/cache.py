import time
from functools import wraps
from typing import Any

_store: dict[str, tuple[Any, float]] = {}


def ttl_cache(seconds: int = 3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__qualname__}::{args}::{tuple(sorted(kwargs.items()))}"
            if key in _store:
                result, ts = _store[key]
                if time.time() - ts < seconds:
                    return result
            result = func(*args, **kwargs)
            _store[key] = (result, time.time())
            return result
        return wrapper
    return decorator
