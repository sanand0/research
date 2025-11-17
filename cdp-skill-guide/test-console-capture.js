const CDP = require('chrome-remote-interface');
const fs = require('fs');
const path = require('path');

/**
 * Test Console Log Capture Pattern from SKILL.md
 *
 * Tests:
 * 1. Basic console.log capture
 * 2. Multiple argument types (string, number, object, array, boolean, null, undefined)
 * 3. All log types (log, info, warn, error, debug)
 * 4. Performance impact
 * 5. Argument formatting and description handling
 */

const results = {
  timestamp: new Date().toISOString(),
  capturedLogs: [],
  testResults: [],
  performance: {
    startTime: 0,
    endTime: 0,
    duration: 0
  },
  errors: [],
  skillmdPattern: {
    used: false,
    notes: []
  }
};

async function main() {
  let browser, client;

  try {
    // Connect to browser
    console.log('[TEST] Connecting to Chrome on port 9222...');
    browser = await CDP({ port: 9222 });

    // Create new target for isolation
    console.log('[TEST] Creating new target...');
    const { targetId } = await browser.Target.createTarget({ url: 'about:blank' });

    // Connect to target
    console.log('[TEST] Connecting to target...');
    client = await CDP({ port: 9222, target: targetId });

    const { Page, Runtime } = client;

    // Enable domains
    console.log('[TEST] Enabling Page and Runtime domains...');
    await Page.enable();
    await Runtime.enable();

    results.performance.startTime = Date.now();

    // Setup console log capture pattern from SKILL.md
    console.log('[TEST] Setting up console log capture listener (SKILL.md pattern)...');
    let captureStartTime = Date.now();

    Runtime.consoleAPICalled(params => {
      const captureTime = Date.now() - captureStartTime;

      // Extract message from args using the pattern from SKILL.md
      const message = params.args.map(arg => {
        // This is the exact pattern from SKILL.md: arg.value || arg.description
        return arg.value || arg.description;
      }).join(' ');

      const logEntry = {
        type: params.type,
        message: message,
        timestamp: new Date().toISOString(),
        captureTime: captureTime,
        args: params.args.map(arg => ({
          type: arg.type,
          value: arg.value,
          description: arg.description
        }))
      };

      results.capturedLogs.push(logEntry);
      console.log(`[CAPTURE] ${params.type.toUpperCase()}: ${message}`);
    });

    results.skillmdPattern.used = true;
    results.skillmdPattern.notes.push('Used exact pattern from SKILL.md: arg.value || arg.description');

    // Navigate to test page
    console.log('[TEST] Navigating to test page...');
    const filePath = path.resolve(__dirname, 'test-page.html');
    const fileUrl = 'file://' + filePath;
    console.log('[TEST] File URL:', fileUrl);

    const navResult = await Page.navigate({
      url: fileUrl
    });

    if (navResult.errorText) {
      throw new Error(`Navigation failed: ${navResult.errorText}`);
    }

    // Wait for page load
    console.log('[TEST] Waiting for page load...');
    await Promise.race([
      Page.loadEventFired(),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Load timeout')), 5000)
      )
    ]).catch(e => {
      console.warn('[TEST] Load event warning:', e.message);
    });

    // Brief pause for initial page logs
    await new Promise(resolve => setTimeout(resolve, 500));

    // Test 1: Generate console.log entries with different argument types
    console.log('[TEST] Test 1: Generating console logs with various argument types...');
    await Runtime.evaluate({
      expression: `
        // String argument
        console.log('Test string argument');

        // Number argument
        console.log(42);
        console.log(3.14159);

        // Boolean arguments
        console.log(true);
        console.log(false);

        // Null and undefined
        console.log(null);
        console.log(undefined);

        // Object
        console.log({key: 'value', nested: {a: 1, b: 2}});

        // Array
        console.log([1, 2, 3, 'four', {five: 5}]);

        // Multiple arguments
        console.log('Multiple', 'string', 'arguments', 42, true);
      `
    });
    results.testResults.push({
      test: 'Test 1: Console.log with various argument types',
      status: 'completed'
    });

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 2: Generate console.info entries
    console.log('[TEST] Test 2: Generating console.info entries...');
    await Runtime.evaluate({
      expression: `
        console.info('Info message 1');
        console.info('Info with object', {type: 'test', id: 123});
        console.info('Info with array', [1, 2, 3]);
      `
    });
    results.testResults.push({
      test: 'Test 2: Console.info entries',
      status: 'completed'
    });

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 3: Generate console.warn entries
    console.log('[TEST] Test 3: Generating console.warn entries...');
    await Runtime.evaluate({
      expression: `
        console.warn('Warning message');
        console.warn('Warning with number', 999);
        console.warn('Multiple warnings', 'a', 'b', 'c');
      `
    });
    results.testResults.push({
      test: 'Test 3: Console.warn entries',
      status: 'completed'
    });

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 4: Generate console.error entries
    console.log('[TEST] Test 4: Generating console.error entries...');
    await Runtime.evaluate({
      expression: `
        console.error('Error message');
        console.error('Error with object', {error: true, code: 500});

        // Simulate error with Error object
        try {
          throw new Error('Simulated error');
        } catch (e) {
          console.error('Caught error:', e);
        }
      `
    });
    results.testResults.push({
      test: 'Test 4: Console.error entries',
      status: 'completed'
    });

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 5: Generate console.debug entries
    console.log('[TEST] Test 5: Generating console.debug entries...');
    await Runtime.evaluate({
      expression: `
        console.debug('Debug message');
        console.debug('Debug with details', {debug: true, level: 'verbose'});
      `
    });
    results.testResults.push({
      test: 'Test 5: Console.debug entries',
      status: 'completed'
    });

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 6: Interact with page buttons to trigger page's own logging
    console.log('[TEST] Test 6: Triggering page interactions (button clicks)...');

    // Click counter button multiple times
    for (let i = 0; i < 3; i++) {
      await Runtime.evaluate({
        expression: 'document.getElementById("counterBtn").click()'
      });
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    // Fill form and click login
    await Runtime.evaluate({
      expression: `
        document.getElementById('username').value = 'testuser';
        document.getElementById('password').value = 'testpass123';
        document.getElementById('loginBtn').click();
      `
    });

    results.testResults.push({
      test: 'Test 6: Page interaction events',
      status: 'completed'
    });

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 7: Edge cases - special characters, long strings, deeply nested objects
    console.log('[TEST] Test 7: Edge case logs with special characters...');
    await Runtime.evaluate({
      expression: `
        // Special characters
        console.log('String with "quotes" and \\'apostrophes\\'');
        console.log('Unicode: 你好世界 🚀 ñ');

        // Long string
        console.log('x'.repeat(200));

        // Deeply nested object
        const deepObj = {
          level1: {
            level2: {
              level3: {
                level4: {
                  level5: 'deep value'
                }
              }
            }
          }
        };
        console.log(deepObj);

        // Circular reference simulation
        const obj = {name: 'test'};
        console.log('Object with methods', {
          data: 'value',
          method: function() { return 42; }
        });
      `
    });
    results.testResults.push({
      test: 'Test 7: Edge case logs',
      status: 'completed'
    });

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 8: Large number of logs (performance test)
    console.log('[TEST] Test 8: Performance test - generating 100 logs...');
    const perfStartTime = Date.now();

    await Runtime.evaluate({
      expression: `
        for (let i = 0; i < 100; i++) {
          console.log('Log #' + i + ' with message');
        }
      `
    });

    const perfEndTime = Date.now();
    results.testResults.push({
      test: 'Test 8: Performance - 100 consecutive logs',
      status: 'completed',
      duration: perfEndTime - perfStartTime
    });

    await new Promise(resolve => setTimeout(resolve, 500));

    // Get page state for verification
    console.log('[TEST] Getting page state for verification...');
    const pageState = await Runtime.evaluate({
      expression: `({
        url: location.href,
        title: document.title,
        outputHTML: document.getElementById('output').innerHTML
      })`,
      returnByValue: true
    });

    results.pageState = pageState.result.value;

    results.performance.endTime = Date.now();
    results.performance.duration = results.performance.endTime - results.performance.startTime;

    // Analyze results
    console.log('\n========== TEST RESULTS ==========\n');
    analyzeResults();

  } catch (error) {
    console.error('[ERROR]', error.message);
    results.errors.push({
      error: error.message,
      stack: error.stack
    });
  } finally {
    // Cleanup
    if (client) {
      await client.close();
    }
    if (browser) {
      try {
        const { targetId: tid } = browser.Target.getTargets ? await browser.Target.getTargets() : { targetId: null };
        await browser.Target.closeTarget({ targetId });
      } catch (e) {
        // Ignore cleanup errors
      }
      await browser.close();
    }

    // Save detailed results
    const reportPath = path.join(__dirname, 'console-capture-results.json');
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    console.log(`\n[TEST] Detailed results saved to: ${reportPath}`);
  }
}

