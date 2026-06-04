# Advanced Prompt Techniques

## RAG (Retrieval Augmented Generation)

### Embedding & Chunking

```ts
// Chunk sizing by content type
const chunkSizes = {
  technicalDocs: { size: 600, overlap: 100 },  // Preserve code blocks
  legal: { size: 400, overlap: 50 },           // Precise clause retrieval
  faq: { size: 300, overlap: 25 },             // One Q&A per chunk
  articles: { size: 1000, overlap: 150 },      // Narrative flow
};

// Embedding prepending (model-dependent hint)
const docChunk = `search_document: ${documentText}`;
const query = `search_query: ${userQuestion}`;
```

### Query Expansion (HyDE)

Generate hypothetical document embeddings to improve retrieval:
```ts
async function expandQuery(question: string) {
  // Generate hypothetical answer
  const hypothesis = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 200,
    messages: [{ role: "user", content: `Write a brief answer to: ${question}` }],
  });

  // Embed both question and hypothesis, search with both
  const questionEmb = await embed(question);
  const hypothesisEmb = await embed(hypothesis.content[0].text);

  // Blend embeddings or search separately and merge results
}
```

### Re-ranking

Use a cross-encoder to re-rank top-K results:
```ts
// After retrieving 10 candidates, re-rank with semantic similarity
const topK = 5;
const scored = candidates.map(c => ({
  ...c,
  score: cosineSimilarity(query, c.text)
})).sort((a, b) => b.score - a.score).slice(0, topK);
```

## Extended Thinking (Claude 4.6+)

For complex reasoning, use adaptive thinking:
```ts
const response = await client.messages.create({
  model: "claude-opus-4-20250514",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000  // Let model use up to 10K tokens for thinking
  },
  messages: [{ role: "user", content: complexProblem }],
});

// response.content[0] will include thinking_block with reasoning
```

**Note:** If thinking inflates token usage, constrain with explicit instructions: "You should spend about 1-2 seconds thinking about this before answering."

## Token Optimization Tactics

1. **Abbreviate examples:** Instead of 20-line few-shot examples, use 3-5 lines
2. **Use JSON for structured input:** XML tags take more tokens than JSON
3. **Compress context:** Use bullet-point summaries instead of prose
4. **Dedup instruction:** After 10 successful calls, stop repeating rules the model clearly knows
5. **Late binding:** Send variable parts (documents, queries) only when needed

## Conversation Context Management

When approaching token limits:
```ts
async function summarizeHistory(messages: Message[]): Promise<string> {
  // Summarize old messages, keep last 3-5 exchanges
  const response = await client.messages.create({
    model: "claude-haiku-3-5-20241022",
    max_tokens: 300,
    system: "Summarize this conversation in bullet points. Keep key facts, decisions.",
    messages: [{ role: "user", content: JSON.stringify(messages) }],
  });
  return response.content[0].text;
}

// Use as: [system, { role: "user", content: `Context:\n${summary}` }, ...recent]
```

## Few-Shot vs. Zero-Shot

- **Few-shot:** Use when output format is complex (JSON with nested arrays) or task is nuanced (tone/style)
- **Zero-shot:** Often sufficient for classification, NER, summarization if system prompt is clear
- **Trade-off:** 1-2 good examples >> 10 mediocre examples. Pick examples that cover edge cases

## Cost-Benefit Analysis

| Technique | Cost Increase | Quality Gain | Best For |
|-----------|---------------|--------------|----------|
| Few-shot (2 examples) | +400 tokens | +5-10% | Format/nuance |
| Chain-of-Thought | +30% tokens | +10-20% | Complex reasoning |
| Prompt caching (5K+ prefix) | +25% first call, -90% reads | Time saved | Repeated queries |
| Batching (10 requests) | -10% per request | Same quality | High-volume |

## Extended Thinking vs. Chain-of-Thought

- **Extended thinking:** Model's internal reasoning, not shown. Use for hard problems (research, debugging).
- **Chain-of-Thought:** Explicit reasoning steps. Use when you need explainability or the task is moderately complex.
- **Combo:** Extended thinking + explicit final summary for best results on very hard problems.
