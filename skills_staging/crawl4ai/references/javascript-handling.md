# JavaScript Handling Guide

Techniques for handling dynamic content, SPAs, and JavaScript-heavy pages.

## Overview

Modern websites often use JavaScript to render content dynamically. This guide covers:
- Waiting for dynamic content
- Executing custom JavaScript
- Handling SPAs (Single Page Applications)
- Virtual scrolling and infinite scroll
- JavaScript interception

---

## 1. Waiting for Dynamic Content

### CSS Selector Wait

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# Wait for specific element to appear
crawler_config = CrawlerRunConfig(
    wait_for="css:.dynamic-content"  # Wait for element with class
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url, config=crawler_config)
```

### JavaScript Condition Wait

```python
# Wait for custom JS condition
crawler_config = CrawlerRunConfig(
    wait_for="js:document.querySelector('.content') !== null"
)

# More complex conditions
crawler_config = CrawlerRunConfig(
    wait_for="js:(() => { const el = document.querySelector('.data'); return el && el.children.length > 0; })()"
)
```

### Network Idle

```python
# Wait for network requests to complete
crawler_config = CrawlerRunConfig(
    wait_for="networkidle"
)
```

### Multiple Conditions

```python
# Wait for element AND network idle
crawler_config = CrawlerRunConfig(
    wait_for="css:.app-loaded",  # First condition
)
# Or chain in JS
crawler_config = CrawlerRunConfig(
    wait_for="js:document.querySelector('.app') && document.readyState === 'complete'"
)
```

---

## 2. Custom JavaScript Execution

### Basic JS Execution

```python
crawler_config = CrawlerRunConfig(
    js_code="""
    // Click a button
    document.querySelector('.load-more').click();

    // Fill a form
    document.querySelector('#email').value = 'test@example.com';
    document.querySelector('#submit').click();
    """
)
```

### Scroll-Based Loading

```python
crawler_config = CrawlerRunConfig(
    js_code="""
    // Scroll to bottom
    window.scrollTo(0, document.body.scrollHeight);

    // Wait for new content
    await new Promise(r => setTimeout(r, 1000));

    // Scroll again if needed
    window.scrollTo(0, document.body.scrollHeight);
    """,
    page_timeout=60000
)
```

### Infinite Scroll Pattern

```python
crawler_config = CrawlerRunConfig(
    js_code="""
    (async () => {
        const scroller = document.querySelector('.infinite-scroll');
        let previousHeight = 0;

        for (let i = 0; i < 10; i++) {  // Max 10 scrolls
            scroller.scrollTop = scroller.scrollHeight;
            await new Promise(r => setTimeout(r, 1000));

            const newHeight = scroller.scrollHeight;
            if (newHeight === previousHeight) break;
            previousHeight = newHeight;
        }
    })();
    """
)
```

### Dynamic Table Handling

```python
crawler_config = CrawlerRunConfig(
    js_code="""
    // Expand all collapsible rows
    document.querySelectorAll('.expand-btn').forEach(btn => {
        if (btn.classList.contains('collapsed')) {
            btn.click();
        }
    });

    // Wait for animations
    await new Promise(r => setTimeout(r, 500));
    """
)
```

---

## 3. Single Page Application (SPA) Handling

### React/Angular/Vue Apps

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# React apps often need more time
crawler_config = CrawlerRunConfig(
    page_timeout=60000,  # Longer timeout
    wait_for="js:window.React !== undefined || document.querySelector('[data-reactroot]')"
)

# Angular apps
crawler_config = CrawlerRunConfig(
    wait_for="js:typeof ng !== 'undefined' || document.querySelector('[ng-app]') === null"
)

# Vue apps
crawler_config = CrawlerRunConfig(
    wait_for="js:document.querySelector('[data-v-app]') || window.Vue"
)
```

### SPA Route Handling

```python
crawler_config = CrawlerRunConfig(
    js_code="""
    // Navigate to route
    window.history.pushState({}, '', '/dashboard');

    // Trigger route change
    window.dispatchEvent(new PopStateEvent('popstate'));

    // Wait for render
    await new Promise(r => setTimeout(r, 2000));
    """
)
```

### Shadow DOM

```python
js_code = """
const host = document.querySelector('custom-element');
const shadow = host.shadowRoot;

// Access shadow DOM content
const content = shadow.querySelector('.content').textContent;
return content;
"""
```

---

## 4. Virtual Scrolling

For pages with thousands of items (Twitter, LinkedIn feeds, etc.):

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai import VirtualScrollConfig

virtual_scroll = VirtualScrollConfig(
    scroll_distance=500,       # Pixels to scroll per step
    scroll_delay=0.5,          # Seconds between scrolls
    max_scrolls=100,           # Maximum scroll iterations
    wait_after_scroll=0.2,     # Wait after each scroll
    scroll_initially=True,     # Start scrolling immediately
)

