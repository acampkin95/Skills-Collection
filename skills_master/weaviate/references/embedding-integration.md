# Embedding Model Integration (v1.26+)

Weaviate v1.26+ supports multiple embedding providers with flexible module configuration. Configure vectorizers for your memory system: OpenAI, Cohere, Anthropic, Ollama, or local models.

---

## OpenAI Embeddings (Cloud-Based, Recommended for Production)

Latest models for high-quality embeddings:

```python
import weaviate
from weaviate.classes.config import Configure, Property, DataType
import os

client = weaviate.connect_to_local(
    port=8080,
    grpc_port=50051,
    headers={"X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]}
)

# Create collection with OpenAI text-embedding-3-small (1536 dims)
client.collections.create(
    name="EpisodicMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(
        model="text-embedding-3-small",  # $0.02 per 1M tokens, 1536 dims
        dimensions=1536
    ),
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="timestamp", data_type=DataType.DATE),
        Property(name="importance", data_type=DataType.NUMBER),
    ]
)

# Or use large model for higher quality
client.collections.create(
    name="SemanticMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(
        model="text-embedding-3-large",  # $0.13 per 1M tokens, 3072 dims
        dimensions=3072
    )
)
```

---

## Anthropic Embeddings (v1.26+ Native Support)

New in Weaviate v1.26 - native Anthropic integration:

```python
# Anthropic models require their own API configuration
client = weaviate.connect_to_local(
    headers={"X-Anthropic-Api-Key": os.environ["ANTHROPIC_API_KEY"]}
)

client.collections.create(
    name="AnthropicMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_anthropic(
        model="claude-embedding-1",  # Latest Anthropic embedding model
        dimensions=1024
    ),
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="timestamp", data_type=DataType.DATE),
    ]
)
```

---

## Cohere Embeddings

For multilingual support and domain specialization:

```python
client = weaviate.connect_to_local(
    headers={"X-Cohere-Api-Key": os.environ["COHERE_API_KEY"]}
)

# embed-english-v3.0: 1024 dims, optimized for retrieval
client.collections.create(
    name="MultilingualMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_cohere(
        model="embed-english-v3.0",
        input_type="search_document"  # or "search_query" when retrieving
    )
)

# For specialized domains
client.collections.create(
    name="DomainMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_cohere(
        model="embed-english-light-v3.0",  # Faster, smaller
        input_type="search_document"
    )
)
```

---

## Local Embeddings: Ollama

For privacy-preserving, offline embedding generation:

```python
# Start Ollama locally: ollama run nomic-embed-text

client.collections.create(
    name="LocalMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_ollama(
        api_endpoint="http://localhost:11434",
        model="nomic-embed-text"  # 768 dims, excellent quality
    ),
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="timestamp", data_type=DataType.DATE),
    ]
)

# Other quality options:
# - mxbai-embed-large: 1024 dims, high quality, slower
# - all-minilm:22m: 384 dims, fast, lower quality
# - all-mpnet-base-v2: 768 dims, balanced
```

---

## LM Studio Integration (OpenAI-Compatible)

For local LLM + embedding in one tool:

```yaml
# docker-compose.yml addition for local setup
environment:
  ENABLE_API_BASED_MODULES: 'true'
  ENABLE_MODULES: 'text2vec-openai,generative-openai'
```

```python
# LM Studio runs on localhost:1234 by default
client = weaviate.connect_to_local(
    port=8080,
    grpc_port=50051,
    headers={"X-OpenAI-Api-Key": "not-needed"}
)

# Point to LM Studio's OpenAI-compatible endpoint
client.collections.create(
    name="LocalEmbeddingMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(
        base_url="http://host.docker.internal:1234/v1",
        model="local-model"  # Whatever model you have loaded
    ),
    generative_config=Configure.Generative.openai(
        base_url="http://host.docker.internal:1234/v1",
        model="local-model"
    )
)
```

---

## Named Vectors for Multi-Aspect Memory (v1.26+)

Store multiple embeddings per memory for different retrieval patterns:

