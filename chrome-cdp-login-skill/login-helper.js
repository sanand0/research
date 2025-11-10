#!/usr/bin/env node

/**
 * Login Helper - Common login patterns for various sites
 *
 * This module provides reusable login functions for sites with
 * easy registration and safe testing environments.
 */

const CDPHelper = require('./cdp-helper');
const path = require('path');

/**
 * Generic login flow
 */
async function genericLogin(cdp, loginUrl, credentials, selectors) {
  console.log('\n=== Starting Login Flow ===');

  // Navigate to login page
  await cdp.goto(loginUrl);

  // Wait for login form
  await cdp.waitForSelector(selectors.usernameInput);

  // Fill credentials
  await cdp.type(selectors.usernameInput, credentials.username);
  await cdp.type(selectors.passwordInput, credentials.password);

  // Submit form
  await Promise.all([
    cdp.waitForNavigation(),
    cdp.click(selectors.submitButton)
  ]);

  // Wait a bit for any redirects
  await cdp.wait(2000);

  console.log('Login completed');
  return true;
}

/**
 * CodePen login
 * Note: CodePen uses social auth primarily, but has username/password for some accounts
 */
async function loginToCodePen(cdp, credentials) {
  const sessionFile = path.join(__dirname, '.sessions', 'codepen-session.json');

  // Try loading existing session first
  if (await cdp.loadSession(sessionFile)) {
    await cdp.goto('https://codepen.io/');
    await cdp.wait(2000);

    // Check if still logged in
    const isLoggedIn = await cdp.exists('[data-component="UserAvatar"]');
    if (isLoggedIn) {
      console.log('Using existing CodePen session');
      return true;
    }
  }

  // Need to login
  await cdp.goto('https://codepen.io/accounts/login');

  // CodePen typically uses social login, but we'll handle email/password if available
  const hasEmailLogin = await cdp.exists('input[name="login"]');

  if (hasEmailLogin) {
    await cdp.type('input[name="login"]', credentials.username);
    await cdp.type('input[name="password"]', credentials.password);
    await cdp.click('button[type="submit"]');
    await cdp.wait(3000);
  } else {
    console.log('Note: CodePen primarily uses social login (GitHub, Twitter, etc.)');
    return false;
  }

  // Save session
  await cdp.saveSession(sessionFile);
  return true;
}

/**
 * Pastebin login
 */
async function loginToPastebin(cdp, credentials) {
  const sessionFile = path.join(__dirname, '.sessions', 'pastebin-session.json');

  // Try loading existing session
  if (await cdp.loadSession(sessionFile)) {
    await cdp.goto('https://pastebin.com/');
    await cdp.wait(2000);

    const isLoggedIn = await cdp.exists('.username');
    if (isLoggedIn) {
      console.log('Using existing Pastebin session');
      return true;
    }
  }

  // Login
  return await genericLogin(cdp, 'https://pastebin.com/login', credentials, {
    usernameInput: 'input[name="user_name"]',
    passwordInput: 'input[name="user_password"]',
    submitButton: 'button[type="submit"]'
  });
}

/**
 * JSFiddle - Note: JSFiddle allows anonymous usage but requires login for saving
 */
async function loginToJSFiddle(cdp, credentials) {
  const sessionFile = path.join(__dirname, '.sessions', 'jsfiddle-session.json');

  // Try loading existing session
  if (await cdp.loadSession(sessionFile)) {
    await cdp.goto('https://jsfiddle.net/');
    await cdp.wait(2000);

    const isLoggedIn = await cdp.exists('.user-logged-in');
    if (isLoggedIn) {
      console.log('Using existing JSFiddle session');
      return true;
    }
  }

  // JSFiddle uses GitHub OAuth primarily
  console.log('Note: JSFiddle uses GitHub OAuth for login');
  console.log('You can use it anonymously without login for most features');
  return false;
}

/**
 * GitHub login (useful for many sites that use GitHub OAuth)
 */
async function loginToGitHub(cdp, credentials) {
  const sessionFile = path.join(__dirname, '.sessions', 'github-session.json');

  // Try loading existing session
  if (await cdp.loadSession(sessionFile)) {
    await cdp.goto('https://github.com/');
    await cdp.wait(2000);

    const isLoggedIn = await cdp.exists('img[alt*="@' + credentials.username + '"]');
    if (isLoggedIn) {
      console.log('Using existing GitHub session');
      return true;
    }
  }

  // Login
  await cdp.goto('https://github.com/login');

  await cdp.type('input[name="login"]', credentials.username);
  await cdp.type('input[name="password"]', credentials.password);

  await Promise.all([
    cdp.waitForNavigation({ timeout: 10000 }),
    cdp.click('input[type="submit"][value="Sign in"]')
  ]);

  // Handle 2FA if present (wait for user intervention)
  await cdp.wait(2000);
  if (await cdp.exists('input[name="otp"]')) {
    console.log('\n=== 2FA REQUIRED ===');
    console.log('Please enter your 2FA code in the browser');
    console.log('Waiting 60 seconds for manual intervention...');
    await cdp.wait(60000);
  }

  // Save session
  await cdp.saveSession(sessionFile);
  return true;
}

/**
 * Create a paste on Pastebin (example action after login)
 */
async function createPasteOnPastebin(cdp, content, title = 'Test Paste') {
  await cdp.goto('https://pastebin.com/');

  await cdp.type('textarea[name="paste_code"]', content);
  await cdp.type('input[name="paste_name"]', title);

  // Select paste expiration
  await cdp.page.select('select[name="paste_expire_date"]', '10M'); // 10 minutes

  // Submit
  await Promise.all([
    cdp.waitForNavigation(),
    cdp.click('button[type="submit"]')
  ]);

  // Get the URL of the created paste
  const url = cdp.page.url();
  console.log(`Paste created: ${url}`);

  return url;
}

/**
 * Create a pen on CodePen (example action after login)
 */
async function createPenOnCodePen(cdp, code) {
  await cdp.goto('https://codepen.io/pen/');

  // Wait for editor to load
  await cdp.wait(3000);

  // CodePen uses a complex editor, so we use evaluate to set content
  await cdp.evaluate((htmlCode) => {
    // This is simplified - actual CodePen editor manipulation is more complex
    const htmlEditor = document.querySelector('.CodeMirror');
    if (htmlEditor && htmlEditor.CodeMirror) {
      htmlEditor.CodeMirror.setValue(htmlCode);
    }
  }, code.html || '');

  console.log('Pen created (note: CodePen editor requires more complex interaction)');
}

/**
 * Wait for manual login (useful for OAuth flows)
 */
async function waitForManualLogin(cdp, checkSelector, timeout = 120000) {
  console.log('\n=== MANUAL LOGIN REQUIRED ===');
  console.log('Please log in manually in the browser window');
  console.log(`Waiting up to ${timeout / 1000} seconds...`);

  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    if (await cdp.exists(checkSelector)) {
      console.log('Login detected!');
      return true;
    }
    await cdp.wait(2000);
  }

  throw new Error('Login timeout');
}

module.exports = {
  genericLogin,
  loginToCodePen,
  loginToPastebin,
  loginToJSFiddle,
  loginToGitHub,
  createPasteOnPastebin,
  createPenOnCodePen,
  waitForManualLogin,
};
