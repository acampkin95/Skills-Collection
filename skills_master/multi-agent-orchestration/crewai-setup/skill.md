---

## Parent router

This skill is a leaf of the [multi-agent-orchestration](../multi-agent-orchestration/SKILL.md) master router.
name: crewai-setup
description: CrewAI multi-agent framework setup, configuration, and development. Use when CrewAI, crew, agent role, task delegation, crew kickoff, agent tools, hierarchical process, sequential process.
---

# CrewAI Development Skill

## Quick Reference

```bash
# Project lifecycle
crewai create crew <name> --skip_provider  # Scaffold new crew
uv sync                                     # Install dependencies
crewai run                                  # Execute crew
crewai test -n 5 -m gpt-4o                 # Test crew
crewai train -n 5 -f training.json         # Train crew
crewai reset-memories -a                    # Reset all memory
```

## Project Structure

```
project/
├── pyproject.toml              # [tool.crewai] type = "crew"
├── .env                        # API keys
├── src/project_name/
│   ├── __init__.py
│   ├── crew.py                 # @CrewBase class
│   ├── main.py                 # run/train/test entrypoints
│   ├── config/
│   │   ├── agents.yaml         # Agent definitions
│   │   └── tasks.yaml          # Task definitions
│   └── tools/
│       └── custom_tool.py      # @tool decorated functions
└── output/                     # Crew output files
```

## LLM Provider Configuration

CrewAI v1.11.0 supports native providers and LiteLLM fallback:

**Native providers** (no extra install): `openai/`, `anthropic/`, `gemini/`, `azure/`, `bedrock/`
**LiteLLM providers** (need `crewai[litellm]`): `groq/`, `deepinfra/`, `together_ai/`, `ollama/`

```yaml
# agents.yaml - provider/model format
researcher:
  llm: deepinfra/meta-llama/Llama-3.3-70B-Instruct-Turbo
  # llm: gemini/gemini-2.0-flash          # Native Google
  # llm: anthropic/claude-sonnet-4-20250514  # Native Anthropic
  # llm: openai/gpt-4o                    # Native OpenAI
  # llm: groq/llama-3.3-70b-versatile     # Via LiteLLM
```

**Required extras by provider:**
```bash
uv add 'crewai[tools]'          # Base + tools
uv add 'crewai[anthropic]'      # Anthropic native
uv add 'crewai[google-genai]'   # Google Gemini native
uv add 'crewai[litellm]'        # Groq, DeepInfra, Together, Ollama
```

**Environment variables:**
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
GROQ_API_KEY=gsk_...
DEEPINFRA_API_KEY=...
SERPER_API_KEY=...              # For SerperDevTool web search
```

## Agent Configuration (agents.yaml)

```yaml
agent_name:
  role: >
    Job title / expertise area
  goal: >
    What the agent is trying to achieve (supports {variable} interpolation)
  backstory: >
    Persona context and expertise description
  llm: provider/model-id
  allow_delegation: false        # Can delegate to other agents
  verbose: true
  # Optional:
  # memory: true                 # Enable agent memory
  # max_iter: 15                 # Max reasoning iterations
  # reasoning: true              # Reflect-then-act (v1.8+)
  # multimodal: true             # Vision/image support
  # inject_date: true            # Auto-inject current date
```

## Task Configuration (tasks.yaml)

```yaml
task_name:
  description: >
    What needs to be done (supports {variable} interpolation)
  expected_output: >
    Specific format/content of the output
  agent: agent_name
  # Optional:
  # context:
  #   - previous_task_name       # Use output from another task
  # output_file: output/file.md  # Save to file
  # async_execution: true        # Run async
```

## Crew Class (@CrewBase)

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

@CrewBase
class MyCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
        )

    @agent
    def writer(self) -> Agent:
        return Agent(config=self.agents_config["writer"])

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @task
    def report_task(self) -> Task:
        return Task(config=self.tasks_config["report_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # or Process.hierarchical
            verbose=True,
            memory=True,  # Enable crew memory
            # planning=True,            # Auto-plan before execution
            # planning_llm="gpt-4o",    # LLM for planning
        )
```

## Custom Tools

```python
from crewai.tools import tool

@tool("Tool Name")
def my_tool(query: str) -> str:
    """Tool description used by the agent to decide when to use this tool."""
    return f"Result for: {query}"
```

## Flows (Multi-Step Pipelines)

```python
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

class MyState(BaseModel):
    topic: str = ""
    result: str = ""

class MyFlow(Flow[MyState]):
    @start()
    def step_one(self):
        self.state.result = f"Researching: {self.state.topic}"
        return self.state.result

    @listen(step_one)
    def step_two(self):
        # Can invoke a crew here
        from my_project.crews.research import ResearchCrew
        result = ResearchCrew().crew().kickoff(inputs={"topic": self.state.topic})
        self.state.result = result.raw
        return self.state.result

flow = MyFlow()
flow.state.topic = "AI"
flow.kickoff()
```

## Multi-Crew Projects

When placing crews in a `crews/` subdirectory, config paths must be relative to the crew file:
```python
# In crews/research.py — use ../ to reach config/ from crews/
agents_config = "../config/agents.yaml"
tasks_config = "../config/tasks.yaml"
```

## Common Issues

### Tool use failures with Groq/open-source models
Groq's Llama models often fail with CrewAI's tool calling format. Use DeepInfra instead for tool-using agents, or remove tools from agents using Groq.

### Provider not found
Error: "model did not match any supported native provider". Install LiteLLM: `uv add 'crewai[litellm]'`

### Anthropic provider missing
Error: "Anthropic native provider not available". Fix: `uv add 'crewai[anthropic]'`

### Gemini quota exceeded
Free tier has strict limits. Switch to a paid plan or use DeepInfra/Groq as alternatives.

### NEVER use these patterns (outdated)
- `ChatOpenAI(model_name=...)` -> Use `LLM(model="openai/gpt-4o")`
- `Agent(llm=ChatOpenAI(...))` -> Use `Agent(llm="openai/gpt-4o")`
- Raw OpenAI client objects -> Use `crewai.LLM` wrapper

## Process Types

- **Sequential**: Tasks run one after another. Default, simplest.
- **Hierarchical**: Manager agent coordinates and delegates. Good for complex workflows.

## Execution

```python
from dotenv import load_dotenv
load_dotenv()
from my_crew.crew import MyCrew

result = MyCrew().crew().kickoff(inputs={"topic": "AI trends"})
print(result.raw)           # Raw text output
print(result.token_usage)   # Token usage stats
```

## Key Dependencies (v1.11.0)

- Python >=3.10, <3.14
- crewai >= 1.11.0
- crewai-tools >= 1.11.0
- python-dotenv >= 1.0.0
- uv for dependency management
