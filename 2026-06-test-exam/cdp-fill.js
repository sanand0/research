// @ts-check
import { readFile } from "node:fs/promises";

const answers = JSON.parse(await readFile(new URL("./answers.json", import.meta.url), "utf8"));
const tabs = await fetch("http://localhost:9222/json/list").then((response) => response.json());
const tab = tabs.find(({ url }) => url === "https://exam.sanand.workers.dev/2026-06-test");
if (!tab) throw new Error("Live exam tab not found");

const socket = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});

const expression = `(() => {
  const answers = ${JSON.stringify(answers)};
  for (const [name, value] of Object.entries(answers)) {
    const input = document.querySelector(\`[name="\${name}"]\`);
    if (!input) throw new Error(\`Missing field: \${name}\`);
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
  }
  return Object.keys(answers);
})()`;

socket.send(JSON.stringify({
  id: 1,
  method: "Runtime.evaluate",
  params: { expression, returnByValue: true },
}));

const result = await new Promise((resolve) => {
  socket.addEventListener("message", ({ data }) => {
    const message = JSON.parse(data);
    if (message.id === 1) resolve(message);
  });
});
console.log(JSON.stringify(result, null, 2));
socket.close();
