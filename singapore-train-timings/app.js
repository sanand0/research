// @ts-check

const DATA_URL = 'data/app-data.json';
const lineNames = {
  MRT: 'MRT network', NSL: 'North–South Line', EWL: 'East–West Line',
  NEL: 'North East Line', CCL: 'Circle Line', DTL: 'Downtown Line', TEL: 'Thomson–East Coast Line'
};

const advice = {
  MRT: 'Treat the published score as network context, not a personal arrival guarantee. Check service alerts before a time-critical trip.',
  NSL: 'July was exceptionally steady. Still add walking and interchange time—the metric only clocks the train at its terminal.',
  EWL: 'This was July’s strongest mature-line punctuality score. A direct EWL journey is structurally simpler than one with a tight transfer.',
  NEL: 'Punctuality improved sharply from May to July, but the largest reported passenger-impact incident in this dataset occurred here.',
  CCL: 'July improved, yet CCL had the lowest punctuality of the mature lines. Give a tight interchange a few extra minutes.',
  DTL: 'Punctuality softened in July even as long-run MKBF remained high. One metric never tells the whole commute.',
  TEL: 'July punctuality was strong, but LTA treats this newer, still-expanding line separately; its long-run mileage metric is not fairly comparable yet.'
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const formatKm = (value) => `${(value / 1_000_000).toFixed(2)}m km`;
const hashState = () => new URLSearchParams(location.hash.split('?')[1] ?? '');

const dialog = /** @type {HTMLDialogElement} */ ($('#detail-dialog'));
const dialogContent = $('#dialog-content');
const tooltip = $('#tooltip');

const openDialog = (content) => {
  dialogContent.innerHTML = content;
  dialog.showModal();
};

const setHash = (updates) => {
  const params = hashState();
  Object.entries(updates).forEach(([key, value]) => params.set(key, value));
  const anchor = location.hash.split('?')[0] || '#story';
  history.replaceState(null, '', `${anchor}?${params}`);
};

const drawWaffle = (punctuality) => {
  const waffle = $('#waffle');
  const late = Math.round((100 - punctuality) * 10);
  waffle.replaceChildren(...Array.from({ length: 1000 }, (_, index) => {
    const square = document.createElement('i');
    square.className = index >= 1000 - late ? 'late' : '';
    square.setAttribute('aria-hidden', 'true');
    return square;
  }));
  waffle.setAttribute('aria-label', `${1000 - late} of 1,000 trips within two minutes; ${late} over two minutes`);
  $('#trip-translation').textContent = `About ${late} in 1,000 trips finished more than two minutes late.`;
};

const chartGeometry = (values) => {
  const width = 900, height = 360, left = 62, right = 26, top = 38, bottom = 52;
  const min = Math.min(...values, 98.5) - .1;
  const max = 100;
  const x = (index) => left + index * (width - left - right) / (values.length - 1);
  const y = (value) => top + (max - value) * (height - top - bottom) / (max - min);
  return { width, height, left, right, top, bottom, min, max, x, y };
};

const svgElement = (name, attrs = {}) => {
  const element = document.createElementNS('http://www.w3.org/2000/svg', name);
  Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, String(value)));
  return element;
};

