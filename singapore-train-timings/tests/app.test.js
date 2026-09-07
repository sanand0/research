import { readFile } from 'node:fs/promises';
import test from 'node:test';
import assert from 'node:assert/strict';

const load = async path => JSON.parse(await readFile(path, 'utf8'));

test('latest line metrics are complete and plausible', async () => {
  const data = await load('data/app-data.json');
  const lines = ['MRT', 'NSL', 'EWL', 'NEL', 'CCL', 'DTL', 'TEL'];
  assert.deepEqual(Object.keys(data.latest.punctuality), lines);
  for (const line of lines) {
    assert.equal(data.latest.punctuality[line].length, 3);
    assert.equal(data.latest.delivery[line].length, 3);
    assert.equal(data.mkbf[line].length, 12);
    assert.ok(data.latest.punctuality[line].every(value => value > 90 && value <= 100));
  }
});

test('headline and translated counts match July network data', async () => {
  const data = await load('data/app-data.json');
  const july = data.latest.punctuality.MRT.at(-1);
  assert.equal(july, 99.29);
  assert.equal(Math.round((100 - july) * 10), 7);
  assert.equal(data.monthlySevereDelays.MRT.at(-1), 0);
});

test('GTFS descriptor is explicitly excluded from the analysis', async () => {
  const data = await load('data/app-data.json');
  const gtfs = data.sources.find(source => source.id === 'gtfs-descriptor');
  assert.match(gtfs.limitation, /expired/i);
});

test('the document exposes accessible interactive controls', async () => {
  const html = await readFile('index.html', 'utf8');
  const css = await readFile('style.css', 'utf8');
  assert.match(html, /role="tablist"/);
  assert.match(html, /aria-live="polite"/);
  assert.match(html, /<dialog id="detail-dialog">/);
  assert.match(css, /prefers-reduced-motion/);
});
