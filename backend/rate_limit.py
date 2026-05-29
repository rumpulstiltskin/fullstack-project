import time
from collections import defaultdict

_buckets: dict[str, list[float]] = defaultdict(list)


def check(key: str, max_calls: int, window_secs: float = 60.0) -> bool:
    """Return True if the request is allowed, False if rate limited."""
    now = time.monotonic()
    calls = _buckets[key]
    _buckets[key] = [t for t in calls if now - t < window_secs]
    if len(_buckets[key]) >= max_calls:
        return False
    _buckets[key].append(now)
    return True


def clear_all() -> None:
    _buckets.clear()
