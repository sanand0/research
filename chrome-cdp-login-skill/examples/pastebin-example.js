#!/usr/bin/env node

/**
 * Example: Create a paste on Pastebin
 *
 * This demonstrates logging into Pastebin and creating a paste.
 * Note: You'll need a Pastebin account. Registration is free and easy.
 */

const CDPHelper = require('../cdp-helper');
const { loginToPastebin, createPasteOnPastebin } = require('../login-helper');
const path = require('path');
const fs = require('fs');

async function main() {
  // Load credentials from environment or config file
  const credentialsFile = path.join(__dirname, '..', '.credentials.json');
  let credentials = {
    pastebin: {
      username: process.env.PASTEBIN_USERNAME || '',
      password: process.env.PASTEBIN_PASSWORD || ''
    }
  };

  if (fs.existsSync(credentialsFile)) {
    credentials = JSON.parse(fs.readFileSync(credentialsFile, 'utf8'));
  }

  if (!credentials.pastebin.username || !credentials.pastebin.password) {
    console.error('Error: Pastebin credentials not found');
    console.error('Please set PASTEBIN_USERNAME and PASTEBIN_PASSWORD environment variables');
    console.error('Or create a .credentials.json file with your credentials');
    process.exit(1);
  }

  const cdp = new CDPHelper({
    headless: false, // Set to true for headless mode
  });

  try {
    // Launch browser
    await cdp.launch();

    // Login to Pastebin
    console.log('Logging into Pastebin...');
    await loginToPastebin(cdp, credentials.pastebin);

    // Create a paste
    const pasteContent = `
# Test Paste from Chrome CDP Automation

This paste was created automatically using Chrome DevTools Protocol.

Date: ${new Date().toISOString()}

## Code Example

function greet(name) {
  console.log(\`Hello, \${name}!\`);
}

greet('World');
    `.trim();

    console.log('\nCreating paste...');
    const url = await createPasteOnPastebin(
      cdp,
      pasteContent,
      'CDP Automation Test - ' + new Date().toISOString()
    );

    console.log('\nSuccess! Paste created at:', url);

    // Take a screenshot
    await cdp.screenshot(path.join(__dirname, 'pastebin-result.png'));

  } catch (error) {
    console.error('Error:', error.message);
    await cdp.screenshot(path.join(__dirname, 'error.png'));
  } finally {
    // Keep browser open for a few seconds to see the result
    await cdp.wait(3000);
    await cdp.close();
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = main;
