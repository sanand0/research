# Chrome CDP Web Automation Skill

## Overview

This skill enables Claude Code to automate web browser interactions using the Chrome DevTools Protocol (CDP). It provides tools for navigating websites, filling forms, logging into services, and performing actions on web pages - particularly useful for sites that require authentication.

## Features

- **Browser Automation**: Navigate, click, type, and interact with web pages
- **Login Flows**: Handle authentication for various websites
- **Session Management**: Save and restore login sessions
- **Form Automation**: Fill and submit forms automatically
- **Data Extraction**: Scrape content from web pages
- **Screenshots**: Capture page state for debugging or documentation
- **Headless/Headed Modes**: Run with or without visible browser window

## Prerequisites

### 1. Chrome/Chromium Installation

The skill requires Chrome or Chromium to be installed. Install using:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y chromium-browser

# macOS (using Homebrew)
brew install --cask google-chrome

# Or download from: https://www.google.com/chrome/
```

### 2. Node.js Dependencies

Navigate to the skill directory and install dependencies:

```bash
cd chrome-cdp-login-skill
npm install
```

This installs `puppeteer-core`, a lightweight CDP client.

### 3. Credentials Setup (Optional)

For sites requiring login, create a `.credentials.json` file:

```json
{
  "pastebin": {
    "username": "your_username",
    "password": "your_password"
  },
  "github": {
    "username": "your_username",
    "password": "your_password"
  }
}
```

**Important**: Add `.credentials.json` to `.gitignore` to avoid committing secrets!

Alternatively, use environment variables:
```bash
export PASTEBIN_USERNAME="your_username"
export PASTEBIN_PASSWORD="your_password"
```

## Quick Start

### Basic Navigation Example

```javascript
const CDPHelper = require('./cdp-helper');

async function example() {
  const cdp = new CDPHelper({ headless: false });

  await cdp.launch();
  await cdp.goto('https://example.com');
  await cdp.screenshot('screenshot.png');
  await cdp.close();
}

example();
```

### Login and Perform Action

```javascript
const CDPHelper = require('./cdp-helper');
const { loginToPastebin, createPasteOnPastebin } = require('./login-helper');

async function createPaste() {
  const cdp = new CDPHelper({ headless: false });

  await cdp.launch();

  // Login
  await loginToPastebin(cdp, {
    username: 'your_username',
    password: 'your_password'
  });

  // Create paste
  const url = await createPasteOnPastebin(
    cdp,
    'Hello from CDP automation!',
    'My First Automated Paste'
  );

  console.log('Created:', url);

  await cdp.close();
}

createPaste();
```

## Core API Reference

### CDPHelper Class

#### Constructor Options

```javascript
const cdp = new CDPHelper({
  headless: false,           // Run in headless mode
  executablePath: '/path/to/chrome', // Chrome executable (auto-detected)
  userDataDir: './.chrome-profile',  // Profile directory
  viewport: { width: 1280, height: 800 },
  defaultTimeout: 30000      // Default timeout in ms
});
```

#### Navigation Methods

- **`launch()`** - Launch browser and create page
- **`goto(url, options)`** - Navigate to URL
- **`waitForNavigation(options)`** - Wait for page navigation

#### Interaction Methods

- **`click(selector, options)`** - Click an element
- **`type(selector, text, options)`** - Type into an input
- **`fillForm(formData)`** - Fill multiple form fields
- **`waitForSelector(selector, options)`** - Wait for element to appear

#### Information Methods

- **`exists(selector)`** - Check if element exists
- **`getText(selector)`** - Get element text content
- **`content()`** - Get full page HTML
- **`evaluate(fn, ...args)`** - Run JavaScript in page context

#### Session Methods

- **`getCookies()`** - Get all cookies
- **`setCookies(cookies)`** - Set cookies
- **`saveSession(filepath)`** - Save cookies and localStorage
- **`loadSession(filepath)`** - Load saved session

#### Utility Methods

- **`screenshot(filepath, options)`** - Take screenshot
- **`wait(milliseconds)`** - Wait for specified time
- **`close()`** - Close browser

## Login Helper Functions

### Supported Sites

The `login-helper.js` module provides pre-built login functions for:

- **Pastebin** - `loginToPastebin(cdp, credentials)`
- **GitHub** - `loginToGitHub(cdp, credentials)`
- **Generic** - `genericLogin(cdp, url, credentials, selectors)`

### Creating Custom Login Functions

```javascript
async function loginToCustomSite(cdp, credentials) {
  // Try loading existing session
  const sessionFile = './sessions/custom-site.json';
  if (await cdp.loadSession(sessionFile)) {
    await cdp.goto('https://customsite.com');
    if (await cdp.exists('.user-avatar')) {
      return true; // Already logged in
    }
  }

  // Perform login
  await cdp.goto('https://customsite.com/login');
  await cdp.type('#username', credentials.username);
  await cdp.type('#password', credentials.password);
  await Promise.all([
    cdp.waitForNavigation(),
    cdp.click('button[type="submit"]')
  ]);

  // Save session for reuse
  await cdp.saveSession(sessionFile);
  return true;
}
```

## Example Workflows

### 1. Share Code on CodePen

```javascript
const cdp = new CDPHelper({ headless: false });

