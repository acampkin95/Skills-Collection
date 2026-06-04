# Prompt Evaluation & Testing

## Why Evaluate

- Detect regressions when changing prompts
- Compare different prompt strategies
- Measure quality objectively
- Build confidence before deploying

## Manual Evaluation Framework

### Test Suite Structure

```ts
// eval/test-cases.ts
interface TestCase {
  id: string;
  input: string;
  expectedOutput?: string;           // Exact match
  expectedContains?: string[];       // Must contain these
  expectedNotContains?: string[];    // Must NOT contain these
  expectedSchema?: object;           // JSON schema
  tags: string[];                    // For filtering
}

const testCases: TestCase[] = [
  {
    id: "sentiment-positive-1",
    input: "I absolutely love this product! Best purchase ever!",
    expectedOutput: "positive",
    tags: ["sentiment", "positive"],
  },
  {
    id: "sentiment-negative-1",
    input: "Terrible experience. Would not recommend.",
    expectedOutput: "negative",
    tags: ["sentiment", "negative"],
  },
  {
    id: "extraction-contact-1",
    input: "Reach John at john@acme.com or 555-0123",
    expectedContains: ["John", "john@acme.com", "555-0123"],
    tags: ["extraction", "contact"],
  },
];
```

### Test Runner

```ts
// eval/runner.ts
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

interface EvalResult {
  testId: string;
  passed: boolean;
  output: string;
  latencyMs: number;
  inputTokens: number;
  outputTokens: number;
  error?: string;
}

async function runEval(
  systemPrompt: string,
  testCases: TestCase[]
): Promise<EvalResult[]> {
  const results: EvalResult[] = [];

  for (const tc of testCases) {
    const start = Date.now();

    try {
      const response = await client.messages.create({
        model: "claude-sonnet-4-20250514",
        max_tokens: 1024,
        system: systemPrompt,
        messages: [{ role: "user", content: tc.input }],
      });

      const output = response.content[0].text;
      const latencyMs = Date.now() - start;

      let passed = true;

      if (tc.expectedOutput && output.trim() !== tc.expectedOutput) {
        passed = false;
      }
      if (tc.expectedContains) {
        for (const s of tc.expectedContains) {
          if (!output.includes(s)) passed = false;
        }
      }
      if (tc.expectedNotContains) {
        for (const s of tc.expectedNotContains) {
          if (output.includes(s)) passed = false;
        }
      }

      results.push({
        testId: tc.id,
        passed,
        output,
        latencyMs,
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens,
      });
    } catch (error) {
      results.push({
        testId: tc.id,
        passed: false,
        output: "",
        latencyMs: Date.now() - start,
        inputTokens: 0,
        outputTokens: 0,
        error: String(error),
      });
    }
  }

  return results;
}

// Report
function printReport(results: EvalResult[]) {
  const passed = results.filter((r) => r.passed).length;
  const total = results.length;
  const avgLatency = results.reduce((s, r) => s + r.latencyMs, 0) / total;
  const totalTokens = results.reduce(
    (s, r) => s + r.inputTokens + r.outputTokens,
    0
  );

  console.log(`\n=== Evaluation Report ===`);
  console.log(`Pass rate: ${passed}/${total} (${((passed / total) * 100).toFixed(1)}%)`);
  console.log(`Avg latency: ${avgLatency.toFixed(0)}ms`);
  console.log(`Total tokens: ${totalTokens}`);

  for (const r of results.filter((r) => !r.passed)) {
    console.log(`\nFAILED: ${r.testId}`);
    console.log(`  Output: ${r.output.slice(0, 200)}`);
    if (r.error) console.log(`  Error: ${r.error}`);
  }
}
```

## A/B Comparison

```ts
async function comparePrompts(
  promptA: string,
  promptB: string,
  testCases: TestCase[]
) {
  console.log("Running Prompt A...");
  const resultsA = await runEval(promptA, testCases);

  console.log("Running Prompt B...");
  const resultsB = await runEval(promptB, testCases);

  const passA = resultsA.filter((r) => r.passed).length;
  const passB = resultsB.filter((r) => r.passed).length;

  console.log(`\n=== A/B Comparison ===`);
  console.log(`Prompt A: ${passA}/${testCases.length} passed`);
  console.log(`Prompt B: ${passB}/${testCases.length} passed`);

  // Show where they differ
  for (let i = 0; i < testCases.length; i++) {
    if (resultsA[i].passed !== resultsB[i].passed) {
      console.log(`\nDifference on: ${testCases[i].id}`);
      console.log(`  A (${resultsA[i].passed ? "PASS" : "FAIL"}): ${resultsA[i].output.slice(0, 100)}`);
      console.log(`  B (${resultsB[i].passed ? "PASS" : "FAIL"}): ${resultsB[i].output.slice(0, 100)}`);
    }
  }
}
```

