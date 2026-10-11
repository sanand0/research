// @ts-check
const data = JSON.parse(document.getElementById('data').textContent);
const { steps, chapters, puzzles, eggs, council } = data;
const $ = (id) => document.getElementById(id);

const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

// PEP and gh- references become links. Applied to already-escaped text.
const linkify = (html) => html
  .replace(/\bPEP (\d{3,4})\b/g, (m, n) => `<a href="https://peps.python.org/pep-${n.padStart(4, '0')}/" target="_blank" rel="noopener">${m}</a>`)
  .replace(/\bgh-(\d{4,6})\b/g, (m, n) => `<a href="https://github.com/python/cpython/issues/${n}" target="_blank" rel="noopener">${m}</a>`)
  .replace(/\b(docs\.python\.org\/3\.15\/whatsnew\/3\.15\.html)\b/g, '<a href="https://$1" target="_blank" rel="noopener">$1</a>');

// The player's thinking: a tiny Markdown subset (paragraphs, **bold**, *italic*, `code`).
const md = (text) => text.split(/\n\n+/).map((para) => `<p>${linkify(esc(para))
  .replace(/`([^`]+)`/g, '<code>$1</code>')
  .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
  .replace(/\*([^*]+)\*/g, '<i>$1</i>')}</p>`).join('');

const termLines = (lines) => lines.map(({ t, s }) => `<div class="l-${s}">${linkify(esc(t)) || '&nbsp;'}</div>`).join('');

const highlight = (code, lang) => window.hljs
  ? window.hljs.highlight(code, { language: lang === 'bash' ? 'bash' : 'python' }).value
  : esc(code);

// Where each curiosity was first found, so the chips can jump there.
const eggStep = {};
steps.forEach((step, i) => step.newEggs.forEach((egg) => (eggStep[egg] ??= i)));

// Each room's examinable nouns, captured on the first visit.
const roomDetails = {};
steps.forEach((step) => step.details && (roomDetails[step.detailsRoom] ??= step.details));

const chapterOf = (i) => chapters.findLastIndex((c) => c.step <= i);

function editorHead(key) {
  const p = puzzles[key];
  return `<div class="editor-bar"><i class="bi bi-code-square"></i><span class="ttl">${esc(p.title)}</span>
    <span class="cite">${linkify(esc(p.citation))}</span><span class="pts">+${p.points}${p.reward ? ` · ${p.rewardSigil ? '<i class="bi bi-gem" title="sigil"></i> ' : ''}${esc(p.reward)}` : ''}</span></div>`;
}

function docsRow(key) {
  const p = puzzles[key];
  const links = p.docs.map(([label, path]) => `<a href="https://docs.python.org/3.15/${path}" target="_blank" rel="noopener"><i class="bi bi-book"></i> ${esc(label)}</a>`);
  if (p.anchor) links.push(`<a href="https://docs.python.org/3.15/whatsnew/3.15.html#${p.anchor}" target="_blank" rel="noopener"><i class="bi bi-newspaper"></i> What's New</a>`);
  return links.length ? `<div class="docs">${links.join('')}</div>` : '';
}

function renderOpen(key) {
  const p = puzzles[key];
  const hints = p.hints.map((h) => `<li>${linkify(esc(h))}</li>`).join('');
  return `<div class="editor">${editorHead(key)}
    <div class="briefing">${linkify(esc(p.briefing))}</div>
    <pre><code class="hljs">${highlight(p.starter, p.lang)}</code></pre>
    <details><summary>Hints the game sells for 1 point each (this run bought none). Peeking here is free.</summary><ol>${hints}</ol></details>
    ${docsRow(key)}</div>`;
}

