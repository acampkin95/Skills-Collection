# Memory Decay and Forgetting

## Exponential Decay Function

```python
import math
from datetime import datetime, timedelta

class MemoryDecay:
    def __init__(self, client, half_life_days: int = 7):
        self.client = client
        self.half_life_days = half_life_days

    def calculate_recency_score(
        self,
        storage_timestamp: datetime,
        current_timestamp: datetime = None
    ) -> float:
        """
        Calculate recency using exponential decay.
        Score = 2^(-age/half_life)
        After half_life days, score drops to 0.5
        """
        current_timestamp = current_timestamp or datetime.now()

        if isinstance(storage_timestamp, str):
            storage_timestamp = datetime.fromisoformat(storage_timestamp.replace('Z', '+00:00'))

        age_days = (current_timestamp - storage_timestamp).total_seconds() / 86400

        # Exponential decay
        decay_rate = math.exp(-math.log(2) * age_days / self.half_life_days)

        return max(0.0, min(1.0, decay_rate))

    def update_all_recency_scores(self, collection_name: str = "EpisodicMemory"):
        """Batch update recency scores for all memories."""
        collection = self.client.collections.get(collection_name)
        current_time = datetime.now()

        updated_count = 0

        for obj in collection.iterator():
            timestamp = obj.properties.get("timestamp")
            if timestamp:
                new_recency = self.calculate_recency_score(timestamp, current_time)

                collection.data.update(
                    uuid=obj.uuid,
                    properties={"recencyScore": new_recency}
                )
                updated_count += 1

        return updated_count

    def calculate_memory_fitness(
        self,
        memory: dict,
        access_weight: float = 0.3,
        importance_weight: float = 0.4,
        recency_weight: float = 0.3
    ) -> float:
        """
        Calculate overall memory fitness for retention decisions.
        Low fitness memories are candidates for removal.
        """
        access_count = memory.get("accessCount", 0)
        # Normalize access frequency (log scale to prevent dominance)
        access_score = min(1.0, math.log10(access_count + 1) / 2)

        importance = memory.get("importanceScore", 0.5)
        recency = memory.get("recencyScore", 0.5)

        fitness = (
            access_weight * access_score +
            importance_weight * importance +
            recency_weight * recency
        )

        return fitness

    def identify_forgetting_candidates(
        self,
        collection_name: str = "EpisodicMemory",
        fitness_threshold: float = 0.3,
        limit: int = 100
    ) -> list[dict]:
        """Identify low-fitness memories for potential removal."""
        collection = self.client.collections.get(collection_name)

        candidates = []

        for obj in collection.iterator():
            fitness = self.calculate_memory_fitness(obj.properties)

            if fitness < fitness_threshold:
                candidates.append({
                    "uuid": str(obj.uuid),
                    "content": obj.properties.get("content", "")[:100],
                    "fitness": fitness,
                    "recency": obj.properties.get("recencyScore", 0),
                    "importance": obj.properties.get("importanceScore", 0),
                    "accessCount": obj.properties.get("accessCount", 0)
                })

            if len(candidates) >= limit:
                break

        return sorted(candidates, key=lambda x: x["fitness"])

    def apply_intelligent_forgetting(
        self,
        collection_name: str = "EpisodicMemory",
        fitness_threshold: float = 0.2,
        dry_run: bool = True
    ) -> dict:
        """
        Remove or archive low-fitness memories.
        Uses gradual degradation before deletion.
        """
        collection = self.client.collections.get(collection_name)
        candidates = self.identify_forgetting_candidates(
            collection_name,
            fitness_threshold,
            limit=500
        )

        degraded = 0
        deleted = 0

        for candidate in candidates:
            uuid = candidate["uuid"]
            fitness = candidate["fitness"]

            if fitness < 0.1:
                # Very low fitness - delete
                if not dry_run:
                    collection.data.delete_by_id(uuid)
                deleted += 1
            else:
                # Low fitness - degrade scores further
                if not dry_run:
                    collection.data.update(
                        uuid=uuid,
                        properties={
                            "importanceScore": max(0, candidate["importance"] - 0.1),
                            "recencyScore": max(0, candidate["recency"] - 0.05)
                        }
                    )
                degraded += 1

        return {
            "degraded": degraded,
            "deleted": deleted,
            "dry_run": dry_run
        }
```
