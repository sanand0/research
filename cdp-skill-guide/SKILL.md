# Chrome DevTools Protocol (CDP) Skill Guide

A comprehensive guide to effectively using CDP for browser automation, debugging, and testing.

## Quick Start

### 1. Launch Chrome with CDP Enabled

```bash
google-chrome-stable \
  --headless \
  --disable-gpu \
  --remote-debugging-port=9222 \
  --no-sandbox \
  --disable-dev-shm-usage \
  --user-data-dir=/tmp/chrome-cdp \
  about:blank
```

**Essential flags explained:**
- `--headless`: Run without UI (for automation)
- `--disable-gpu`: Prevent GPU-related issues in containers
- `--remote-debugging-port=9222`: Enable CDP on port 9222
- `--no-sandbox`: Required when running as root or in containers
- `--disable-dev-shm-usage`: Avoid shared memory issues in Docker
- `--user-data-dir=/tmp/chrome-cdp`: Isolate browser profile

### 2. Verify CDP is Running

```bash
curl -s http://localhost:9222/json/version
```

Expected output:
```json
{
  "Browser": "Chrome/142.0.7444.162",
  "Protocol-Version": "1.3",
  "webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser/..."
}
```

### 3. Install CDP Client (Node.js)

```bash
npm install chrome-remote-interface
```

### 4. Basic Connection

```javascript
const CDP = require('chrome-remote-interface');

async function main() {
  const client = await CDP({ port: 9222 });
  const { Page, Runtime } = client;

  await Page.enable();
  await Runtime.enable();

  await Page.navigate({ url: 'https://example.com' });
  await Page.loadEventFired();

  const { result } = await Runtime.evaluate({
    expression: 'document.title'
  });
  console.log('Title:', result.value);

  await client.close();
}

main();
```

---

## Core Concepts

### CDP Architecture

```
Browser Instance (port 9222)
├── /json/version  - Browser info
├── /json/list     - List all targets
└── Targets (pages/tabs)
    ├── WebSocket connection per target
    └── Domains (Page, Runtime, DOM, Network, etc.)
```

### Key Pattern: Always Enable Domains First

```javascript
// WRONG - will fail
await Page.navigate({ url: 'https://example.com' });

// CORRECT
await Page.enable();  // Enable first!
await Page.navigate({ url: 'https://example.com' });
```

### Target Management

Create isolated browser contexts:

```javascript
const browser = await CDP({ port: 9222 });

// Create new tab
const { targetId } = await browser.Target.createTarget({
  url: 'about:blank'
});

// Connect to that specific tab
const client = await CDP({ port: 9222, target: targetId });

// ... do work ...

// Clean up
await browser.Target.closeTarget({ targetId });
await client.close();
await browser.close();
```

---

## Common Operations

### Navigation

```javascript
// Navigate and wait for load
await Page.navigate({ url: 'https://example.com' });
await Page.loadEventFired();

// Check for navigation errors
const navResult = await Page.navigate({ url: 'https://example.com' });
if (navResult.errorText) {
  console.error('Navigation failed:', navResult.errorText);
}
```

### Form Filling

```javascript
// Method 1: Direct JavaScript (recommended)
await Runtime.evaluate({
  expression: `
    document.getElementById('username').value = 'myuser';
    document.getElementById('password').value = 'mypass';
  `
});

// Method 2: Using Input domain (more realistic)
const { Input } = client;
await Runtime.evaluate({
  expression: 'document.getElementById("username").focus()'
});
await Input.insertText({ text: 'myuser' });
```

### Clicking Elements

```javascript
// Method 1: JavaScript click (simplest)
await Runtime.evaluate({
  expression: 'document.getElementById("submitBtn").click()'
});

// Method 2: Coordinate-based click (more realistic)
const { result } = await Runtime.evaluate({
  expression: `
    const btn = document.getElementById("submitBtn");
    const rect = btn.getBoundingClientRect();
    ({ x: rect.x + rect.width/2, y: rect.y + rect.height/2 })
  `,
  returnByValue: true
});
await Input.dispatchMouseEvent({
  type: 'click',
  x: result.x,
  y: result.y,
  button: 'left',
  clickCount: 1
});
```

### Extracting Data

