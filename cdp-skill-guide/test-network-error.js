const CDP = require('chrome-remote-interface');

async function testNetworkError() {
  let client;
  try {
    console.log('Connecting to Chrome via CDP...');
    client = await CDP({ port: 9222 });

    const { Page, Network, Runtime } = client;

    await Page.enable();
    await Network.enable();
    await Runtime.enable();

    // Set up network event listeners
    Network.requestWillBeSent(params => {
      console.log('Request:', params.request.url);
    });

    Network.loadingFailed(params => {
      console.log('LOADING FAILED:', params.errorText);
      console.log('  Request ID:', params.requestId);
      console.log('  Canceled:', params.canceled);
    });

    Network.responseReceived(params => {
      console.log('Response:', params.response.status, params.response.url);
    });

    console.log('\nAttempting navigation to example.com...');
    const navResult = await Page.navigate({ url: 'https://example.com' });
    console.log('Navigation result:', navResult);

    // Wait a bit for events
    await new Promise(resolve => setTimeout(resolve, 3000));

    const urlResult = await Runtime.evaluate({
      expression: 'window.location.href'
    });
    console.log('Final URL:', urlResult.result.value);

    const errorResult = await Runtime.evaluate({
      expression: 'document.body.innerText'
    });
    console.log('Page content:', errorResult.result.value);

  } catch (err) {
    console.error('ERROR:', err.message);
  } finally {
    if (client) {
      await client.close();
    }
  }
}

testNetworkError();
