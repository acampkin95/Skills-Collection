# Memory Collection Schema Design

## Episodic Memory Collection

```python
from weaviate.classes.config import Configure, Property, DataType, Tokenization
from datetime import datetime

def create_episodic_memory_collection(client):
    """
    Episodic memory stores specific events with full spatiotemporal context.
    Enables case-based reasoning from past experiences.
    """
    return client.collections.create(
        name="EpisodicMemory",
        description="Stores specific events and interactions with temporal context",
        properties=[
            # Core content
            Property(
                name="content",
                data_type=DataType.TEXT,
                description="The memory content/description"
            ),
            Property(
                name="eventType",
                data_type=DataType.TEXT,
                tokenization=Tokenization.FIELD,
                description="Category: interaction, observation, decision, outcome"
            ),

            # Temporal context
            Property(name="timestamp", data_type=DataType.DATE),
            Property(name="sessionId", data_type=DataType.TEXT),
            Property(name="sequenceIndex", data_type=DataType.INT),

            # Actor context
            Property(name="actors", data_type=DataType.TEXT_ARRAY),
            Property(name="agentId", data_type=DataType.TEXT),
            Property(name="userId", data_type=DataType.TEXT),

            # Actions and outcomes
            Property(name="actionsTaken", data_type=DataType.TEXT_ARRAY),
            Property(name="observedOutcomes", data_type=DataType.TEXT_ARRAY),
            Property(name="successScore", data_type=DataType.NUMBER),

            # Context factors
            Property(name="contextFactors", data_type=DataType.TEXT_ARRAY),
            Property(
                name="metadata",
                data_type=DataType.OBJECT,
                nested_properties=[
                    Property(name="source", data_type=DataType.TEXT),
                    Property(name="confidence", data_type=DataType.NUMBER),
                    Property(name="tags", data_type=DataType.TEXT_ARRAY),
                ]
            ),

            # Memory management scores
            Property(name="importanceScore", data_type=DataType.NUMBER),
            Property(name="recencyScore", data_type=DataType.NUMBER),
            Property(name="accessCount", data_type=DataType.INT),
            Property(name="lastAccessedAt", data_type=DataType.DATE),

            # Consolidation tracking
            Property(name="consolidatedToSemantic", data_type=DataType.BOOL),
            Property(name="consolidationDate", data_type=DataType.DATE),
        ],
        vectorizer_config=Configure.Vectorizer.text2vec_ollama(
            api_endpoint="http://host.docker.internal:11434",
            model="nomic-embed-text"
        ),
    )
```

## Semantic Memory Collection

```python
def create_semantic_memory_collection(client):
    """
    Semantic memory stores generalized facts without temporal binding.
    Represents distilled knowledge from episodic experiences.
    """
    return client.collections.create(
        name="SemanticMemory",
        description="Stores generalized facts and knowledge",
        properties=[
            # Core fact
            Property(name="fact", data_type=DataType.TEXT),
            Property(
                name="factType",
                data_type=DataType.TEXT,
                tokenization=Tokenization.FIELD,
                description="Type: preference, fact, rule, relationship"
            ),

            # Classification
            Property(name="domain", data_type=DataType.TEXT),
            Property(name="category", data_type=DataType.TEXT),
            Property(name="tags", data_type=DataType.TEXT_ARRAY),

            # Relationships
            Property(name="relatedConcepts", data_type=DataType.TEXT_ARRAY),
            Property(name="contradicts", data_type=DataType.TEXT_ARRAY),
            Property(name="supports", data_type=DataType.TEXT_ARRAY),

            # Applicability
            Property(name="applicabilityConditions", data_type=DataType.TEXT),
            Property(name="exceptions", data_type=DataType.TEXT_ARRAY),

            # Provenance
            Property(name="derivedFromEpisodes", data_type=DataType.TEXT_ARRAY),
            Property(name="sourceDocuments", data_type=DataType.TEXT_ARRAY),
            Property(name="confidenceScore", data_type=DataType.NUMBER),

            # Lifecycle
            Property(name="createdAt", data_type=DataType.DATE),
            Property(name="lastUpdated", data_type=DataType.DATE),
            Property(name="lastValidated", data_type=DataType.DATE),
            Property(name="usageFrequency", data_type=DataType.INT),
            Property(name="importanceScore", data_type=DataType.NUMBER),
        ],
        vectorizer_config=Configure.Vectorizer.text2vec_ollama(
            api_endpoint="http://host.docker.internal:11434",
            model="nomic-embed-text"
        ),
    )
```