```javascript
// Get text content
const { result } = await Runtime.evaluate({
  expression: 'document.body.innerText'
});

// Get structured data
const { result } = await Runtime.evaluate({
  expression: `
    Array.from(document.querySelectorAll('table tr')).map(row =>
      Array.from(row.cells).map(cell => cell.textContent)
    )
  `,
  returnByValue: true
});

// Get element attributes
const { result } = await Runtime.evaluate({
  expression: `
    Array.from(document.querySelectorAll('a')).map(a => ({
      href: a.href,
      text: a.textContent
    }))
  `,
  returnByValue: true
});
```

### Console Log Capture

```javascript
const logs = [];

Runtime.consoleAPICalled(params => {
  const message = params.args.map(arg => {
    // Preserve falsy values (false, 0, null, undefined)
    if (arg.value !== undefined) {
      return String(arg.value);
    }
    if (arg.description) {
      return arg.description;
    }
    return 'undefined';
  }).join(' ');
  logs.push({ type: params.type, message });
});

await Runtime.enable();
// ... page operations ...

console.log('Captured logs:', logs);
```

**Important notes:**
- `console.warn()` generates type `"warning"` (not `"warn"`)
- Objects show generic descriptions like `"Object"` or `"Array(5)"`
- Listener overhead is <1ms per log (safe for production)

### Screenshots

```javascript
// Full page screenshot
const screenshot = await Page.captureScreenshot({
  format: 'png',
  fromSurface: true
});

// Save to file
const fs = require('fs');
fs.writeFileSync('screenshot.png', Buffer.from(screenshot.data, 'base64'));

// Specific viewport
await Page.captureScreenshot({
  format: 'jpeg',
  quality: 80,
  clip: { x: 0, y: 0, width: 800, height: 600, scale: 1 }
});
```

### Network Monitoring

```javascript
await Network.enable();

Network.requestWillBeSent(params => {
  console.log('Request:', params.request.method, params.request.url);
});

Network.responseReceived(params => {
  console.log('Response:', params.response.status, params.response.url);
});

Network.loadingFailed(params => {
  console.error('Failed:', params.errorText);
});
```

---

## Troubleshooting Common Errors

### Error: Cannot connect to Chrome

**Symptoms:**
```
Error: connect ECONNREFUSED 127.0.0.1:9222
```

**Solutions:**
1. Verify Chrome is running: `pgrep chrome`
2. Check port is open: `curl http://localhost:9222/json/version`
3. Ensure no other process uses port 9222: `lsof -i :9222`
4. Kill existing Chrome and restart: `pkill -9 chrome`

### Error: net::ERR_NAME_NOT_RESOLVED

**Cause:** DNS resolution failed (common in containers)

**Solutions:**
1. Use system proxy:
   ```bash
   google-chrome-stable --proxy-server="$HTTPS_PROXY" ...
   ```
2. Configure DNS servers:
   ```bash
   --host-resolver-rules="MAP * ~NOTFOUND, EXCLUDE localhost"
   ```
3. Use IP addresses instead of hostnames

### Error: net::ERR_TUNNEL_CONNECTION_FAILED

**Cause:** Proxy authentication or configuration issue

**Solutions:**
1. Check proxy environment variables: `env | grep -i proxy`
2. Ensure proxy URL is correctly formatted
3. Verify proxy credentials are valid

### Error: Multiple targets not supported in headless mode

**Cause:** Another Chrome instance running or command parsing error

**Solutions:**
1. Kill all Chrome processes: `pkill -9 chrome`
2. Avoid line continuation in shell commands
3. Use single-line command or proper escaping

### Error: Screenshot hangs/times out

**Cause:** Shared memory permission issues in containers

**Solutions:**
1. Increase shared memory:
   ```bash
   docker run --shm-size=2gb ...
   ```
2. Use different temp directory:
   ```bash
   --disk-cache-dir=/var/cache/chrome
   ```
3. Add timeout wrapper:
   ```javascript
   const screenshot = await Promise.race([
     Page.captureScreenshot(),
     new Promise((_, reject) =>
       setTimeout(() => reject(new Error('Timeout')), 10000)
     )
   ]);
   ```

### Non-Fatal Errors (Ignorable)

These errors appear in Chrome stderr but don't affect CDP:

```
ERROR: Failed to connect to the bus: ... (D-Bus errors)
ERROR: Failed to read /proc/sys/fs/inotify/max_user_watches
ERROR: Could not bind NETLINK socket: Permission denied
ERROR: Creating shared memory in /tmp/... failed
```

**Why they're safe:** These relate to system features not needed for headless browser automation.

---

## Best Practices

### 1. Always Clean Up Resources

```javascript
let client;
try {
  client = await CDP({ port: 9222 });
  // ... operations ...
} finally {
  if (client) await client.close();
}
```

### 2. Use Timeouts for Async Operations

```javascript
async function waitWithTimeout(promise, ms, errorMessage) {
  let timeoutId;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timeoutId = setTimeout(() => reject(new Error(errorMessage)), ms);
      })
    ]);
  } finally {
    clearTimeout(timeoutId); // Clean up dangling timer
  }
}

await waitWithTimeout(
  Page.loadEventFired(),
  30000,
  'Page load timeout'
);
```

**Recommended timeouts by operation:**
- Simple DOM operations: 1-2 seconds
- Page navigation: 10-15 seconds
- Complex page load: 30 seconds
- Screenshots: 5 seconds
- Network operations: 15-20 seconds

### 3. Prefer Runtime.evaluate for DOM Operations

```javascript
// More reliable than DOM domain
await Runtime.evaluate({
  expression: `
    const element = document.querySelector('.dynamic-class');
    element.click();
  `
});
```

### 4. Handle Navigation Errors Gracefully

```javascript
const navResult = await Page.navigate({ url });
if (navResult.errorText) {
  // Handle specific errors
  if (navResult.errorText.includes('ERR_NAME_NOT_RESOLVED')) {
    throw new Error(`DNS lookup failed for ${url}`);
  }
  throw new Error(`Navigation failed: ${navResult.errorText}`);
}

try {
  await waitWithTimeout(Page.loadEventFired(), 30000, 'Load timeout');
} catch (e) {
  // Page might be usable even if load event doesn't fire
  console.warn('Load event timeout, continuing...');
}
```

### 5. Create Fresh Targets for Isolation

```javascript
// Each task gets its own tab (maximum isolation)
async function runInIsolation(url, task) {
  const browser = await CDP({ port: 9222 });
  const { targetId } = await browser.Target.createTarget({ url: 'about:blank' });
  const client = await CDP({ port: 9222, target: targetId });

  try {
    await task(client);
  } finally {
    await browser.Target.closeTarget({ targetId });
    await client.close();
    await browser.close();
  }
}

// More efficient for multiple tasks (reuse browser connection)
async function runMultipleInIsolation(tasks) {
  const browser = await CDP({ port: 9222 });
  try {
    const results = [];
    for (const task of tasks) {
      const { targetId } = await browser.Target.createTarget({ url: 'about:blank' });
      const client = await CDP({ port: 9222, target: targetId });
      try {
        results.push(await task(client));
      } finally {
        await browser.Target.closeTarget({ targetId });
        await client.close();
      }
    }
    return results;
  } finally {
    await browser.close();
  }
}
```

**Performance notes:**
- Target creation: ~20-30ms
- Task execution: ~300-400ms total
- Cleanup: ~20ms
- Recommended concurrency: 3-5 simultaneous targets
- Memory per target: ~10-20MB

### 6. Monitor Memory Usage

```javascript
const { Runtime } = client;

const heapInfo = await Runtime.getHeapUsage();
console.log('Heap used:', heapInfo.usedSize);
console.log('Heap total:', heapInfo.totalSize);
```

---

## Environment-Specific Configuration

### Docker/Container Setup

```dockerfile
FROM node:18

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Required for headless Chrome
ENV CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Chrome
        uses: browser-actions/setup-chrome@latest
      - name: Run tests
        run: |
          google-chrome-stable --headless --disable-gpu \
            --remote-debugging-port=9222 --no-sandbox &
          sleep 3
          npm test
```

### Proxy Configuration

```javascript
// Launch with proxy
const spawn = require('child_process').spawn;

const proxy = process.env.HTTPS_PROXY;
const chrome = spawn('google-chrome-stable', [
  '--headless',
  '--disable-gpu',
  '--remote-debugging-port=9222',
  '--no-sandbox',
  `--proxy-server=${proxy}`,
  'about:blank'
]);

// Or set via CDP (partial support)
await Network.enable();
await Network.setExtraHTTPHeaders({
  headers: { 'Proxy-Authorization': 'Basic ...' }
});
```