await cdp.launch();
await cdp.goto('https://codepen.io/pen/');
await cdp.wait(3000);

// Set HTML
await cdp.evaluate(() => {
  const editor = document.querySelector('[data-lang="html"] .CodeMirror');
  if (editor && editor.CodeMirror) {
    editor.CodeMirror.setValue('<h1>Hello World!</h1>');
  }
});

await cdp.screenshot('codepen-result.png');
await cdp.close();
```

### 2. Scrape Data After Login

```javascript
const cdp = new CDPHelper();

await cdp.launch();
await loginToCustomSite(cdp, credentials);

await cdp.goto('https://example.com/dashboard');

const data = await cdp.evaluate(() => {
  return Array.from(document.querySelectorAll('.data-item')).map(item => ({
    title: item.querySelector('h3')?.textContent,
    value: item.querySelector('.value')?.textContent
  }));
});

console.log(data);
await cdp.close();
```

### 3. Form Automation with Wait Conditions

```javascript
const cdp = new CDPHelper();

await cdp.launch();
await cdp.goto('https://example.com/form');

// Fill form
await cdp.fillForm({
  '#name': 'John Doe',
  '#email': 'john@example.com',
  '#message': 'This is an automated message'
});

// Select from dropdown
await cdp.page.select('#country', 'US');

// Check checkbox
await cdp.click('#agree-terms');

// Submit and wait for success message
await cdp.click('button[type="submit"]');
await cdp.waitForSelector('.success-message');

const message = await cdp.getText('.success-message');
console.log('Success:', message);

await cdp.close();
```

## Testing Sites

These sites are safe for testing automation (they allow easy registration and have no harmful consequences):

1. **Pastebin.com** - Text sharing
   - Free registration
   - Create/delete pastes safely

2. **JSFiddle.net** - Code playground
   - Anonymous usage allowed
   - GitHub OAuth for saving

3. **CodePen.io** - Code sharing
   - Free registration
   - Create pens anonymously or with account

4. **DB-Fiddle.com** - SQL playground
   - Anonymous usage
   - No registration required for testing

5. **Imgur.com** - Image sharing
   - Free registration
   - Upload/delete images

## Best Practices

### 1. Session Management

Always try to load existing sessions before logging in again:

```javascript
const sessionFile = '.sessions/site-session.json';
if (await cdp.loadSession(sessionFile)) {
  // Check if still logged in
  if (await cdp.exists('.logged-in-indicator')) {
    return true; // Reuse session
  }
}
// Otherwise proceed with login
```

### 2. Error Handling

Always wrap automation in try-catch and take screenshots on errors:

```javascript
try {
  await cdp.login();
  await cdp.performAction();
} catch (error) {
  await cdp.screenshot('error.png');
  throw error;
} finally {
  await cdp.close();
}
```

### 3. Waiting Strategies

Use appropriate wait strategies:

```javascript
// Wait for selector
await cdp.waitForSelector('.element');

