const CDP = require('chrome-remote-interface');

async function testWithNewTarget() {
  let browser;
  let client;

  try {
    console.log('1. Connecting to browser...');
    browser = await CDP({ port: 9222 });

    console.log('2. Creating new target (tab)...');
    const { targetId } = await browser.Target.createTarget({
      url: 'about:blank'
    });
    console.log('   Target ID:', targetId);

    console.log('3. Attaching to target...');
    client = await CDP({ port: 9222, target: targetId });

    const { Page, Runtime, Network } = client;

    console.log('4. Enabling domains...');
    await Page.enable();
    await Network.enable();
    await Runtime.enable();

    // Monitor network
    let requestCount = 0;
    let errorInfo = null;

    Network.requestWillBeSent(() => requestCount++);
    Network.loadingFailed(params => {
      errorInfo = params.errorText;
    });

    console.log('5. Navigating to httpbin.org (test site)...');
    const navResult = await Page.navigate({ url: 'https://httpbin.org/get' });
    console.log('   Navigation result:', navResult);

    if (navResult.errorText) {
      console.log('   ERROR:', navResult.errorText);
    }

    console.log('6. Waiting for load...');
    try {
      await Promise.race([
        Page.loadEventFired(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 10000))
      ]);
      console.log('   Page loaded successfully');
    } catch (e) {
      console.log('   Load event timeout/error:', e.message);
    }

    console.log('7. Getting page info...');
    const urlResult = await Runtime.evaluate({ expression: 'window.location.href' });
    console.log('   URL:', urlResult.result.value);

    const titleResult = await Runtime.evaluate({ expression: 'document.title' });
    console.log('   Title:', titleResult.result.value);

    const bodyResult = await Runtime.evaluate({
      expression: 'document.body.innerText.substring(0, 200)'
    });
    console.log('   Body (first 200 chars):', bodyResult.result.value);

    console.log('8. Network stats:');
    console.log('   Requests:', requestCount);
    if (errorInfo) console.log('   Last error:', errorInfo);

    console.log('\n=== Test Complete ===');

  } catch (err) {
    console.error('ERROR:', err.message);
  } finally {
    if (client) await client.close();
    if (browser) await browser.close();
  }
}

testWithNewTarget();
