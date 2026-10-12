#!/usr/bin/env python3
"""
Example: Memory consolidation - converting episodic memories to semantic knowledge.

This demonstrates the cognitive pattern of "learning from experience":
- Collect multiple related episodes
- Extract generalizable patterns
- Store as semantic facts for future reference
"""

import weaviate
from datetime import datetime, timedelta
import time

from weaviate_memory import (
    create_memory_collections,
    MemoryStore,
    MemoryConsolidation,
    MemoryMetrics
)


def main():
    client = weaviate.connect_to_local(
        host="localhost",
        port=8080,
        grpc_port=50051
    )
    
    try:
        print("=" * 60)
        print("MEMORY CONSOLIDATION EXAMPLE")
        print("Converting episodic experiences to semantic knowledge")
        print("=" * 60)
        
        # Initialize
        create_memory_collections(client)
        store = MemoryStore(client)
        consolidation = MemoryConsolidation(client)
        metrics = MemoryMetrics(client)
        
        # Simulate multiple related experiences
        print("\n1. Storing related experiences...")
        
        # Code review experiences
        experiences = [
            {
                "content": "Code review feedback was well-received when I started with positives",
                "event_type": "code_review",
                "actions": ["identified_positives", "suggested_improvements", "explained_reasoning"],
                "outcomes": ["feedback_accepted", "changes_implemented"],
                "success_score": 0.9
            },
            {
                "content": "Code review went poorly when I only focused on problems",
                "event_type": "code_review", 
                "actions": ["listed_issues", "requested_changes"],
                "outcomes": ["defensive_response", "delayed_fixes"],
                "success_score": 0.3
            },
            {
                "content": "Detailed code review with examples helped developer understand issues",
                "event_type": "code_review",
                "actions": ["provided_examples", "explained_best_practices", "offered_pair_session"],
                "outcomes": ["improved_understanding", "quality_improved"],
                "success_score": 0.95
            },
            {
                "content": "Quick code review with specific actionable items was efficient",
                "event_type": "code_review",
                "actions": ["identified_specific_lines", "provided_fixes", "kept_scope_focused"],
                "outcomes": ["quick_turnaround", "clear_fixes"],
                "success_score": 0.85
            },
        ]
        
        # Debugging experiences
        debugging_experiences = [
            {
                "content": "Systematic debugging starting with logs found the issue faster",
                "event_type": "debugging",
                "actions": ["checked_logs", "isolated_component", "added_debug_output"],
                "outcomes": ["root_cause_found", "issue_fixed"],
                "success_score": 0.9
            },
            {
                "content": "Random debugging without structure wasted time",
                "event_type": "debugging",
                "actions": ["tried_random_fixes", "guessed_at_cause"],
                "outcomes": ["wasted_time", "introduced_new_bugs"],
                "success_score": 0.2
            },
            {
                "content": "Binary search approach to debugging found issue in complex system",
                "event_type": "debugging",
                "actions": ["divided_system", "tested_halves", "narrowed_scope"],
                "outcomes": ["efficient_diagnosis", "clear_fix_path"],
                "success_score": 0.95
            },
        ]
        
        all_experiences = experiences + debugging_experiences
        
        for exp in all_experiences:
            store.store_episode(
                content=exp["content"],
                event_type=exp["event_type"],
                session_id="consolidation-demo",
                actions=exp["actions"],
                outcomes=exp["outcomes"],
                success_score=exp["success_score"],
                importance=0.6
            )
            print(f"   Stored: {exp['content'][:50]}...")
        
        print(f"\n   Total episodes stored: {len(all_experiences)}")
        
        # Check consolidation candidates
        print("\n2. Identifying consolidation candidates...")
        
        candidates = consolidation.identify_consolidation_candidates(
            min_episode_count=3,
            hours_back=1000  # Look back far enough to find our test data
        )
        
        for event_type, episodes in candidates.items():
            print(f"   {event_type}: {len(episodes)} episodes ready for consolidation")
        
        # Run consolidation cycle
        print("\n3. Running consolidation cycle...")
        
        result = consolidation.run_consolidation_cycle()
        
        print(f"   Episodes consolidated: {result['episodes_consolidated']}")
        print(f"   New semantic facts created: {result['new_semantic_facts']}")
        
        if result["facts"]:
            print("\n   Generated facts:")
            for fact in result["facts"]:
                print(f"   - [{fact['event_type']}] {fact['fact']}")
        
        # Show statistics
        print("\n4. Consolidation statistics...")
        
        stats = consolidation.get_consolidation_statistics()
        print(f"   Unconsolidated episodes: {stats['unconsolidated_episodes']}")
        print(f"   Consolidated episodes: {stats['consolidated_episodes']}")
        print(f"   Consolidation rate: {stats['consolidation_rate']:.1f}%")
        print(f"   Derived semantic facts: {stats['derived_semantic_facts']}")
        
        # Verify semantic facts exist
        print("\n5. Verifying stored semantic facts...")
        
        semantic = client.collections.get("SemanticMemory")
        response = semantic.query.fetch_objects(limit=10)
        
        for obj in response.objects:
            fact_type = obj.properties.get("factType", "")
            if fact_type == "consolidated_pattern":
                fact = obj.properties.get("fact", "")[:80]
                domain = obj.properties.get("domain", "")
                print(f"   [{domain}] {fact}...")
        
        print("\n" + "=" * 60)
        print("Consolidation example completed!")
        print("=" * 60)
        
    finally:
        client.close()


if __name__ == "__main__":
    main()
