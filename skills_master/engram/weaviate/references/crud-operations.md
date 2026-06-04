# Memory CRUD Operations (Python v4.x)

Core operations for storing, retrieving, updating, and deleting memories in Weaviate. Updated for Python client v4.x with async support (as of Weaviate v1.26+).

---

## Store Episodic Memory (Synchronous)

```python
from datetime import datetime
import weaviate.classes.query as wvc

class MemoryStore:
    def __init__(self, client):
        self.client = client
        self.episodic = client.collections.get("EpisodicMemory")
        self.semantic = client.collections.get("SemanticMemory")
        self.procedural = client.collections.get("ProceduralMemory")

    def store_episode(
        self,
        content: str,
        event_type: str,
        session_id: str,
        user_id: str = None,
        agent_id: str = None,
        actions: list[str] = None,
        outcomes: list[str] = None,
        context_factors: list[str] = None,
        success_score: float = None,
        importance: float = 0.5,
        metadata: dict = None
    ) -> str:
        """Store an episodic memory with full context."""

        memory_object = {
            "content": content,
            "eventType": event_type,
            "timestamp": datetime.now().isoformat(),
            "sessionId": session_id,
            "sequenceIndex": self._get_next_sequence_index(session_id),
            "userId": user_id,
            "agentId": agent_id,
            "actionsTaken": actions or [],
            "observedOutcomes": outcomes or [],
            "contextFactors": context_factors or [],
            "successScore": success_score,
            "importanceScore": importance,
            "recencyScore": 1.0,  # Starts at max, decays over time
            "accessCount": 0,
            "consolidatedToSemantic": False,
            "metadata": metadata or {},
        }

        uuid = self.episodic.data.insert(properties=memory_object)
        return str(uuid)

    def _get_next_sequence_index(self, session_id: str) -> int:
        """Get next sequence index for session ordering."""
        results = self.episodic.query.fetch_objects(
            where=wvc.Filter.by_property("sessionId").equal(session_id),
            limit=1,
            sort=wvc.Sort.by_property("sequenceIndex", ascending=False)
        )
        if results.objects:
            return results.objects[0].properties.get("sequenceIndex", 0) + 1
        return 0

    def store_semantic_fact(
        self,
        fact: str,
        fact_type: str,
        domain: str = None,
        category: str = None,
        confidence: float = 0.8,
        derived_from_episodes: list[str] = None,
        related_concepts: list[str] = None,
        applicability_conditions: str = None
    ) -> str:
        """Store a semantic fact/knowledge item."""

        fact_object = {
            "fact": fact,
            "factType": fact_type,
            "domain": domain,
            "category": category,
            "confidenceScore": confidence,
            "derivedFromEpisodes": derived_from_episodes or [],
            "relatedConcepts": related_concepts or [],
            "applicabilityConditions": applicability_conditions,
            "createdAt": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "usageFrequency": 0,
            "importanceScore": 0.5,
        }

        uuid = self.semantic.data.insert(properties=fact_object)
        return str(uuid)

    def store_procedure(
        self,
        name: str,
        description: str,
        goal_type: str,
        steps: list[str],
        prerequisites: list[str] = None,
        success_criteria: list[str] = None,
        applicable_contexts: list[str] = None,
        decision_points: list[dict] = None
    ) -> str:
        """Store a procedural workflow."""

        procedure_object = {
            "workflowName": name,
            "workflowDescription": description,
            "goalType": goal_type,
            "steps": steps,
            "prerequisiteStates": prerequisites or [],
            "successCriteria": success_criteria or [],
            "applicableContexts": applicable_contexts or [],
            "decisionPoints": decision_points or [],
            "successRate": 0.0,
            "executionCount": 0,
            "version": 1,
            "createdAt": datetime.now().isoformat(),
            "lastModified": datetime.now().isoformat(),
        }

        uuid = self.procedural.data.insert(properties=procedure_object)
        return str(uuid)
```

---

## Async Store Operations (v1.26+)

For high-concurrency environments, use async client:

```python
import weaviate
from weaviate.classes.config import Configure
import asyncio

async def async_store_episode(async_client, content: str, importance: float = 0.5) -> str:
    """Store episodic memory asynchronously."""
    episodic = async_client.collections.get("EpisodicMemory")

    uuid = await episodic.data.insert(
        properties={
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "importanceScore": importance,
        }
    )
    return str(uuid)

async def async_batch_store(async_client, memories: list[dict]) -> dict:
    """Batch insert multiple memories concurrently."""
    episodic = async_client.collections.get("EpisodicMemory")

    tasks = [
        episodic.data.insert(properties=memory)
        for memory in memories
    ]

    results = await asyncio.gather(*tasks)
    return {"inserted": len(results), "uuids": [str(r) for r in results]}

# Usage
async with weaviate.connect_to_local() as async_client:
    result = await async_store_episode(async_client, "User prefers brevity", 0.9)
```

