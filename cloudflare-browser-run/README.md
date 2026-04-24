# Cloudflare Browser Run Samples

Small examples for Cloudflare Browser Run, formerly Browser Rendering.

## What the docs say

Browser Run exposes two useful layers:

- **Quick Actions**: one HTTP request for screenshots, PDFs, HTML, Markdown, links, structured JSON, snapshots, scraping, or crawling. These call Cloudflare's REST API and require `CLOUDFLARE_ACCOUNT_ID` plus an API token with `Browser Rendering - Edit`. See Cloudflare's [Quick Actions docs](https://developers.cloudflare.com/browser-run/quick-actions/).
- **Browser Sessions**: full browser automation with Puppeteer, Playwright, or raw Chrome DevTools Protocol. In Workers, the browser is exposed as a binding. In local development, Wrangler can run that binding against a local browser. See the [Puppeteer docs](https://developers.cloudflare.com/browser-run/puppeteer/) and [CDP docs](https://developers.cloudflare.com/browser-run/cdp/).

Useful operational details:

- Dynamic pages may need `goToOptions.waitUntil: "networkidle2"` or a specific `waitForSelector`; Browser Run defaults to `domcontentloaded`.
- Browser Run requests are identified as bot traffic by Cloudflare.
- Quick Actions return an `X-Browser-Ms-Used` response header for usage tracking.

This repo uses the Worker binding path so the examples can be run locally without Cloudflare credentials.

## Install

```sh
npm install
```

## Run the samples

```sh
npm run samples
```

The runner starts `wrangler dev`, calls each route, and writes outputs to `artifacts/`.

Latest local run:

```text
/screenshot -> artifacts/screenshot.png (1280x720 PNG)
/dom        -> artifacts/dom-manipulated.png (1280x720 PNG)
/form       -> {"title":"Cloudflare - Wikipedia","heading":"Cloudflare"}
/scrape     -> 5 Hacker News story links
```

## Routes

```text
/screenshot - take a PNG screenshot of example.com
/dom        - edit the page DOM, then screenshot it
/form       - fill Wikipedia search and return the result
/scrape     - scrape Hacker News story links
```

## Cloudflare-hosted Browser Run

Deploying this Worker, or using direct CDP/Quick Actions against Cloudflare's API, requires Cloudflare credentials:

```sh
export CLOUDFLARE_ACCOUNT_ID="..."
export CLOUDFLARE_API_TOKEN="..."
```

The token needs `Browser Rendering - Edit`.
