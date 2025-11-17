const puppeteer = require('puppeteer-core');

async function testPuppeteerWithProxy() {
  let browser;
  try {
    console.log('1. Parsing proxy URL...');
    const proxyUrl = new URL(process.env.HTTPS_PROXY);
    const proxyServer = `${proxyUrl.hostname}:${proxyUrl.port}`;
    console.log('   Proxy server:', proxyServer);
    console.log('   Username:', proxyUrl.username.substring(0, 30) + '...');

    console.log('2. Launching browser with proxy...');
    browser = await puppeteer.launch({
      executablePath: '/usr/bin/google-chrome-stable',
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        `--proxy-server=${proxyServer}`
      ]
    });

    console.log('3. Creating new page...');
    const page = await browser.newPage();

    console.log('4. Setting up proxy authentication...');
    await page.authenticate({
      username: proxyUrl.username,
      password: proxyUrl.password
    });

    console.log('5. Navigating to httpbin.org...');
    const response = await page.goto('https://httpbin.org/get', {
      waitUntil: 'networkidle0',
      timeout: 30000
    });

    console.log('   Status:', response.status());
    console.log('   URL:', response.url());

    console.log('6. Getting page content...');
    const content = await page.evaluate(() => document.body.innerText);
    console.log('\nPage content:\n', content);

    console.log('\n=== SUCCESS! Proxy authentication works! ===');

  } catch (err) {
    console.error('ERROR:', err.message);
    if (err.stack) console.error('Stack:', err.stack.split('\n').slice(0, 5).join('\n'));
  } finally {
    if (browser) {
      console.log('\n7. Closing browser...');
      await browser.close();
    }
  }
}

testPuppeteerWithProxy();