---

## Retrieve Memory with Access Tracking

```python
def access_memory(self, collection_name: str, uuid: str) -> dict:
    """Retrieve memory and update access tracking."""
    collection = self.client.collections.get(collection_name)

    # Fetch the object
    obj = collection.query.fetch_object_by_id(uuid)

    if obj:
        # Update access tracking
        current_count = obj.properties.get("accessCount", 0)
        collection.data.update(
            uuid=uuid,
            properties={
                "accessCount": current_count + 1,
                "lastAccessedAt": datetime.now().isoformat()
            }
        )

    return obj.properties if obj else None
```

---

## Update Memory Properties

```python
def update_importance_score(self, collection_name: str, uuid: str, new_score: float):
    """Update a memory's importance score."""
    collection = self.client.collections.get(collection_name)
    collection.data.update(
        uuid=uuid,
        properties={"importanceScore": new_score}
    )

def mark_as_consolidated(self, episode_uuid: str):
    """Mark episodic memory as consolidated to semantic."""
    self.episodic.data.update(
        uuid=episode_uuid,
        properties={
            "consolidatedToSemantic": True,
            "consolidationDate": datetime.now().isoformat()
        }
    )

def update_access_metrics(self, uuid: str, access_count: int, last_used: str):
    """Track memory usage patterns."""
    collection = self.client.collections.get("EpisodicMemory")
    collection.data.update(
        uuid=uuid,
        properties={
            "accessCount": access_count,
            "lastAccessedAt": last_used
        }
    )
```

---

## Delete Memory

```python
def forget_memory(self, collection_name: str, uuid: str) -> bool:
    """Delete a specific memory."""
    collection = self.client.collections.get(collection_name)
    try:
        collection.data.delete_by_id(uuid)
        return True
    except Exception as e:
        print(f"Error deleting memory {uuid}: {e}")
        return False

def bulk_forget(self, collection_name: str, uuids: list[str]) -> dict:
    """Delete multiple memories efficiently."""
    collection = self.client.collections.get(collection_name)

    deleted = 0
    failed = 0

    for uuid in uuids:
        try:
            collection.data.delete_by_id(uuid)
            deleted += 1
        except Exception:
            failed += 1

    return {"deleted": deleted, "failed": failed}
```

---

## Batch Import for Historical Memories

v4.x supports concurrent batch operations:

```python
def batch_import_memories(
    self,
    memories: list[dict],
    collection_name: str = "EpisodicMemory",
    batch_size: int = 100,
    concurrent_requests: int = 4
) -> dict:
    """Efficiently import historical memories in parallel."""
    collection = self.client.collections.get(collection_name)

    imported = 0
    failed = 0
    failed_objects = []

    with collection.batch.fixed_size(
        batch_size=batch_size,
        concurrent_requests=concurrent_requests
    ) as batch:
        for memory in memories:
            # Ensure required fields
            if "timestamp" not in memory:
                memory["timestamp"] = datetime.now().isoformat()
            if "importanceScore" not in memory:
                memory["importanceScore"] = 0.5
            if "recencyScore" not in memory:
                memory["recencyScore"] = 0.5

            batch.add_object(properties=memory)

    # Check for failures
    if batch.failed_objects:
        failed_objects = batch.failed_objects
        failed = len(failed_objects)

    imported = len(memories) - failed

    return {
        "imported": imported,
        "failed": failed,
        "total": len(memories),
        "failed_objects": failed_objects
    }
```

---

## Connection Management Patterns

Always use context managers for safe resource cleanup:

```python
# Synchronous
with weaviate.connect_to_local(port=8080, grpc_port=50051) as client:
    # Operations here
    pass

# Asynchronous
async def async_operations():
    async with weaviate.connect_to_local() as async_client:
        # Async operations here
        pass
    await asyncio.run(async_operations())
```

---

## Error Handling Best Practices

```python
def safe_insert(self, collection_name: str, properties: dict) -> tuple[str, bool]:
    """Insert with error handling."""
    try:
        collection = self.client.collections.get(collection_name)
        uuid = collection.data.insert(properties=properties)
        return str(uuid), True
    except weaviate.exceptions.WeaviateInvalidInputError as e:
        print(f"Invalid input: {e}")
        return None, False
    except weaviate.exceptions.WeaviateConnectionError as e:
        print(f"Connection error: {e}")
        return None, False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, False
```

Key v4 error types:
- `WeaviateInvalidInputError`: Schema mismatch
- `WeaviateConnectionError`: Network issues
- `WeaviateQueryError`: Query execution failures
