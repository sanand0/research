#!/usr/bin/env node

/**
 * Test script for Chrome CDP Login Skill
 *
 * This script validates the skill setup and functionality.
 */

const fs = require('fs');
const path = require('path');

console.log('===========================================');
console.log('Chrome CDP Login Skill - Validation Test');
console.log('===========================================\n');

let testsPassed = 0;
let testsFailed = 0;

function test(description, fn) {
  try {
    fn();
    console.log(`✓ ${description}`);
    testsPassed++;
  } catch (error) {
    console.log(`✗ ${description}`);
    console.log(`  Error: ${error.message}`);
    testsFailed++;
  }
}

// Test 1: Check dependencies
test('package.json exists', () => {
  const packagePath = path.join(__dirname, 'package.json');
  if (!fs.existsSync(packagePath)) {
    throw new Error('package.json not found');
  }
  const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  if (!pkg.dependencies || !pkg.dependencies['puppeteer-core']) {
    throw new Error('puppeteer-core not in dependencies');
  }
});

// Test 2: Check core modules
test('CDPHelper module loads', () => {
  const CDPHelper = require('./cdp-helper');
  if (typeof CDPHelper !== 'function') {
    throw new Error('CDPHelper is not a constructor');
  }
});

test('LoginHelper module loads', () => {
  const loginHelper = require('./login-helper');
  if (typeof loginHelper.genericLogin !== 'function') {
    throw new Error('loginHelper.genericLogin is not a function');
  }
});

// Test 3: Check CDPHelper instantiation
test('CDPHelper can be instantiated', () => {
  const CDPHelper = require('./cdp-helper');
  const cdp = new CDPHelper({ headless: true });
  if (!cdp.options) {
    throw new Error('CDPHelper instance missing options');
  }
});

// Test 4: Check file structure
test('SKILL.md exists', () => {
  const skillPath = path.join(__dirname, 'SKILL.md');
  if (!fs.existsSync(skillPath)) {
    throw new Error('SKILL.md not found');
  }
  const content = fs.readFileSync(skillPath, 'utf8');
  if (content.length < 1000) {
    throw new Error('SKILL.md seems incomplete');
  }
});

test('Examples directory exists', () => {
  const examplesPath = path.join(__dirname, 'examples');
  if (!fs.existsSync(examplesPath)) {
    throw new Error('examples directory not found');
  }
});

test('Example scripts exist', () => {
  const examples = [
    'basic-navigation.js',
    'pastebin-example.js',
    'jsfiddle-example.js'
  ];

  examples.forEach(example => {
    const examplePath = path.join(__dirname, 'examples', example);
    if (!fs.existsSync(examplePath)) {
      throw new Error(`${example} not found`);
    }
  });
});

// Test 5: Check helper functions
test('CDPHelper has required methods', () => {
  const CDPHelper = require('./cdp-helper');
  const cdp = new CDPHelper();

  const requiredMethods = [
    'launch', 'goto', 'click', 'type', 'waitForSelector',
    'screenshot', 'close', 'exists', 'getText', 'saveSession',
    'loadSession', 'fillForm', 'evaluate'
  ];

  requiredMethods.forEach(method => {
    if (typeof cdp[method] !== 'function') {
      throw new Error(`CDPHelper missing method: ${method}`);
    }
  });
});

// Test 6: Check login helpers
test('Login helpers have required functions', () => {
  const loginHelper = require('./login-helper');

  const requiredFunctions = [
    'genericLogin',
    'loginToPastebin',
    'loginToGitHub',
    'createPasteOnPastebin',
    'waitForManualLogin'
  ];

  requiredFunctions.forEach(fn => {
    if (typeof loginHelper[fn] !== 'function') {
      throw new Error(`loginHelper missing function: ${fn}`);
    }
  });
});

// Test 7: Chrome detection (non-blocking)
test('Chrome detection works (may warn if not installed)', () => {
  const CDPHelper = require('./cdp-helper');
  const cdp = new CDPHelper();

  try {
    const chromePath = cdp.findChrome();
    console.log(`  Chrome found at: ${chromePath}`);
  } catch (error) {
    // This is expected if Chrome is not installed
    console.log('  Warning: Chrome not found (expected in some environments)');
  }
});

// Test 8: Check gitignore
test('.gitignore exists and contains credentials', () => {
  const gitignorePath = path.join(__dirname, '.gitignore');
  if (!fs.existsSync(gitignorePath)) {
    throw new Error('.gitignore not found');
  }
  const content = fs.readFileSync(gitignorePath, 'utf8');
  if (!content.includes('.credentials.json')) {
    throw new Error('.gitignore missing .credentials.json');
  }
});

// Summary
console.log('\n===========================================');
console.log('Test Results');
console.log('===========================================');
console.log(`Tests passed: ${testsPassed}`);
console.log(`Tests failed: ${testsFailed}`);

if (testsFailed === 0) {
  console.log('\n✓ All tests passed! Skill is ready to use.');
  console.log('\nNote: Some functionality requires Chrome/Chromium to be installed.');
  console.log('To fully test the skill, run: node examples/basic-navigation.js');
  process.exit(0);
} else {
  console.log('\n✗ Some tests failed. Please review the errors above.');
  process.exit(1);
}