## Procedural Memory Collection

```python
def create_procedural_memory_collection(client):
    """
    Procedural memory stores learned workflows and skill sequences.
    Enables execution of complex multi-step processes.
    """
    return client.collections.create(
        name="ProceduralMemory",
        description="Stores learned workflows and methods",
        properties=[
            # Workflow identity
            Property(name="workflowName", data_type=DataType.TEXT),
            Property(name="workflowDescription", data_type=DataType.TEXT),
            Property(name="goalType", data_type=DataType.TEXT),

            # Prerequisites
            Property(name="prerequisiteStates", data_type=DataType.TEXT_ARRAY),
            Property(name="requiredInputs", data_type=DataType.TEXT_ARRAY),
            Property(name="requiredTools", data_type=DataType.TEXT_ARRAY),

            # Steps
            Property(name="steps", data_type=DataType.TEXT_ARRAY),
            Property(
                name="decisionPoints",
                data_type=DataType.OBJECT_ARRAY,
                nested_properties=[
                    Property(name="stepIndex", data_type=DataType.INT),
                    Property(name="condition", data_type=DataType.TEXT),
                    Property(name="ifTrue", data_type=DataType.TEXT),
                    Property(name="ifFalse", data_type=DataType.TEXT),
                ]
            ),

            # Outcomes
            Property(name="expectedOutputs", data_type=DataType.TEXT_ARRAY),
            Property(name="successCriteria", data_type=DataType.TEXT_ARRAY),
            Property(name="failureModes", data_type=DataType.TEXT_ARRAY),

            # Performance metrics
            Property(name="successRate", data_type=DataType.NUMBER),
            Property(name="avgExecutionTime", data_type=DataType.NUMBER),
            Property(name="executionCount", data_type=DataType.INT),
            Property(name="lastExecuted", data_type=DataType.DATE),

            # Applicability
            Property(name="applicableContexts", data_type=DataType.TEXT_ARRAY),
            Property(name="incompatibleWith", data_type=DataType.TEXT_ARRAY),

            # Versioning
            Property(name="version", data_type=DataType.INT),
            Property(name="refinementHistory", data_type=DataType.TEXT_ARRAY),
            Property(name="createdAt", data_type=DataType.DATE),
            Property(name="lastModified", data_type=DataType.DATE),
        ],
        vectorizer_config=Configure.Vectorizer.text2vec_ollama(
            api_endpoint="http://host.docker.internal:11434",
            model="nomic-embed-text"
        ),
    )
```

## Working Memory Collection (Short-Term Context)

```python
def create_working_memory_collection(client):
    """
    Working memory holds active context for current session.
    Fast access, auto-expires, bridges to long-term memory.
    """
    return client.collections.create(
        name="WorkingMemory",
        description="Active session context and scratchpad",
        properties=[
            Property(name="content", data_type=DataType.TEXT),
            Property(name="contextType", data_type=DataType.TEXT),
            Property(name="sessionId", data_type=DataType.TEXT),
            Property(name="turnIndex", data_type=DataType.INT),
            Property(name="timestamp", data_type=DataType.DATE),
            Property(name="expiresAt", data_type=DataType.DATE),
            Property(name="promoteTpLongTerm", data_type=DataType.BOOL),
            Property(name="relatedLongTermMemories", data_type=DataType.TEXT_ARRAY),
        ],
        vectorizer_config=Configure.Vectorizer.text2vec_ollama(
            api_endpoint="http://host.docker.internal:11434",
            model="nomic-embed-text"
        ),
    )
```
