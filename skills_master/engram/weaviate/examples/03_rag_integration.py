#!/usr/bin/env python3
"""
Example: RAG (Retrieval-Augmented Generation) with memory context.

Demonstrates:
- Building context from memories
- Per-object generation
- Synthesized responses from multiple memories
- Full context RAG pipeline
"""

import weaviate
from weaviate_memory import (
    create_memory_collections,
    MemoryStore,
    MemoryRetrieval,
    ContextBuilder,
    MemoryAugmentedRAG
)


def main():
    client = weaviate.connect_to_local(
        host="localhost",
        port=8080,
        grpc_port=50051
    )
    
    try:
        print("=" * 60)
        print("RAG WITH MEMORY CONTEXT EXAMPLE")
        print("=" * 60)
        
        # Initialize
        create_memory_collections(
            client,
            use_ollama=True,
            generative_model="llama3.2"  # Or your preferred model
        )
        store = MemoryStore(client)
        retrieval = MemoryRetrieval(client)
        context_builder = ContextBuilder(retrieval, max_tokens=4000)
        rag = MemoryAugmentedRAG(client)
        
        # Populate with sample memories
        print("\n1. Populating memory with experiences...")
        
        memories = [
            {
                "content": "Successfully implemented caching with Redis reducing API response time by 60%",
                "event_type": "implementation",
                "actions": ["designed_cache_strategy", "implemented_redis", "benchmarked"],
                "outcomes": ["performance_improved", "user_satisfaction_up"],
                "success_score": 0.95
            },
            {
                "content": "Attempted to use Memcached but Redis was better fit for complex data structures",
                "event_type": "decision",
                "actions": ["evaluated_memcached", "compared_features", "chose_redis"],
                "outcomes": ["informed_decision", "right_tool_selected"],
                "success_score": 0.9
            },
            {
                "content": "Database query optimization reduced page load from 3s to 200ms",
                "event_type": "optimization",
                "actions": ["profiled_queries", "added_indexes", "rewrote_n+1"],
                "outcomes": ["dramatic_improvement", "happy_stakeholders"],
                "success_score": 0.98
            },
            {
                "content": "User prefers seeing performance metrics with before/after comparisons",
                "event_type": "observation",
                "actions": ["noted_preference"],
                "outcomes": ["communication_improved"],
                "success_score": 0.8
            }
        ]
        
        for mem in memories:
            store.store_episode(
                content=mem["content"],
                event_type=mem["event_type"],
                session_id="rag-demo",
                user_id="user-alex",
                actions=mem["actions"],
                outcomes=mem["outcomes"],
                success_score=mem["success_score"],
                importance=0.7
            )
        
        # Add semantic facts
        store.store_semantic_fact(
            fact="Redis is preferred over Memcached for complex caching scenarios",
            fact_type="insight",
            domain="caching",
            confidence=0.9
        )
        
        store.store_semantic_fact(
            fact="Performance optimizations should be measured with before/after metrics",
            fact_type="best_practice",
            domain="performance",
            confidence=0.95
        )
        
        print(f"   Stored {len(memories)} episodes and 2 semantic facts")
        
        # Build context for a query
        print("\n2. Building context for query...")
        
        query = "How should I approach improving API performance?"
        
        context = context_builder.build_context_for_query(
            query=query,
            include_episodic=True,
            include_semantic=True,
            user_id="user-alex"
        )
        
        print(f"   Context length: {len(context)} chars")
        print(f"   Estimated tokens: {context_builder.estimate_tokens(context)}")
        print("\n   Context preview:")
        print("   " + "-" * 40)
        for line in context.split("\n")[:10]:
            print(f"   {line}")
        print("   ...")
        
        # RAG with synthesis
        print("\n3. Generating synthesized response...")
        
        synthesis_result = rag.generate_synthesis(
            query=query,
            limit=5
        )
        
        print(f"   Source memories used: {len(synthesis_result['source_memories'])}")
        print("\n   Synthesized response:")
        print("   " + "-" * 40)
        if synthesis_result.get("synthesis"):
            response_lines = synthesis_result["synthesis"].split("\n")
            for line in response_lines[:15]:
                print(f"   {line}")
        else:
            print("   (Generative module not configured - showing retrieval results)")
            for mem in synthesis_result["source_memories"][:3]:
                print(f"   - {mem.get('content', '')[:80]}...")
        
        # Full context RAG
        print("\n4. Full context RAG pipeline...")
        
        full_result = rag.answer_with_full_context(
            query="What caching strategies have worked well?",
            user_id="user-alex"
        )
        
        print(f"   Sources used: {full_result['source_count']}")
        print("\n   Source types:")
        for source in full_result["sources"]:
            print(f"   - [{source['type']}] {source['content']}...")
        
        # Multi-collection RAG
        print("\n5. Multi-collection RAG...")
        
        multi_result = rag.multi_collection_rag(
            query="performance optimization techniques",
            collections=["EpisodicMemory", "SemanticMemory"],
            limit_per_collection=3
        )
        
        print(f"   Results across collections: {multi_result['result_count']}")
        print("\n   Combined context:")
        print("   " + "-" * 40)
        for line in multi_result["context"].split("\n")[:8]:
            print(f"   {line}")
        
        print("\n" + "=" * 60)
        print("RAG example completed!")
        print("=" * 60)
        
    finally:
        client.close()


if __name__ == "__main__":
    main()
