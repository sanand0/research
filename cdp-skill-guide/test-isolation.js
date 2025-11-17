#!/usr/bin/env node

/**
 * Test: Create Fresh Targets for Isolation Pattern
 * Tests the isolation pattern from SKILL.md section:
 * "Best Practices > 5. Create Fresh Targets for Isolation"
 */

const CDP = require('chrome-remote-interface');
const fs = require('fs');

// Test configuration
const TEST_PAGE = 'file:///home/user/research/cdp-skill-guide/test-page.html';
const NUM_TARGETS = 3;
const RESULTS = {
  targets: [],
  startTime: null,
  endTime: null,
  errors: []
};

/**
 * Helper function from SKILL.md: runInIsolation pattern
 * (As documented, but adapted to track metrics)
 */
async function runInIsolation(taskId, task) {
  const taskStart = Date.now();
  const browser = await CDP({ port: 9222 });
  const createTargetStart = Date.now();

  const { targetId } = await browser.Target.createTarget({ url: 'about:blank' });
  const createTargetDuration = Date.now() - createTargetStart;

  const client = await CDP({ port: 9222, target: targetId });

  try {
    const taskResult = await task(client);
    return {
      taskId,
      targetId,
      success: true,
      createTargetDuration,
      taskDuration: Date.now() - taskStart,
      result: taskResult
    };
  } catch (err) {
    return {
      taskId,
      targetId,
      success: false,
      createTargetDuration,
      taskDuration: Date.now() - taskStart,
      error: err.message
    };
  } finally {
    await browser.Target.closeTarget({ targetId });
    await client.close();
    await browser.close();
  }
}

/**
 * Task: Set unique username in form and verify
 */
async function setAndVerifyUsername(client, username) {
  const { Page, Runtime } = client;

  // Enable domains
  await Page.enable();
  await Runtime.enable();

  // Navigate to test page
  const navResult = await Page.navigate({ url: TEST_PAGE });
  if (navResult.errorText) {
    throw new Error(`Navigation failed: ${navResult.errorText}`);
  }

  // Wait for page load
  try {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('Load timeout')), 10000);
      Page.loadEventFired(() => {
        clearTimeout(timer);
        resolve();
      });
    });
  } catch (e) {
    console.warn(`  Warning: ${e.message}, continuing anyway...`);
  }

  // Set username
  await Runtime.evaluate({
    expression: `document.getElementById('username').value = '${username}';`
  });

  // Get the value back to verify
  const { result } = await Runtime.evaluate({
    expression: `document.getElementById('username').value`,
    returnByValue: true
  });

  if (result.value !== username) {
    throw new Error(`Username mismatch: expected '${username}', got '${result.value}'`);
  }

  return {
    username,
    verified: true,
    value: result.value
  };
}

/**
 * Main test function
 */
async function runTests() {
  console.log('\n=== CDP Isolation Pattern Test ===\n');
  console.log(`Testing pattern: "Create Fresh Targets for Isolation"`);
  console.log(`Number of targets: ${NUM_TARGETS}`);
  console.log(`Test page: ${TEST_PAGE}\n`);

  RESULTS.startTime = Date.now();
  const usernames = ['alice', 'bob', 'charlie'];
  const tasks = [];

  // Create tasks - each will run in isolation
  for (let i = 0; i < NUM_TARGETS; i++) {
    const username = usernames[i];
    const task = async (client) => {
      return setAndVerifyUsername(client, username);
    };

    tasks.push(runInIsolation(i + 1, task));
  }

  // Run all tasks in parallel
  console.log('Creating 3 isolated targets in parallel...\n');
  const results = await Promise.all(tasks);
  RESULTS.endTime = Date.now();

  // Process results
  let allSuccess = true;
  for (const result of results) {
    console.log(`Target ${result.taskId}:`);
    console.log(`  Target ID: ${result.targetId}`);
    console.log(`  Create target time: ${result.createTargetDuration}ms`);
    console.log(`  Total task time: ${result.taskDuration}ms`);

    if (result.success) {
      console.log(`  Status: SUCCESS`);
      console.log(`  Username set to: "${result.result.username}"`);
      console.log(`  Verified: ${result.result.verified}`);
      RESULTS.targets.push(result);
    } else {
      console.log(`  Status: FAILED`);
      console.log(`  Error: ${result.error}`);
      RESULTS.errors.push(result);
      allSuccess = false;
    }
    console.log();
  }

  return allSuccess;
}

/**
 * Test isolation: verify targets had independent state
 */