function renderAttempt(step) {
  const { verdict, key } = step;
  const ok = verdict.solved;
  return `<div class="editor">${editorHead(key)}
    <pre><code class="hljs">${highlight(step.code, step.lang)}</code></pre>
    <div class="verdict ${ok ? 'ok' : 'no'}"><div class="head"><i class="bi ${ok ? 'bi-check-circle-fill' : 'bi-x-circle-fill'}"></i>${ok ? 'Solved' : 'Not yet'} <span class="l-dim">· ctrl+r</span></div>${linkify(esc(verdict.message))}${verdict.output ? `<div class="out">printed: ${esc(verdict.output.trim())}</div>` : ''}${step.paid.length ? `<div style="margin-top:.5rem">${termLines(step.paid)}</div>` : ''}</div></div>`;
}

function renderStep(step, i, current) {
  const parts = [];
  if (step.think) parts.push(`<div class="think"><i class="bi bi-chat-square-dots" aria-hidden="true"></i>${md(step.think)}</div>`);
  if (step.kind === 'cmd') {
    const out = step.out.length ? termLines(step.out) : '';
    parts.push(`<div class="term"><span class="prompt">&gt; </span><span class="typed">${esc(step.cmd)}</span>${out ? `<div style="margin-top:.35rem">${out}</div>` : ''}</div>`);
    if (step.opens) parts.push(renderOpen(step.opens));
  }
  if (step.kind === 'puzzle') parts.push(renderAttempt(step));
  for (const egg of step.newEggs) {
    const person = council.includes(egg);
    parts.push(`<div class="egg-flash"><i class="bi ${person ? 'bi-person-check-fill' : 'bi-stars'}"></i>${person ? 'Person' : 'Curiosity'} found: ${esc(egg)} · ${esc(eggs[egg])}</div>`);
  }
  const cls = i === current ? 'current' : 'past';
  return `<article class="step ${cls}" id="s${i}" data-i="${i}">${parts.join('')}</article>`;
}

// ---------- side panes ----------
let lastState = null;

function renderStats(st) {
  const rows = [
    ['Score', `${st.score} / ${st.possible}`, st.score / st.possible],
    ['Puzzles', `${st.solved} / ${st.puzzles}`, st.solved / st.puzzles],
    ['Sigils', `${st.sigils} / ${st.sigilTotal}`, st.sigils / st.sigilTotal],
    ['Rooms', `${st.rooms} / ${st.roomTotal}`, st.rooms / st.roomTotal],
    ...(st.people ? [['People', `${st.people} / ${council.length}`, st.people / council.length]] : []),
    ['Moves', `${st.moves}`, null],
  ];
  $('stats').innerHTML = rows.map(([k, v, f]) => {
    const prev = lastState && $('stats').querySelector(`[data-k="${k}"]`)?.textContent;
    const bump = prev && prev !== v ? ' class="bump"' : '';
    return `<dt>${k}</dt><dd data-k="${k}"${bump}>${v}</dd>${f === null ? '' : `<dt></dt><dd style="display:block"><meter min="0" max="1" value="${f}" aria-label="${k}"></meter></dd>`}`;
  }).join('') + (st.finished ? '<dt></dt><dd class="l-good"><b>Finished</b></dd>' : '')
    + (st.people ? '<dt></dt><dd class="l-dim" style="font-size:.7rem" title="This line only appears once you have named one person">↑ appeared after naming someone</dd>' : '');
}

function renderMap(st) {
  $('map').innerHTML = st.map.map(({ t, s, sp }) => {
    if (s === 'title') return `<span class="l-title">${esc(t)}</span>`;
    // Apply progress spans (sorted, non-overlapping), then mark the you-are-here cell.
    let html = '', at = 0;
    for (const [a, b, style] of sp) { html += esc(t.slice(at, a)) + `<span class="m-${style}">${esc(t.slice(a, b))}</span>`; at = b; }
    html += esc(t.slice(at));
    return html.replace(/&gt;(\S+?)&lt;/, '<span class="here">&gt;$1&lt;</span>');
  }).join('\n');
}

