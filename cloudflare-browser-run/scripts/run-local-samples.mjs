import { mkdir, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { once } from "node:events";

const baseUrl = "http://127.0.0.1:8787";
const outDir = new URL("../artifacts/", import.meta.url);
const samples = [
  { path: "/screenshot", file: "screenshot.png", type: "binary" },
  { path: "/dom", file: "dom-manipulated.png", type: "binary" },
  { path: "/form", file: "form-wikipedia.json", type: "json" },
  { path: "/scrape", file: "scrape-hacker-news.json", type: "json" },
];

await mkdir(outDir, { recursive: true });

const wrangler = spawn(
  "npx",
  ["wrangler", "dev", "--port", "8787", "--log-level", "warn"],
  {
    detached: true,
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, CI: "true" },
  },
);

try {
  await waitForDevServer();

  for (const sample of samples) {
    const response = await fetch(`${baseUrl}${sample.path}`);

    if (!response.ok) {
      throw new Error(`${sample.path} failed: ${response.status}`);
    }

    const target = new URL(sample.file, outDir);

    if (sample.type === "binary") {
      const body = new Uint8Array(await response.arrayBuffer());
      await writeFile(target, body);
      console.log(`${sample.path} -> ${target.pathname} (${body.length} bytes)`);
      continue;
    }

    const body = await response.json();
    await writeFile(target, `${JSON.stringify(body, null, 2)}\n`);
    console.log(`${sample.path} -> ${target.pathname}`);
    console.log(JSON.stringify(body, null, 2));
  }
} finally {
  await stopWrangler();
}

async function waitForDevServer() {
  const deadline = Date.now() + 60_000;
  let lastOutput = "";

  wrangler.stdout.on("data", (chunk) => {
    lastOutput += chunk.toString();
  });
  wrangler.stderr.on("data", (chunk) => {
    lastOutput += chunk.toString();
  });

  while (Date.now() < deadline) {
    try {
      const response = await fetch(`${baseUrl}/health`);
      if (response.ok) {
        return;
      }
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }

  throw new Error(`wrangler dev did not start:\n${lastOutput}`);
}

async function stopWrangler() {
  if (wrangler.exitCode !== null) {
    return;
  }

  signalWrangler("SIGINT");

  const stopped = await Promise.race([
    once(wrangler, "exit").then(() => true),
    new Promise((resolve) => setTimeout(() => resolve(false), 5_000)),
  ]);

  if (stopped) {
    return;
  }

  signalWrangler("SIGTERM");
  await Promise.race([
    once(wrangler, "exit"),
    new Promise((resolve) => setTimeout(resolve, 2_000)),
  ]);

  if (wrangler.exitCode === null) {
    signalWrangler("SIGKILL");
  }
}

function signalWrangler(signal) {
  try {
    process.kill(-wrangler.pid, signal);
  } catch {
    wrangler.kill(signal);
  }
}
