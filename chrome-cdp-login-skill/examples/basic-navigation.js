#!/usr/bin/env node

/**
 * Example: Basic navigation and interaction
 *
 * Demonstrates the core CDP helper capabilities without requiring login.
 */

const CDPHelper = require('../cdp-helper');
const path = require('path');

async function main() {
  const cdp = new CDPHelper({
    headless: false, // Set to true for headless operation
  });

  try {
    console.log('Launching browser...');
    await cdp.launch();

    // Example 1: Navigate to a page
    console.log('\n=== Example 1: Navigation ===');
    await cdp.goto('https://example.com');
    await cdp.wait(1000);

    // Get page title
    const title = await cdp.evaluate(() => document.title);
    console.log('Page title:', title);

    // Take screenshot
    await cdp.screenshot(path.join(__dirname, 'example-com.png'));

    // Example 2: Search on a search engine
    console.log('\n=== Example 2: Form Interaction ===');
    await cdp.goto('https://duckduckgo.com');

    // Wait for search box
    await cdp.waitForSelector('input[name="q"]');

    // Type search query
    await cdp.type('input[name="q"]', 'Chrome DevTools Protocol');

    // Submit search
    await Promise.all([
      cdp.waitForNavigation(),
      cdp.click('button[type="submit"]')
    ]);

    console.log('Search completed');
    await cdp.wait(2000);

    // Example 3: Extract data from page
    console.log('\n=== Example 3: Data Extraction ===');
    const results = await cdp.evaluate(() => {
      const items = [];
      const resultElements = document.querySelectorAll('[data-result="result"]');

      for (let i = 0; i < Math.min(3, resultElements.length); i++) {
        const elem = resultElements[i];
        const title = elem.querySelector('h2')?.textContent || '';
        const link = elem.querySelector('a')?.href || '';
        items.push({ title, link });
      }

      return items;
    });

    console.log('Top 3 search results:');
    results.forEach((result, i) => {
      console.log(`${i + 1}. ${result.title}`);
      console.log(`   ${result.link}`);
    });

    // Example 4: Check if element exists
    console.log('\n=== Example 4: Element Detection ===');
    const hasSearchBox = await cdp.exists('input[name="q"]');
    console.log('Search box present:', hasSearchBox);

    // Take final screenshot
    await cdp.screenshot(path.join(__dirname, 'search-results.png'));

    console.log('\nAll examples completed successfully!');

  } catch (error) {
    console.error('Error:', error.message);
    await cdp.screenshot(path.join(__dirname, 'error.png'));
  } finally {
    await cdp.wait(2000);
    await cdp.close();
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = main;
