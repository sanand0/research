import puppeteer from "@cloudflare/puppeteer";
import { run as screenshot } from "./samples/01-screenshot.js";
import { run as dom } from "./samples/02-manipulate-dom.js";
import { run as form } from "./samples/03-fill-form.js";
import { run as scrape } from "./samples/04-scrape.js";

const routes = {
  "/": index,
  "/health": health,
  "/screenshot": runInBrowser(screenshot),
  "/dom": runInBrowser(dom),
  "/form": runInBrowser(form),
  "/scrape": runInBrowser(scrape),
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const handler = routes[url.pathname];

    if (!handler) {
      return new Response("Not found\n", { status: 404 });
    }

    try {
      return await handler(request, env);
    } catch (error) {
      return Response.json({ error: error.message }, { status: 500 });
    }
  },
};

function index() {
  return new Response(
    [
      "Cloudflare Browser Run samples",
      "",
      "/screenshot - take a PNG screenshot of example.com",
      "/dom        - edit the page DOM, then screenshot it",
      "/form       - fill Wikipedia search and return the result",
      "/scrape     - scrape Hacker News story links",
      "",
    ].join("\n"),
    { headers: { "content-type": "text/plain; charset=utf-8" } },
  );
}

function health() {
  return new Response("ok\n", {
    headers: { "content-type": "text/plain; charset=utf-8" },
  });
}

function runInBrowser(sample) {
  return async (_request, env) => {
    const browser = await puppeteer.launch(env.MYBROWSER);

    try {
      const page = await browser.newPage();
      await page.setViewport({ width: 1280, height: 720 });
      return await sample(page);
    } finally {
      await browser.close();
    }
  };
}
