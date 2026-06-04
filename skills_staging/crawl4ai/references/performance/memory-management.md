# Memory Management

Memory-efficient crawling strategies.

## Memory-Efficient Processing

### Chunk Processing

```python
import asyncio
from typing import Callable, Any

class MemoryEfficientProcessor:
    def __init__(self, chunk_size: int = 50):
        self.chunk_size = chunk_size

    async def process_in_chunks(
        self,
        urls: list,
        processor: Callable,
        on_chunk_complete: Callable = None
    ) -> list:
        """Process URLs in chunks to control memory usage."""
        results = []

        for i in range(0, len(urls), self.chunk_size):
            chunk = urls[i:i + self.chunk_size]
            chunk_results = await asyncio.gather(
                *[processor(url) for url in chunk],
                return_exceptions=True
            )

            results.extend(chunk_results)

            if on_chunk_complete:
                on_chunk_complete(i, len(chunk))

            # Force garbage collection
            import gc
            gc.collect()

        return results
```

---

## Cleanup Patterns

```python
class CleanupManager:
    def __init__(self):
        self.temp_files = []

    def add_temp_file(self, path: str):
        self.temp_files.append(path)

    async def cleanup(self):
        """Clean up temporary files."""
        import os
        for path in self.temp_files:
            try:
                os.remove(path)
            except:
                pass
        self.temp_files.clear()
```
