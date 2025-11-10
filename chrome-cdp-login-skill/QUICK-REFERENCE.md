# Chrome CDP Quick Reference

## Setup

```bash
./setup.sh
```

## Basic Usage

```javascript
const CDPHelper = require('./cdp-helper');

const cdp = new CDPHelper({ headless: false });
await cdp.launch();
await cdp.goto('https://example.com');
await cdp.screenshot('result.png');
await cdp.close();
```

## Common Operations

### Navigation
```javascript
await cdp.goto('https://example.com');
await cdp.waitForNavigation();
```

### Finding Elements
```javascript
await cdp.waitForSelector('.button');
const exists = await cdp.exists('.button');
const text = await cdp.getText('.heading');
```

### Interaction
```javascript
await cdp.click('button');
await cdp.type('input[name="email"]', 'user@example.com');
await cdp.fillForm({
  '#name': 'John Doe',
  '#email': 'john@example.com'
});
```

### Data Extraction
```javascript
const data = await cdp.evaluate(() => {
  return document.querySelector('h1').textContent;
});
```

### Session Management
```javascript
await cdp.saveSession('.sessions/mysite.json');
await cdp.loadSession('.sessions/mysite.json');
```

### Screenshots
```javascript
await cdp.screenshot('page.png');
await cdp.screenshot('full-page.png', { fullPage: true });
```

### Waiting
```javascript
await cdp.wait(1000);  // Time-based
await cdp.waitForSelector('.element');  // Element-based
await cdp.waitForNavigation();  // Navigation-based
```

## Login Pattern

```javascript
const { loginToPastebin } = require('./login-helper');

await loginToPastebin(cdp, {
  username: 'myuser',
  password: 'mypass'
});
```

## Error Handling

```javascript
try {
  await cdp.launch();
  // ... operations
} catch (error) {
  await cdp.screenshot('error.png');
  console.error(error);
} finally {
  await cdp.close();
}
```

## Examples Directory

- `basic-navigation.js` - Core features demo
- `pastebin-example.js` - Login and create paste
- `jsfiddle-example.js` - Code editor manipulation

Run with: `node examples/basic-navigation.js`
