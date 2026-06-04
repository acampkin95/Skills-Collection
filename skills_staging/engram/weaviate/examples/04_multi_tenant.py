#!/usr/bin/env python3
"""
Example: Multi-tenant memory isolation for multiple agents/users.

Demonstrates:
- Per-tenant memory isolation
- Hybrid architecture (shared + tenant-specific)
- Tenant-specific overrides of shared knowledge
"""

import weaviate
from weaviate_memory import (
    create_memory_collections,
    create_multi_tenant_collections,
    TenantMemoryManager,
    HybridMemoryArchitecture,
    MemoryStore
)


def main():
    client = weaviate.connect_to_local(
        host="localhost",
        port=8080,
        grpc_port=50051
    )
    
    try:
        print("=" * 60)
        print("MULTI-TENANT MEMORY EXAMPLE")
        print("=" * 60)
        
        # Create both standard and multi-tenant collections
        print("\n1. Creating collections...")
        
        create_memory_collections(client)
        create_multi_tenant_collections(client)
        
        print("   Created standard and multi-tenant collections")
        
        # Initialize tenant managers for different agents
        print("\n2. Initializing tenant managers...")
        
        agent_alpha = TenantMemoryManager(client, "agent-alpha")
        agent_beta = TenantMemoryManager(client, "agent-beta")
        
        print("   Created managers for agent-alpha and agent-beta")
        
        # Store memories for agent-alpha
        print("\n3. Storing memories for agent-alpha...")
        
        alpha_memories = [
            ("Helped user with Python debugging using print statements", "interaction"),
            ("User prefers detailed explanations with examples", "observation"),
            ("Successfully resolved async deadlock issue", "achievement"),
        ]
        
        for content, event_type in alpha_memories:
            agent_alpha.store_memory(
                content=content,
                memory_type="episodic",
                event_type=event_type,
                importance=0.7
            )
            print(f"   Stored: {content[:50]}...")
        
        # Store memories for agent-beta
        print("\n4. Storing memories for agent-beta...")
        
        beta_memories = [
            ("Assisted with Docker deployment troubleshooting", "interaction"),
            ("User wants concise, actionable responses only", "observation"),
            ("Implemented CI/CD pipeline for the project", "achievement"),
        ]
        
        for content, event_type in beta_memories:
            agent_beta.store_memory(
                content=content,
                memory_type="episodic",
                event_type=event_type,
                importance=0.7
            )
            print(f"   Stored: {content[:50]}...")
        
        # Verify isolation
        print("\n5. Verifying memory isolation...")
        
        alpha_all = agent_alpha.get_all_memories(limit=10)
        beta_all = agent_beta.get_all_memories(limit=10)
        
        print(f"   agent-alpha memories: {len(alpha_all)}")
        print(f"   agent-beta memories: {len(beta_all)}")
        
        # Search within tenant
        print("\n6. Searching within tenant scope...")
        
        alpha_results = agent_alpha.search_memories("debugging", limit=5)
        beta_results = agent_beta.search_memories("debugging", limit=5)
        
        print(f"   agent-alpha 'debugging' results: {len(alpha_results)}")
        for r in alpha_results:
            print(f"     - {r['properties'].get('content', '')[:50]}...")
        
        print(f"   agent-beta 'debugging' results: {len(beta_results)}")
        for r in beta_results:
            print(f"     - {r['properties'].get('content', '')[:50]}...")
        
        # Hybrid architecture demo
        print("\n7. Demonstrating hybrid architecture...")
        
        # Initialize shared knowledge store
        store = MemoryStore(client)
        
        # Store shared knowledge
        store.store_semantic_fact(
            fact="Python 3.11+ has significant performance improvements",
            fact_type="fact",
            domain="python",
            confidence=0.95
        )
        
        store.store_semantic_fact(
            fact="Docker containers should have resource limits in production",
            fact_type="best_practice",
            domain="docker",
            confidence=0.9
        )
        
        print("   Stored shared knowledge")
        
        # Create hybrid architecture for agent-alpha
        hybrid_alpha = HybridMemoryArchitecture(client, "agent-alpha")
        
        # Store tenant-specific override
        hybrid_alpha.store_tenant_override(
            fact="For this project, Python 3.10 is required due to dependencies",
            domain="python",
            confidence=0.95
        )
        
        print("   agent-alpha has tenant-specific Python override")
        
        # Retrieve with overrides
        print("\n8. Retrieving knowledge with overrides...")
        
        python_knowledge = hybrid_alpha.retrieve_knowledge_with_overrides(
            query="Python version requirements",
            limit=5
        )
        
        for item in python_knowledge:
            source = item["source"]
            props = item["properties"]
            fact = props.get("fact", "")[:60]
            print(f"   [{source}] {fact}...")
        
        # Clean up demo tenant data
        print("\n9. Cleanup...")
        
        # Note: In production you'd be more careful about cleanup
        print("   Tenant data would persist until explicitly cleared")
        
        print("\n" + "=" * 60)
        print("Multi-tenant example completed!")
        print("=" * 60)
        
    finally:
        client.close()


if __name__ == "__main__":
    main()
