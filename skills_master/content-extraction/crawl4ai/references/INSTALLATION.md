# Crawl4AI Installation Guide

Complete installation instructions for all deployment methods.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Method 1: Local Python Installation](#method-1-local-python-installation)
- [Method 2: Docker Installation](#method-2-docker-installation)
- [Method 3: Docker from Source](#method-3-docker-from-source)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Prerequisites

### All Methods
- Python 3.10 or higher
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space

### Docker Method
- Docker 20.10.0+ and Docker Compose
- Additional 2GB RAM for containers

### Check Your System

```bash
# Python version
python --version

# Docker version
docker --version
docker-compose --version

# Available memory
free -h  # Linux
vm_stat  # macOS
```

## Method 1: Local Python Installation

Best for: Development, testing, and local use

### Step 1: Install Crawl4AI

```bash
# Basic installation
pip install crawl4ai

# Or with all features (transformers, torch)
pip install crawl4ai[all]

# Or with transformer support only
pip install crawl4ai[transformer]
```

### Step 2: Run Setup

```bash
# Install and configure browsers
crawl4ai-setup

# This will:
# - Install Playwright
# - Download browser binaries (Chromium)
# - Configure system dependencies (Linux)
```

### Step 3: Verify Installation

```bash
# Run diagnostics
crawl4ai-doctor

# Should show:
# ✓ Python version OK
# ✓ Playwright installed
# ✓ Browsers available
# ✓ System dependencies OK
```

### Step 4: Test Basic Crawl

```bash
# Run validation script
python scripts/validate_setup.py

# Or test manually
python -c "
import asyncio
from crawl4ai import AsyncWebCrawler

async def test():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun('https://example.com')
        print(f'Success: {result.success}')
        print(f'Content: {len(result.markdown.raw_markdown)} chars')

asyncio.run(test())
"
```

### Step 5: Install Optional Dependencies

```bash
# For LLM extraction
pip install openai anthropic litellm

# For transformer-based strategies
pip install transformers torch sentence-transformers

# For HTTP client examples
pip install requests aiohttp
```

### Linux-Specific Setup

On Linux, you may need additional system dependencies:

```bash
# Ubuntu/Debian
playwright install-deps

# Or manually
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2
```

## Method 2: Docker Installation

Best for: Production, scalability, and isolated environments

### Step 1: Navigate to Docker Directory

```bash
cd docker
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your settings
nano .env  # or vim, code, etc.
```

Required settings:
```bash
# At minimum, set these if using LLM features
OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here  # Optional
# GROQ_API_KEY=gsk_your-key-here  # Optional
```

### Step 3: Run Automated Setup

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh

# The script will:
# 1. Check Docker installation
# 2. Check system resources
# 3. Create directory structure
# 4. Pull Docker images
# 5. Start services
# 6. Verify health
```

### Step 4: Verify Services

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f crawl4ai

# Health check
curl http://localhost:11235/health

# Access playground
open http://localhost:11235/playground
```

### Manual Docker Setup

If you prefer manual setup:

```bash
# Pull image
docker pull unclecode/crawl4ai:latest

# Create directories
mkdir -p data cache logs

# Create .env file
cp .env.template .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:11235/health
```

### Docker Compose Services

The compose file starts:
- **crawl4ai** - Main crawler service (port 11235)
- **redis** - Job queue backend (port 6379)
- **redis-commander** - Redis UI (port 8081, optional)

```bash
# Start all services
docker-compose up -d

# Start without monitoring tools
docker-compose up -d crawl4ai redis

# Start with monitoring
docker-compose --profile monitoring up -d
```

## Method 3: Docker from Source

Best for: Custom builds, development, or specific requirements

### Step 1: Clone Repository

```bash
git clone https://github.com/unclecode/crawl4ai.git
cd crawl4ai
```

### Step 2: Build Image

```bash
# Basic build
docker build -t crawl4ai:custom .

# Or with all features
docker build \
  --build-arg INSTALL_TYPE=all \
  -t crawl4ai:custom-full \
  .

# Multi-architecture build
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --build-arg INSTALL_TYPE=all \
  -t crawl4ai:custom-multi \
  --load \
  .
```

### Step 3: Run Custom Image

```bash
docker run -d \
  -p 11235:11235 \
  --name crawl4ai \
  --shm-size=3g \
  -v $(pwd)/data:/data \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  crawl4ai:custom
```

## Verification

After installation, verify everything works:

### 1. Run Validation Script

```bash
python scripts/validate_setup.py
```

This checks:
- Python version
- Crawl4AI installation
- Dependencies
- Browser availability
- API keys
- Basic crawling
- Docker setup

### 2. Test Examples

```bash
# Basic crawling
python examples/01_basic_crawling.py

# CSS extraction
python examples/02_css_extraction.py

# LLM extraction (requires API key)
python examples/03_llm_extraction.py

# Docker API (requires Docker running)
python examples/04_docker_api_client.py
```

### 3. Check Docker API

```bash
# Health check
curl http://localhost:11235/health

# Test crawl
curl -X POST http://localhost:11235/crawl \
  -H 'Content-Type: application/json' \
  -d '{"urls": ["https://example.com"]}'

# Open playground
open http://localhost:11235/playground
```

## Troubleshooting

### Browser Installation Issues

**Problem**: Browsers fail to install or launch

**Solution**:
```bash
# Re-run setup
crawl4ai-setup

# Check diagnostics
crawl4ai-doctor

# On Linux, install system dependencies
playwright install-deps
```

### Permission Errors

**Problem**: Permission denied on Linux/Mac

**Solution**:
```bash
# Make scripts executable
chmod +x setup.sh
chmod +x scripts/*.py
chmod +x examples/*.py

# Or run with python
python scripts/validate_setup.py
```

### Docker Memory Issues

**Problem**: Container crashes or is slow

**Solution**:
```bash
# Increase shared memory in docker-compose.yml
shm_size: '3gb'  # or higher

# Or in docker run
docker run --shm-size=3g ...
```

### Port Already in Use

**Problem**: Port 11235 already in use

**Solution**:
```bash
# Find what's using the port
lsof -i :11235  # macOS/Linux
netstat -ano | findstr :11235  # Windows

# Kill the process or change port in docker-compose.yml
ports:
  - "8080:11235"  # Use different external port
```

### API Key Errors

**Problem**: LLM extraction fails

**Solution**:
```bash
# Check environment variables
echo $OPENAI_API_KEY

# Set for current session
export OPENAI_API_KEY=sk-your-key-here

# Set permanently in .env (Docker)
# Or in ~/.bashrc, ~/.zshrc (local)
echo 'export OPENAI_API_KEY=sk-your-key-here' >> ~/.bashrc
```

### Module Not Found

**Problem**: ImportError or ModuleNotFoundError

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install missing package
pip install <package-name>

# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Docker Image Pull Fails

**Problem**: Cannot pull Docker image

**Solution**:
```bash
# Try different registry
docker pull unclecode/crawl4ai:latest

# Or build from source
git clone https://github.com/unclecode/crawl4ai.git
cd crawl4ai
docker build -t crawl4ai:local .
```

### Network/Firewall Issues

**Problem**: Cannot access external sites

**Solution**:
```python
# Use proxy
from crawl4ai import BrowserConfig

config = BrowserConfig(
    proxy="http://proxy.example.com:8080",
    proxy_config={
        "server": "http://proxy.example.com:8080",
        "username": "user",
        "password": "pass"
    }
)
```

## Environment Variables

### Required for LLM Features
```bash
OPENAI_API_KEY=sk-...
```

### Optional
```bash
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
```

### Crawl4AI Configuration
```bash
MAX_CONCURRENT_TASKS=10
CRAWL4AI_CACHE_DIR=./cache
CRAWL4AI_DOWNLOAD_DIR=./downloads
LOG_LEVEL=INFO
```

### Set Environment Variables

**Linux/Mac**:
```bash
# Current session
export OPENAI_API_KEY=sk-...

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY=sk-...' >> ~/.bashrc
source ~/.bashrc
```

**Windows**:
```cmd
# Current session
set OPENAI_API_KEY=sk-...

# Permanent
setx OPENAI_API_KEY sk-...
```

**Docker**:
```bash
# Edit .env file in docker directory
nano docker/.env
```

## Next Steps

1. **Read Documentation**
   ```bash
   # Quick reference
   cat QUICKREF.md
   
   # Full skill documentation
   cat SKILL.md
   ```

2. **Try Examples**
   ```bash
   python examples/01_basic_crawling.py
   ```

3. **Explore Playground**
   ```
   http://localhost:11235/playground
   ```

4. **Join Community**
   - Discord: https://discord.gg/jP8KfhDhyN
   - GitHub: https://github.com/unclecode/crawl4ai

## Support

- 📖 Documentation: https://docs.crawl4ai.com/
- 🐛 Issues: https://github.com/unclecode/crawl4ai/issues
- 💬 Discord: https://discord.gg/jP8KfhDhyN
- ⭐ Star the repo: https://github.com/unclecode/crawl4ai

## Summary

| Method | Best For | Command |
|--------|----------|---------|
| **Local Python** | Development, Testing | `pip install crawl4ai && crawl4ai-setup` |
| **Docker** | Production, Scaling | `cd docker && ./setup.sh` |
| **From Source** | Custom Builds | `git clone ... && docker build ...` |

**Recommended**: Start with Docker for easiest setup and production readiness.

---

**Still having issues?** Run `python scripts/validate_setup.py` for detailed diagnostics!
