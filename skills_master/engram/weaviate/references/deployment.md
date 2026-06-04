# Weaviate Docker Deployment (v1.26+)

Production deployment patterns for Weaviate v1.26+ with Docker Compose. Covers single-node and HA multi-node setups with modern security, monitoring, and resource management.

---

## Production Single-Node Configuration (v1.26+)

```yaml
version: '3.8'

services:
  weaviate:
    image: cr.weaviate.io/semitechnologies/weaviate:1.26.0
    command: ["--host", "0.0.0.0", "--port", "8080", "--scheme", "http"]
    restart: unless-stopped
    ports:
      - "8080:8080"    # REST API
      - "50051:50051"  # gRPC (required for async Python v4 client)
      - "2112:2112"    # Prometheus metrics

    volumes:
      - weaviate_memory_data:/var/lib/weaviate
      - ./backups:/var/lib/weaviate/backups

    environment:
      # Core Configuration
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      QUERY_DEFAULTS_LIMIT: 25
      QUERY_MAXIMUM_RESULTS: 10000
      CLUSTER_HOSTNAME: 'memory-node-1'

      # Memory Management (v1.26+ scalar quantization support)
      GOMEMLIMIT: '6GiB'  # 75-80% of container memory
      LIMIT_RESOURCES: 'true'
      DISK_USE_WARNING_PERCENTAGE: 80
      DISK_USE_READONLY_PERCENTAGE: 90

      # Authentication & Authorization
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: '${WEAVIATE_API_KEY}'
      AUTHENTICATION_APIKEY_USERS: 'memory-admin'

      # Module Configuration (v1.26+ enhancements)
      ENABLE_API_BASED_MODULES: 'true'
      ENABLE_MODULES: 'text2vec-openai,text2vec-ollama,generative-openai,backup-filesystem'

      # Monitoring & Observability
      PROMETHEUS_MONITORING_ENABLED: 'true'
      PROMETHEUS_MONITORING_PORT: 2112

      # Vector Search Enhancements (v1.26+)
      VECTOR_INDEX_CONFIG: |
        {
          "vectorIndexType": "hnsw",
          "vectorizer": "text2vec-openai"
        }

    healthcheck:
      test: ["CMD", "curl", "-f", "-H", "Authorization: Bearer ${WEAVIATE_API_KEY}", "http://localhost:8080/v1/.well-known/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  weaviate_memory_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data
```

---

## Environment Variables (.env file)

```bash
# Weaviate Configuration
WEAVIATE_API_KEY=secure-api-key-here-min-32-chars
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8080
WEAVIATE_GRPC_PORT=50051

# Embedding Provider (choose one)
# For OpenAI:
OPENAI_API_KEY=sk-...
OPENAI_MODEL=text-embedding-3-small

# For Ollama (local):
OLLAMA_API_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text

# Resource Limits
MEMORY_LIMIT=8Gi
CPU_LIMIT=4000m
```

---

## High-Availability Multi-Node Setup (3-Node Raft)

For production with fault tolerance:

