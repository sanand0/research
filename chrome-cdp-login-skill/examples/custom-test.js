/**
 * Custom Test Script for Chrome CDP Automation Skill
 *
 * This example demonstrates:
 * - Creating a CDPHelper instance
 * - Navigating to example.com
 * - Extracting page title and main heading
 * - Taking a screenshot
 * - Proper error handling and cleanup
 */

const CDPHelper = require('../cdp-helper');

async function customTest() {
  // Create a CDPHelper instance with visible browser window for debugging
  const cdp = new CDPHelper({
    headless: false,           // Run in visible mode to see what's happening
    viewport: { width: 1280, height: 800 },
    defaultTimeout: 30000      // 30 second timeout for operations
  });

  try {
    // Launch the browser and create a new page
    console.log('Launching browser...');
    await cdp.launch();

    // Navigate to example.com
    console.log('Navigating to example.com...');
    await cdp.goto('https://example.com', {
      waitUntil: 'networkidle2'  // Wait until network activity settles
    });

    // Wait a moment for page to fully render
    await cdp.wait(1000);

    // Extract the page title using evaluate()
    console.log('Extracting page title...');
    const pageTitle = await cdp.evaluate(() => {
      return document.title;
    });
    console.log('Page Title:', pageTitle);

    // Extract the main heading text using getText()
    console.log('Extracting main heading...');
    const mainHeading = await cdp.getText('h1');
    console.log('Main Heading:', mainHeading);

    // Alternative: Extract heading using evaluate() for more control
    const headingDetails = await cdp.evaluate(() => {
      const h1 = document.querySelector('h1');
      return {
        text: h1?.textContent,
        tagName: h1?.tagName,
        exists: !!h1
      };
    });
    console.log('Heading Details:', headingDetails);

    // Take a screenshot of the page
    console.log('Taking screenshot...');
    await cdp.screenshot('example-com-screenshot.png');
    console.log('Screenshot saved to: example-com-screenshot.png');

    // Optional: Get additional page information
    const pageInfo = await cdp.evaluate(() => {
      return {
        url: window.location.href,
        readyState: document.readyState,
        paragraphCount: document.querySelectorAll('p').length,
        linkCount: document.querySelectorAll('a').length
      };
    });
    console.log('Page Info:', pageInfo);

    console.log('\nTest completed successfully!');

  } catch (error) {
    // Error handling: log the error and take a screenshot for debugging
    console.error('Error occurred during test:', error.message);

    try {
      // Try to capture error state in a screenshot
      await cdp.screenshot('error-screenshot.png');
      console.log('Error screenshot saved to: error-screenshot.png');
    } catch (screenshotError) {
      console.error('Failed to take error screenshot:', screenshotError.message);
    }

    // Re-throw the error for calling code to handle
    throw error;

  } finally {
    // Always close the browser, even if an error occurred
    console.log('Closing browser...');
    await cdp.close();
    console.log('Browser closed.');
  }
}

// Run the test if this script is executed directly
if (require.main === module) {
  customTest()
    .then(() => {
      console.log('\n=== Test execution completed ===');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n=== Test execution failed ===');
      console.error(error);
      process.exit(1);
    });
}

// Export for potential use in other scripts
module.exports = { customTest };
