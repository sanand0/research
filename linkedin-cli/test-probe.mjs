// @ts-check
import assert from 'node:assert/strict';
import test from 'node:test';
import { summarize } from './probe.mjs';

test('summaries preserve root count and continuation despite total zero, without private values', () => {
  const summary = summarize({ status: 200, contentType: 'application/json', body: JSON.stringify({
    data: { data: { feedDashProfileUpdatesByMemberShareFeed: { '*elements': ['urn:li:activity:123'], paging: { start: 0, count: 5, total: 0 }, metadata: { paginationToken: 'PRIVATE_CURSOR' } } } },
    included: [{ $type: 'Update', entityUrn: 'urn:li:activity:123', text: 'PRIVATE_POST_TEXT', csrf: 'PRIVATE_TOKEN' }],
  }) });
  assert.equal(summary.collections[0].references, 1);
  assert.equal(summary.collections[0].paging.total, 0);
  assert.equal(summary.collections[0].hasPaginationToken, true);
  assert.doesNotMatch(JSON.stringify(summary), /PRIVATE_|urn:li:activity:123/);
});

test('SDUI summaries count unique activity IDs without exporting content or IDs', () => {
  const summary = summarize({ status: 200, contentType: 'application/octet-stream', body: '0:["PRIVATE_POST_TEXT","urn:li:activity:123","urn:li:activity:123","urn:li:activity:456"]\n' });
  assert.equal(summary.activityIdCount, 2);
  assert.doesNotMatch(JSON.stringify(summary), /PRIVATE_|urn:li:activity:/);
});