## Model-as-Judge

Use a model to evaluate another model's output:

```ts
async function judgeOutput(
  question: string,
  answer: string,
  criteria: string[]
): Promise<{ score: number; reasoning: string }> {
  const response = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1024,
    system: `You are an evaluator. Score the given answer on a scale of 1-5 for each criterion.
Be strict and objective. Return JSON.`,
    messages: [
      {
        role: "user",
        content: `Question: ${question}

Answer to evaluate:
${answer}

Score each criterion (1-5):
${criteria.map((c, i) => `${i + 1}. ${c}`).join("\n")}

Return JSON:
{
  "scores": { "criterion_name": score },
  "overall": number,
  "reasoning": "explanation"
}`,
      },
    ],
  });

  return JSON.parse(response.content[0].text);
}

// Usage
const result = await judgeOutput(
  "Explain how React hooks work",
  modelOutput,
  [
    "Accuracy: Are all technical claims correct?",
    "Completeness: Are key concepts covered?",
    "Clarity: Is the explanation easy to understand?",
    "Examples: Are helpful code examples provided?",
  ]
);
```

## Regression Detection

```ts
// eval/regression.ts
import { readFileSync, writeFileSync, existsSync } from "fs";

interface Baseline {
  promptHash: string;
  results: Record<string, boolean>;
  date: string;
}

function saveBaseline(promptHash: string, results: EvalResult[]) {
  const baseline: Baseline = {
    promptHash,
    results: Object.fromEntries(results.map((r) => [r.testId, r.passed])),
    date: new Date().toISOString(),
  };
  writeFileSync("eval/baseline.json", JSON.stringify(baseline, null, 2));
}

function checkRegression(current: EvalResult[]): string[] {
  if (!existsSync("eval/baseline.json")) return [];

  const baseline: Baseline = JSON.parse(
    readFileSync("eval/baseline.json", "utf-8")
  );

  const regressions: string[] = [];
  for (const result of current) {
    const baselinePassed = baseline.results[result.testId];
    if (baselinePassed === true && !result.passed) {
      regressions.push(
        `REGRESSION: ${result.testId} was passing, now failing`
      );
    }
  }

  return regressions;
}
```

## Metrics

| Metric | When to Use | Formula |
|--------|-------------|---------|
| **Accuracy** | Classification tasks | correct / total |
| **Precision** | When false positives are costly | TP / (TP + FP) |
| **Recall** | When false negatives are costly | TP / (TP + FN) |
| **F1** | Balance precision & recall | 2 * (P * R) / (P + R) |
| **BLEU** | Text generation similarity | n-gram overlap |
| **Exact Match** | Structured extraction | output === expected |
| **Contains** | Partial extraction | expected in output |
| **Judge Score** | Open-ended quality | model-rated 1-5 |

## Prompt Versioning

```ts
// prompts/sentiment.ts
export const PROMPT_VERSIONS = {
  "v1": {
    system: "Classify as positive, negative, or neutral.",
    date: "2025-01-01",
    notes: "Initial version",
  },
  "v2": {
    system: `Classify the sentiment of the following text.
Respond with exactly one word: positive, negative, or neutral.
Consider sarcasm and context carefully.`,
    date: "2025-01-15",
    notes: "Added sarcasm handling, stricter output format",
  },
  "v3": {
    system: `You are a sentiment classifier. Analyze the text and respond with a JSON object:
{"sentiment": "positive" | "negative" | "neutral", "confidence": 0.0-1.0}
Consider: tone, sarcasm, context, intensity.`,
    date: "2025-01-20",
    notes: "Added confidence score, JSON output",
  },
};

export const CURRENT_VERSION = "v3";
export const currentPrompt = PROMPT_VERSIONS[CURRENT_VERSION];
```

## CI Integration

```yaml
# .github/workflows/eval.yml
name: Prompt Evaluation
on:
  pull_request:
    paths:
      - "prompts/**"
      - "eval/**"

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx tsx eval/run.ts
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      - name: Check regressions
        run: npx tsx eval/check-regression.ts
```
