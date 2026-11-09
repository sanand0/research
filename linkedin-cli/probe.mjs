#!/usr/bin/env node
// @ts-check
import { parseArgs } from 'node:util';
import { connect, evaluate } from './cdp.mjs';

const queries = {
  search: 'voyagerSearchDashClusters.e438ab99259203e9c1cd3f358e217282',
  posts: 'voyagerFeedDashProfileUpdates.be2623b61657a92a693eb8d9c67aeec0',
  comments: 'voyagerFeedDashProfileUpdates.8f05a4e5ad12d9cb2b56eaa22afbcab9',
  reactions: 'voyagerFeedDashProfileUpdates.3a42619bc23360ce8c29e737277e2ea9',
};
const surfaces = ['me', 'profile', 'people', 'content', 'posts', 'comments', 'reactions', 'legacy-feed', 'home'];
const schema = {
  description: 'Read-only research probe. Outputs structural metadata, never credentials or records.',
  usage: 'node probe.mjs --surface people --limit 5 --start 0',
  options: { surface: surfaces, cdp: 'http://localhost:9222', limit: '1..10', start: '0..1000', describe: 'Print schema without contacting browser' },
  notes: ['Uses own profile for profile/activity tests.', 'home creates and closes one background tab; replays one captured feed-pagination POST.', 'Other surfaces use GETs in the existing LinkedIn tab.', 'Query IDs are observations from 2026-11-08, not permanent contracts.'],
};

/** Summarize shape only; HTTP 200 does not imply a validated semantic parser. */
export function summarize(result) {
  let payload;
  try { payload = JSON.parse(result.body); } catch { /* SDUI is a stream, not one JSON object. */ }
  const data = payload?.data?.data ?? payload?.data;
  const collections = data && typeof data === 'object'
    ? Object.entries(data).filter(([, value]) => value && typeof value === 'object' && ('paging' in value || '*elements' in value))
    : [];
  return {
    status: result.status, contentType: result.contentType, characters: result.body.length,
    keys: payload ? Object.keys(payload) : [], includedCount: payload?.included?.length,
    types: [...new Set((payload?.included ?? []).map(entity => entity.$type))],
    collections: collections.map(([name, value]) => ({ name, references: value['*elements']?.length, paging: value.paging && { start: value.paging.start, count: value.paging.count, total: value.paging.total }, hasPaginationToken: Boolean(value.metadata?.paginationToken) })),
    ...(payload ? {} : { activityIdCount: new Set(result.body.match(/urn:li:activity:\d+/g) ?? []).size }),
  };
}

async function main() {
  const { values } = parseArgs({ options: {
    surface: { type: 'string', default: 'me' }, cdp: { type: 'string', default: 'http://localhost:9222' },
    limit: { type: 'string', default: '5' }, start: { type: 'string', default: '0' },
    describe: { type: 'boolean' }, help: { type: 'boolean' },
  } });
  if (values.describe || values.help) return console.log(JSON.stringify(schema, null, 2));
  const limit = Number(values.limit), start = Number(values.start);
  if (!surfaces.includes(values.surface) || !Number.isInteger(limit) || limit < 1 || limit > 10 || !Number.isInteger(start) || start < 0 || start > 1000) throw new Error('Invalid input. Run node probe.mjs --describe');
  const endpoint = new URL(values.cdp);
  if (!['localhost', '127.0.0.1', '[::1]'].includes(endpoint.hostname) || endpoint.protocol !== 'http:') throw new Error('CDP must be a local HTTP endpoint');
  const tabs = await (await fetch(new URL('/json/list', endpoint))).json();
  const tab = tabs.find(item => item.type === 'page' && item.url.startsWith('https://www.linkedin.com/'));
  if (!tab) throw new Error('Open and sign into LinkedIn in the CDP browser first');
  const page = await connect(tab.webSocketDebuggerUrl);
  try {
    if (values.surface === 'home') return await captureHome(endpoint);
    const api = path => evaluate(page, `(async () => {
      const csrf = document.cookie.match(/(?:^|; )JSESSIONID=([^;]+)/)?.[1]?.replace(/^"|"$/g, '');
      if (!csrf) throw new Error('No JSESSIONID in LinkedIn page');
      const response = await fetch(${JSON.stringify(path)}, { credentials: 'include', headers: {
        'csrf-token': csrf, 'x-restli-protocol-version': '2.0.0', accept: 'application/vnd.linkedin.normalized+json+2.1',
      }});
      return { status: response.status, contentType: response.headers.get('content-type'), body: await response.text() };
    })()`);
    let path = '/voyager/api/me';
    if (['profile', 'posts', 'comments', 'reactions'].includes(values.surface)) {
      const me = await api(path);
      if (me.status !== 200) throw new Error(`Identity read failed: HTTP ${me.status}`);
      const self = JSON.parse(me.body).included?.find(entity => entity.publicIdentifier);
      if (!self) throw new Error('Identity schema changed');
      if (values.surface === 'profile') path = '/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity=' + encodeURIComponent(self.publicIdentifier) + '&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfile-76';
      else {
        const urn = 'urn:li:fsd_profile:' + self.entityUrn.split(':').at(-1);
        path = `/voyager/api/graphql?includeWebMetadata=true&variables=(count:${limit},start:${start},profileUrn:${encodeURIComponent(urn)})&queryId=${queries[values.surface]}`;
      }
    } else if (['people', 'content'].includes(values.surface)) {
      const type = values.surface === 'people' ? 'PEOPLE' : 'CONTENT';
      path = `/voyager/api/graphql?variables=(start:${start},count:${limit},origin:GLOBAL_SEARCH_HEADER,query:(keywords:artificial%20intelligence,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(${type}))),includeFiltersInResponse:false))&queryId=${queries.search}`;
    } else if (values.surface === 'legacy-feed') path = `/voyager/api/feed/updatesV2?count=${limit}&start=${start}&q=feedByType&feedType=HOMEPAGE`;
    console.error(`Reading ${values.surface}; limit=${limit}, start=${start}`);
    const result = await api(path);
    console.log(JSON.stringify({ schema_version: 1, surface: values.surface, observed_at: new Date().toISOString(), ...summarize(result) }, null, 2));
    if (result.status !== 200) process.exitCode = 1;
  } finally { page.close(); }
}

