const CDP = require('chrome-remote-interface');

async function testBasicNavigation() {
  let client;
  try {
    console.log('Connecting to Chrome via CDP...');
    client = await CDP({ port: 9222 });

    const { Page, Runtime, Network } = client;

    console.log('Enabling required domains...');
    await Page.enable();
    await Network.enable();
    await Runtime.enable();

    console.log('Navigating to example.com...');
    await Page.navigate({ url: 'https://example.com' });

    console.log('Waiting for page load...');
    await Page.loadEventFired();

    console.log('Getting page title...');
    const titleResult = await Runtime.evaluate({
      expression: 'document.title'
    });
    console.log('Page title:', titleResult.result.value);

    console.log('Getting page URL...');
    const urlResult = await Runtime.evaluate({
      expression: 'window.location.href'
    });
    console.log('Page URL:', urlResult.result.value);

    console.log('Getting page content length...');
    const contentResult = await Runtime.evaluate({
      expression: 'document.body.innerText.length'
    });
    console.log('Content length:', contentResult.result.value, 'characters');

    console.log('\n=== Basic Navigation Test PASSED ===');

  } catch (err) {
    console.error('ERROR:', err.message);
    console.error('Stack:', err.stack);
  } finally {
    if (client) {
      console.log('Closing connection...');
      await client.close();
    }
  }
}

testBasicNavigation();