const drawTrend = (data, line) => {
  const values = data.annual.punctuality[line];
  const years = data.annual.years;
  const svg = $('#trend-chart');
  const g = chartGeometry(values);
  svg.replaceChildren();

  [99, 99.5, 100].filter(value => value >= g.min).forEach(value => {
    const y = g.y(value);
    svg.append(svgElement('line', { x1: g.left, x2: g.width - g.right, y1: y, y2: y, class: 'chart-grid' }));
    const label = svgElement('text', { x: g.left - 12, y: y + 4, 'text-anchor': 'end', class: 'chart-axis' });
    label.textContent = `${value.toFixed(1)}%`;
    svg.append(label);
  });

  years.forEach((year, index) => {
    const label = svgElement('text', { x: g.x(index), y: g.height - 15, 'text-anchor': 'middle', class: 'chart-axis' });
    label.textContent = year;
    svg.append(label);
  });

  const path = svgElement('path', {
    d: values.map((value, index) => `${index ? 'L' : 'M'}${g.x(index)},${g.y(value)}`).join(' '),
    class: 'chart-line'
  });
  svg.append(path);

  values.forEach((value, index) => {
    const point = svgElement('circle', { cx: g.x(index), cy: g.y(value), r: 7, class: 'chart-point', tabindex: 0, role: 'button', 'aria-label': `${years[index]}: ${value.toFixed(2)}% punctual` });
    point.dataset.tip = `${years[index]} · ${value.toFixed(2)}% within 2 minutes`;
    svg.append(point);
  });
  $('#trend-title').textContent = `${lineNames[line]} punctuality`;
};

const renderLine = (data, line) => {
  const selected = data.latest.punctuality[line].at(-1);
  $('#selected-line-name').textContent = lineNames[line];
  $('#punctuality-value').textContent = selected.toFixed(2);
  $('#delivery-value').textContent = `${data.latest.delivery[line].at(-1).toFixed(2)}%`;
  $('#mkbf-value').textContent = formatKm(data.mkbf[line].at(-1));
  $('#line-advice').textContent = advice[line];
  $$('.line-tabs button').forEach(button => button.setAttribute('aria-selected', String(button.dataset.line === line)));
  drawWaffle(selected);
  drawTrend(data, line);
  setHash({ line });
};

const renderIncidents = (data) => {
  const strip = $('#incident-strip');
  strip.replaceChildren(...data.monthlySevereDelays.months.map((month, index) => {
    const cell = document.createElement('div');
    cell.className = 'month';
    const bar = document.createElement('div');
    bar.className = 'month-bar';
    for (let mark = 0; mark < data.monthlySevereDelays.MRT[index]; mark += 1) {
      const dot = document.createElement('i');
      dot.className = 'incident-mark';
      dot.dataset.tip = `${month}: ${data.monthlySevereDelays.MRT[index]} MRT delay${data.monthlySevereDelays.MRT[index] === 1 ? '' : 's'} over 30 minutes`;
      bar.append(dot);
    }
    const label = document.createElement('span');
    label.className = 'month-label';
    label.textContent = month.replace(' 20', ' ’');
    cell.append(bar, label);
    return cell;
  }));
};

const sourcesMarkup = (data) => `
  <p class="eyebrow">PROVENANCE</p>
  <h2>Every number has a platform.</h2>
  <p>Three official datasets were downloaded and preserved locally. The GTFS descriptor is also preserved, but its expired signed link means it contributes no timing values.</p>
  <ul class="source-list">${data.sources.map(source => `<li>
    <h3>${source.title}</h3>
    <p>${source.publisher} · ${source.coverage}</p>
    ${source.limitation ? `<p><strong>Not used:</strong> ${source.limitation}</p>` : ''}
    <p class="source-meta">Downloaded ${source.downloaded} · <a href="${source.local}" target="_blank">local file</a> · <a href="${source.url}" target="_blank" rel="noreferrer">official source</a></p>
  </li>`).join('')}</ul>
  <h3>Transformations</h3>
  <p>Tables were transcribed from the two LTA PDFs into <a href="data/app-data.json" target="_blank">app-data.json</a> and checked against extracted PDF text. The 1,000-trip grid rounds <code>(100 − punctuality) × 10</code> to the nearest whole trip.</p>
  <h3>Definitions that matter</h3>
  <ul><li><strong>Punctuality:</strong> train trips completing within two minutes of schedule at a terminal or turnaround point.</li><li><strong>Service delivery:</strong> actual train-km divided by scheduled train-km.</li><li><strong>MKBF:</strong> rolling 12-month train-km between delays longer than five minutes. TEL is published separately.</li><li><strong>Severe delay:</strong> service delay longer than 30 minutes.</li></ul>`;

