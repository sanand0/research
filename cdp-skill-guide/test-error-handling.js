const CDP = require('chrome-remote-interface');
const fs = require('fs');

// ============================================================================
// CORE HELPER: waitWithTimeout - as documented in SKILL.md
// ============================================================================
async function waitWithTimeout(promise, ms, errorMessage) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error(errorMessage)), ms)
    )
  ]);
}

// ============================================================================
// TEST UTILITIES
// ============================================================================
const testResults = {
  passed: [],
  failed: []
};

function logTest(name, passed, details = '') {
  const status = passed ? '[OK]' : '[FAIL]';
  const message = `${status} ${name}`;
  if (passed) {
    testResults.passed.push(name);
    console.log(`\n${message}`);
  } else {
    testResults.failed.push(name);
    console.log(`\n${message}`);
    if (details) console.log(`    Error: ${details}`);
  }
}

// ============================================================================
// TEST 1: waitWithTimeout - Successful operation
// ============================================================================
async function testSuccessfulTimeout() {
  console.log('\n' + '='.repeat(70));
  console.log('TEST 1: waitWithTimeout - Successful Operation');
  console.log('='.repeat(70));

  try {
    const successPromise = new Promise(resolve => {
      setTimeout(() => resolve('success'), 50);
    });

    await waitWithTimeout(successPromise, 500, 'Operation timeout');
    logTest('waitWithTimeout - operation completes before timeout', true);
  } catch (err) {
    logTest('waitWithTimeout - operation completes before timeout', false, err.message);
  }
}

// ============================================================================
// TEST 2: waitWithTimeout - Timeout occurs
// ============================================================================
async function testTimeoutRejection() {
  console.log('\n' + '='.repeat(70));
  console.log('TEST 2: waitWithTimeout - Timeout Rejection');
  console.log('='.repeat(70));

  try {
    const slowPromise = new Promise(resolve => {
      setTimeout(() => resolve('never'), 5000);
    });

    await waitWithTimeout(slowPromise, 100, 'Operation timed out after 100ms');
    logTest('waitWithTimeout - timeout properly rejects promise', false, 'No timeout occurred');
  } catch (err) {
    if (err.message.includes('timed out')) {
      logTest('waitWithTimeout - timeout properly rejects promise', true);
      console.log(`  Timeout message: "${err.message}"`);
    } else {
      logTest('waitWithTimeout - timeout properly rejects promise', false, `Wrong error: ${err.message}`);
    }
  }
}

// ============================================================================
// TEST 3: Finally block cleanup on success
// ============================================================================
async function testFinallyBlockSuccess() {
  console.log('\n' + '='.repeat(70));
  console.log('TEST 3: Finally Block - Success Case');
  console.log('='.repeat(70));

  let cleanupExecuted = false;
  let operationSucceeded = false;

  try {
    try {
      operationSucceeded = true;
      console.log('Operation succeeded');
    } finally {
      cleanupExecuted = true;
      console.log('Finally block executed (cleanup)');
    }
  } catch (err) {
    logTest('Finally block - executed after success', false, err.message);
    return;
  }

  if (cleanupExecuted && operationSucceeded) {
    logTest('Finally block - executed after success', true);
    console.log('  Pattern: try { success } finally { cleanup }');
  } else {
    logTest('Finally block - executed after success', false, 'Cleanup not executed');
  }
}

// ============================================================================
// TEST 4: Finally block cleanup on error
// ============================================================================
async function testFinallyBlockError() {
  console.log('\n' + '='.repeat(70));
  console.log('TEST 4: Finally Block - Error Case');
  console.log('='.repeat(70));

  let cleanupExecuted = false;
  let errorCaught = false;

  try {
    try {
      throw new Error('Simulated operation error');
    } catch (opErr) {
      errorCaught = true;
      console.log(`Caught error: "${opErr.message}"`);
    } finally {
      cleanupExecuted = true;
      console.log('Finally block executed despite error (cleanup still happens)');
    }
  } catch (err) {
    logTest('Finally block - executed even on error', false, err.message);
    return;
  }

  if (cleanupExecuted && errorCaught) {
    logTest('Finally block - executed even on error', true);
    console.log('  Pattern: try { error } catch { handle } finally { cleanup }');
  } else {
    logTest('Finally block - executed even on error', false, 'Cleanup not executed');
  }
}

