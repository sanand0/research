#!/usr/bin/env node

/**
 * Chrome CDP Helper for Web Automation
 *
 * Provides simplified functions for common web automation tasks using
 * Chrome DevTools Protocol via Puppeteer.
 */

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

class CDPHelper {
  constructor(options = {}) {
    this.options = {
      headless: options.headless !== false, // default to true
      executablePath: options.executablePath || null, // Will be determined at launch
      userDataDir: options.userDataDir || path.join(__dirname, '.chrome-profile'),
      viewport: options.viewport || { width: 1280, height: 800 },
      defaultTimeout: options.defaultTimeout || 30000,
      ...options
    };
    this.browser = null;
    this.page = null;
  }

  /**
   * Find Chrome executable in common locations
   */
  findChrome() {
    const possiblePaths = [
      '/usr/bin/google-chrome',
      '/usr/bin/chromium-browser',
      '/usr/bin/chromium',
      '/usr/local/bin/chrome',
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    ];

    for (const chromePath of possiblePaths) {
      if (fs.existsSync(chromePath)) {
        return chromePath;
      }
    }

    // Try which command
    const { execSync } = require('child_process');
    try {
      const result = execSync('which google-chrome chromium-browser chromium 2>/dev/null | head -1', {
        encoding: 'utf8'
      }).trim();
      if (result) return result;
    } catch (e) {
      // Ignore errors
    }

    throw new Error('Chrome/Chromium not found. Please install Chrome or specify executablePath.');
  }

  /**
   * Launch browser and create a new page
   */
  async launch() {
    // Find Chrome if not specified
    if (!this.options.executablePath) {
      this.options.executablePath = this.findChrome();
    }

    console.log('Launching Chrome with options:', {
      executablePath: this.options.executablePath,
      headless: this.options.headless
    });

    this.browser = await puppeteer.launch({
      executablePath: this.options.executablePath,
      headless: this.options.headless,
      userDataDir: this.options.userDataDir,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
      ],
      defaultViewport: this.options.viewport,
    });

    this.page = await this.browser.newPage();
    await this.page.setDefaultTimeout(this.options.defaultTimeout);

    // Set a realistic user agent
    await this.page.setUserAgent(
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );

    return this.page;
  }

  /**
   * Navigate to a URL and wait for network idle
   */
  async goto(url, options = {}) {
    console.log(`Navigating to: ${url}`);
    return await this.page.goto(url, {
      waitUntil: options.waitUntil || 'networkidle2',
      timeout: options.timeout || this.options.defaultTimeout,
    });
  }

  /**
   * Wait for a selector to appear
   */
  async waitForSelector(selector, options = {}) {
    console.log(`Waiting for selector: ${selector}`);
    return await this.page.waitForSelector(selector, {
      timeout: options.timeout || this.options.defaultTimeout,
      visible: options.visible !== false,
    });
  }

  /**
   * Type text into an input field
   */
  async type(selector, text, options = {}) {
    await this.waitForSelector(selector);
    await this.page.type(selector, text, {
      delay: options.delay || 50, // Simulate human typing
    });
  }

  /**
   * Click an element
   */
  async click(selector, options = {}) {
    await this.waitForSelector(selector);
    console.log(`Clicking: ${selector}`);
    await this.page.click(selector, options);
  }

  /**
   * Wait for navigation to complete
   */
  async waitForNavigation(options = {}) {
    return await this.page.waitForNavigation({
      waitUntil: options.waitUntil || 'networkidle2',
      timeout: options.timeout || this.options.defaultTimeout,
    });
  }

  /**
   * Take a screenshot
   */
  async screenshot(filepath, options = {}) {
    console.log(`Taking screenshot: ${filepath}`);
    return await this.page.screenshot({
      path: filepath,
      fullPage: options.fullPage || false,
      ...options
    });
  }

  /**
   * Get page content
   */
  async content() {
    return await this.page.content();
  }

  /**
   * Evaluate JavaScript in the page context
   */
  async evaluate(fn, ...args) {
    return await this.page.evaluate(fn, ...args);
  }

  /**
   * Fill a form with data
   */
  async fillForm(formData) {
    for (const [selector, value] of Object.entries(formData)) {
      await this.type(selector, value);
    }
  }

  /**
   * Wait for a specific amount of time
   */
  async wait(milliseconds) {
    console.log(`Waiting ${milliseconds}ms...`);
    return new Promise(resolve => setTimeout(resolve, milliseconds));
  }

  /**
   * Check if an element exists
   */
  async exists(selector) {
    try {
      const element = await this.page.$(selector);
      return element !== null;
    } catch (e) {
      return false;
    }
  }

  /**
   * Get text content from an element
   */
  async getText(selector) {
    await this.waitForSelector(selector);
    return await this.page.$eval(selector, el => el.textContent);
  }

  /**
   * Get all cookies
   */
  async getCookies() {
    return await this.page.cookies();
  }

  /**
   * Set cookies
   */
  async setCookies(cookies) {
    return await this.page.setCookie(...cookies);
  }

  /**
   * Save session data (cookies and localStorage)
   */
  async saveSession(filepath) {
    const cookies = await this.getCookies();
    const localStorage = await this.page.evaluate(() => {
      return JSON.stringify(window.localStorage);
    });

    fs.writeFileSync(filepath, JSON.stringify({
      cookies,
      localStorage: JSON.parse(localStorage)
    }, null, 2));

    console.log(`Session saved to: ${filepath}`);
  }

  /**
   * Load session data
   */
  async loadSession(filepath) {
    if (!fs.existsSync(filepath)) {
      console.log('No saved session found');
      return false;
    }

    const session = JSON.parse(fs.readFileSync(filepath, 'utf8'));

    if (session.cookies) {
      await this.setCookies(session.cookies);
    }

    if (session.localStorage) {
      await this.page.evaluate((data) => {
        for (const [key, value] of Object.entries(data)) {
          window.localStorage.setItem(key, value);
        }
      }, session.localStorage);
    }

    console.log(`Session loaded from: ${filepath}`);
    return true;
  }

  /**
   * Close the browser
   */
  async close() {
    if (this.browser) {
      await this.browser.close();
      console.log('Browser closed');
    }
  }
}

// Export for use as a module
module.exports = CDPHelper;

// CLI support
if (require.main === module) {
  console.log('CDP Helper Library');
  console.log('Use: const CDPHelper = require("./cdp-helper");');
}
