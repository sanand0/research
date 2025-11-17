const CDP = require('chrome-remote-interface');

async function testWithProxyAuth() {
  let browser, client;

  try {
    console.log('1. Getting proxy credentials...');
    const proxyUrl = new URL(process.env.HTTPS_PROXY);
    const proxyAuth = Buffer.from(`${proxyUrl.username}:${proxyUrl.password}`).toString('base64');

    console.log('   Proxy host:', proxyUrl.hostname);
    console.log('   Proxy port:', proxyUrl.port);
    console.log('   Auth header:', proxyAuth.substring(0, 30) + '...');

    console.log('2. Connecting to browser...');
    browser = await CDP({ port: 9222 });

    console.log('3. Creating new target...');
    const { targetId } = await browser.Target.createTarget({ url: 'about:blank' });

    console.log('4. Attaching to target...');
    client = await CDP({ port: 9222, target: targetId });

    const { Page, Network, Fetch, Runtime } = client;

    console.log('5. Enabling domains...');
    await Network.enable();
    await Page.enable();
    await Runtime.enable();

    console.log('6. Setting up Fetch interception for proxy auth...');
    await Fetch.enable({
      handleAuthRequests: true,
      patterns: [{ urlPattern: '*' }]
    });

    // Handle auth requests
    let authHandled = false;
    Fetch.authRequired(async params => {
      console.log('   AUTH REQUIRED:', params.authChallenge.source);
      if (!authHandled) {
        authHandled = true;
        await Fetch.continueWithAuth({
          requestId: params.requestId,
          authChallengeResponse: {
            response: 'ProvideCredentials',
            username: proxyUrl.username,
            password: proxyUrl.password
          }
        });
        console.log('   Provided proxy credentials');
      }
    });

    // Continue all other requests
    Fetch.requestPaused(async params => {
      await Fetch.continueRequest({ requestId: params.requestId });
    });

    // Monitor network
    Network.requestWillBeSent(p => console.log('   Request:', p.request.url));
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

testWithProxyAuth();
