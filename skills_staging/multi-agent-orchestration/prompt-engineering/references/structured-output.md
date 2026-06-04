# Structured Output Patterns

## JSON Mode via System Prompt

```ts
const response = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  system: `Extract the following information as JSON. 
Return ONLY valid JSON matching this schema:
{
  "name": string,
  "email": string | null,
  "phone": string | null,
  "company": string | null
}`,
  messages: [
    { role: "user", content: "Contact John Smith at john@acme.com, Acme Corp" },
  ],
});

const result = JSON.parse(response.content[0].text);
// { name: "John Smith", email: "john@acme.com", phone: null, company: "Acme Corp" }
```

## Tool Use for Guaranteed Structure

The most reliable method - forces output to match a schema:

```ts
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

// Define the output schema as a tool
const extractionTool = {
  name: "save_extraction",
  description: "Save the extracted structured data",
  input_schema: {
    type: "object" as const,
    properties: {
      products: {
        type: "array",
        items: {
          type: "object",
          properties: {
            name: { type: "string", description: "Product name" },
            price: { type: "number", description: "Price in USD" },
            category: {
              type: "string",
              enum: ["electronics", "clothing", "food", "other"],
            },
            inStock: { type: "boolean" },
          },
          required: ["name", "price", "category", "inStock"],
        },
      },
      totalProducts: { type: "number" },
    },
    required: ["products", "totalProducts"],
  },
};

const response = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  tool_choice: { type: "tool", name: "save_extraction" },
  tools: [extractionTool],
  messages: [
    {
      role: "user",
      content: `Extract products from: "We have the iPhone 16 ($999, electronics, in stock) 
      and Nike Air Max ($120, clothing, out of stock)"`,
    },
  ],
});

const toolBlock = response.content.find((b) => b.type === "tool_use")!;
const data = toolBlock.input;
// Guaranteed to match the schema
```

## Zod Schema Validation

```ts
import { z } from "zod";

const ProductSchema = z.object({
  name: z.string(),
  price: z.number().positive(),
  category: z.enum(["electronics", "clothing", "food", "other"]),
  inStock: z.boolean(),
});

const ExtractionSchema = z.object({
  products: z.array(ProductSchema),
  totalProducts: z.number(),
});

type Extraction = z.infer<typeof ExtractionSchema>;

async function extractProducts(text: string): Promise<Extraction> {
  const response = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1024,
    system: `Extract products as JSON matching: ${JSON.stringify(ExtractionSchema.shape)}
Return ONLY valid JSON.`,
    messages: [{ role: "user", content: text }],
  });

  const raw = JSON.parse(response.content[0].text);
  return ExtractionSchema.parse(raw);  // Throws if invalid
}
```

## Retry with Feedback

```ts
async function extractWithRetry<T>(
  schema: z.ZodSchema<T>,
  prompt: string,
  maxRetries = 3
): Promise<T> {
  let lastError: string | undefined;

  for (let i = 0; i < maxRetries; i++) {
    const systemPrompt = lastError
      ? `Previous attempt had validation errors: ${lastError}\nPlease fix and try again.\n\nExtract as JSON.`
      : "Extract as JSON. Return ONLY valid JSON.";

    const response = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: "user", content: prompt }],
    });

    try {
      const text = response.content[0].text;
      // Handle markdown code blocks
      const json = text.replace(/```json?\n?|\n?```/g, "").trim();
      const parsed = JSON.parse(json);
      return schema.parse(parsed);
    } catch (error) {
      if (error instanceof z.ZodError) {
        lastError = error.errors.map((e) => `${e.path.join(".")}: ${e.message}`).join("; ");
      } else {
        lastError = String(error);
      }
    }
  }

  throw new Error(`Failed after ${maxRetries} retries. Last error: ${lastError}`);
}
```

## Vercel AI SDK Patterns

```ts
import { generateObject, generateText, streamObject } from "ai";
import { anthropic } from "@ai-sdk/anthropic";
import { z } from "zod";

// Generate structured object
const { object } = await generateObject({
  model: anthropic("claude-sonnet-4-20250514"),
  schema: z.object({
    recipe: z.object({
      name: z.string(),
      ingredients: z.array(
        z.object({
          name: z.string(),
          amount: z.string(),
        })
      ),
      steps: z.array(z.string()),
    }),
  }),
  prompt: "Generate a recipe for chocolate chip cookies",
});

console.log(object.recipe.name);
console.log(object.recipe.ingredients);

// Stream structured object (partial results)
const { partialObjectStream } = streamObject({
  model: anthropic("claude-sonnet-4-20250514"),
  schema: z.object({
    notifications: z.array(
      z.object({
        name: z.string(),
        message: z.string(),
        urgency: z.enum(["low", "medium", "high"]),
      })
    ),
  }),
  prompt: "Generate 5 notifications for a project management app",
});

for await (const partial of partialObjectStream) {
  console.log("Partial:", partial);
  // Incrementally receive the object as it's generated
}
```

### Enum Output

```ts
import { generateObject } from "ai";
import { anthropic } from "@ai-sdk/anthropic";
import { z } from "zod";

const { object } = await generateObject({
  model: anthropic("claude-sonnet-4-20250514"),
  output: "enum",
  enum: ["positive", "negative", "neutral"],
  prompt: `Classify sentiment: "${userInput}"`,
});

// object is one of: "positive" | "negative" | "neutral"
```

### Tool Calling with AI SDK

```ts
import { generateText, tool } from "ai";
import { anthropic } from "@ai-sdk/anthropic";
import { z } from "zod";

const { text, toolResults } = await generateText({
  model: anthropic("claude-sonnet-4-20250514"),
  tools: {
    weather: tool({
      description: "Get the weather for a location",
      parameters: z.object({
        location: z.string().describe("City name"),
      }),
      execute: async ({ location }) => {
        // Your implementation
        return { temp: 72, conditions: "sunny" };
      },
    }),
  },
  prompt: "What's the weather in San Francisco?",
});
```

## Response Validation Pattern

```ts
function createStructuredExtractor<T>(schema: z.ZodSchema<T>) {
  return async (input: string, instruction: string): Promise<T> => {
    // Method 1: Try tool use (most reliable)
    try {
      const zodToJsonSchema = await import("zod-to-json-schema");
      const jsonSchema = zodToJsonSchema.default(schema);

      const response = await client.messages.create({
        model: "claude-sonnet-4-20250514",
        max_tokens: 2048,
        tool_choice: { type: "tool", name: "output" },
        tools: [{
          name: "output",
          description: "Output the structured result",
          input_schema: jsonSchema as any,
        }],
        messages: [{ role: "user", content: `${instruction}\n\nInput: ${input}` }],
      });

      const toolBlock = response.content.find((b) => b.type === "tool_use");
      return schema.parse(toolBlock!.input);
    } catch {
      // Method 2: Fallback to JSON mode with retry
      return extractWithRetry(schema, `${instruction}\n\nInput: ${input}`);
    }
  };
}

// Usage
const extractContact = createStructuredExtractor(
  z.object({
    name: z.string(),
    email: z.string().email().nullable(),
    phone: z.string().nullable(),
  })
);

const contact = await extractContact(
  "Call Jane at 555-0123 or email jane@example.com",
  "Extract contact information from the text"
);
```
