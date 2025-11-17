const puppeteer = require('puppeteer-core');
const proxyChain = require('proxy-chain');

async function testRealWorldTasks() {
  let browser, anonymizedProxy;
  const results = {
    tasks: [],
    errors: [],
    warnings: []
  };

  try {
    console.log('=== Real-World CDP Task Testing ===\n');

    // Setup proxy
    console.log('Setting up proxy...');
    anonymizedProxy = await proxyChain.anonymizeProxy(process.env.HTTPS_PROXY);
    console.log('Proxy ready:', anonymizedProxy);

    browser = await puppeteer.launch({
      executablePath: '/usr/bin/google-chrome-stable',
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--ignore-certificate-errors',
        `--proxy-server=${anonymizedProxy}`
      ]
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });

    // Task 1: Extract news headlines from HackerNews
    console.log('\n--- Task 1: Extract HackerNews Headlines ---');
    try {
      await page.goto('https://news.ycombinator.com', { waitUntil: 'networkidle0', timeout: 30000 });
      const headlines = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('.titleline > a'))
          .slice(0, 5)
          .map(el => ({ title: el.textContent, url: el.href }));
      });
      console.log('Top 5 Headlines:');
      headlines.forEach((h, i) => console.log(`  ${i + 1}. ${h.title}`));
      results.tasks.push({ name: 'HackerNews Headlines', status: 'SUCCESS', count: headlines.length });
    } catch (err) {
      console.error('  Error:', err.message);
      results.errors.push({ task: 'HackerNews', error: err.message });
    }

    // Task 2: Fill search form on DuckDuckGo
    console.log('\n--- Task 2: Search on DuckDuckGo ---');
    try {
      await page.goto('https://duckduckgo.com', { waitUntil: 'networkidle0', timeout: 30000 });
      await page.type('input[name="q"]', 'Chrome DevTools Protocol automation');
      await Promise.all([
        page.click('button[type="submit"]'),
        page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 20000 })
      ]);
      const resultCount = await page.evaluate(() => {
        const results = document.querySelectorAll('[data-testid="result"]');
        return results.length;
      });
      console.log(`  Found ${resultCount} search results`);
      results.tasks.push({ name: 'DuckDuckGo Search', status: 'SUCCESS', resultCount });
    } catch (err) {
      console.error('  Error:', err.message);
      results.errors.push({ task: 'DuckDuckGo', error: err.message });
    }

    // Task 3: Take screenshot of GitHub trending
    console.log('\n--- Task 3: Screenshot GitHub Trending ---');
    try {
      await page.goto('https://github.com/trending', { waitUntil: 'networkidle0', timeout: 30000 });
      const screenshotPath = '/home/user/research/cdp-skill-guide/github-trending.png';
      await page.screenshot({ path: screenshotPath, fullPage: false });
      console.log('  Screenshot saved:', screenshotPath);
      results.tasks.push({ name: 'GitHub Screenshot', status: 'SUCCESS' });
    } catch (err) {
      console.error('  Error:', err.message);
      results.errors.push({ task: 'GitHub Screenshot', error: err.message });
    }

    // Task 4: Extract JSON API data
    console.log('\n--- Task 4: Fetch JSON API Data ---');
    try {
      await page.goto('https://jsonplaceholder.typicode.com/posts/1', { waitUntil: 'networkidle0' });
      const jsonData = await page.evaluate(() => {
        try {
          return JSON.parse(document.body.innerText);
        } catch {
          return document.body.innerText;
        }
      });
      console.log('  API Response:', jsonData);
      results.tasks.push({ name: 'JSON API', status: 'SUCCESS', dataType: typeof jsonData });
    } catch (err) {
      console.error('  Error:', err.message);
      results.errors.push({ task: 'JSON API', error: err.message });
    }

    // Task 5: Intercept and modify requests
    console.log('\n--- Task 5: Request Interception ---');
    try {
      await page.setRequestInterception(true);
      let blockedImages = 0;
      page.on('request', req => {
        if (req.resourceType() === 'image') {
          blockedImages++;
          req.abort();
        } else {
          req.continue();
        }
      });
      await page.goto('https://example.com', { waitUntil: 'networkidle0' });
      console.log(`  Blocked ${blockedImages} images`);
      await page.setRequestInterception(false);
      results.tasks.push({ name: 'Request Interception', status: 'SUCCESS', blocked: blockedImages });
    } catch (err) {
      console.error('  Error:', err.message);
      results.errors.push({ task: 'Request Interception', error: err.message });
    }

    // Task 6: Extract cookies
    console.log('\n--- Task 6: Cookie Management ---');
    try {
      await page.goto('https://httpbin.org/cookies/set/test_cookie/cdp_value', { waitUntil: 'networkidle0' });
      const cookies = await page.cookies();
      console.log('  Cookies:', cookies.map(c => `${c.name}=${c.value}`));
      results.tasks.push({ name: 'Cookie Management', status: 'SUCCESS', cookieCount: cookies.length });
    } catch (err) {
      console.error('  Error:', err.message);
      results.errors.push({ task: 'Cookie Management', error: err.message });
    }

    // Task 7: Evaluate complex JavaScript
    console.log('\n--- Task 7: Complex JS Evaluation ---');
    try {
      await page.goto('https://example.com', { waitUntil: 'networkidle0' });
      const result = await page.evaluate(() => {
        // Inject and execute complex logic
        const metrics = {
          loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
          domElements: document.getElementsByTagName('*').length,
          links: document.querySelectorAll('a').length,
          textLength: document.body.innerText.length,
          title: document.title
        };
        return metrics;
      });
      console.log('  Page Metrics:', result);
      results.tasks.push({ name: 'Complex JS', status: 'SUCCESS', metrics: result });
    } catch (err) {
      console.error('  Error:', err.message);
      results.errors.push({ task: 'Complex JS', error: err.message });
    }

    console.log('\n=== Summary ===');
    console.log(`Tasks completed: ${results.tasks.length}`);
    console.log(`Errors: ${results.errors.length}`);
    results.tasks.forEach(t => console.log(`  ✓ ${t.name}: ${t.status}`));
    results.errors.forEach(e => console.log(`  ✗ ${e.task}: ${e.error}`));

  } catch (err) {
    console.error('Critical error:', err.message);
  } finally {
    if (browser) await browser.close();
    if (anonymizedProxy) await proxyChain.closeAnonymizedProxy(anonymizedProxy, true);
  }

  return results;
}

testRealWorldTasks();