const methodMarkup = `
  <p class="eyebrow">READ THE CLOCK</p><h2>“On time” has an address.</h2>
  <p>LTA’s Train Punctuality clocks a trip at the end of a line or scheduled turnaround. It counts the trip as punctual if it finishes within two minutes of schedule.</p>
  <p>That captures operating consistency, including slower running and long dwell times. It does <strong>not</strong> publish the delay at every station, your actual platform wait, or a guarantee for the next train.</p>
  <p>That is why this app says “trips,” never “commuters,” in the 1,000-trip view.</p>`;

const positionTooltip = (target) => {
  if (!target) return;
  const text = target.dataset.tip;
  if (!text) return;
  tooltip.textContent = text;
  tooltip.hidden = false;
  const box = target.getBoundingClientRect();
  const left = Math.min(innerWidth - 245, Math.max(10, box.left + box.width / 2 - 100));
  const top = Math.max(10, box.top - tooltip.offsetHeight - 10);
  Object.assign(tooltip.style, { left: `${left}px`, top: `${top}px` });
};

const main = async () => {
  const response = await fetch(DATA_URL);
  if (!response.ok) throw new Error(`Could not load ${DATA_URL}: ${response.status}`);
  const data = await response.json();
  const initialLine = hashState().get('line');
  const line = initialLine in lineNames ? initialLine : 'MRT';
  renderLine(data, line);
  renderIncidents(data);

  $$('.line-tabs button').forEach(button => button.addEventListener('click', () => renderLine(data, button.dataset.line)));
  $('.line-tabs').addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    const tabs = $$('.line-tabs button');
    const index = tabs.indexOf(document.activeElement);
    const next = (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    tabs[next].focus();
    tabs[next].click();
  });

  const openSources = () => openDialog(sourcesMarkup(data));
  $('#sources-button').addEventListener('click', openSources);
  $('#footer-sources').addEventListener('click', openSources);
  $('#method-button').addEventListener('click', () => openDialog(methodMarkup));
  $('#trend-help').addEventListener('click', () => openDialog('<p class="eyebrow">HONEST SCALES</p><h2>A close-up, clearly labelled.</h2><p>Punctuality values cluster near 100%, so a zero-based line chart would make real variation invisible. The axis is deliberately cropped and labelled at every gridline. Use the 1,000-trip grid above to keep the magnitude in perspective.</p>'));
  $('.impact-card').addEventListener('click', () => {
    const incident = data.incidents[0];
    openDialog(`<p class="eyebrow">PASSENGER IMPACT</p><h2>${incident.passengers} people, one disruption.</h2><p>On ${new Date(`${incident.date}T00:00:00`).toLocaleDateString('en-SG', { dateStyle: 'long' })}, a North East Line delay longer than 30 minutes affected an estimated ${incident.passengers} passengers—${incident.share} of the line’s daily passengers.</p><p>LTA estimates impact using historical average ridership through the affected section and time period. It is a range, not an actual tap count.</p>`);
  });

  document.addEventListener('pointerover', event => positionTooltip(event.target.closest?.('[data-tip]')));
  document.addEventListener('pointerout', event => { if (event.target.closest?.('[data-tip]')) tooltip.hidden = true; });
  document.addEventListener('focusin', event => positionTooltip(event.target.closest?.('[data-tip]')));
  document.addEventListener('focusout', () => { tooltip.hidden = true; });

  const themeButton = $('#theme-button');
  const savedTheme = hashState().get('theme');
  if (savedTheme === 'light') document.documentElement.dataset.theme = 'light';
  const updateThemeLabel = () => themeButton.setAttribute('aria-label', `Switch to ${document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'} theme`);
  updateThemeLabel();
  themeButton.addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    setHash({ theme });
    updateThemeLabel();
  });
};

main().catch(error => {
  console.error(error);
  openDialog(`<h2>Data did not load.</h2><p>${error.message}</p><p>Serve this folder over HTTP; browsers block JSON fetches from <code>file://</code>.</p>`);
});
