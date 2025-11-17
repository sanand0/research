const CDP = require('chrome-remote-interface');
const fs = require('fs');
const path = require('path');

async function testCDPOperations() {
  let browser, client;

  try {
    console.log('=== CDP Operations Test Suite ===\n');

    // 1. Connect to browser
    console.log('1. CONNECTING TO BROWSER');
    browser = await CDP({ port: 9222 });
    console.log('   Connected to browser\n');

    // 2. Create new target
    console.log('2. CREATING NEW TARGET');
    const { targetId } = await browser.Target.createTarget({ url: 'about:blank' });
    console.log('   Target ID:', targetId, '\n');

    // 3. Attach to target
    console.log('3. ATTACHING TO TARGET');
    client = await CDP({ port: 9222, target: targetId });
    console.log('   Attached successfully\n');

    const { Page, Runtime, DOM, Input, Network } = client;

    // 4. Enable domains
    console.log('4. ENABLING DOMAINS');
    await Page.enable();
    await DOM.enable();
    await Runtime.enable();
    await Network.enable();
    console.log('   Enabled: Page, DOM, Runtime, Network\n');

    // 5. Setup console listener
    console.log('5. SETTING UP CONSOLE LISTENER');
    const consoleLogs = [];
    Runtime.consoleAPICalled(params => {
      const msg = params.args.map(a => a.value || a.description).join(' ');
      consoleLogs.push({ type: params.type, message: msg });
    });
    console.log('   Console listener active\n');

    // 6. Navigate to local file
    console.log('6. NAVIGATING TO LOCAL HTML');
    const filePath = path.resolve(__dirname, 'test-page.html');
    const fileUrl = 'file://' + filePath;
    console.log('   URL:', fileUrl);

    await Page.navigate({ url: fileUrl });
    await Page.loadEventFired();
    console.log('   Page loaded\n');

    // 7. Get page info
    console.log('7. GETTING PAGE INFO');
    const titleResult = await Runtime.evaluate({ expression: 'document.title' });
    console.log('   Title:', titleResult.result.value);

    const h1Result = await Runtime.evaluate({ expression: 'document.querySelector("h1").textContent' });
    console.log('   H1:', h1Result.result.value, '\n');

    // 8. DOM Queries
    console.log('8. DOM QUERIES');
    const { root } = await DOM.getDocument();
    const inputNodes = await DOM.querySelectorAll({
      nodeId: root.nodeId,
      selector: 'input'
    });
    console.log('   Found', inputNodes.nodeIds.length, 'input elements');

    const buttons = await DOM.querySelectorAll({
      nodeId: root.nodeId,
      selector: 'button'
    });
    console.log('   Found', buttons.nodeIds.length, 'button elements\n');

    // 9. Fill form using Runtime.evaluate (simpler approach)
    console.log('9. FILLING FORM');
    await Runtime.evaluate({
      expression: `
        document.getElementById('username').value = 'testuser';
        document.getElementById('password').value = 'secret123';
      `
    });

    const usernameValue = await Runtime.evaluate({
      expression: 'document.getElementById("username").value'
    });
    console.log('   Username set to:', usernameValue.result.value);

    const passwordValue = await Runtime.evaluate({
      expression: 'document.getElementById("password").value'
    });
    console.log('   Password length:', passwordValue.result.value.length, '\n');

    // 10. Click button using JavaScript
    console.log('10. CLICKING BUTTON');
    await Runtime.evaluate({
      expression: 'document.getElementById("loginBtn").click()'
    });
    console.log('    Clicked login button');

    // Wait a bit for the event handler
    await new Promise(r => setTimeout(r, 100));

    const output = await Runtime.evaluate({
      expression: 'document.getElementById("output").innerText'
    });
    console.log('    Output:', output.result.value.split('\\n').pop(), '\n');

    // 11. Click counter multiple times
    console.log('11. INCREMENTING COUNTER');
    for (let i = 0; i < 3; i++) {
      await Runtime.evaluate({
        expression: 'document.getElementById("counterBtn").click()'
      });
    }
    await new Promise(r => setTimeout(r, 100));

    const counterValue = await Runtime.evaluate({
      expression: 'document.getElementById("count").textContent'
    });
    console.log('    Counter value after 3 clicks:', counterValue.result.value, '\n');

    // 12. Execute custom JavaScript
    console.log('12. EXECUTING CUSTOM JAVASCRIPT');
    const evalResult = await Runtime.evaluate({
      expression: `
        (function() {
          return {
            url: window.location.href,
            timestamp: new Date().toISOString(),
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight
          };
        })()
      `,
      returnByValue: true
    });
    console.log('    Result:', evalResult.result.value, '\n');

    // 13. Get computed styles
    console.log('13. GETTING COMPUTED STYLES');
    const bodyStyle = await Runtime.evaluate({
      expression: 'getComputedStyle(document.body).fontFamily'
    });
    console.log('    Body font-family:', bodyStyle.result.value, '\n');

    // 14. Take screenshot
    console.log('14. TAKING SCREENSHOT');
    const screenshot = await Page.captureScreenshot({ format: 'png' });
    const screenshotPath = path.join(__dirname, 'screenshot.png');
    fs.writeFileSync(screenshotPath, Buffer.from(screenshot.data, 'base64'));
    console.log('    Saved to:', screenshotPath);
    const stats = fs.statSync(screenshotPath);
    console.log('    Size:', Math.round(stats.size / 1024), 'KB\n');

    // 15. Get all console logs
    console.log('15. CONSOLE LOGS CAPTURED');
    consoleLogs.forEach((log, i) => {
      console.log(`    [${log.type}] ${log.message}`);
    });
    console.log('');

    // 16. Get DOM as HTML
    console.log('16. GETTING PAGE HTML');
    const htmlResult = await Runtime.evaluate({
      expression: 'document.documentElement.outerHTML'
    });
    const htmlLength = htmlResult.result.value.length;
    console.log('    HTML length:', htmlLength, 'characters\n');

    // 17. Close target
    console.log('17. CLOSING TARGET');
    await browser.Target.closeTarget({ targetId });
    console.log('    Target closed\n');

    console.log('=== ALL TESTS PASSED ===');

  } catch (err) {
    console.error('ERROR:', err.message);
    console.error('Stack:', err.stack);
  } finally {
    if (client) await client.close();
    if (browser) await browser.close();
  }
}

testCDPOperations();