async function captureHome(endpoint) {
  const version = await (await fetch(new URL('/json/version', endpoint))).json();
  const browser = await connect(version.webSocketDebuggerUrl);
  let target, page;
  try {
    console.error('Creating a background feed tab; observing one pagination request');
    target = await browser.call('Target.createTarget', { url: 'about:blank', background: true });
    const tabs = await (await fetch(new URL('/json/list', endpoint))).json();
    page = await connect(tabs.find(tab => tab.id === target.targetId).webSocketDebuggerUrl);
    let request, requestId;
    const observed = new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('No feed-pagination response within 30 seconds')), 30000);
      page.on(async event => {
        if (event.method === 'Network.requestWillBeSent' && !request) {
          const url = new URL(event.params.request.url);
          if (url.pathname === '/flagship-web/rsc-action/actions/pagination' && url.searchParams.get('sduiid') === 'com.linkedin.sdui.pagers.feed.mainFeed') {
            request = event.params.request; requestId = event.params.requestId;
          }
        }
        if (event.method === 'Network.loadingFinished' && event.params.requestId === requestId) {
          try { const response = await page.call('Network.getResponseBody', { requestId }); clearTimeout(timeout); resolve(response); }
          catch (error) { clearTimeout(timeout); reject(error); }
        }
      });
    });
    // Handle a timeout even if navigation/scrolling is still in progress.
    observed.catch(() => {});
    await page.call('Network.enable', { maxResourceBufferSize: 15000000, maxTotalBufferSize: 30000000 });
    // Simulates focus for layout/scroll processing without activating the tab/window.
    await page.call('Emulation.setFocusEmulationEnabled', { enabled: true });
    await page.call('Page.navigate', { url: 'https://www.linkedin.com/feed/foryou/' });
    const scroller = setInterval(() => page.call('Input.dispatchMouseEvent', { type: 'mouseWheel', x: 700, y: 650, deltaY: 2000, deltaX: 0 }).catch(() => {}), 1000);
    let captured;
    try { captured = await observed; } finally { clearInterval(scroller); }
    const body = captured.base64Encoded ? Buffer.from(captured.body, 'base64').toString() : captured.body;
    const headers = Object.fromEntries(Object.entries(request.headers).filter(([name]) => /^(accept$|content-type$|csrf-token$|x-li-|x-restli-)/i.test(name)));
    console.error('Replaying the captured read-only feed-pagination POST once');
    const replay = await evaluate(page, `(async () => {
      const response = await fetch(${JSON.stringify(request.url)}, { method: 'POST', credentials: 'include', headers: ${JSON.stringify(headers)}, body: ${JSON.stringify(request.postData)} });
      return { status: response.status, contentType: response.headers.get('content-type'), body: await response.text() };
    })()`);
    const ids = text => [...new Set(text.match(/urn:li:activity:\d+/g) ?? [])].sort();
    console.log(JSON.stringify({ schema_version: 1, surface: 'home', observed_at: new Date().toISOString(), captured: { characters: body.length, activityIdCount: ids(body).length }, replay: summarize(replay), sameActivityIds: JSON.stringify(ids(body)) === JSON.stringify(ids(replay.body)) }, null, 2));
    if (replay.status !== 200) process.exitCode = 1;
  } finally {
    if (target) await browser.call('Target.closeTarget', { targetId: target.targetId });
    page?.close(); browser.close();
  }
}

if (import.meta.url === new URL(process.argv[1], 'file:').href) main().catch(error => {
  console.error(JSON.stringify({ ok: false, error: { code: 'PROBE_FAILED', message: error.message } })); process.exitCode = 1;
});
