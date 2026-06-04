# Claude / Anthropic API Reference

## Setup

```bash
npm install @anthropic-ai/sdk
```

```ts
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});
```

## Messages API

### Basic Request

```ts
const message = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [
    { role: "user", content: "Explain quantum computing in one paragraph." }
  ],
});

console.log(message.content[0].text);
```

### System Prompt

```ts
const message = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  system: "You are a helpful coding assistant. Always include code examples.",
  messages: [
    { role: "user", content: "How do I read a file in Node.js?" }
  ],
});
```

### Multi-Turn Conversation

```ts
const message = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [
    { role: "user", content: "What is TypeScript?" },
    { role: "assistant", content: "TypeScript is a typed superset of JavaScript..." },
    { role: "user", content: "Show me an example of generics." },
  ],
});
```

## Streaming

```ts
const stream = client.messages.stream({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Write a poem about coding." }],
});

for await (const event of stream) {
  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
    process.stdout.write(event.delta.text);
  }
}

// Or use the helper
const stream2 = client.messages.stream({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello" }],
});

stream2.on("text", (text) => process.stdout.write(text));

const finalMessage = await stream2.finalMessage();
```

## Tool Use (Function Calling)

### Define and Use Tools

```ts
const response = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  tools: [
    {
      name: "get_weather",
      description: "Get the current weather for a location. Use when the user asks about weather.",
      input_schema: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "City name, e.g. 'San Francisco, CA'",
          },
          unit: {
            type: "string",
            enum: ["celsius", "fahrenheit"],
            description: "Temperature unit",
          },
        },
        required: ["location"],
      },
    },
  ],
  messages: [{ role: "user", content: "What's the weather in Tokyo?" }],
});

// Check if model wants to use a tool
const toolUse = response.content.find((b) => b.type === "tool_use");
if (toolUse) {
  console.log("Tool:", toolUse.name);
  console.log("Input:", toolUse.input);
  // { location: "Tokyo", unit: "celsius" }

  // Execute the tool, then send result back
  const weatherData = await fetchWeather(toolUse.input);

  const followUp = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1024,
    tools: [/* same tools */],
    messages: [
      { role: "user", content: "What's the weather in Tokyo?" },
      { role: "assistant", content: response.content },
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: toolUse.id,
            content: JSON.stringify(weatherData),
          },
        ],
      },
    ],
  });
}
```

### Force Tool Use

```ts
// Force the model to use a specific tool
const response = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  tool_choice: { type: "tool", name: "extract_data" },
  tools: [{ name: "extract_data", /* ... */ }],
  messages: [{ role: "user", content: text }],
});

// Force any tool (model must use at least one)
tool_choice: { type: "any" }

// Let model decide (default)
tool_choice: { type: "auto" }
```

## Vision (Images / Multimodal)

### Base64 Image

```ts
const message = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: [
        {
          type: "image",
          source: {
            type: "base64",
            media_type: "image/png",
            data: base64ImageData,
          },
        },
        {
          type: "text",
          text: "Describe what you see in this image.",
        },
      ],
    },
  ],
});
```

### URL Image

```ts
const message = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: [
      {
        type: "image",
        source: {
          type: "url",
          url: "https://example.com/image.png",
        },
      },
      { type: "text", text: "What's in this image?" },
    ],
  }],
});
```

### Multi-Image Analysis

```ts
// Compare two images or analyze multiple
const message = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: [
      {
        type: "image",
        source: { type: "base64", media_type: "image/png", data: beforeImage },
      },
      {
        type: "image",
        source: { type: "base64", media_type: "image/png", data: afterImage },
      },
      {
        type: "text",
        text: "Compare these two UI screenshots. List all visual differences.",
      },
    ],
  }],
});
```

### Vision Use Cases

| Task | Prompt Pattern |
|------|---------------|
| OCR / text extraction | "Extract all text from this image verbatim" |
| UI review | "Review this UI for accessibility issues" |
| Chart reading | "Extract the data points from this chart as JSON" |
| Diagram → code | "Convert this wireframe to React JSX with Tailwind" |
| Document analysis | "Summarize the key points from this document page" |

## Extended Thinking

```ts
const response = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000,  // max tokens for thinking
  },
  messages: [
    { role: "user", content: "Solve this complex math problem..." },
  ],
});

// Response includes thinking blocks
for (const block of response.content) {
  if (block.type === "thinking") {
    console.log("Thinking:", block.thinking);
  }
  if (block.type === "text") {
    console.log("Answer:", block.text);
  }
}
```

### Extended Thinking Best Practices

- **Budget sizing**: Start with 5,000-10,000 tokens. Increase for harder problems.
- **When to use**: Complex math, multi-step reasoning, code architecture, debugging
- **When NOT to use**: Simple Q&A, classification, formatting tasks (wastes tokens)
- **Streaming with thinking**: Thinking blocks stream first, then text blocks

