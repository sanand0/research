#!/usr/bin/env node

/**
 * Example: Create and run code on JSFiddle
 *
 * JSFiddle allows anonymous usage, so this demonstrates automation
 * without necessarily requiring login.
 */

const CDPHelper = require('../cdp-helper');
const path = require('path');

async function main() {
  const cdp = new CDPHelper({
    headless: false,
  });

  try {
    await cdp.launch();

    console.log('Navigating to JSFiddle...');
    await cdp.goto('https://jsfiddle.net/');

    // Wait for the editor to load
    await cdp.wait(3000);

    console.log('Setting up a simple JavaScript example...');

    // JSFiddle uses complex editor components, so we'll use evaluate
    await cdp.evaluate(() => {
      // Set HTML
      const htmlPanel = document.querySelector('[data-lang="html"]');
      if (htmlPanel) {
        const htmlEditor = htmlPanel.querySelector('.CodeMirror');
        if (htmlEditor && htmlEditor.CodeMirror) {
          htmlEditor.CodeMirror.setValue(`
<div id="app">
  <h1>Hello from CDP Automation!</h1>
  <button onclick="showMessage()">Click Me</button>
  <p id="message"></p>
</div>
          `.trim());
        }
      }

      // Set JavaScript
      const jsPanel = document.querySelector('[data-lang="javascript"]');
      if (jsPanel) {
        const jsEditor = jsPanel.querySelector('.CodeMirror');
        if (jsEditor && jsEditor.CodeMirror) {
          jsEditor.CodeMirror.setValue(`
function showMessage() {
  document.getElementById('message').textContent =
    'Clicked at ' + new Date().toLocaleTimeString();
}

console.log('JSFiddle automation test loaded!');
          `.trim());
        }
      }

      // Set CSS
      const cssPanel = document.querySelector('[data-lang="css"]');
      if (cssPanel) {
        const cssEditor = cssPanel.querySelector('.CodeMirror');
        if (cssEditor && cssEditor.CodeMirror) {
          cssEditor.CodeMirror.setValue(`
#app {
  font-family: Arial, sans-serif;
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  border: 2px solid #333;
  border-radius: 8px;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background: #0056b3;
}
          `.trim());
        }
      }
    });

    console.log('Code set! Waiting a moment...');
    await cdp.wait(2000);

    // Click the Run button
    console.log('Running the code...');
    const runButton = await cdp.page.$('#run');
    if (runButton) {
      await runButton.click();
      await cdp.wait(2000);
    }

    // Take a screenshot
    await cdp.screenshot(path.join(__dirname, 'jsfiddle-result.png'), {
      fullPage: true
    });

    console.log('\nSuccess! Screenshot saved to examples/jsfiddle-result.png');

  } catch (error) {
    console.error('Error:', error.message);
    console.error(error.stack);
    await cdp.screenshot(path.join(__dirname, 'error.png'));
  } finally {
    await cdp.wait(5000); // Keep open to see the result
    await cdp.close();
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = main;
