const CDP = require('chrome-remote-interface');

async function testWithProxyPreAuth() {
  let browser, client;

  try {
    console.log('1. Getting proxy credentials...');
    const proxyUrl = new URL(process.env.HTTPS_PROXY);
    const proxyAuth = Buffer.from(`${proxyUrl.username}:${proxyUrl.password}`).toString('base64');

    console.log('2. Connecting to browser...');
    browser = await CDP({ port: 9222 });

    console.log('3. Creating new target...');
    const { targetId } = await browser.Target.createTarget({ url: 'about:blank' });

    console.log('4. Attaching to target...');
    client = await CDP({ port: 9222, target: targetId });

    const { Page, Network, Runtime } = client;

    console.log('5. Enabling Network with extra headers...');
    await Network.enable();
    await Page.enable();
    await Runtime.enable();

    console.log('6. Setting Proxy-Authorization header globally...');
    await Network.setExtraHTTPHeaders({
      headers: {
        'Proxy-Authorization': `Basic ${proxyAuth}`
      }
    });

    // Monitor network
    Network.requestWillBeSent(p => {
      console.log('   Request:', p.request.url);
      console.log('   Headers:', Object.keys(p.request.headers).join(', '));
    });
    Network.loadingFailed(p => console.log('   FAILED:', p.errorText));
    Network.responseReceived(p => console.log('   Response:', p.response.status, p.response.url));

    console.log('7. Navigating to httpbin.org...');
    const navResult = await Page.navigate({ url: 'https://httpbin.org/get' });
    console.log('   Nav result:', navResult);

    if (!navResult.errorText) {
      console.log('8. Waiting for load...');
      await Promise.race([
        Page.loadEventFired(),
        new Promise((_, r) => setTimeout(() => r(new Error('timeout')), 15000))
      ]).catch(e => console.log('   Load timeout:', e.message));

      console.log('9. Getting page content...');
      const result = await Runtime.evaluate({
        expression: 'document.body.innerText.substring(0, 500)'
      });
      console.log('   Content:', result.result.value);
    } else {
      console.log('   Navigation error:', navResult.errorText);
    }

    console.log('10. Cleaning up...');
    await browser.Target.closeTarget({ targetId });

  } catch (err) {
    console.error('ERROR:', err.message);
  } finally {
    if (client) await client.close();
    if (browser) await browser.close();
  }
}

testWithProxyPreAuth();