---

## Debugging CDP Scripts

### Enable Verbose Logging

```javascript
const CDP = require('chrome-remote-interface');

// Log all CDP messages
const client = await CDP({ port: 9222 });
client.on('event', (message) => {
  console.log('CDP Event:', message);
});
```

### Use Chrome's Built-in Inspector

Open `chrome://inspect` in a regular Chrome browser and connect to your headless instance.

### Dump Page State

```javascript
async function debugPageState(client) {
  const { Runtime } = client;

  const info = await Runtime.evaluate({
    expression: `({
      url: location.href,
      title: document.title,
      readyState: document.readyState,
      bodyLength: document.body.innerHTML.length,
      errors: window.__errors || []
    })`,
    returnByValue: true
  });

  console.log('Page State:', info.result.value);
}
```

---

## Performance Optimization

### Disable Unnecessary Features

```bash
google-chrome-stable \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --disable-dev-shm-usage \
  --disable-extensions \
  --disable-plugins \
  --disable-images \                    # Faster loading
  --blink-settings=imagesEnabled=false \
  --disable-javascript \                # If not needed
  --remote-debugging-port=9222
```

### Block Unnecessary Resources

```javascript
await Network.enable();
await Network.setBlockedURLs({
  urls: [
    '*.png', '*.jpg', '*.gif',  // Images
    '*.woff', '*.woff2',         // Fonts
    '*analytics*', '*tracking*'   // Trackers
  ]
});
```

### Reuse Browser Instance

```javascript
// Start Chrome once, reuse for multiple tasks
const browser = await CDP({ port: 9222 });

for (const task of tasks) {
  const { targetId } = await browser.Target.createTarget({ url: 'about:blank' });
  const client = await CDP({ port: 9222, target: targetId });

  await runTask(client, task);

  await browser.Target.closeTarget({ targetId });
  await client.close();
}

await browser.close();
```

---

## Security Considerations

1. **Never expose CDP port publicly** - Use localhost only or secure tunnels
2. **Sanitize user input** - Don't inject untrusted code via Runtime.evaluate
3. **Use isolated profiles** - `--user-data-dir` prevents data leakage
4. **Monitor resource usage** - Headless Chrome can consume significant memory
5. **Validate downloaded content** - Check file types and sizes before saving

---

## Quick Reference

### CDP Endpoints

| Endpoint | Description |
|----------|-------------|
| `/json/version` | Browser version info |
| `/json/list` | List all targets |
| `/json/new?url=` | Create new target |
| `/json/close/{targetId}` | Close target |
| `/json/activate/{targetId}` | Activate target |

### Essential Domains

| Domain | Purpose | Key Methods |
|--------|---------|-------------|
| `Page` | Page lifecycle | navigate, loadEventFired, captureScreenshot |
| `Runtime` | JavaScript execution | evaluate, consoleAPICalled |
| `DOM` | DOM tree access | getDocument, querySelectorAll |
| `Network` | Network monitoring | enable, requestWillBeSent, responseReceived |
| `Input` | User input simulation | dispatchMouseEvent, insertText |
| `Target` | Tab management | createTarget, closeTarget |

### Common Chrome Flags

| Flag | Purpose |
|------|---------|
| `--headless` | No UI |
| `--disable-gpu` | No GPU rendering |
| `--no-sandbox` | Disable sandbox (containers) |
| `--disable-dev-shm-usage` | Avoid /dev/shm issues |
| `--remote-debugging-port=N` | Enable CDP |
| `--user-data-dir=PATH` | Isolated profile |
| `--proxy-server=URL` | Configure proxy |
| `--disable-extensions` | No extensions |
| `--window-size=W,H` | Set viewport |

---

## Further Resources

- [Chrome DevTools Protocol Documentation](https://chromedevtools.github.io/devtools-protocol/)
- [chrome-remote-interface npm package](https://github.com/cyrus-and/chrome-remote-interface)
- [Puppeteer (higher-level CDP wrapper)](https://pptr.dev/)
- [CDP Protocol Viewer](https://vanilla.aslushnikov.com/)
