#!/usr/bin/env node
// @ts-check
import { connect, evaluate } from './cdp.mjs';

/** Test a browser-independent HTTP request; cookie values exist only in memory. */
async function main() {
  const tabs = await (await fetch('http://localhost:9222/json/list')).json();
  const tab = tabs.find(item => item.type === 'page' && item.url.startsWith('https://www.linkedin.com/'));
  if (!tab) throw new Error('No LinkedIn CDP tab');
  const page = await connect(tab.webSocketDebuggerUrl);
  try {
    const { cookies } = await page.call('Network.getCookies', { urls: ['https://www.linkedin.com/'] });
    const selected = cookies.filter(cookie => ['li_at', 'JSESSIONID'].includes(cookie.name));
    if (!selected.some(cookie => cookie.name === 'li_at') || !selected.some(cookie => cookie.name === 'JSESSIONID')) throw new Error('Missing session cookies');
    const userAgent = await evaluate(page, 'navigator.userAgent');
    const csrf = selected.find(cookie => cookie.name === 'JSESSIONID').value.replace(/^"|"$/g, '');
    console.error('Testing direct HTTP identity read; session cookies stay in memory');
    const response = await fetch('https://www.linkedin.com/voyager/api/me', {
      redirect: 'manual', signal: AbortSignal.timeout(20000), headers: {
        cookie: selected.map(cookie => `${cookie.name}=${cookie.value}`).join('; '),
        'csrf-token': csrf, 'x-restli-protocol-version': '2.0.0',
        accept: 'application/vnd.linkedin.normalized+json+2.1', 'user-agent': userAgent,
      },
    });
    const text = await response.text();
    let body;
    try { body = JSON.parse(text); } catch { /* Only metadata is exported. */ }
    console.log(JSON.stringify({ observed_at: new Date().toISOString(), transport: 'Node fetch outside browser; two cookies in memory', status: response.status, contentType: response.headers.get('content-type'), keys: body ? Object.keys(body) : [], types: [...new Set((body?.included ?? []).map(entity => entity.$type))] }, null, 2));
    if (response.status !== 200) process.exitCode = 1;
  } finally { page.close(); }
}
main().catch(error => { console.error(JSON.stringify({ ok: false, error: { code: 'HTTP_PROBE_FAILED', message: error.message } })); process.exitCode = 1; });