```ts
// Streaming with extended thinking
const stream = client.messages.stream({
  model: "claude-sonnet-4-20250514",
  max_tokens: 16000,
  thinking: { type: "enabled", budget_tokens: 8000 },
  messages: [{ role: "user", content: complexQuestion }],
});

for await (const event of stream) {
  if (event.type === "content_block_start") {
    if (event.content_block.type === "thinking") {
      process.stdout.write("[Thinking...]\n");
    }
  }
  if (event.type === "content_block_delta") {
    if (event.delta.type === "thinking_delta") {
      // Optionally show thinking to user
      process.stdout.write(event.delta.thinking);
    }
    if (event.delta.type === "text_delta") {
      process.stdout.write(event.delta.text);
    }
  }
}
```

## Prompt Caching

```ts
const response = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  system: [
    {
      type: "text",
      text: longSystemPrompt,    // e.g., 5000+ tokens
      cache_control: { type: "ephemeral" },
    },
  ],
  messages: [{ role: "user", content: "Quick question..." }],
});

// Cache also works on messages
messages: [
  {
    role: "user",
    content: [
      {
        type: "text",
        text: longDocument,
        cache_control: { type: "ephemeral" },
      },
    ],
  },
  { role: "assistant", content: "I've read the document." },
  { role: "user", content: "What's the main theme?" },
]
```

### Cache Control Details

```ts
// Check cache usage in response
const response = await client.messages.create({ /* ... with cache_control */ });
console.log(response.usage);
// {
//   input_tokens: 50,
//   output_tokens: 120,
//   cache_creation_input_tokens: 5000,  // First request: writes to cache
//   cache_read_input_tokens: 0,
// }

// Subsequent request with same prefix:
// {
//   input_tokens: 50,
//   cache_creation_input_tokens: 0,
//   cache_read_input_tokens: 5000,      // Cache hit — 90% cheaper
// }
```

**Cache rules:**
- Cached content must be a **prefix** (system prompt, then earliest messages)
- Cache lives for **5 minutes** (ephemeral), refreshed on use
- Minimum cacheable content: **1,024 tokens** (Sonnet/Opus) or **2,048 tokens** (Haiku)
- Cache read tokens cost 10% of regular input token price

## Batch API (High-Throughput)

```ts
// Create a batch of requests for async processing (50% cost savings)
const batch = await client.batches.create({
  requests: [
    {
      custom_id: "request-1",
      params: {
        model: "claude-sonnet-4-20250514",
        max_tokens: 1024,
        messages: [{ role: "user", content: "Summarize document 1..." }],
      },
    },
    {
      custom_id: "request-2",
      params: {
        model: "claude-sonnet-4-20250514",
        max_tokens: 1024,
        messages: [{ role: "user", content: "Summarize document 2..." }],
      },
    },
    // Up to 10,000 requests per batch
  ],
});

console.log(batch.id);           // batch_abc123
console.log(batch.processing_status); // "in_progress"

// Poll for completion (typically completes within 24 hours)
const result = await client.batches.retrieve(batch.id);
if (result.processing_status === "ended") {
  // Download results
  for (const item of result.results) {
    console.log(item.custom_id, item.result.message.content[0].text);
  }
}
```

### When to Use Batch API

| Use Case | Batch? | Why |
|----------|--------|-----|
| Bulk document processing | Yes | 50% cost savings, no rate limits |
| Nightly report generation | Yes | Not time-sensitive |
| Dataset labeling/annotation | Yes | High volume, uniform tasks |
| Real-time chat | No | Needs instant response |
| Interactive code review | No | User waiting for result |

## Model Selection Guide

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| `claude-opus-4-20250514` | Complex reasoning, code generation, analysis | Slow | $$$ |
| `claude-sonnet-4-20250514` | Balanced: good reasoning + speed | Medium | $$ |
| `claude-haiku-3-5-20241022` | Fast responses, simple tasks, classification | Fast | $ |

## Error Handling

```ts
import Anthropic from "@anthropic-ai/sdk";

try {
  const response = await client.messages.create({ /* ... */ });
} catch (error) {
  if (error instanceof Anthropic.APIError) {
    console.error("Status:", error.status);
    console.error("Message:", error.message);

    switch (error.status) {
      case 400: // Invalid request
        break;
      case 401: // Auth error
        break;
      case 429: // Rate limited
        const retryAfter = error.headers?.["retry-after"];
        break;
      case 529: // Overloaded
        break;
    }
  }
}
```

## Rate Limiting & Retries

```ts
// SDK has built-in retries
const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
  maxRetries: 3,  // default: 2
  timeout: 60_000, // default: 10 minutes
});
```
