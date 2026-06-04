# User Agent Management

Rotating and customizing user agents for crawling.

## User Agent Pools

```python
from dataclasses import dataclass
from typing import List
import random

@dataclass
class UserAgent:
    string: str
    platform: str
    browser: str
    version: str

USER_AGENTS = {
    "chrome_desktop": UserAgent(
        string="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        platform="Windows",
        browser="Chrome",
        version="120.0.0.0",
    ),
    "chrome_mac": UserAgent(
        string="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        platform="macOS",
        browser="Chrome",
        version="120.0.0.0",
    ),
    "safari_iphone": UserAgent(
        string="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        platform="iOS",
        browser="Safari",
        version="17.0",
    ),
    "firefox_desktop": UserAgent(
        string="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        platform="Windows",
        browser="Firefox",
        version="121.0",
    ),
}

class UserAgentRotator:
    def __init__(self, agents: List[UserAgent] = None):
        self.agents = agents or list(USER_AGENTS.values())
        self.current = 0

    def get(self) -> str:
        """Get next user agent."""
        agent = self.agents[self.current]
        self.current = (self.current + 1) % len(self.agents)
        return agent.string

    def get_random(self) -> str:
        """Get random user agent."""
        return random.choice(self.agents).string
```

## Usage

```python
from crawl4ai import BrowserConfig

config = BrowserConfig(
    headless=True,
    user_agent=UserAgentRotator().get(),
)
```
