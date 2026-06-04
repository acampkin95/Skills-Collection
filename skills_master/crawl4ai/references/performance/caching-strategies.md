# Caching Strategies

Result caching patterns for efficiency.

## Cache Implementation

### In-Memory Cache

```python
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional

class MemoryCache:
    def __init__(self, ttl_minutes: int = 60):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def _get_key(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    def get(self, url: str) -> Optional[dict]:
        """Get cached result."""
        key = self._get_key(url)

        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry["timestamp"] < self.ttl:
                return entry["data"]

            del self.cache[key]

        return None

    def set(self, url: str, data: dict):
        """Cache result."""
        key = self._get_key(url)
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now(),
        }

    def clear(self):
        self.cache.clear()
```

### Redis Cache

```python
import redis
import json
from datetime import timedelta

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379", ttl: int = 3600):
        self.client = redis.from_url(url)
        self.ttl = ttl

    def get(self, key: str) -> Optional[dict]:
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, data: dict):
        self.client.setex(key, self.ttl, json.dumps(data))

    def delete(self, key: str):
        self.client.delete(key)

    def clear_pattern(self, pattern: str):
        keys = self.client.keys(pattern)
        if keys:
            self.client.delete(*keys)
```
