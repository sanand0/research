const CDP = require('chrome-remote-interface');

async function testSimpleNavigation() {
  let client;
  try {
    console.log('Connecting to Chrome...');
    client = await CDP({ port: 9222 });
    const { Page, Runtime, Network } = client;

    await Page.enable();
    await Runtime.enable();
    await Network.enable();

    Network.requestWillBeSent(p => console.log('  Request:', p.request.url.substring(0, 80)));
    Network.responseReceived(p => console.log('  Response:', p.response.status, p.response.url.substring(0, 60)));
    Network.loadingFailed(p => console.log('  FAILED:', p.errorText));

    console.log('Navigating to httpbin.org/get...');
    const nav = await Page.navigate({ url: 'https://httpbin.org/get' });

    if (nav.errorText) {
      console.log('Navigation error:', nav.errorText);
      return;
    }

    console.log('Waiting for load...');
    await Promise.race([
      Page.loadEventFired(),
      new Promise((_, r) => setTimeout(() => r(new Error('timeout')), 20000))
    ]).catch(e => console.log('Load timeout:', e.message));

    console.log('Getting content...');
    const result = await Runtime.evaluate({
      expression: 'document.body.innerText.substring(0, 800)'
    });
    console.log('\nPage content:\n', result.result.value);

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    if (client) await client.close();
  }
}

testSimpleNavigation();