// Wait for navigation
await Promise.all([
  cdp.waitForNavigation(),
  cdp.click('button')
]);

// Wait for network idle
await cdp.goto(url, { waitUntil: 'networkidle2' });

// Simple time wait (use sparingly)
await cdp.wait(1000);
```

### 4. Headless vs Headed Mode

- **Development**: Use `headless: false` to see what's happening
- **Production**: Use `headless: true` for faster, resource-efficient execution
- **Debugging**: Use headed mode with screenshots

### 5. Credentials Security

- Never commit credentials to git
- Use environment variables or encrypted storage
- Use `.gitignore` for credential files
- Consider using OAuth where possible

## Troubleshooting

### Chrome Not Found

If you see "Chrome/Chromium not found", either:

1. Install Chrome/Chromium (see Prerequisites)
2. Specify path explicitly:
   ```javascript
   const cdp = new CDPHelper({
     executablePath: '/path/to/chrome'
   });
   ```

### Selectors Not Working

If selectors aren't found:

1. Open browser in headed mode
2. Use browser DevTools to inspect elements
3. Verify selector syntax
4. Add waits before interaction
5. Take screenshots to debug

### Login Failing

If login doesn't work:

1. Check credentials are correct
2. Look for CAPTCHA challenges
3. Check for 2FA requirements
4. Verify selectors haven't changed
5. Try manual intervention with `waitForManualLogin()`

### Session Not Persisting

If sessions don't save/load:

1. Ensure `.sessions` directory exists
2. Check file permissions
3. Verify cookies are being saved
4. Try clearing old sessions and re-login

## Advanced Patterns

### Handling OAuth Flows

For sites using OAuth (GitHub, Google, etc.):

```javascript
// Option 1: Manual intervention
await cdp.goto('https://site.com/login');
await cdp.click('.login-with-github');

const { waitForManualLogin } = require('./login-helper');
await waitForManualLogin(cdp, '.user-avatar', 120000);

await cdp.saveSession('session.json');
```

### Taking Action After Login

```javascript
async function automatedWorkflow(cdp, credentials) {
  // Login
  await loginToSite(cdp, credentials);

  // Perform actions
  await cdp.goto('https://site.com/create');
  await cdp.fillForm({ ... });
  await cdp.click('button[type="submit"]');

  // Extract result
  const result = await cdp.evaluate(() => {
    return document.querySelector('.result').textContent;
  });

  return result;
}
```

### Retry Logic

```javascript
async function withRetry(fn, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    }
  }
}

await withRetry(() => cdp.click('.button'));
```

## Running Examples

The `examples/` directory contains ready-to-run examples:

```bash
# Basic navigation
node examples/basic-navigation.js

# Pastebin automation (requires credentials)
node examples/pastebin-example.js

# JSFiddle example (no login required)
node examples/jsfiddle-example.js
```

## Integration with Claude Code

When using this skill with Claude Code, the assistant can:

1. Create custom automation scripts for specific tasks
2. Debug web interactions by taking screenshots
3. Handle multi-step workflows involving authentication
4. Extract data from authenticated pages
5. Test web applications with real browser interactions

Example request to Claude Code:

> "Using the Chrome CDP skill, log into Pastebin and create a paste with the contents of my README.md file"

Claude Code will then:
1. Use the CDPHelper to launch Chrome
2. Call loginToPastebin with credentials
3. Use createPasteOnPastebin with the file contents
4. Return the URL of the created paste

## Limitations

1. **CAPTCHA**: Cannot bypass CAPTCHA challenges (use manual intervention)
2. **2FA**: Requires manual code entry or pre-configured TOTP
3. **Rate Limiting**: Respect site rate limits and terms of service
4. **Dynamic Content**: Complex SPAs may require custom wait logic
5. **Browser Detection**: Some sites detect automation; use responsibly

## License and Usage

This skill is for educational and authorized testing purposes only. Always:

- Respect website terms of service
- Use for legitimate automation needs
- Don't abuse rate limits
- Obtain proper authorization for testing
- Don't use for malicious purposes

## Resources

- [Puppeteer Documentation](https://pptr.dev/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [CSS Selectors Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
