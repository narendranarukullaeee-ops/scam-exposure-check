import time
from collections import defaultdict, deque
from datetime import date


class SlidingWindow:
    """In-memory limiter. Fine for one small instance; use Redis if you scale out."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit, self.window = limit, window_seconds
        self.hits = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now, q = time.time(), self.hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True


class DailyCap:
    """Hard global ceiling so a flood can never run up provider bills."""

    def __init__(self, limit: int):
        self.limit, self.day, self.used = limit, date.today(), 0

    def take(self) -> bool:
        if date.today() != self.day:
            self.day, self.used = date.today(), 0
        if self.used >= self.limit:
            return False
        self.used += 1
        return True
