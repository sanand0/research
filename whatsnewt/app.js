// @ts-check
/* An interactive, dependency-free companion. No Python executes in the browser.
   Canonical challenge data is generated from Barry Warsaw's Apache-2.0 game. */
const GAME_DATA = window.GAME;
const $ = id => document.getElementById(id);
const routes = GAME_DATA.route;
const scenes = [...routes, {room: "secrets", via: "secrets"}, {room: "ending", via: "north"}];
const secretsAt = routes.length;
const endingAt = routes.length + 1;
const narratives = {
  foyer: "The interpreter stirs before your program does. Somebody has been slipping executable surprises into the startup machinery. Find a safer invitation to begin.",
  import_hall: "Every chest springs open before you touch it. The keeper offers two lazy seals. Make these imports wait until you actually need them.",
  vault: "Two keys sit on a velvet cushion. One mapping may never change; the other is a single, unmistakable absence that even None cannot impersonate.",
  typing: "The keepers of types have written three riddles on the walls: sealed records, types as values, and family trees with no diamond-shaped loopholes.",
  gardens: "Beds within beds. Labels upon labels. There is an asterisk-shaped shortcut through these tangled comprehensions.",
  crypt: "Here lie four once-familiar Python APIs. The coffins are not empty; they hold better modern replacements.",
  atrium: "The Great Loop returns you to a familiar crossroads. The Release Gate lies north, but no amount of enthusiasm can replace six sigils.",
  oracle: "An oracle that knows what you meant before you did. Correct broken lines; then find the distinction between a prefix and a search.",
  babel: "A thousand encodings shout at once. The new interpreter quietly chooses UTF-8. The old locale still has its place—if you request it.",
  scriptorium: "One smiling face can contain many code points. Trim human-visible characters, not just slices of bytes or Unicode scalar values.",
  weir: "Eight workers reach for one stream. The secret is not more locks everywhere; it is one iterator that knows how to share.",
  forge: "A hot bytearray waits on the anvil. Take its bytes without making a second copy, and notice the much faster machinery around you.",
  numerarium: "Some arithmetic is stubbornly whole. The abacus demands combinatorics, square roots and a clean integer-only module.",
  observatory: "Watch without touching. Attach a sampling profiler to a running process, turn samples into flamegraphs, and trace Python's new performance tools.",
  gate: "The gate bears the marks of your six sigils. One last manifest combines the ideas you've learned into a single file."
};
let state = {
  step: 0, spoilers: false, theme: "dark",
  read: new Set(), taken: new Set(), found: new Set(), visited: new Set()
};
const storageKey = "whatsnewt-expedition-v1";
function readStored() {
  try {
    const s = JSON.parse(localStorage.getItem(storageKey) || "{}");
    state.read = new Set(s.read || []);
    state.taken = new Set(s.taken || []);
    state.found = new Set(s.found || []);
    state.visited = new Set(s.visited || []);
    state.theme = s.theme || "dark";
  } catch { /* file:// can disable storage; the guide still works */ }
}
function saveStored() {
  try {
    localStorage.setItem(storageKey, JSON.stringify({
      read: [...state.read], taken: [...state.taken],
      found: [...state.found], visited: [...state.visited], theme: state.theme
    }));
  } catch { /* in-memory progress is fine */ }
}
function node(tag, cls = "", content = "") {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (content !== "") e.textContent = String(content);
  return e;
}
function add(parent, ...children) { children.forEach(child => parent.append(child)); return parent; }
function clear(id) { $(id).replaceChildren(); return $(id); }
function link(text, href) {
  const a = node("a", "", text);
  a.href = href;
  a.target = "_blank";
  a.rel = "noopener noreferrer";
  return a;
}
function button(label, fn, cls = "mini-button") {
  const b = node("button", cls, label);
  b.type = "button";
  b.addEventListener("click", fn);
  return b;
}
function toast(message) {
  const t = $("toast");
  t.textContent = message;
  t.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => t.classList.remove("show"), 1700);
}
function copyText(text) {
  const fallback = () => {
    const input = node("textarea");
    input.value = text;
    input.style.position = "fixed";
    input.style.opacity = "0";
    document.body.append(input);
    input.select();
    document.execCommand("copy");
    input.remove();
  };
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(text).then(() => toast("Copied to clipboard"))
      .catch(() => {fallback(); toast("Copied to clipboard");});
  } else { fallback(); toast("Copied to clipboard"); }
}
function codeView(content) {
  const pre = node("pre", "framed-code");
  add(pre, node("code", "", content));
  return pre;
}
function makeUrl() {
  return "#step=" + state.step + "&spoilers=" + (state.spoilers ? "1" : "0") + "&theme=" + state.theme;
}
function parseHash() {
  const hash = location.hash.slice(1);
  if (hash === "secrets") return {step: secretsAt};
  if (hash === "ending") return {step: endingAt};
  const p = new URLSearchParams(hash);
  const parsed = Number(p.get("step"));
  return {
    step: p.has("step") && Number.isFinite(parsed) ? Math.min(scenes.length - 1, Math.max(0, parsed)) : 0,
    spoilers: p.has("spoilers") ? p.get("spoilers") === "1" : state.spoilers,
    theme: p.get("theme") === "light" ? "light" : p.get("theme") === "dark" ? "dark" : state.theme
  };
}
function navigate(step, scroll = true, push = true) {
  state.step = Math.min(scenes.length - 1, Math.max(0, step));
  if (state.step < routes.length) state.visited.add(routes[state.step].room);
  saveStored();
  if (push) history.pushState(null, "", makeUrl());
  render();
  if (scroll) $("scene").scrollIntoView({behavior: "smooth", block: "start"});
}
function setOption(k, v) {
  state[k] = v;
  if (k === "theme") saveStored();
  history.replaceState(null, "", makeUrl());
  render();
}
function currentRoom() { return state.step < routes.length ? GAME_DATA.rooms[routes[state.step].room] : GAME_DATA.rooms.gate; }
function currentKey() { return state.step < routes.length ? routes[state.step].room : "gate"; }
function oneLine(text) { return text.replace(/\s+/g, " ").trim(); }
function srcUrl(key) {
  const c = GAME_DATA.puzzles[key].citation;
  const pep = /^PEP (\d+)/.exec(c);
  return pep ? "https://peps.python.org/pep-" + pep[1].padStart(4, "0") + "/" :
    "https://docs.python.org/3.15/whatsnew/3.15.html";
}
function renderMap() {
  const main = clear("map");
  const lower = clear("lower-map");
  const seen = new Set(routes.filter((r, i) => i <= state.step).map(r => r.room));
  for (const [key, room] of Object.entries(GAME_DATA.rooms)) {
    const idx = routes.findIndex(r => r.room === key);
    const active = currentKey() === key;
    const b = button(room.label, () => navigate(idx), "map-room" +
      (active ? " current" : "") + (seen.has(key) ? " visited" : ""));
    b.title = room.name + " — " + room.subtitle;
    b.setAttribute("aria-label", room.name + (active ? ", current room" : ""));
    if (active) b.setAttribute("aria-current", "location");
    if (room.level === 0) {
      b.style.gridColumn = String(room.column + 1);
      b.style.gridRow = String(room.row + 1);
      main.append(b);
    } else lower.append(b);
  }
}
function renderChapters() {
  const chapters = clear("chapters");
  const q = $("find").value.trim().toLowerCase();
  const unique = routes.map(r => r.room).filter((v, i, a) => a.indexOf(v) === i);
  const entries = unique.map((key, i) => ({
    label: GAME_DATA.rooms[key].name, subtitle: GAME_DATA.rooms[key].subtitle,
    key, index: routes.findIndex(r => r.room === key), n: String(i + 1).padStart(2, "0")
  }));
  entries.push({label: "The secret passages", subtitle: "11 Easter eggs & the jump command", index: secretsAt, n: "✳"});
  entries.push({label: "The perfect ending", subtitle: "375 points & final verdict", index: endingAt, n: "★"});
  const searchable = e => {
    if (!e.key) return e.label + " " + e.subtitle;
    const room = GAME_DATA.rooms[e.key];
    return [e.label, e.subtitle, ...room.puzzles.flatMap(k =>
      [k, GAME_DATA.puzzles[k].title, GAME_DATA.puzzles[k].citation]),
      ...room.items.map(k => GAME_DATA.items[k].name)].join(" ");
  };
  for (const item of entries.filter(e => searchable(e).toLowerCase().includes(q))) {
    const active = state.step === item.index || (item.key && currentKey() === item.key && state.step < routes.length);
    const b = button("", () => navigate(item.index), "chapter" + (active ? " active" : ""));
    if (active) b.setAttribute("aria-current", "step");
    add(b, node("span", "chapter-index", item.n), node("span", "chapter-label", item.label));
    if (item.key && GAME_DATA.rooms[item.key].puzzles.length && GAME_DATA.rooms[item.key].puzzles.every(k => state.read.has(k)))
      add(b, node("span", "chapter-check", "✓"));
    chapters.append(b);
  }
  if (!chapters.childElementCount) chapters.append(node("p", "sidebar-note", "No matching chapters."));
}
function renderHud() {
  const scene = scenes[state.step];
  const ref = state.step < routes.length ? scene : routes[routes.length - 1];
  $("score").replaceChildren(document.createTextNode(String(ref.score).padStart(3, "0") + " "), node("span", "", "/ 375"));
  $("sigils").replaceChildren(document.createTextNode(String(ref.sigils) + " "), node("span", "", "/ 6"));
  $("learned").replaceChildren(document.createTextNode(String(state.read.size) + " "), node("span", "", "/ 18"));
  $("found-secrets").replaceChildren(document.createTextNode(String(state.found.size) + " "), node("span", "", "/ 11"));
  $("progress").max = scenes.length;
  $("progress").value = state.step + 1;
  $("meter-label").textContent = "ENCOUNTER " + (state.step + 1) + " OF " + scenes.length;
  $("stage").textContent = "ENCOUNTER " + String(state.step + 1).padStart(2, "0") + " / " + scenes.length;
  $("step-count").textContent = String(state.step + 1).padStart(2, "0") + " / " + scenes.length;
  $("spoilers").setAttribute("aria-pressed", String(state.spoilers));
  $("spoilers").textContent = state.spoilers ? "Hide all answers" : "Show all answers";
  document.documentElement.dataset.theme = state.theme;
  $("theme").textContent = state.theme === "dark" ? "☼ Light" : "☾ Dark";
  $("prev").disabled = state.step === 0;
  $("next").disabled = state.step === endingAt;
  $("next").textContent = state.step === secretsAt ? "Cross the release gate →" :
    state.step === endingAt ? "Expedition complete" : "Next encounter →";
}
function addLog(text, command = false) {
  const lines = $("log");
  const e = node("div", command ? "line-input" : "line-soft", text);
  lines.append(e);
  if (lines.childElementCount > 28) lines.firstElementChild.remove();
  lines.scrollTop = lines.scrollHeight;
}
function initLog() {
  clear("log");
  if (state.step === secretsAt) {
    addLog("> secrets", true);
    addLog("Curiosities: eleven words worth saying. Six of them are the people who shaped Python 3.15.");
    addLog("Try a name at the prompt, or click SAY on a card below.");
    return;
  }
  if (state.step === endingAt) {
    addLog("> north", true);
    addLog("You step through.");
    addLog("Score 375 / 375  ·  Puzzles 18 / 18  ·  Curiosities 11 / 11 (after you find them)");
    return;
  }
  const r = routes[state.step];
  addLog(r.via === "foyer" ? "> look" : "> " + r.via, true);
  addLog(GAME_DATA.rooms[r.room].blurb);
  if (r.collect.length) addLog("On the floor: " + r.collect.join(", ") + ".");
  if (r.answer.length) addLog("Puzzles: " + r.answer.map(k => GAME_DATA.puzzles[k].title).join("; "));
  if (!r.first) addLog("You have been here before. The next route is a detour back to the main path.");
}
function renderPickups(r) {
  const section = clear("pickups");
  if (!r.collect.length) return;
  add(section, node("h3", "section-heading", "Souvenirs worth collecting"));
  const grid = node("div", "pickups");
  const room = GAME_DATA.rooms[r.room];
  for (const key of room.items) {
    const item = GAME_DATA.items[key];
    const card = node("article", "pickup-card");
    add(card, node("span", "lozenge", "+5 POINTS · FOUND ON THE FLOOR"),
      node("h4", "", item.name), node("p", "", item.description));
    const b = button(state.taken.has(key) ? "✓ Picked up" : "Take " + item.name, () => {
      state.taken.add(key); saveStored(); b.classList.add("done"); b.textContent = "✓ Picked up";
      addLog("> take " + r.collect[0], true); addLog("You take " + item.name + ".");
      toast("Souvenir recorded");
    });
    if (state.taken.has(key)) b.classList.add("done");
    card.append(b); grid.append(card);
  }
  section.append(grid);
}
function renderPuzzles(r) {
  const section = clear("puzzles");
  if (!r.answer.length) return;
  add(section, node("h3", "section-heading", r.answer.length === 1 ? "The puzzle" : "The puzzles"));
  r.answer.forEach((key, i) => {
    const p = GAME_DATA.puzzles[key];
    const card = node("article", "puzzle-card");
    card.id = "puzzle-" + key;
    const head = node("div", "puzzle-head");
    add(head, node("span", "puzzle-marker", "PUZZLE " + String.fromCharCode(65 + i) +
      "  /  " + p.points + " POINTS"), link(p.citation + " ↗", srcUrl(key)));
    add(card, head, node("h4", "", p.title), node("p", "puzzle-desc", p.briefing));
    add(card, node("div", "code-label", "YOU ARE GIVEN THIS STARTER"), codeView(p.starter.trim()));
    const hints = node("details", "hint-details");
    const list = node("ol", "hints");
    p.hints.forEach(h => list.append(node("li", "", h)));
    add(hints, node("summary", "", "Need a nudge? " + p.hints.length + " hints from the game"), list);
    card.append(hints);
    const solution = node("details", "solution");
    solution.open = state.spoilers;
    add(solution, node("summary", "", "Reveal the reference solution"),
      node("div", "code-label", p.language === "bash" ? "THE CONTENT OF myapp.start" : "TESTED IN PYTHON 3.15"),
      codeView(p.solution.trim()));
    const actions = node("div", "mini-actions");
    const read = button(state.read.has(key) ? "✓ Understood" : "Mark understood", () => {
      if (state.read.has(key)) state.read.delete(key); else state.read.add(key);
      saveStored(); render();
    });
    if (state.read.has(key)) read.classList.add("done");
    add(actions, button("Copy answer ↗", () => copyText(p.solution.trim())), read);
    solution.append(actions);
    card.append(solution);
    if (p.reward) {
      const reward = GAME_DATA.items[p.reward];
      card.append(node("p", "reward-line", "↳ REWARD: " + reward.name.toUpperCase() +
        (reward.sigil ? "  ✦ SIGIL" : "")));
    }
    section.append(card);
  });
}
function renderExamine(room) {
  const section = clear("examine");
  const keys = Object.keys(room.details);
  if (!keys.length) return;
  const outer = node("details", "inspect-details");
  const contents = node("div", "examiner");
  const shown = new Set();
  keys.forEach(key => {
    const content = room.details[key];
    if (shown.has(content)) return;
    shown.add(content);
    const one = node("details");
    add(one, node("summary", "", "examine " + key), node("p", "", content));
    contents.append(one);
  });
  add(outer, node("summary", "", "Explore the room · " + shown.size + " inspectable clues"), contents);
  section.append(outer);
}
function renderSecrets() {
  const section = clear("special");
  add(section, node("h3", "section-heading", "The 11 hidden commands"),
    node("p", "secret-intro", "They are not offered by Tab completion. Type each as a command in the real game. The six named contributors open the secret 'jump ROOM' shortcut for rooms you have already visited. The other five are references to computing folklore."));
  const grid = node("div", "secret-grid");
  for (const [name, secret] of Object.entries(GAME_DATA.secrets)) {
    const card = node("article", "secret-card" + (state.found.has(name) ? " discovered" : ""));
    card.id = "secret-" + name;
    add(card, node("span", "puzzle-marker", secret.council ? "COUNCIL · UNLOCKS JUMP" : "CURIOSITY"),
      node("h4", "", "> " + name), node("p", "", secret.label));
    if (state.found.has(name) || state.spoilers) {
      card.append(node("blockquote", "", name === "zen" ?
        "Each invocation draws a random Zen of Python line. Try it repeatedly." :
        secret.response.join("\n")));
      if (name === "zen") {
        const details = node("details", "hint-details");
        const list = node("ol", "hints");
        GAME_DATA.zen.forEach(z => list.append(node("li", "", z.saying +
          (z.note ? " — " + z.note : ""))));
        add(details, node("summary", "", "All 19 possible Zen lines"), list);
        card.append(details);
      }
    } else card.append(node("p", "", "Say the word to hear the game's reply."));
    card.append(button(state.found.has(name) ? "✓ Discovered" : "Say " + name, () => {
      discover(name);
    }, "mini-button" + (state.found.has(name) ? " done" : "")));
    grid.append(card);
  }
  section.append(grid);
  const councilFound = GAME_DATA.council.every(k => state.found.has(k));
  const unlock = node("article", "pickup-card");
  add(unlock, node("h4", "", councilFound ? "The sixth name unlocks a passage." : "A door marked JUMP"),
    node("p", "", councilFound ?
      "You can now use 'jump foyer', 'jump vault', or any room already visited. Jump cannot take you somewhere new." :
      "Try 'jump foyer' before speaking all six names. The game answers: Nothing happens... yet."));
  section.append(unlock);
}
function renderEnding() {
  const section = clear("special");
  add(section, node("h3", "section-heading", "The perfect run"),
    node("p", "ending-intro", "After you solve the Release Manifest, the gate opens. Go north. If you skipped anything, the game warns you once and asks you to go north again to leave anyway. For a complete expedition, solve all 18, collect all eight floor souvenirs, visit all 15 rooms and find all 11 curiosities before leaving."));
  const score = node("div", "ending-score", "375");
  add(score, node("small", "", " / 375"));
  section.append(score);
  const grid = node("div", "ending-metrics");
  [
    ["18 / 18", "PUZZLES"],
    ["6 / 6", "SIGILS"],
    ["8 / 8", "FLOOR SOUVENIRS"],
    ["15 / 15", "ROOMS"],
    ["11 / 11", "CURIOSITIES"]
  ].forEach(pair => {
    const card = node("div");
    add(card, node("strong", "", pair[0]), node("small", "", pair[1]));
    grid.append(card);
  });
  section.append(grid);
  const allRead = GAME_DATA.totals.puzzles === state.read.size;
  const allSecrets = GAME_DATA.totals.curiosities === state.found.size;
  section.append(node("p", "secret-intro", "Your guide progress: " + state.read.size +
    " puzzle solutions marked understood, " + state.taken.size +
    " floor souvenirs marked collected, and " + state.found.size +
    " hidden commands discovered. " + (allRead && allSecrets ? "Expedition complete." :
    "The 375 above is the independently executed upstream reference score, not your personal game score.")));
  section.append(button("Return to the beginning ↺", () => navigate(0), "action-secondary"));
}
function render() {
  renderHud();
  renderMap();
  renderChapters();
  clear("pickups"); clear("puzzles"); clear("examine"); clear("special");
  if (state.step === secretsAt || state.step === endingAt) {
    const secret = state.step === secretsAt;
    $("room-label").textContent = secret ? "THE SECRET PASSAGE" : "AFTER THE LAST PUZZLE";
    $("room-title").textContent = secret ? "The Hidden Council" : "You step through.";
    $("room-subtitle").textContent = secret ? "Eleven commands. Six people. One shortcut." :
      "The Release Gate · final reckoning";
    $("story").textContent = secret ?
      "You hear a hollow voice. It sounds suspiciously like a Python core developer." :
      "Outside the interpreter, the light has changed. You've left with more than a version number.";
    $("room-glyph").textContent = secret ? "11" : "✓";
    $("room-type").textContent = secret ? "HIDDEN ENCOUNTER" : "EPILOGUE";
    $("move").textContent = secret ? "speak the secret commands" : "north";
    $("route-note").textContent = secret ? "Visit this encounter before leaving the gate." :
      "One north if complete; twice if warned about omissions.";
    if (secret) renderSecrets(); else renderEnding();
  } else {
    const r = routes[state.step], room = GAME_DATA.rooms[r.room];
    $("room-label").textContent = "ROOM " + String(Object.keys(GAME_DATA.rooms).indexOf(r.room) + 1).padStart(2, "0");
    $("room-title").textContent = room.name;
    $("room-subtitle").textContent = room.subtitle;
    $("story").textContent = narratives[r.room] || room.description;
    $("room-glyph").textContent = String(Object.keys(GAME_DATA.rooms).indexOf(r.room) + 1).padStart(2, "0");
    $("room-type").textContent = room.level ? "BELOW THE MAIN FLOOR" : "MAIN FLOOR";
    $("move").textContent = r.via === "foyer" ? "look" : r.via;
    $("route-note").textContent = r.first ? "First visit. Solve the puzzles and take anything on the floor." :
      "Return visit. You've already solved this room.";
    renderPickups(r); renderPuzzles(r); renderExamine(room);
  }
  initLog();
}
function discover(name) {
  const s = GAME_DATA.secrets[name];
  if (!s) return false;
  const fresh = !state.found.has(name);
  state.found.add(name); saveStored();
  addLog("> " + name, true);
  const reply = name === "zen" ? (() => {
    const z = GAME_DATA.zen[Math.floor(Math.random() * GAME_DATA.zen.length)];
    return [z.saying, ...(z.note ? [z.note] : [])];
  })() : s.response;
  reply.forEach(line => addLog(line));
  if (fresh) toast("Secret found: " + state.found.size + " / 11");
  if (state.step === secretsAt) renderSecrets();
  renderHud();
  return true;
}
function command(value) {
  const raw = value.trim();
  const words = raw.toLowerCase().split(/\s+/);
  if (!raw) return;
  const verb = words[0], rest = words.slice(1).join(" ");
  if (GAME_DATA.secrets[verb] && words.length === 1) {
    discover(verb); renderHud(); return;
  }
  addLog("> " + raw, true);
  const room = currentRoom();
  if (verb === "look" || verb === "l") { addLog(room.description); return; }
  if (verb === "inventory" || verb === "i" || verb === "inv") {
    const names = [...state.taken].map(k => GAME_DATA.items[k]?.name).filter(Boolean);
    addLog(names.length ? names.join(", ") : "Your field-guide inventory is empty. Mark souvenirs above.");
    return;
  }
  if (verb === "score") {
    addLog("Reference score: " + routes[Math.min(state.step,routes.length-1)].score +
      " / 375. Your puzzle reading: " + state.read.size + "/18.");
    return;
  }
  if (verb === "help" || verb === "?") {
    addLog("look · examine <thing> · take <thing> · solve · hint · inventory · map · score · secrets · north/south/east/west/up/down · jump <room> · [hidden word]");
    return;
  }
  if (verb === "secrets") {
    addLog(state.step >= routes.length - 1 ? Object.keys(GAME_DATA.secrets).join(", ") :
      "That would be telling. Some are words worth saying out loud; some are people worth naming.");
    return;
  }
  if (verb === "hint") {
    const key = room.puzzles[0];
    addLog(key ? GAME_DATA.puzzles[key].hints[0] : "There is no unsolved puzzle in this room.");
    return;
  }
  if (["solve", "try", "edit"].includes(verb)) {
    const key = room.puzzles[rest ? Math.max(0, rest.charCodeAt(0)-97) : 0] || room.puzzles[0];
    if (!key) {addLog("Nothing to solve here."); return;}
    addLog("Scroll to " + GAME_DATA.puzzles[key].title + " to inspect its verified solution. The original TUI runs Python 3.15; this browser guide does not.");
    $("puzzles").scrollIntoView({behavior:"smooth",block:"start"}); return;
  }
  if (["examine", "x", "inspect", "read"].includes(verb)) {
    const clue = Object.entries(room.details).find(([k]) => k.includes(rest) || rest.includes(k));
    const item = Object.values(GAME_DATA.items).find(x => x.name.toLowerCase().includes(rest) && rest.length > 2);
    addLog(clue ? clue[1] : item ? item.description : "Nothing by that name here. Open Explore the room for all targets.");
    return;
  }
  if (["take", "get", "pick", "grab"].includes(verb)) {
    const key = room.items.find(k => GAME_DATA.items[k].name.toLowerCase().includes(rest) ||
      rest.includes(GAME_DATA.items[k].name.replace(/^(a |an |the )/, "").split(" ").at(-1)));
    if (!key) {addLog("Nothing by that name is lying here."); return;}
    state.taken.add(key); saveStored(); addLog("You take " + GAME_DATA.items[key].name + ".");
    renderPickups(routes[Math.min(state.step, routes.length-1)]); return;
  }
  if (verb === "map") { $("sidebar").scrollIntoView({behavior:"smooth"}); addLog("The map shows all rooms in this guide. Click one to jump."); return; }
  if (verb === "jump" || verb === "teleport") {
    if (!GAME_DATA.council.every(k => state.found.has(k))) { addLog("Nothing happens... yet."); return; }
    const matched = Object.keys(GAME_DATA.rooms).find(k =>
      k.replaceAll("_"," ").includes(rest) || GAME_DATA.rooms[k].name.toLowerCase().includes(rest) ||
      GAME_DATA.rooms[k].label.toLowerCase() === rest);
    if (!matched) {addLog("No room by that name.");return;}
    if (!state.visited.has(matched)) {addLog("You have not been there yet.");return;}
    const idx = routes.findIndex(r=>r.room===matched);
    navigate(idx); addLog("The building rearranges itself around you."); return;
  }
  const dirs = ["north","south","east","west","up","down","n","s","e","w","u","d"];
  if (dirs.includes(verb)) {
    const direction = {n:"north",s:"south",e:"east",w:"west",u:"up",d:"down"}[verb] || verb;
    if (currentKey() === "gate" && direction === "north") {navigate(endingAt);return;}
    const target = room.exits[direction];
    if (!target) {addLog("That way does not open.");return;}
    const next = routes.findIndex((r,i)=>i>state.step && r.room === target);
    navigate(next >= 0 ? next : routes.findIndex(r=>r.room===target));
    return;
  }
  addLog("I do not know how to " + raw + ". Try help.");
}
$("command-form").addEventListener("submit", e => {
  e.preventDefault();
  const raw = $("command").value;
  $("command").value = "";
  command(raw);
});
$("prev").addEventListener("click", () => navigate(state.step - 1));
$("next").addEventListener("click", () => navigate(state.step + 1));
$("begin").addEventListener("click", () => navigate(0));
$("spoilers").addEventListener("click", () => setOption("spoilers", !state.spoilers));
$("theme").addEventListener("click", () => setOption("theme", state.theme === "dark" ? "light" : "dark"));
$("find").addEventListener("input", renderChapters);
document.addEventListener("keydown", e => {
  if (e.altKey || e.ctrlKey || e.metaKey) return;
  const editing = ["INPUT","TEXTAREA","SELECT"].includes(document.activeElement?.tagName);
  if (e.key === "/" && !editing) { e.preventDefault(); $("find").focus(); return; }
  if (editing) return;
  if (e.key === "ArrowRight") {e.preventDefault();navigate(state.step + 1);}
  if (e.key === "ArrowLeft") {e.preventDefault();navigate(state.step - 1);}
});
window.addEventListener("popstate", () => {
  Object.assign(state, parseHash());
  render();
  $("scene").scrollIntoView({behavior:"smooth",block:"start"});
});
window.addEventListener("hashchange", () => {
  Object.assign(state, parseHash()); render();
  $("scene").scrollIntoView({behavior:"smooth",block:"start"});
});
readStored();
Object.assign(state, parseHash());
if (state.step < routes.length) state.visited.add(routes[state.step].room);
render();