crawler_config = CrawlerRunConfig(
    virtual_scroll_config=virtual_scroll
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url, config=crawler_config)
```

### Manual Virtual Scroll Control

```python
js_code = """
(async () => {
    const container = document.querySelector('.virtual-scroll');
    const itemHeight = 50;
    const visibleItems = 20;
    const totalItems = 1000;

    // Scroll to position
    const scrollTo = (index) => {
        container.scrollTop = index * itemHeight;
    };

    // Load items at position
    for (let i = 0; i < totalItems; i += visibleItems) {
        scrollTo(i);
        await new Promise(r => setTimeout(r, 100));

        // Process visible items
        const items = container.querySelectorAll('.visible-item');
        for (const item of items) {
            console.log(item.textContent);
        }
    }
})();
"""
```

---

## 5. JavaScript Interception

### Modify Page Behavior

```python
js_code = """
// Block analytics
window.dataLayer = [];

// Override console.log
const originalLog = console.log;
console.log = function(...args) {
    // Filter or modify logs
    if (args[0]?.includes('debug')) return;
    originalLog.apply(console, args);
};

// Prevent redirects
window.addEventListener('beforeunload', (e) => {
    e.preventDefault();
    e.returnValue = '';
});
"""
```

### Network Request Mocking

```python
js_code = """
// Intercept fetch requests
const originalFetch = window.fetch;
window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    if (args[0].includes('/api/')) {
        // Log or modify API responses
        console.log('API Request:', args[0]);
    }
    return response;
};

// Intercept XHR
const originalXHR = window.XMLHttpRequest;
window.XMLHttpRequest = class extends originalXHR {
    open(method, url) {
        if (url.includes('/api/')) {
            console.log('XHR Request:', method, url);
        }
        super.open(...arguments);
    }
};
"""
```

---

## 6. Cookie and Session Handling

```python
# Set cookies before crawl
browser_config = BrowserConfig(
    cookies=[
        {"name": "session", "value": "abc123", "domain": ".example.com"},
        {"name": "preferences", "value": "dark_mode", "domain": ".example.com"}
    ]
)

# Or via JavaScript
js_code = """
document.cookie = "session=abc123; path=/; domain=.example.com";
document.cookie = "preferences=dark_mode; path=/; domain=.example.com";
"""
```

### Login Flow

```python
async def login_and_crawl(url, login_url, credentials):
    browser_config = BrowserConfig(headless=True)

    crawler_config = CrawlerRunConfig(
        js_code=f"""
        document.querySelector('#username').value = '{credentials['username']}';
        document.querySelector('#password').value = '{credentials['password']}';
        document.querySelector('#login-form').submit();
        """,
        wait_for="css:.dashboard"  # Wait for logged-in state
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Login first
        await crawler.arun(login_url, config=crawler_config)

        # Now access protected page with same session
        result = await crawler.arun(url)

    return result
```

---

## 7. Common Patterns

### Modal/Dialog Handling

```python
js_code = """
// Close modal if present
const modal = document.querySelector('.modal, .overlay');
if (modal) {
    const closeBtn = modal.querySelector('.close, .cancel, [aria-label='close']');
    if (closeBtn) closeBtn.click();
}

// Dismiss cookie banner
const cookieBanner = document.querySelector('[class*="cookie"], [class*="gdpr"]');
if (cookieBanner) {
    const acceptBtn = cookieBanner.querySelector('button');
    if (acceptBtn) acceptBtn.click();
}
"""
```

### Lazy Image Loading

```python
js_code = """
// Trigger lazy loading
const lazyImages = document.querySelectorAll('img[data-src]');
lazyImages.forEach(img => {
    img.src = img.dataset.src;
    img.removeAttribute('data-src');
});

// Wait for images to load
await new Promise(r => setTimeout(r, 2000));
"""
```

### React Hydration Wait

```python
crawler_config = CrawlerRunConfig(
    wait_for="js:(() => {
        const root = document.querySelector('#root');
        if (!root) return false;
        // Check if React has hydrated
        return root.children.length > 0 &&
               !document.body.classList.contains('hydrating');
    })()",
    page_timeout=30000
)
```

---

## 8. Troubleshooting

### JavaScript Not Executing

```python
# Verify JS is enabled
browser_config = BrowserConfig(
    java_script_enabled=True
)

# Add error catching
js_code = """
try {
    // Your code here
} catch (e) {
    console.error('JS Error:', e.message);
    return { error: e.message };
}
return 'success';
"""
```

### Element Not Found

```python
# Add retry logic
js_code = """
(async () => {
    for (let i = 0; i < 10; i++) {
        const el = document.querySelector('.target');
        if (el) return el.textContent;
        await new Promise(r => setTimeout(r, 500));
    }
    return 'Element not found';
})();
"""
```

### Slow Rendering

```python
# Increase delays
js_code = """
await new Promise(r => setTimeout(r, 3000));  // 3 second wait
// Then proceed
"""
```
