#!/usr/bin/env python3
"""
Crawl4AI Installation and Setup Validator
==========================================

This script validates your Crawl4AI installation and configuration.
Run this after setup to ensure everything is working correctly.
"""

import asyncio
import sys
import os
from typing import Optional, Tuple, List, Dict


class Colors:
    """Terminal colors for output formatting.

    Provides ANSI escape codes for colored and bold terminal text output.
    Used to enhance readability of validation messages and status indicators.
    """
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str) -> None:
    """Print a section header with visual separator.

    Displays a formatted header with blue colored borders and bold text
    to visually separate validation sections in terminal output.

    Args:
        text: The header text to display between separator lines.

    Returns:
        None. Output is printed to stdout.
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")


def print_success(text: str) -> None:
    """Print a success message with green checkmark indicator.

    Displays a success status message formatted with a green checkmark
    and reset color code for terminal readability.

    Args:
        text: The success message to display.

    Returns:
        None. Output is printed to stdout.
    """
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")


def print_warning(text: str) -> None:
    """Print a warning message with yellow warning indicator.

    Displays a warning status message formatted with a yellow warning symbol
    and reset color code for terminal readability.

    Args:
        text: The warning message to display.

    Returns:
        None. Output is printed to stdout.
    """
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")


def print_error(text: str) -> None:
    """Print an error message with red X indicator.

    Displays an error status message formatted with a red X symbol
    and reset color code for terminal readability.

    Args:
        text: The error message to display.

    Returns:
        None. Output is printed to stdout.
    """
    print(f"{Colors.RED}✗{Colors.RESET} {text}")


def print_info(text: str) -> None:
    """Print an info message with blue info indicator.

    Displays an informational status message formatted with a blue info symbol
    and reset color code for terminal readability.

    Args:
        text: The info message to display.

    Returns:
        None. Output is printed to stdout.
    """
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {text}")


# Test 1: Check Python Version
def check_python_version() -> bool:
    """Verify Python version meets minimum requirement.

    Checks that the installed Python version is 3.10 or higher,
    which is required for Crawl4AI compatibility.

    Args:
        None.

    Returns:
        bool: True if Python 3.10+ is detected, False otherwise.

    Raises:
        No exceptions raised; errors are logged to stdout.
    """
    print_info("Checking Python version...")

    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} detected")
        print("  Crawl4AI requires Python 3.10 or higher")
        return False


# Test 2: Check Crawl4AI Installation
def check_crawl4ai_installed() -> bool:
    """Check if Crawl4AI is installed and report version.

    Attempts to import the crawl4ai module and extract its version information.
    Provides installation instructions if the module is not found.

    Args:
        None.

    Returns:
        bool: True if Crawl4AI is installed, False otherwise.

    Raises:
        No exceptions raised; import errors are caught and logged to stdout.
    """
    print_info("Checking Crawl4AI installation...")
    
    try:
        import crawl4ai
        version = getattr(crawl4ai, '__version__', 'unknown')
        print_success(f"Crawl4AI installed (version: {version})")
        return True
    except ImportError:
        print_error("Crawl4AI not installed")
        print("  Run: pip install crawl4ai")
        return False


# Test 3: Check Required Dependencies
def check_dependencies() -> Tuple[bool, List]:
    """Check if required and optional dependencies are installed.

    Validates that all required dependencies (playwright, aiohttp, pydantic) are
    present and reports on optional dependencies (openai, anthropic, requests).
    Returns a tuple indicating success status and list of missing required packages.

    Args:
        None.

    Returns:
        Tuple[bool, List]: A tuple containing:
            - bool: True if all required dependencies are installed, False otherwise
            - List: List of missing required dependency names (empty if all present)

    Raises:
        No exceptions raised; import errors are caught and logged to stdout.
    """
    print_info("Checking dependencies...")
    
    required = {
        'playwright': 'playwright',
        'aiohttp': 'aiohttp',
        'pydantic': 'pydantic',
    }
    
    optional = {
        'openai': 'openai',
        'anthropic': 'anthropic',
        'requests': 'requests',
    }
    
    missing = []
    optional_missing = []
    
    # Check required
    for name, import_name in required.items():
        try:
            __import__(import_name)
            print_success(f"{name} installed")
        except ImportError:
            missing.append(name)
            print_error(f"{name} not installed")
    
    # Check optional
    for name, import_name in optional.items():
        try:
            __import__(import_name)
            print_success(f"{name} installed (optional)")
        except ImportError:
            optional_missing.append(name)
            print_warning(f"{name} not installed (optional)")
    
    if missing:
        print_error(f"Missing required dependencies: {', '.join(missing)}")
        return False, missing
    
    if optional_missing:
        print_warning(f"Missing optional dependencies: {', '.join(optional_missing)}")
    
    return True, []


# Test 4: Check Browser Installation
def check_browsers() -> bool:
    """Check if Playwright browsers are installed and functional.

    Attempts to launch a Chromium browser instance via Playwright to verify
    that browser binaries are present and executable. Reports installation
    instructions if browsers cannot be launched.

    Args:
        None.

    Returns:
        bool: True if Chromium browser is installed and can be launched, False otherwise.

    Raises:
        No exceptions raised; import and launch errors are caught and logged to stdout.
    """
    print_info("Checking browser installation...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Try to launch browser
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print_success("Chromium browser installed and working")
                return True
            except Exception as e:
                print_error(f"Browser launch failed: {e}")
                print("  Run: crawl4ai-setup")
                return False
    except ImportError:
        print_error("Playwright not installed")
        print("  Run: pip install playwright")
        return False


# Test 5: Check API Keys
def check_api_keys() -> Dict:
    """Check if LLM API keys are configured in environment variables.

    Verifies presence of OpenAI, Anthropic, and Groq API keys in the environment.
    All keys are optional but at least one should be configured for LLM extraction.

    Args:
        None.

    Returns:
        Dict: Dictionary mapping API key names to boolean status (True if configured).
            Keys: 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GROQ_API_KEY'

    Raises:
        No exceptions raised; environment variable access does not raise errors.
    """
    print_info("Checking API key configuration...")
    
    keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
    }
    
    configured = {}
    for key, value in keys.items():
        if value:
            print_success(f"{key} configured")
            configured[key] = True
        else:
            print_warning(f"{key} not configured (optional)")
            configured[key] = False
    
    if not any(configured.values()):
        print_warning("No LLM API keys configured - LLM extraction will not work")
    
    return configured


# Test 6: Test Basic Crawl
async def test_basic_crawl() -> bool:
    """Test basic crawling functionality with Crawl4AI.

    Performs a test crawl of example.com to verify that the AsyncWebCrawler
    is functioning correctly with a 30-second timeout and cache bypass mode.

    Args:
        None.

    Returns:
        bool: True if crawl succeeds and markdown content is retrieved, False otherwise.

    Raises:
        No exceptions raised; import errors and crawl failures are caught and logged to stdout.
    """
    print_info("Testing basic crawl...")
    
    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
        
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url="https://example.com",
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    page_timeout=30000
                )
            )
            
            if result.success:
                markdown_len = len(result.markdown.raw_markdown)
                print_success(f"Basic crawl successful ({markdown_len} chars)")
                return True
            else:
                print_error(f"Crawl failed: {result.error_message}")
                return False
                
    except Exception as e:
        print_error(f"Crawl test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test 7: Check Docker Setup
def check_docker_setup() -> bool:
    """Check if Docker is installed and the daemon is running.

    Verifies Docker installation by running 'docker --version' and confirms
    that the Docker daemon is operational by executing 'docker info'.
    Each command has a 5-second timeout for responsiveness checks.

    Args:
        None.

    Returns:
        bool: True if Docker is installed and daemon is running, False otherwise.

    Raises:
        No exceptions raised; subprocess timeouts and FileNotFoundError are caught and logged to stdout.
    """
    print_info("Checking Docker setup...")
    
    import subprocess
    
    # Check Docker
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success(f"Docker installed: {result.stdout.strip()}")
        else:
            print_warning("Docker not available")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_warning("Docker not installed or not in PATH")
        return False
    
    # Check if daemon is running
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Docker daemon is running")
            return True
        else:
            print_warning("Docker daemon not running")
            return False
    except subprocess.TimeoutExpired:
        print_warning("Docker daemon check timed out")
        return False


# Test 8: Check Docker API
def check_docker_api() -> bool:
    """Check if Crawl4AI Docker API is accessible at localhost:11235.

    Attempts to reach the health endpoint of the Crawl4AI Docker API running
    at http://localhost:11235/health with a 5-second timeout. Reports the
    playground URL if the API is accessible.

    Args:
        None.

    Returns:
        bool: True if API health endpoint returns 200 status code, False otherwise.

    Raises:
        No exceptions raised; connection errors, missing requests library, and other
        exceptions are caught and logged as warnings to stdout.
    """
    print_info("Checking Crawl4AI Docker API...")
    
    try:
        import requests
        response = requests.get('http://localhost:11235/health', timeout=5)
        
        if response.status_code == 200:
            print_success("Crawl4AI API is accessible at http://localhost:11235")
            print_info("  Playground: http://localhost:11235/playground")
            return True
        else:
            print_warning("API returned unexpected status")
            return False
    except requests.exceptions.ConnectionError:
        print_warning("Crawl4AI API not accessible")
        print("  Start with: cd docker && docker-compose up -d")
        return False
    except ImportError:
        print_warning("requests library not installed (optional)")
        return False
    except Exception as e:
        print_warning(f"API check failed: {e}")
        return False


async def run_all_tests() -> bool:
    """Run all validation tests and generate comprehensive installation report.

    Orchestrates the complete validation suite including environment checks (Python version,
    Crawl4AI installation, dependencies), browser checks (Playwright), configuration checks
    (LLM API keys), functionality tests (basic crawling), and Docker checks. Provides a
    detailed summary showing which components passed or failed, and recommends next steps.

    Args:
        None.

    Returns:
        bool: True if all core components pass (Python, Crawl4AI, dependencies, browsers),
              False if any core component fails.

    Raises:
        No exceptions raised; all test failures are caught and logged to stdout with
        appropriate status indicators and guidance.
    """
    
    print_header("Crawl4AI Installation Validator")
    
    results = {
        'python': False,
        'crawl4ai': False,
        'dependencies': False,
        'browsers': False,
        'api_keys': {},
        'basic_crawl': False,
        'docker': False,
        'docker_api': False
    }
    
    # Run tests
    print_header("1. Environment Checks")
    results['python'] = check_python_version()
    results['crawl4ai'] = check_crawl4ai_installed()
    
    if results['crawl4ai']:
        results['dependencies'], _ = check_dependencies()
    
    print_header("2. Browser Checks")
    if results['crawl4ai'] and results['dependencies']:
        results['browsers'] = check_browsers()
    
    print_header("3. Configuration Checks")
    results['api_keys'] = check_api_keys()
    
    print_header("4. Functionality Tests")
    if results['browsers']:
        results['basic_crawl'] = await test_basic_crawl()
    else:
        print_warning("Skipping crawl test - browsers not available")
    
    print_header("5. Docker Checks")
    results['docker'] = check_docker_setup()
    if results['docker']:
        results['docker_api'] = check_docker_api()
    
    # Summary
    print_header("Validation Summary")
    
    core_passed = all([
        results['python'],
        results['crawl4ai'],
        results['dependencies'],
        results['browsers']
    ])
    
    if core_passed:
        print_success("Core installation: PASSED ✓")
        
        if results['basic_crawl']:
            print_success("Basic functionality: PASSED ✓")
        else:
            print_error("Basic functionality: FAILED ✗")
    else:
        print_error("Core installation: FAILED ✗")
        print("\nPlease fix the issues above and run this script again.")
        return False
    
    # Optional features
    print()
    if any(results['api_keys'].values()):
        print_success("LLM integration: Available")
    else:
        print_info("LLM integration: Not configured (optional)")
    
    if results['docker_api']:
        print_success("Docker API: Available")
    elif results['docker']:
        print_info("Docker: Installed but API not running")
    else:
        print_info("Docker: Not available (optional)")
    
    print()
    print_header("Next Steps")
    
    if not any(results['api_keys'].values()):
        print("• Configure LLM API keys for advanced extraction:")
        print("  export OPENAI_API_KEY=sk-...")
    
    if results['docker'] and not results['docker_api']:
        print("• Start Docker API:")
        print("  cd docker && ./setup.sh")
    
    if core_passed:
        print("• Try the examples:")
        print("  python examples/01_basic_crawling.py")
        print("  python examples/02_css_extraction.py")
    
    print()
    return core_passed


def main() -> None:
    """Main entry point for the Crawl4AI installation validator.

    Executes the complete validation test suite asynchronously and exits with
    appropriate status code (0 for success, 1 for failure). Handles keyboard
    interrupts and unexpected exceptions with graceful error messaging.

    Args:
        None.

    Returns:
        None. Exits the process via sys.exit() with status code 0 or 1.

    Raises:
        No exceptions raised; KeyboardInterrupt and Exception are caught and handled
        with appropriate exit codes and error messages.
    """
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
