#!/usr/bin/env python3
"""
Example: Basic memory operations demonstrating the Weaviate Memory System.

Prerequisites:
1. Start Weaviate: docker-compose up -d
2. Start Ollama: ollama serve
3. Pull embedding model: ollama pull nomic-embed-text
"""

import weaviate
from datetime import datetime

from weaviate_memory import (
    create_memory_collections,
    MemoryStore,
    MemoryRetrieval,
    MemoryDecay,
    MemoryMetrics
)


def main():
    # Connect to Weaviate
    client = weaviate.connect_to_local(
        host="localhost",
        port=8080,
        grpc_port=50051
    )
    
    try:
        print("=" * 60)
        print("WEAVIATE MEMORY SYSTEM - BASIC EXAMPLE")
        print("=" * 60)
        
        # Initialize collections
        print("\n1. Creating memory collections...")
        collections = create_memory_collections(
            client,
            use_ollama=True,
            ollama_endpoint="http://localhost:11434",
            ollama_model="nomic-embed-text"
        )
        print(f"   Created: {list(collections.keys())}")
        
        # Initialize components
        store = MemoryStore(client)
        retrieval = MemoryRetrieval(client)
        decay = MemoryDecay(client, half_life_days=7)
        metrics = MemoryMetrics(client)
        
        # Store episodic memories
        print("\n2. Storing episodic memories...")
        
        episode1 = store.store_episode(
            content="User asked about Python async patterns and I explained asyncio basics",
            event_type="interaction",
            session_id="session-001",
            user_id="user-alex",
            actions=["explained_concept", "provided_code_example"],
            outcomes=["user_understood", "requested_followup"],
            success_score=0.9,
            importance=0.7
        )
        print(f"   Stored episode: {episode1[:8]}...")
        
        episode2 = store.store_episode(
            content="Helped debug a FastAPI authentication middleware issue",
            event_type="interaction",
            session_id="session-001",
            user_id="user-alex",
            actions=["diagnosed_issue", "suggested_fix", "verified_solution"],
            outcomes=["bug_fixed", "code_committed"],
            success_score=0.95,
            importance=0.8
        )
        print(f"   Stored episode: {episode2[:8]}...")
        
        episode3 = store.store_episode(
            content="User prefers concise code examples over lengthy explanations",
            event_type="observation",
            session_id="session-001",
            user_id="user-alex",
            importance=0.6
        )
        print(f"   Stored episode: {episode3[:8]}...")
        
        # Store semantic facts
        print("\n3. Storing semantic facts...")
        
        fact1 = store.store_semantic_fact(
            fact="Alex prefers TypeScript for frontend and Python for backend",
            fact_type="preference",
            domain="programming",
            user_id="user-alex",
            confidence=0.9
        )
        print(f"   Stored fact: {fact1[:8]}...")
        
        fact2 = store.store_semantic_fact(
            fact="When explaining async patterns, use real-world analogies",
            fact_type="insight",
            domain="communication",
            confidence=0.85
        )
        print(f"   Stored fact: {fact2[:8]}...")
        
        # Store procedural memory
        print("\n4. Storing procedural memory...")
        
        procedure = store.store_procedure(
            name="Debug FastAPI Issue",
            description="Standard approach to debugging FastAPI applications",
            goal_type="troubleshooting",
            steps=[
                "Check request/response logs",
                "Verify middleware order",
                "Test endpoint isolation",
                "Review dependency injection",
                "Check async/await patterns"
            ],
            prerequisites=["FastAPI app running", "Access to logs"],
            required_tools=["uvicorn", "httpie", "pytest"],
            success_criteria=["Issue identified", "Fix verified", "Tests passing"]
        )
        print(f"   Stored procedure: {procedure[:8]}...")
        
        # Retrieve memories
        print("\n5. Retrieving relevant memories...")
        
        results = retrieval.retrieve_relevant_memories(
            query="async programming patterns",
            memory_types=["episodic", "semantic"],
            limit=5
        )
        
        for i, mem in enumerate(results):
            score = mem["scores"]["composite"]
            mem_type = mem["type"]
            if mem_type == "episodic":
                content = mem["properties"].get("content", "")[:60]
            else:
                content = mem["properties"].get("fact", "")[:60]
            print(f"   {i+1}. [{mem_type}] (score: {score:.3f}) {content}...")
        
        # Search with context
        print("\n6. Contextual search...")
        
        context_results = retrieval.search_with_context(
            query="debugging",
            user_id="user-alex",
            event_types=["interaction"],
            min_importance=0.5
        )
        
        print(f"   Found {len(context_results)} memories matching context")
        
        # Find applicable procedures
        print("\n7. Finding applicable procedures...")
        
        procedures = retrieval.retrieve_applicable_procedures(
            goal="debug an API issue",
            context="FastAPI application"
        )
        
        for proc in procedures:
            name = proc["properties"].get("workflowName")
            relevance = proc.get("relevance", 0)
            print(f"   - {name} (relevance: {relevance:.3f})")
        
        # Update recency scores
        print("\n8. Updating recency scores...")
        
        updated = decay.update_all_recency_scores("EpisodicMemory")
        print(f"   Updated {updated} episodic memories")
        
        # Get decay statistics
        print("\n9. Memory decay statistics...")
        
        stats = decay.get_decay_statistics("EpisodicMemory")
        print(f"   Total memories: {stats['total_memories']}")
        print(f"   Average recency: {stats['avg_recency']:.3f}")
        print(f"   Average importance: {stats['avg_importance']:.3f}")
        print(f"   Low fitness count: {stats['low_fitness_count']}")
        
        # System health report
        print("\n10. System health report...")
        
        report = metrics.generate_health_report()
        print(report)
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)
        
    finally:
        client.close()


if __name__ == "__main__":
    main()
