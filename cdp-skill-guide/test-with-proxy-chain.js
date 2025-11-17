const puppeteer = require('puppeteer-core');
const proxyChain = require('proxy-chain');

async function testWithProxyChain() {
  let browser, anonymizedProxy;
  try {
    console.log('1. Creating anonymized proxy...');
    const oldProxyUrl = process.env.HTTPS_PROXY;
    console.log('   Original proxy:', oldProxyUrl.substring(0, 60) + '...');

    // Create a local proxy that handles auth
    anonymizedProxy = await proxyChain.anonymizeProxy(oldProxyUrl);
    console.log('   Anonymized proxy:', anonymizedProxy);

    console.log('2. Launching browser...');
    browser = await puppeteer.launch({
      executablePath: '/usr/bin/google-chrome-stable',
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--ignore-certificate-errors',  // Accept proxy's SSL interception cert
        `--proxy-server=${anonymizedProxy}`
      ]
    });

    console.log('3. Creating new page...');
    const page = await browser.newPage();

    console.log('4. Navigating to httpbin.org...');
    const response = await page.goto('https://httpbin.org/get', {
      waitUntil: 'networkidle0',
      timeout: 30000
    });

    console.log('   Status:', response.status());
    console.log('   URL:', response.url());

    console.log('5. Getting page content...');
    const content = await page.evaluate(() => document.body.innerText);
    console.log('\nPage content:\n', content);

    console.log('\n=== SUCCESS! Proxy chain works! ===');

    // Test another site
    console.log('\n6. Testing example.com...');
    await page.goto('https://example.com', { waitUntil: 'networkidle0' });
    const title = await page.title();
    console.log('   Title:', title);

    const text = await page.evaluate(() => document.body.innerText.substring(0, 200));
    console.log('   Content:', text);

  } catch (err) {
    console.error('ERROR:', err.message);
  } finally {
    if (browser) {
      console.log('\n7. Closing browser...');
      await browser.close();
    }
    if (anonymizedProxy) {
      console.log('8. Closing proxy...');
      await proxyChain.closeAnonymizedProxy(anonymizedProxy, true);
    }
  }
}

testWithProxyChain();