```python
from weaviate.classes.config import Configure, Property, DataType

client.collections.create(
    name="MultiAspectMemory",
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="summary", data_type=DataType.TEXT),
        Property(name="emotionalContext", data_type=DataType.TEXT),
        Property(name="keywords", data_type=DataType.TEXT_ARRAY),
    ],
    vectorizer_config=[
        # Content vector: full memory text for semantic search
        Configure.NamedVectors.text2vec_openai(
            name="content_vector",
            source_properties=["content"],
            model="text-embedding-3-small"
        ),
        # Summary vector: concise representation
        Configure.NamedVectors.text2vec_openai(
            name="summary_vector",
            source_properties=["summary"],
            model="text-embedding-3-small"
        ),
        # Emotional context: for mood/tone-based retrieval
        Configure.NamedVectors.text2vec_ollama(
            name="emotional_vector",
            source_properties=["emotionalContext"],
            api_endpoint="http://localhost:11434",
            model="nomic-embed-text"
        )
    ]
)

# Query specific vector space
collection = client.collections.get("MultiAspectMemory")

# Retrieve by emotional context
results = collection.query.near_text(
    query="user frustration with response time",
    target_vector="emotional_vector",
    limit=5
)

# Retrieve by summary
results = collection.query.near_text(
    query="quick overview of recent interactions",
    target_vector="summary_vector",
    limit=5
)
```

---

## Hybrid Query with Multiple Vectors

Combine semantic search across vector spaces:

```python
# Multi-vector hybrid search
results = collection.query.hybrid(
    query="user feedback on system performance",
    alpha=0.7,  # 70% semantic, 30% lexical
    target_vector="content_vector",  # Primary semantic space
    limit=10
)

# Or search emotional context with BM25 fallback
results = collection.query.hybrid(
    query="frustrated with latency",
    alpha=0.5,  # Balanced semantic and keyword
    target_vector="emotional_vector",
    limit=5
)
```

---

## Comparison: Which Model to Choose?

| Model | Cost | Quality | Speed | Best For |
|-------|------|---------|-------|----------|
| OpenAI text-embedding-3-small | $ | Excellent | Fast | Production RAG, general use |
| OpenAI text-embedding-3-large | $$ | Highest | Medium | High-accuracy semantic search |
| Anthropic embed-1 | $ | Excellent | Fast | Enterprises using Claude |
| Cohere embed-v3 | $$ | Excellent | Medium | Multilingual, retrieval-optimized |
| nomic-embed-text (Ollama) | Free | Excellent | Slow (CPU) | Privacy-critical, offline-first |
| mxbai-embed-large (Ollama) | Free | Very Good | Slower | Offline, highest accuracy |
| all-minilm (Ollama) | Free | Good | Fast | Low-resource deployments |

---

## Production Configuration Example

Recommended setup for scalable agent memory:

```python
import weaviate
from weaviate.classes.config import Configure, Property, DataType
import os

# Production: Use OpenAI for speed + quality
client = weaviate.connect_to_custom(
    host="memory.production.example.com",
    port=8080,
    grpc_port=50051,
    scheme="https",
    auth_credentials=weaviate.auth.BearerToken(os.environ["WEAVIATE_API_KEY"]),
    headers={"X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]}
)

# Episodic: Fast, semantic search
client.collections.create(
    name="EpisodicMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(
        model="text-embedding-3-small",
        dimensions=1536
    ),
    vector_index_config=Configure.VectorIndex.hnsw(
        quantizer=Configure.VectorIndex.Quantizer.sq()  # Scalar quantization
    ),
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="timestamp", data_type=DataType.DATE),
        Property(name="importance", data_type=DataType.NUMBER),
        Property(name="tenant_id", data_type=DataType.TEXT),  # Multi-tenancy
    ]
)

# Semantic: Higher quality for facts
client.collections.create(
    name="SemanticMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(
        model="text-embedding-3-large",
        dimensions=3072
    ),
    properties=[
        Property(name="fact", data_type=DataType.TEXT),
        Property(name="confidence", data_type=DataType.NUMBER),
        Property(name="domain", data_type=DataType.TEXT),
    ]
)
```

---

## Environment Setup

```bash
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
COHERE_API_KEY=...
WEAVIATE_API_KEY=secure-key-here

# For local development
OLLAMA_ENDPOINT=http://localhost:11434
LM_STUDIO_ENDPOINT=http://localhost:1234
```

All models integrate transparently with Weaviate's query APIs - switch models by changing config only, no code changes needed.
