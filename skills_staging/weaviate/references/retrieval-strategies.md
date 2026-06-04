# Memory Retrieval Strategies

## Hybrid Search with Recency-Importance Weighting

```python
import math
from datetime import datetime, timedelta
import weaviate.classes.query as wvc

class MemoryRetrieval:
    def __init__(self, client):
        self.client = client
        self.episodic = client.collections.get("EpisodicMemory")
        self.semantic = client.collections.get("SemanticMemory")
        self.procedural = client.collections.get("ProceduralMemory")

    def retrieve_relevant_memories(
        self,
        query: str,
        memory_types: list[str] = None,
        limit: int = 10,
        importance_weight: float = 0.3,
        recency_weight: float = 0.3,
        similarity_weight: float = 0.4,
        min_importance: float = 0.0
    ) -> list[dict]:
        """
        Retrieve memories using hybrid scoring:
        - Semantic similarity to query
        - Recency (exponential decay)
        - Importance score
        """
        memory_types = memory_types or ["episodic", "semantic"]
        all_results = []

        for mem_type in memory_types:
            collection = getattr(self, mem_type, None)
            if not collection:
                continue

            # Hybrid search combines vector similarity and BM25
            response = collection.query.hybrid(
                query=query,
                alpha=0.7,  # 0.7 = 70% vector, 30% keyword
                limit=limit * 2,  # Fetch extra for reranking
                return_metadata=wvc.MetadataQuery(distance=True)
            )

            for obj in response.objects:
                # Calculate composite score
                similarity = 1.0 - (obj.metadata.distance / 2.0) if obj.metadata.distance else 0.5
                recency = obj.properties.get("recencyScore", 0.5)
                importance = obj.properties.get("importanceScore", 0.5)

                if importance < min_importance:
                    continue

                composite = (
                    similarity_weight * similarity +
                    recency_weight * recency +
                    importance_weight * importance
                )

                all_results.append({
                    "uuid": str(obj.uuid),
                    "type": mem_type,
                    "properties": obj.properties,
                    "scores": {
                        "similarity": similarity,
                        "recency": recency,
                        "importance": importance,
                        "composite": composite
                    }
                })

        # Sort by composite score and return top results
        all_results.sort(key=lambda x: x["scores"]["composite"], reverse=True)
        return all_results[:limit]

    def retrieve_session_context(
        self,
        session_id: str,
        limit: int = 20
    ) -> list[dict]:
        """Retrieve all memories from a specific session in order."""
        response = self.episodic.query.fetch_objects(
            filters=wvc.Filter.by_property("sessionId").equal(session_id),
            limit=limit,
            sort=wvc.Sort.by_property("sequenceIndex", ascending=True)
        )
        return [obj.properties for obj in response.objects]

    def retrieve_user_preferences(
        self,
        user_id: str,
        domain: str = None
    ) -> list[dict]:
        """Retrieve semantic memories that are user preferences."""
        filters = [
            wvc.Filter.by_property("factType").equal("preference")
        ]

        if domain:
            filters.append(wvc.Filter.by_property("domain").equal(domain))

        combined_filter = filters[0]
        for f in filters[1:]:
            combined_filter = combined_filter & f

        response = self.semantic.query.fetch_objects(
            filters=combined_filter,
            limit=50
        )
        return [obj.properties for obj in response.objects]

    def retrieve_applicable_procedures(
        self,
        goal: str,
        context: str = None,
        min_success_rate: float = 0.0
    ) -> list[dict]:
        """Find procedures that match the goal and context."""
        response = self.procedural.query.near_text(
            query=f"{goal} {context or ''}",
            limit=10,
            return_metadata=wvc.MetadataQuery(distance=True)
        )

        results = []
        for obj in response.objects:
            success_rate = obj.properties.get("successRate", 0)
            if success_rate >= min_success_rate:
                results.append({
                    "properties": obj.properties,
                    "relevance": 1.0 - (obj.metadata.distance / 2.0),
                    "success_rate": success_rate
                })

        return sorted(results, key=lambda x: x["success_rate"], reverse=True)
```

## Temporal-Aware Retrieval

```python
def retrieve_memories_in_timeframe(
    self,
    start_date: datetime,
    end_date: datetime = None,
    event_types: list[str] = None,
    limit: int = 100
) -> list[dict]:
    """Retrieve memories within a specific time window."""
    end_date = end_date or datetime.now()

    filters = [
        wvc.Filter.by_property("timestamp").greater_than(start_date.isoformat()),
        wvc.Filter.by_property("timestamp").less_than(end_date.isoformat())
    ]

    if event_types:
        type_filter = wvc.Filter.by_property("eventType").equal(event_types[0])
        for et in event_types[1:]:
            type_filter = type_filter | wvc.Filter.by_property("eventType").equal(et)
        filters.append(type_filter)

    combined_filter = filters[0]
    for f in filters[1:]:
        combined_filter = combined_filter & f

    response = self.episodic.query.fetch_objects(
        filters=combined_filter,
        limit=limit,
        sort=wvc.Sort.by_property("timestamp", ascending=False)
    )

    return [obj.properties for obj in response.objects]

def retrieve_recent_interactions(
    self,
    hours_back: int = 24,
    user_id: str = None
) -> list[dict]:
    """Retrieve recent interactions for context building."""
    cutoff = datetime.now() - timedelta(hours=hours_back)

    filters = [
        wvc.Filter.by_property("timestamp").greater_than(cutoff.isoformat())
    ]

    if user_id:
        filters.append(wvc.Filter.by_property("userId").equal(user_id))

    combined_filter = filters[0]
    for f in filters[1:]:
        combined_filter = combined_filter & f

    response = self.episodic.query.fetch_objects(
        filters=combined_filter,
        limit=50,
        sort=wvc.Sort.by_property("timestamp", ascending=False)
    )

    return [obj.properties for obj in response.objects]
```

## Semantic Search with Filters

```python
def search_memories_with_context(
    self,
    query: str,
    user_id: str = None,
    event_types: list[str] = None,
    domains: list[str] = None,
    min_importance: float = None,
    limit: int = 10
) -> list[dict]:
    """Semantic search with contextual filters."""

    filter_conditions = []

    if user_id:
        filter_conditions.append(
            wvc.Filter.by_property("userId").equal(user_id)
        )

    if event_types:
        type_filter = wvc.Filter.by_property("eventType").equal(event_types[0])
        for et in event_types[1:]:
            type_filter = type_filter | wvc.Filter.by_property("eventType").equal(et)
        filter_conditions.append(type_filter)

    if min_importance:
        filter_conditions.append(
            wvc.Filter.by_property("importanceScore").greater_or_equal(min_importance)
        )

    combined_filter = None
    if filter_conditions:
        combined_filter = filter_conditions[0]
        for f in filter_conditions[1:]:
            combined_filter = combined_filter & f

    response = self.episodic.query.near_text(
        query=query,
        filters=combined_filter,
        limit=limit,
        return_metadata=wvc.MetadataQuery(distance=True)
    )

    return [{
        "uuid": str(obj.uuid),
        "properties": obj.properties,
        "distance": obj.metadata.distance
    } for obj in response.objects]
```