// ============================================================================
// TEST 5: Nested try-catch-finally
// ============================================================================
async function testNestedErrorHandling() {
  console.log('\n' + '='.repeat(70));
  console.log('TEST 5: Nested Error Handling');
  console.log('='.repeat(70));

  let outerCleanup = false;
  let innerCatch = false;
  let outerCatch = false;

  try {
    try {
      try {
        // Inner operation that throws
        throw new Error('Inner operation failed');
      } catch (innerErr) {
        innerCatch = true;
        console.log(`Inner catch: "${innerErr.message}"`);
        // Don't rethrow
      }
    } finally {
      console.log('Middle finally (no cleanup needed)');
    }
  } catch (outerErr) {
    outerCatch = true;
    console.log(`Outer catch: "${outerErr.message}"`);
  } finally {
    outerCleanup = true;
    console.log('Outer finally (main cleanup)');
  }

  if (innerCatch && outerCleanup && !outerCatch) {
    logTest('Nested error handling - proper error containment', true);
    console.log('  Error handled at inner level, outer cleanup still executed');
  } else {
    logTest('Nested error handling - proper error containment', false, 'Unexpected error flow');
  }
}

// ============================================================================
// TEST 6: Graceful degradation - continue despite error
// ============================================================================
async function testGracefulDegradation() {
  console.log('\n' + '='.repeat(70));
  console.log('TEST 6: Graceful Degradation - Continue After Error');
  console.log('='.repeat(70));

  let continueAfterError = false;
  let timeoutCaught = false;

  try {
    // Simulate timeout
    try {
      await waitWithTimeout(
        new Promise(resolve => setTimeout(resolve, 1000)),
        50,
        'Operation timeout'
      );
    } catch (timeoutErr) {
      timeoutCaught = true;
      console.warn(`Load timeout caught: "${timeoutErr.message}" (continuing anyway...)`);
    }

    // Try to continue using the page/resource
    if (timeoutCaught) {
      continueAfterError = true;
      console.log('Successfully continued operations despite timeout');
    }

    if (timeoutCaught && continueAfterError) {
      logTest('Graceful degradation - continue after timeout', true);
      console.log('  Pattern: catch timeout, log warning, continue with fallback behavior');
    } else {
      logTest('Graceful degradation - continue after timeout', false);
    }
  } catch (err) {
    logTest('Graceful degradation - continue after timeout', false, err.message);
  }
}

// ============================================================================
// TEST 7: Promise.race mechanism
// ============================================================================
async function testPromiseRace() {
  console.log('\n' + '='.repeat(70));
  console.log('TEST 7: Promise.race - Race Mechanism');
  console.log('='.repeat(70));

  let raceWorked = false;

  try {
    const operation = new Promise(resolve => {
      setTimeout(() => resolve('operation result'), 100);
    });

    const timeout = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('timeout')), 500);
    });

    const result = await Promise.race([operation, timeout]);

    if (result === 'operation result') {
      raceWorked = true;
      console.log('Promise.race resolved with operation result (operation faster than timeout)');
    }

    if (raceWorked) {
      logTest('Promise.race - operation completes before timeout', true);
    } else {
      logTest('Promise.race - operation completes before timeout', false);
    }
  } catch (err) {
    logTest('Promise.race - operation completes before timeout', false, err.message);
  }
}

// ============================================================================
// TEST 8: Promise.race with timeout winning
// ============================================================================
async function testPromiseRaceTimeout() {
  console.log('\n' + '='.repeat(70));
  console.log('TEST 8: Promise.race - Timeout Wins Race');
  console.log('='.repeat(70));

  let timeoutWon = false;

  try {
    const slowOperation = new Promise(resolve => {
      setTimeout(() => resolve('operation result'), 5000);
    });

    const fastTimeout = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Race timeout (operation too slow)')), 100);
    });

    await Promise.race([slowOperation, fastTimeout]);
    logTest('Promise.race - timeout properly rejects slow operation', false);
  } catch (err) {
    if (err.message.includes('timeout')) {
      timeoutWon = true;
      logTest('Promise.race - timeout properly rejects slow operation', true);
      console.log(`  Timeout won race: "${err.message}"`);
    } else {
      logTest('Promise.race - timeout properly rejects slow operation', false, err.message);
    }
  }
}