```yaml
version: '3.8'

services:
  weaviate-memory-1:
    image: cr.weaviate.io/semitechnologies/weaviate:1.26.0
    init: true
    command: ["--host", "0.0.0.0", "--port", "8080", "--scheme", "http"]
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "50051:50051"
      - "2112:2112"

    volumes:
      - ./data-memory-1:/var/lib/weaviate
      - ./backups:/var/lib/weaviate/backups

    environment:
      # Node Identity
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      CLUSTER_HOSTNAME: 'memory-1'
      CLUSTER_GOSSIP_BIND_PORT: '7100'
      CLUSTER_DATA_BIND_PORT: '7101'

      # Raft Consensus (v1.26+)
      RAFT_JOIN: 'memory-1,memory-2,memory-3'
      RAFT_BOOTSTRAP_EXPECT: 3

      # Memory & Resources
      GOMEMLIMIT: '8GiB'
      LIMIT_RESOURCES: 'true'

      # Authentication
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: '${WEAVIATE_API_KEY}'

      # Modules
      ENABLE_API_BASED_MODULES: 'true'
      ENABLE_MODULES: 'text2vec-openai,text2vec-ollama,generative-openai,backup-filesystem'

      # Monitoring
      PROMETHEUS_MONITORING_ENABLED: 'true'

    healthcheck:
      test: ["CMD", "curl", "-f", "-H", "Authorization: Bearer ${WEAVIATE_API_KEY}", "http://localhost:8080/v1/.well-known/ready"]
      interval: 30s
      timeout: 10s
      retries: 3

  weaviate-memory-2:
    image: cr.weaviate.io/semitechnologies/weaviate:1.26.0
    init: true
    command: ["--host", "0.0.0.0", "--port", "8080", "--scheme", "http"]
    restart: unless-stopped
    ports:
      - "8081:8080"
      - "50052:50051"
      - "2113:2112"

    volumes:
      - ./data-memory-2:/var/lib/weaviate
      - ./backups:/var/lib/weaviate/backups

    depends_on:
      - weaviate-memory-1

    environment:
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      CLUSTER_HOSTNAME: 'memory-2'
      CLUSTER_GOSSIP_BIND_PORT: '7102'
      CLUSTER_DATA_BIND_PORT: '7103'
      CLUSTER_JOIN: 'weaviate-memory-1:7100'
      RAFT_JOIN: 'memory-1,memory-2,memory-3'
      RAFT_BOOTSTRAP_EXPECT: 3
      GOMEMLIMIT: '8GiB'
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: '${WEAVIATE_API_KEY}'
      ENABLE_API_BASED_MODULES: 'true'
      ENABLE_MODULES: 'text2vec-openai,text2vec-ollama,generative-openai,backup-filesystem'
      PROMETHEUS_MONITORING_ENABLED: 'true'

    healthcheck:
      test: ["CMD", "curl", "-f", "-H", "Authorization: Bearer ${WEAVIATE_API_KEY}", "http://localhost:8080/v1/.well-known/ready"]
      interval: 30s
      timeout: 10s
      retries: 3

  weaviate-memory-3:
    image: cr.weaviate.io/semitechnologies/weaviate:1.26.0
    init: true
    command: ["--host", "0.0.0.0", "--port", "8080", "--scheme", "http"]
    restart: unless-stopped
    ports:
      - "8082:8080"
      - "50053:50051"
      - "2114:2112"

    volumes:
      - ./data-memory-3:/var/lib/weaviate
      - ./backups:/var/lib/weaviate/backups

    depends_on:
      - weaviate-memory-1

    environment:
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      CLUSTER_HOSTNAME: 'memory-3'
      CLUSTER_GOSSIP_BIND_PORT: '7104'
      CLUSTER_DATA_BIND_PORT: '7105'
      CLUSTER_JOIN: 'weaviate-memory-1:7100'
      RAFT_JOIN: 'memory-1,memory-2,memory-3'
      RAFT_BOOTSTRAP_EXPECT: 3
      GOMEMLIMIT: '8GiB'
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: '${WEAVIATE_API_KEY}'
      ENABLE_API_BASED_MODULES: 'true'
      ENABLE_MODULES: 'text2vec-openai,text2vec-ollama,generative-openai,backup-filesystem'
      PROMETHEUS_MONITORING_ENABLED: 'true'

    healthcheck:
      test: ["CMD", "curl", "-f", "-H", "Authorization: Bearer ${WEAVIATE_API_KEY}", "http://localhost:8080/v1/.well-known/ready"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  data-memory-1:
    driver: local
  data-memory-2:
    driver: local
  data-memory-3:
    driver: local
```

---

## Connection Setup for Deployment Targets

### Local Docker (development)
```python
import weaviate

with weaviate.connect_to_local(
    port=8080,
    grpc_port=50051,
    headers={"Authorization": f"Bearer {api_key}"}
) as client:
    # Operations
    pass
```

### Remote Server/Production
```python
client = weaviate.connect_to_custom(
    host="memory.example.com",
    port=8080,
    grpc_port=50051,
    scheme="https",
    auth_credentials=weaviate.auth.BearerToken(api_key),
    skip_init_checks=False  # Validate connection on init
)
```

### Kubernetes Helm Chart
Use official Weaviate Helm chart:
```bash
helm repo add weaviate https://charts.weaviate.io
helm install weaviate weaviate/weaviate \
  --set image.tag=1.26.0 \
  --set persistenceVolume.enabled=true \
  --set persistenceVolume.size=50Gi
```

---

## Monitoring & Maintenance

### Prometheus Metrics (v1.26+)
Access at `http://localhost:2112/metrics`. Key metrics:
- `weaviate_objects_total` - Number of objects per collection
- `weaviate_query_duration_seconds` - Query latency
- `weaviate_batch_duration_seconds` - Batch operation timing
- `weaviate_vectorindex_size_bytes` - Vector index memory usage

### Backup Strategy
```bash
# Filesystem backup (included in compose)
curl -X POST http://localhost:8080/v1/backups/filesystem \
  -H "Authorization: Bearer $WEAVIATE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path": "/var/lib/weaviate/backups"}'

# Restore from backup
curl -X POST http://localhost:8080/v1/backups/filesystem/restore \
  -H "Authorization: Bearer $WEAVIATE_API_KEY" \
  -d '{"backupIdentifier": "backup-name"}'
```

### Memory Monitoring
```python
# Check collection sizes
with weaviate.connect_to_local() as client:
    for collection_name in ["EpisodicMemory", "SemanticMemory"]:
        col = client.collections.get(collection_name)
        count = col.aggregate.over_all()
        print(f"{collection_name}: {count} objects")
```

---

## v1.26 New Features for Deployment

1. **Scalar Quantization (SQ)**: 75% storage reduction for vectors
2. **Async Replication**: Non-blocking data sync in clusters
3. **Multi-target Vector Search**: Query across multiple vector spaces
4. **Improved Range Filters**: Efficient metadata filtering
5. **gRPC Streaming**: Faster batch operations (async Python client)

Enable SQ in collection config:
```python
from weaviate.classes.config import Recalibrate

collection = client.collections.create(
    name="QuantizedMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    vector_index_config=Configure.VectorIndex.hnsw(
        quantizer=Configure.VectorIndex.Quantizer.sq()
    )
)
```