async function testIsolationIntegrity() {
  console.log('=== Isolation Integrity Test ===\n');
  console.log('Verifying that each target maintained its own isolated state...\n');

  // Create 3 targets simultaneously
  const browser = await CDP({ port: 9222 });
  const targets = [];

  console.log('Step 1: Creating 3 targets...');
  const createStart = Date.now();

  for (let i = 0; i < 3; i++) {
    const { targetId } = await browser.Target.createTarget({ url: 'about:blank' });
    targets.push({
      id: i + 1,
      targetId,
      client: await CDP({ port: 9222, target: targetId })
    });
  }

  const createDuration = Date.now() - createStart;
  console.log(`Created 3 targets in ${createDuration}ms\n`);

  // Navigate all to same page but with different wait times
  console.log('Step 2: Navigating all targets to test page...');
  const navigateStart = Date.now();

  for (const target of targets) {
    const { Page, Runtime } = target.client;
    await Page.enable();
    await Runtime.enable();

    const navResult = await Page.navigate({ url: TEST_PAGE });
    if (navResult.errorText) {
      throw new Error(`Navigation failed: ${navResult.errorText}`);
    }

    // Wait for load
    try {
      await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Timeout')), 10000);
        Page.loadEventFired(() => {
          clearTimeout(timer);
          resolve();
        });
      });
    } catch (e) {
      console.warn(`  Warning: ${e.message}`);
    }
  }

  const navigateDuration = Date.now() - navigateStart;
  console.log(`Navigated all targets in ${navigateDuration}ms\n`);

  // Set different values in each target
  console.log('Step 3: Setting unique values in each target...');
  const usernames = ['user1', 'user2', 'user3'];

  for (let i = 0; i < targets.length; i++) {
    const { Runtime } = targets[i].client;
    const username = usernames[i];

    await Runtime.evaluate({
      expression: `document.getElementById('username').value = '${username}';`
    });

    console.log(`  Target ${targets[i].id}: Set username to "${username}"`);
  }
  console.log();

  // Verify each target still has its own value
  console.log('Step 4: Verifying isolation - each target has independent state...');
  let isolationPassed = true;

  for (let i = 0; i < targets.length; i++) {
    const { Runtime } = targets[i].client;
    const expectedUsername = usernames[i];

    const { result } = await Runtime.evaluate({
      expression: `document.getElementById('username').value`,
      returnByValue: true
    });

    const actualUsername = result.value;
    const isCorrect = actualUsername === expectedUsername;

    console.log(`  Target ${targets[i].id}:`);
    console.log(`    Expected: "${expectedUsername}"`);
    console.log(`    Actual:   "${actualUsername}"`);
    console.log(`    Status:   ${isCorrect ? 'ISOLATED' : 'NOT ISOLATED'}`);

    if (!isCorrect) {
      isolationPassed = false;
    }
  }
  console.log();

  // Cleanup
  console.log('Step 5: Cleaning up...');
  const cleanupStart = Date.now();

  for (const target of targets) {
    await browser.Target.closeTarget({ targetId: target.targetId });
    await target.client.close();
  }

  await browser.close();

  const cleanupDuration = Date.now() - cleanupStart;
  console.log(`Cleaned up all targets in ${cleanupDuration}ms\n`);

  return {
    isolationPassed,
    createDuration,
    navigateDuration,
    cleanupDuration
  };
}

/**
 * Main execution
 */
async function main() {
  try {
    // Test 1: Pattern as documented
    const patternTestPassed = await runTests();

    console.log('\n=== Test Results Summary ===\n');
    console.log(`Total time: ${RESULTS.endTime - RESULTS.startTime}ms`);
    console.log(`Targets created: ${RESULTS.targets.length}`);
    console.log(`Errors encountered: ${RESULTS.errors.length}`);
    console.log(`Pattern test result: ${patternTestPassed ? 'PASS' : 'FAIL'}\n`);

    if (RESULTS.errors.length > 0) {
      console.log('Errors:');
      for (const error of RESULTS.errors) {
        console.log(`  - ${error.error}`);
      }
      console.log();
    }

    // Test 2: Isolation integrity
    const isolationTest = await testIsolationIntegrity();

    console.log('=== Isolation Integrity Result ===\n');
    console.log(`Isolation verified: ${isolationTest.isolationPassed ? 'YES' : 'NO'}`);
    console.log(`Time to create targets: ${isolationTest.createDuration}ms`);
    console.log(`Time to navigate targets: ${isolationTest.navigateDuration}ms`);
    console.log(`Time to cleanup targets: ${isolationTest.cleanupDuration}ms\n`);

    // Overall result
    const overallPassed = patternTestPassed && isolationTest.isolationPassed;

    console.log('=== Overall Result ===\n');
    console.log(`Pattern works as documented: ${overallPassed ? 'YES' : 'NO'}\n`);

    process.exit(overallPassed ? 0 : 1);

  } catch (error) {
    console.error('Test error:', error.message);
    process.exit(1);
  }
}

main();
