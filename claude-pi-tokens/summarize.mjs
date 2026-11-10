// @ts-check
// Recompute the benchmark numbers from sanitized evidence.
// With --from-raw, extract sanitized evidence from local (untracked) CLI logs first.
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const groups = {
  'Claude cache on': ['claude-cache-on', 'claude-cache-on-2', 'claude-cache-on-3'],
  'Claude cache off': ['claude-cache-off', 'claude-cache-off-2', 'claude-cache-off-3'],
  'Pi subscription': ['pi-sdk', 'pi-sdk-budgeted', 'pi-sdk-budgeted-3'],
};
const names = Object.values(groups).flat();
const evidencePath = path.join(root, 'usage-evidence.json');
const read = (name) => fs.readFileSync(path.join(root, name), 'utf8');
const checksum = (name) => createHash('sha256').update(fs.readFileSync(path.join(root, name))).digest('hex');
const sum = (rows, key) => rows.reduce((value, row) => value + row[key], 0);
const round = (value, digits = 9) => Number(value.toFixed(digits));

/** Read model usage only. Do not copy transcripts, user names, request ids or absolute paths. */
function extract(name, variant, trial) {
  const events = read(`${name}/events.jsonl`).trim().split('\n').map((line) => JSON.parse(line));
  const file = `${name}/index.html`;
  const sha256 = checksum(file);
  const htmlBytes = fs.statSync(path.join(root, file)).size;
  const quota = events.find((item) => item.type === 'rate_limit_event')?.rate_limit_info?.unifiedWindows;
  if (variant === 'Pi subscription') {
    const messages = events.filter((item) => item.type === 'message_end' && item.message?.role === 'assistant').map((item) => item.message);
    if (!messages.length) throw new Error(`${name}: no assistant messages`);
    return {
      name, variant, trial, status: messages.at(-1).stopReason, turns: messages.length,
      costUsd: round(messages.reduce((value, msg) => value + msg.usage.cost.total, 0)),
      input: messages.reduce((value, msg) => value + msg.usage.input, 0),
      cacheRead: messages.reduce((value, msg) => value + msg.usage.cacheRead, 0),
      cacheWrite: messages.reduce((value, msg) => value + msg.usage.cacheWrite, 0),
      output: messages.reduce((value, msg) => value + msg.usage.output, 0),
      htmlBytes, sha256, quotaAtStart: null,
    };
  }
  const result = events.find((item) => item.type === 'result');
  if (!result) throw new Error(`${name}: no final result`);
  const usage = result.usage;
  return {
    name, variant, trial, status: result.subtype, turns: result.num_turns,
    costUsd: round(result.total_cost_usd), input: usage.input_tokens,
    cacheRead: usage.cache_read_input_tokens, cacheWrite: usage.cache_creation_input_tokens,
    output: usage.output_tokens, htmlBytes, sha256,
    quotaAtStart: quota ? { fiveHour: quota.five_hour?.utilization ?? null, sevenDay: quota.seven_day?.utilization ?? null } : null,
  };
}

if (process.argv.includes('--from-raw')) {
  const rows = Object.entries(groups).flatMap(([variant, runs]) => runs.map((name, index) => extract(name, variant, index + 1)));
  fs.writeFileSync(evidencePath, `${JSON.stringify(rows, null, 2)}\n`);
}

const rows = JSON.parse(fs.readFileSync(evidencePath, 'utf8'));
if (rows.length !== 9 || rows.some((row) => !names.includes(row.name))) throw new Error('Expected exactly 9 benchmark runs');
for (const row of rows) {
  const file = `${row.name}/index.html`;
  if (row.sha256 !== checksum(file) || row.htmlBytes !== fs.statSync(path.join(root, file)).size) throw new Error(`HTML does not match evidence: ${file}`);
  if (!(row.status === 'success' || row.status === 'stop')) throw new Error(`Unsuccessful run: ${row.name}`);
}

const metrics = rows.map(({ sha256, ...row }) => ({
  ...row, total: row.input + row.cacheRead + row.cacheWrite + row.output,
  inputContext: row.input + row.cacheRead + row.cacheWrite,
}));
fs.writeFileSync(path.join(root, 'results.json'), `${JSON.stringify(metrics, null, 2)}\n`);
const columns = ['variant', 'name', 'trial', 'status', 'turns', 'costUsd', 'input', 'cacheRead', 'cacheWrite', 'output', 'total', 'inputContext', 'htmlBytes'];
fs.writeFileSync(path.join(root, 'results.tsv'), [columns.join('\t'), ...metrics.map((row) => columns.map((key) => row[key]).join('\t'))].join('\n') + '\n');
for (const variant of Object.keys(groups)) {
  const subset = metrics.filter((row) => row.variant === variant);
  const mean = (key) => sum(subset, key) / subset.length;
  console.log(`${variant}: ${subset.length} successes; mean cost $${mean('costUsd').toFixed(6)}, context ${Math.round(mean('inputContext'))}, output ${Math.round(mean('output'))}, total ${Math.round(mean('total'))} tokens; mean turns ${mean('turns').toFixed(2)}`);
}