function renderCarrying(st) {
  const before = new Set(lastState?.carrying.map((c) => c.key) ?? []);
  $('carrying').innerHTML = st.carrying.length
    ? st.carrying.map((c) => `<li class="${lastState && !before.has(c.key) ? 'new' : ''}">${c.sigil ? '<i class="bi bi-gem" title="sigil"></i>' : '<i class="bi bi-dot"></i>'} ${esc(c.name)}</li>`).join('')
    : '<li class="l-dim">nothing yet</li>';
}

function renderEggs(st, current) {
  const found = new Set(st.curiosities);
  $('egg-count').textContent = `${found.size} / ${Object.keys(eggs).length}`;
  $('eggs').innerHTML = Object.keys(eggs).map((egg) => {
    const person = council.includes(egg);
    const has = found.has(egg);
    // Unfound ones stay hidden, as the game hides them, but show their shape.
    const label = has ? egg : '?'.repeat(egg.length);
    const title = has ? `${eggs[egg]} · found at step ${eggStep[egg] + 1}. Click to jump there.` : 'Not found yet';
    return `<button class="egg ${has ? 'found' : ''} ${person ? 'person' : ''}" ${has ? `data-go="${eggStep[egg]}"` : 'disabled'} title="${esc(title)}"><i class="bi ${person ? 'bi-person' : 'bi-stars'}"></i>${esc(label)}</button>`;
  }).join('');
}

let examined = null;
function renderExamine(st) {
  const nouns = roomDetails[st.room] ?? {};
  $('exam-room').textContent = data.rooms[st.room].label;
  const names = Object.keys(nouns);
  if (!names.includes(examined)) examined = null;
  $('examine').innerHTML = `<p class="hint">Try it yourself: <code>examine &lt;noun&gt;</code></p><div class="nouns">${names.map((n) =>
    `<button aria-pressed="${n === examined}" data-noun="${esc(n)}">${esc(n)}</button>`).join('')}</div>${examined ? `<div class="said">${termLines(nouns[examined])}</div>` : ''}`;
}

// ---------- navigation ----------
let current = 0;

function go(i, { jump = false } = {}) {
  current = Math.max(0, Math.min(steps.length - 1, i));
  const step = steps[current];
  const ci = chapterOf(current);
  const chapter = chapters[ci];
  const end = chapters[ci + 1]?.step ?? steps.length;
  const html = [`<header class="chapter-head"><div class="kicker">Chapter ${ci + 1} of ${chapters.length} · ${esc(chapter.subtitle)}</div><h2>${esc(chapter.title)}</h2></header>`];
  for (let j = chapter.step; j <= current && j < end; j++) html.push(renderStep(steps[j], j, current));
  if (current === steps.length - 1) html.push('<div class="think" style="text-align:center"><p><b>Game over: 375 / 375.</b> Press <kbd>Home</kbd> to replay, or pick any chapter above.</p></div>');
  $('feed').innerHTML = html.join('');

  const st = step.state;
  renderStats(st); renderMap(st); renderCarrying(st); renderEggs(st, current); renderExamine(st);
  lastState = st;
  $('room-name').textContent = st.roomName;
  $('chapter-pick').value = String(ci);
  $('scrub').value = String(current);
  $('pos').textContent = `step ${current + 1} / ${steps.length}`;
  $('prev').disabled = current === 0;
  $('next').disabled = current === steps.length - 1;
  history.replaceState(null, '', `#step=${current + 1}`);
  // Stepping glides along; a jump (load, chapter, scrubber, egg) lands with the step centered.
  const smooth = !jump && !matchMedia('(prefers-reduced-motion: reduce)').matches;
  $(`s${current}`)?.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', block: jump ? 'center' : 'nearest' });
}

const goChapter = (delta) => {
  const ci = Math.max(0, Math.min(chapters.length - 1, chapterOf(current) + delta));
  go(chapters[ci].step, { jump: true });
};