function analyzeResults() {
  console.log(`Total logs captured: ${results.capturedLogs.length}`);
  console.log(`Test duration: ${results.performance.duration}ms\n`);

  // Group logs by type
  const logsByType = {};
  results.capturedLogs.forEach(log => {
    if (!logsByType[log.type]) {
      logsByType[log.type] = [];
    }
    logsByType[log.type].push(log);
  });

  console.log('Logs by type:');
  Object.entries(logsByType).forEach(([type, logs]) => {
    console.log(`  ${type}: ${logs.length}`);
  });

  // Check for expected log types
  console.log('\nLog type verification:');
  const expectedTypes = ['log', 'info', 'warn', 'error', 'debug'];
  expectedTypes.forEach(type => {
    const captured = logsByType[type] ? logsByType[type].length : 0;
    const status = captured > 0 ? '✓' : '✗';
    console.log(`  ${status} ${type}: ${captured} logs`);
  });

  // Analyze argument types
  console.log('\nArgument types captured:');
  const argTypes = new Set();
  results.capturedLogs.forEach(log => {
    log.args.forEach(arg => {
      if (arg.type) {
        argTypes.add(arg.type);
      }
    });
  });
  argTypes.forEach(type => {
    console.log(`  • ${type}`);
  });

  // Check for formatting issues
  console.log('\nFormatting verification:');
  let formatIssues = 0;
  results.capturedLogs.forEach((log, idx) => {
    if (!log.message || log.message.length === 0) {
      console.log(`  ✗ Log ${idx}: Empty message`);
      formatIssues++;
    }
    if (log.type && !log.timestamp) {
      console.log(`  ✗ Log ${idx}: Missing timestamp`);
      formatIssues++;
    }
  });
  if (formatIssues === 0) {
    console.log('  ✓ All logs properly formatted');
  }

  // Performance analysis
  console.log('\nPerformance metrics:');
  console.log(`  Total duration: ${results.performance.duration}ms`);
  console.log(`  Logs per second: ${(results.capturedLogs.length / results.performance.duration * 1000).toFixed(2)}`);

  const captureTimes = results.capturedLogs.map(log => log.captureTime);
  const avgCaptureTime = captureTimes.reduce((a, b) => a + b, 0) / captureTimes.length;
  const maxCaptureTime = Math.max(...captureTimes);
  const minCaptureTime = Math.min(...captureTimes);

  console.log(`  Average capture time: ${avgCaptureTime.toFixed(2)}ms`);
  console.log(`  Min capture time: ${minCaptureTime}ms`);
  console.log(`  Max capture time: ${maxCaptureTime}ms`);

  // Report any issues
  if (results.errors.length > 0) {
    console.log('\nErrors encountered:');
    results.errors.forEach(err => {
      console.log(`  ✗ ${err.error}`);
    });
  } else {
    console.log('\n✓ No errors encountered');
  }

  // Specific observations
  console.log('\nObservations:');

  // Check if page logs were captured (from page interaction)
  const pageInteractionLogs = results.capturedLogs.filter(log =>
    log.message.includes('Counter clicked') ||
    log.message.includes('Login attempted') ||
    log.message.includes('Page loaded')
  );

  if (pageInteractionLogs.length > 0) {
    console.log(`  ✓ Page interaction logs captured: ${pageInteractionLogs.length}`);
  } else {
    console.log(`  ✗ No page interaction logs captured`);
  }

  // Check for complex type handling
  const complexTypes = results.capturedLogs.filter(log =>
    log.message.includes('{') || log.message.includes('[')
  );

  console.log(`  ✓ Complex object/array logs: ${complexTypes.length}`);

  // Summary
  console.log('\nSummary:');
  const totalExpected = results.capturedLogs.length;
  const allTypesCaptured = expectedTypes.every(type => logsByType[type] && logsByType[type].length > 0);

  if (allTypesCaptured && formatIssues === 0 && results.errors.length === 0) {
    console.log('✓ Console capture pattern WORKS AS DOCUMENTED');
  } else {
    console.log('✗ Some issues found with console capture pattern');
  }
}

main().catch(console.error);