// ============================================================================
// TEST 9: Error message preservation through Promise.race
// ============================================================================
async function testErrorMessagePreservation() {
  console.log('\n' + '='.repeat(70));
  console.log('TEST 9: Error Message Preservation');
  console.log('='.repeat(70));

  const customMessage = 'Custom timeout error message for debugging';
  let messagePreserved = false;

  try {
    const operation = new Promise(resolve => {
      setTimeout(() => resolve('result'), 1000);
    });

    await waitWithTimeout(operation, 50, customMessage);
  } catch (err) {
    if (err.message === customMessage) {
      messagePreserved = true;
      console.log(`Error message preserved: "${err.message}"`);
    }
  }

  if (messagePreserved) {
    logTest('Error message preservation - custom message in timeout error', true);
  } else {
    logTest('Error message preservation - custom message in timeout error', false);
  }
}

// ============================================================================
// TEST 10: Error stacktrace in waitWithTimeout
// ============================================================================
async function testStacktracePreservation() {
  console.log('\n' + '='.repeat(70));
  console.log('TEST 10: Stack Trace Preservation');
  console.log('='.repeat(70));

  let stackPresent = false;

  try {
    await waitWithTimeout(
      new Promise(resolve => setTimeout(resolve, 1000)),
      50,
      'Stack trace test'
    );
  } catch (err) {
    // Stack trace should be present and be a string
    if (err.stack && typeof err.stack === 'string' && err.stack.length > 0) {
      stackPresent = true;
      console.log('Stack trace preserved (error has valid stack property)');
      // Show first line of stack for verification
      const firstLine = err.stack.split('\n')[0];
      console.log(`  Stack trace starts with: "${firstLine}"`);
    }
  }

  if (stackPresent) {
    logTest('Stack trace preservation - error has valid stack trace', true);
  } else {
    logTest('Stack trace preservation - error has valid stack trace', false);
  }
}

// ============================================================================
// MAIN TEST RUNNER
// ============================================================================
async function runAllTests() {
  console.log('\n' + '█'.repeat(70));
  console.log('CDP ERROR HANDLING PATTERN TESTING');
  console.log('█'.repeat(70));
  console.log('\nTesting error handling patterns documented in SKILL.md:');
  console.log('  - waitWithTimeout helper function');
  console.log('  - Finally block cleanup (success and error cases)');
  console.log('  - Graceful degradation on timeouts');
  console.log('  - Promise.race mechanism');
  console.log('  - Error message and stack preservation');
  console.log('\n' + '█'.repeat(70));

  // Run all tests
  await testSuccessfulTimeout();
  await testTimeoutRejection();
  await testFinallyBlockSuccess();
  await testFinallyBlockError();
  await testNestedErrorHandling();
  await testGracefulDegradation();
  await testPromiseRace();
  await testPromiseRaceTimeout();
  await testErrorMessagePreservation();
  await testStacktracePreservation();

  // Print summary
  printSummary();
}

// ============================================================================
// TEST SUMMARY
// ============================================================================
function printSummary() {
  console.log('\n' + '█'.repeat(70));
  console.log('TEST SUMMARY');
  console.log('█'.repeat(70));

  const total = testResults.passed.length + testResults.failed.length;
  const passRate = total > 0 ? Math.round((testResults.passed.length / total) * 100) : 0;

  console.log(`\nTotal Tests: ${total}`);
  console.log(`Passed: ${testResults.passed.length}`);
  console.log(`Failed: ${testResults.failed.length}`);
  console.log(`Pass Rate: ${passRate}%`);

  if (testResults.failed.length > 0) {
    console.log('\nFailed Tests:');
    testResults.failed.forEach(name => console.log(`  [FAIL] ${name}`));
  } else {
    console.log('\nAll tests PASSED!');
  }

  console.log('\n' + '█'.repeat(70));
}

// Run if executed directly
runAllTests().catch(err => {
  console.error('Fatal error:', err.message);
  console.error(err.stack);
  process.exit(1);
});