let timer = null;
function togglePlay(force) {
  const on = force ?? !timer;
  clearInterval(timer); timer = null;
  if (on) timer = setInterval(() => (current < steps.length - 1 ? go(current + 1) : togglePlay(false)), 3200);
  $('play').innerHTML = on ? '<i class="bi bi-pause-fill"></i><span class="lbl">Pause</span>' : '<i class="bi bi-play-fill"></i><span class="lbl">Auto</span>';
}

// ---------- theme ----------
function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  /** @type {HTMLLinkElement} */ ($('hl-dark')).disabled = theme !== 'dark';
  /** @type {HTMLLinkElement} */ ($('hl-light')).disabled = theme === 'dark';
  $('theme-btn').innerHTML = `<i class="bi ${theme === 'dark' ? 'bi-sun' : 'bi-moon-stars'}"></i>`;
  try { localStorage.setItem('whatsnewt-theme', theme); } catch { /* storage may be blocked */ }
}
let saved = null;
try { saved = localStorage.getItem('whatsnewt-theme'); } catch { /* storage may be blocked */ }
setTheme(saved ?? (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'));

// ---------- wiring ----------
$('chapter-pick').innerHTML = chapters.map((c, i) => `<option value="${i}">${i + 1}. ${esc(c.title)}</option>`).join('');
$('chapter-pick').addEventListener('change', (e) => { go(chapters[+/** @type {HTMLSelectElement} */ (e.target).value].step, { jump: true }); });
$('scrub').max = String(steps.length - 1);
$('scrub').addEventListener('input', (e) => go(+/** @type {HTMLInputElement} */ (e.target).value, { jump: true }));
$('prev').addEventListener('click', () => go(current - 1));
$('next').addEventListener('click', () => go(current + 1));
$('play').addEventListener('click', () => togglePlay());
$('theme-btn').addEventListener('click', () => setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'));
$('help-btn').addEventListener('click', () => /** @type {HTMLDialogElement} */ ($('help')).showModal());
$('eggs').addEventListener('click', (e) => {
  const at = /** @type {HTMLElement} */ (e.target).closest('[data-go]');
  if (at) go(+at.dataset.go, { jump: true });
});
$('examine').addEventListener('click', (e) => {
  const b = /** @type {HTMLElement} */ (e.target).closest('[data-noun]');
  if (!b) return;
  examined = examined === b.dataset.noun ? null : b.dataset.noun;
  renderExamine(steps[current].state);
  $('examine').querySelector(`[data-noun="${CSS.escape(examined ?? '')}"]`)?.focus();
});
$('feed').addEventListener('click', (e) => {
  const art = /** @type {HTMLElement} */ (e.target).closest('.step.past');
  if (art && !(/** @type {HTMLElement} */ (e.target).closest('a, summary, details'))) go(+art.dataset.i);
});

document.addEventListener('keydown', (e) => {
  if (e.target instanceof HTMLInputElement || e.target instanceof HTMLSelectElement || e.metaKey || e.ctrlKey || e.altKey) return;
  if ($('help').hasAttribute('open')) return;
  const actions = {
    ArrowRight: () => go(current + 1), ' ': () => go(current + 1), ArrowLeft: () => go(current - 1),
    ']': () => goChapter(1), '[': () => goChapter(-1), Home: () => go(0, { jump: true }), End: () => go(steps.length - 1, { jump: true }),
    p: () => togglePlay(), t: () => $('theme-btn').click(), '?': () => $('help-btn').click(),
  };
  const act = actions[e.key];
  if (!act || (e.key === ' ' && e.target instanceof HTMLButtonElement)) return;
  e.preventDefault();
  if (e.key !== 'p') togglePlay(false);
  act();
});

const fromHash = () => +(new URLSearchParams(location.hash.slice(1)).get('step') ?? 1) - 1;
window.addEventListener('hashchange', () => go(fromHash(), { jump: true }));
go(fromHash(), { jump: true });
