"""
Unit tests for Weaviate Memory System.

Uses embedded Weaviate for isolation - no Docker required.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

# Test decay calculations (no Weaviate needed)
class TestDecayCalculations:
    """Test exponential decay without Weaviate connection."""
    
    def test_recency_score_fresh(self):
        """Fresh memories should have high recency."""
        import math
        
        half_life_days = 7
        age_days = 0
        
        # Exponential decay: 2^(-age/half_life)
        score = math.pow(2, -age_days / half_life_days)
        
        assert score == 1.0
    
    def test_recency_score_half_life(self):
        """At half-life, recency should be 0.5."""
        import math
        
        half_life_days = 7
        age_days = 7
        
        score = math.pow(2, -age_days / half_life_days)
        
        assert abs(score - 0.5) < 0.001
    
    def test_recency_score_old(self):
        """Old memories should have low recency."""
        import math
        
        half_life_days = 7
        age_days = 28  # 4 half-lives
        
        score = math.pow(2, -age_days / half_life_days)
        
        assert score < 0.1  # 2^-4 = 0.0625
    
    def test_fitness_calculation(self):
        """Test composite fitness scoring."""
        import math
        
        access_count = 10
        importance = 0.7
        recency = 0.5
        
        access_weight = 0.3
        importance_weight = 0.4
        recency_weight = 0.3
        
        access_score = min(1.0, math.log10(access_count + 1) / 2)
        
        fitness = (
            access_weight * access_score +
            importance_weight * importance +
            recency_weight * recency
        )
        
        assert 0 < fitness < 1
        assert fitness > 0.4  # Should be reasonably fit


class TestMemoryStoreMocked:
    """Test MemoryStore with mocked Weaviate client."""
    
    def test_store_episode_structure(self):
        """Verify episode structure is correct."""
        from weaviate_memory.store import MemoryStore
        
        # Mock client
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.data.insert = Mock(return_value="test-uuid")
        mock_collection.query.fetch_objects = Mock(return_value=Mock(objects=[]))
        mock_client.collections.get = Mock(return_value=mock_collection)
        
        store = MemoryStore(mock_client)
        
        uuid = store.store_episode(
            content="Test content",
            event_type="interaction",
            session_id="session-001",
            user_id="user-001",
            actions=["action1", "action2"],
            outcomes=["outcome1"],
            success_score=0.9,
            importance=0.7
        )
        
        # Verify insert was called
        assert mock_collection.data.insert.called
        
        # Get the properties that were passed
        call_args = mock_collection.data.insert.call_args
        properties = call_args.kwargs.get("properties", {})
        
        assert properties["content"] == "Test content"
        assert properties["eventType"] == "interaction"
        assert properties["sessionId"] == "session-001"
        assert properties["importanceScore"] == 0.7
        assert properties["recencyScore"] == 1.0
        assert properties["consolidatedToSemantic"] == False
    
    def test_store_semantic_fact_structure(self):
        """Verify semantic fact structure is correct."""
        from weaviate_memory.store import MemoryStore
        
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.data.insert = Mock(return_value="test-uuid")
        mock_client.collections.get = Mock(return_value=mock_collection)
        
        store = MemoryStore(mock_client)
        
        uuid = store.store_semantic_fact(
            fact="Python is great for AI",
            fact_type="opinion",
            domain="programming",
            confidence=0.8
        )
        
        call_args = mock_collection.data.insert.call_args
        properties = call_args.kwargs.get("properties", {})
        
        assert properties["fact"] == "Python is great for AI"
        assert properties["factType"] == "opinion"
        assert properties["domain"] == "programming"
        assert properties["confidenceScore"] == 0.8


class TestContextBuilder:
    """Test context building utilities."""
    
    def test_token_estimation(self):
        """Test token count estimation."""
        from weaviate_memory.context import ContextBuilder
        
        # Mock retrieval
        mock_retrieval = Mock()
        builder = ContextBuilder(mock_retrieval, max_tokens=4000)
        
        # ~4 chars per token
        text = "a" * 400  # Should be ~100 tokens
        estimated = builder.estimate_tokens(text)
        
        assert estimated == 100
    
    def test_memory_compression(self):
        """Test memory compression formats."""
        from weaviate_memory.context import ContextBuilder
        
        mock_retrieval = Mock()
        builder = ContextBuilder(mock_retrieval)
        
        # Episodic compression
        episodic = {"content": "A very long content string", "eventType": "interaction"}
        compressed = builder.compress_memory(episodic, "episodic")
        assert "[interaction]" in compressed
        
        # Semantic compression
        semantic = {"fact": "Important fact here"}
        compressed = builder.compress_memory(semantic, "semantic")
        assert "[FACT]" in compressed
        
        # Procedural compression
        procedural = {"workflowName": "Debug", "steps": ["step1", "step2", "step3"]}
        compressed = builder.compress_memory(procedural, "procedural")
        assert "[WORKFLOW: Debug]" in compressed


class TestConversationMemoryManager:
    """Test conversation history management."""
    
    def test_add_message(self):
        """Test adding messages to history."""
        from weaviate_memory.context import ConversationMemoryManager
        
        manager = ConversationMemoryManager(max_context_tokens=4000)
        
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi there!")
        
        assert len(manager.conversation_history) == 2
        assert manager.conversation_history[0]["role"] == "user"
        assert manager.conversation_history[1]["role"] == "assistant"
    
    def test_should_summarize(self):
        """Test summarization trigger."""
        from weaviate_memory.context import ConversationMemoryManager
        
        manager = ConversationMemoryManager(max_context_tokens=100)
        
        # Add enough to trigger summarization
        for i in range(20):
            manager.add_message("user", "This is a test message " * 10)
        
        # Should have compacted
        assert len(manager.summaries) > 0 or len(manager.conversation_history) < 20
    
    def test_get_last_n_messages(self):
        """Test retrieving recent messages."""
        from weaviate_memory.context import ConversationMemoryManager
        
        manager = ConversationMemoryManager()
        
        for i in range(10):
            manager.add_message("user", f"Message {i}")
        
        last_3 = manager.get_last_n_messages(3)
        
        assert len(last_3) == 3
        assert last_3[-1]["content"] == "Message 9"


# Integration tests (require Weaviate)
@pytest.fixture
def weaviate_client():
    """Create embedded Weaviate client for testing."""
    try:
        import weaviate
        from weaviate.embedded import EmbeddedOptions
        
        client = weaviate.WeaviateClient(
            embedded_options=EmbeddedOptions()
        )
        client.connect()
        yield client
        client.close()
    except Exception as e:
        pytest.skip(f"Embedded Weaviate not available: {e}")


@pytest.mark.integration
class TestIntegration:
    """Integration tests with embedded Weaviate."""
    
    def test_create_collections(self, weaviate_client):
        """Test collection creation."""
        from weaviate_memory.schemas import create_memory_collections
        
        collections = create_memory_collections(
            weaviate_client,
            use_ollama=False  # No vectorizer for testing
        )
        
        assert "episodic" in collections
        assert "semantic" in collections
        assert "procedural" in collections
    
    def test_store_and_retrieve(self, weaviate_client):
        """Test basic store and retrieve flow."""
        from weaviate_memory.schemas import create_memory_collections
        from weaviate_memory.store import MemoryStore
        
        create_memory_collections(weaviate_client, use_ollama=False)
        store = MemoryStore(weaviate_client)
        
        uuid = store.store_episode(
            content="Integration test memory",
            event_type="test",
            session_id="test-session",
            importance=0.5
        )
        
        assert uuid is not None
        assert len(uuid) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
