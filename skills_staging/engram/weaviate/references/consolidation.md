# Memory Consolidation

## Episodic to Semantic Consolidation

```python
from datetime import datetime, timedelta
from collections import Counter
import weaviate.classes.query as wvc

class MemoryConsolidation:
    def __init__(self, client, llm_client=None):
        self.client = client
        self.llm = llm_client
        self.episodic = client.collections.get("EpisodicMemory")
        self.semantic = client.collections.get("SemanticMemory")

    def identify_consolidation_candidates(
        self,
        min_episode_count: int = 3,
        hours_back: int = 48
    ) -> dict[str, list]:
        """
        Find groups of related episodic memories
        that could be consolidated into semantic facts.
        """
        cutoff = datetime.now() - timedelta(hours=hours_back)

        # Fetch recent unconsolidated episodes
        response = self.episodic.query.fetch_objects(
            filters=(
                wvc.Filter.by_property("consolidatedToSemantic").equal(False) &
                wvc.Filter.by_property("timestamp").greater_than(cutoff.isoformat())
            ),
            limit=200
        )

        # Group by event type
        groups = {}
        for obj in response.objects:
            event_type = obj.properties.get("eventType", "unknown")
            if event_type not in groups:
                groups[event_type] = []
            groups[event_type].append({
                "uuid": str(obj.uuid),
                "content": obj.properties.get("content", ""),
                "outcomes": obj.properties.get("observedOutcomes", []),
                "success": obj.properties.get("successScore", 0.5)
            })

        # Filter groups with enough episodes
        return {k: v for k, v in groups.items() if len(v) >= min_episode_count}

    def consolidate_episodes_to_fact(
        self,
        episodes: list[dict],
        event_type: str
    ) -> str:
        """
        Consolidate a group of episodes into a semantic fact.
        Uses LLM to extract generalizable knowledge.
        """
        if not episodes:
            return None

        # Build prompt for consolidation
        episodes_text = "\n".join([
            f"- {ep['content']}: Outcomes: {', '.join(ep['outcomes'])}, Success: {ep['success']}"
            for ep in episodes[:10]
        ])

        if self.llm:
            # Use LLM for intelligent consolidation
            prompt = f"""Analyze these related episodes and extract ONE generalizable fact or pattern:

Event Type: {event_type}
Episodes:
{episodes_text}

Provide a single concise factual statement that captures the pattern these episodes demonstrate.
Format: A clear, actionable fact that can guide future decisions."""

            # Call LLM
            # fact = self.llm.generate(prompt)
            fact = f"Based on {len(episodes)} {event_type} episodes: pattern identified"
        else:
            # Simple heuristic consolidation
            avg_success = sum(ep['success'] for ep in episodes) / len(episodes)
            common_outcomes = self._find_common_outcomes(episodes)

            fact = f"In {event_type} situations, common outcomes include: {', '.join(common_outcomes[:3])}. Average success rate: {avg_success:.2f}"

        return fact

    def _find_common_outcomes(self, episodes: list[dict]) -> list[str]:
        """Find outcomes that appear in multiple episodes."""
        all_outcomes = []
        for ep in episodes:
            all_outcomes.extend(ep.get("outcomes", []))

        counts = Counter(all_outcomes)
        return [outcome for outcome, count in counts.most_common(5) if count > 1]

    def run_consolidation_cycle(self) -> dict:
        """Execute one consolidation cycle."""
        candidates = self.identify_consolidation_candidates()

        consolidated_count = 0
        new_facts = []

        for event_type, episodes in candidates.items():
            fact = self.consolidate_episodes_to_fact(episodes, event_type)

            if fact:
                # Store as semantic memory
                episode_uuids = [ep["uuid"] for ep in episodes]

                fact_uuid = self.semantic.data.insert({
                    "fact": fact,
                    "factType": "consolidated_pattern",
                    "domain": event_type,
                    "confidenceScore": 0.7,
                    "derivedFromEpisodes": episode_uuids,
                    "createdAt": datetime.now().isoformat(),
                    "lastUpdated": datetime.now().isoformat(),
                    "usageFrequency": 0,
                    "importanceScore": 0.6
                })

                # Mark episodes as consolidated
                for ep_uuid in episode_uuids:
                    self.episodic.data.update(
                        uuid=ep_uuid,
                        properties={
                            "consolidatedToSemantic": True,
                            "consolidationDate": datetime.now().isoformat()
                        }
                    )

                consolidated_count += len(episodes)
                new_facts.append(fact)

        return {
            "episodes_consolidated": consolidated_count,
            "new_semantic_facts": len(new_facts),
            "facts": new_facts
        }
```
