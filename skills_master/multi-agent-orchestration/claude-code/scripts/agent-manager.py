#!/usr/bin/env python3
"""
Claude Code Agent Manager - Create and manage subagents for parallel development.

Usage:
    python3 agent-manager.py create <name> <description> [--model <model>] [--color <color>]
    python3 agent-manager.py list
    python3 agent-manager.py delete <name>
    python3 agent-manager.py run <name> "<task>"
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

AGENTS_DIR: Path = Path.home() / ".claude" / "agents"

def ensure_agents_dir() -> None:
    """Create agents directory if it doesn't exist."""
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)

def create_agent(name: str, description: str, model: str = "sonnet", color: str = "blue") -> Path:
    """Create a new subagent configuration."""
    ensure_agents_dir()

    agent_file = AGENTS_DIR / f"{name}.yaml"

    if agent_file.exists():
        print(f"Error: Agent '{name}' already exists")
        sys.exit(1)

    agent_config = {
        "name": name,
        "description": description,
        "model": model,
        "color": color,
        "created": datetime.now().isoformat()
    }

    with open(agent_file, 'w') as f:
        yaml.dump(agent_config, f)

    print(f"Created agent: {name} ({model})")
    return agent_file

def list_agents() -> None:
    """List all configured agents."""
    ensure_agents_dir()

    agents: List[Dict[str, Any]] = []
    for agent_file in AGENTS_DIR.glob("*.yaml"):
        with open(agent_file) as f:
            agent = yaml.safe_load(f)
            if agent is not None:
                agent['file'] = agent_file.name
                agents.append(agent)

    if not agents:
        print("No agents configured. Create one with: python3 agent-manager.py create <name> <description>")
        return

    print(f"{'Name':<20} {'Model':<12} {'Description'}")
    print("-" * 80)
    for agent in agents:
        desc = agent.get('description', '')[:50]
        print(f"{agent['name']:<20} {agent.get('model', 'sonnet'):<12} {desc}")

def delete_agent(name: str) -> None:
    """Delete a subagent configuration."""
    ensure_agents_dir()

    agent_file = AGENTS_DIR / f"{name}.yaml"

    if not agent_file.exists():
        print(f"Error: Agent '{name}' not found")
        sys.exit(1)

    agent_file.unlink()
    print(f"Deleted agent: {name}")

def run_agent(name: str, task: str) -> None:
    """Run a task with a specific agent."""
    ensure_agents_dir()

    agent_file = AGENTS_DIR / f"{name}.yaml"

    if not agent_file.exists():
        print(f"Error: Agent '{name}' not found")
        sys.exit(1)

    with open(agent_file) as f:
        agent = yaml.safe_load(f)
        if agent is None:
            print(f"Error: Failed to load agent configuration from {agent_file}")
            sys.exit(1)

    model = agent.get('model', 'sonnet')
    print(f"Running agent '{name}' ({model})...")
    print(f"Task: {task}")
    print("\nThis would invoke Claude Code with the specified agent configuration.")
    print(f"\nCommand: claude --model {model} \"{task}\"")

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 4:
            print("Usage: python3 agent-manager.py create <name> <description> [--model <model>] [--color <color>]")
            sys.exit(1)
        name = sys.argv[2]
        description = sys.argv[3]
        model = "sonnet"
        color = "blue"
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == "--model" and i + 1 < len(sys.argv):
                model = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--color" and i + 1 < len(sys.argv):
                color = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        create_agent(name, description, model, color)

    elif command == "list":
        list_agents()

    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: python3 agent-manager.py delete <name>")
            sys.exit(1)
        delete_agent(sys.argv[2])

    elif command == "run":
        if len(sys.argv) < 4:
            print("Usage: python3 agent-manager.py run <name> \"<task>\"")
            sys.exit(1)
        run_agent(sys.argv[2], sys.argv[3])

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
