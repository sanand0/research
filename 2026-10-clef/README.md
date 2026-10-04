# Cloudflare Clef quick investigation — 2026-10-04

## Bottom line

Yes: this Cloudflare account can run both:

- @cf/cloudflare/clef — 27B multimodal decision model
- @cf/cloudflare/clef-flash — 9B multimodal decision model

The account already has an account-level **Workers Paid** subscription at **$5/month**, verified with `cf accounts subscriptions get`. The existing cf OAuth login has ai:read and ai:write, so no new API key was required for these tests.

Clef is a decision model, not a text generator: give it state plus typed questions (noul, choice, score) and it returns probabilities / bounded decisions.

## Billing

Cloudflare Workers AI currently gives **10,000 Neurons/day free**, reset at 00:00 UTC, including on Workers Paid. Above that, Workers Paid charges **$0.011 / 1,000 Neurons**.

| Model | Token price | Neurons |
| --- | ---: | ---: |
| Clef | $0.24 / M input tokens | 21,818 / M input tokens |
| Clef-flash | $0.09 / M input tokens | 8,182 / M input tokens |

There is no output-token charge listed for Clef because it returns structured decisions rather than generated text.

If all of the daily free allocation were spent only on one model, 10,000 neurons is roughly:

- Clef: **458k input tokens/day**
- Clef-flash: **1.22M input tokens/day**

The allocation is shared across Workers AI models.

The smoke + benchmark in this directory made 13 requests/model at 248 input tokens/request = 6,448 input tokens total. That is about **96.7 neurons**. If all of it had been billable rather than covered by the daily free allocation, the list-price cost would be about **$0.00106**.

cf billing usage get-v1 returned HTTP 403 because the current OAuth token lacks billing-usage permission. That is not required for inference. The exact day's account-wide neuron consumption can still be checked in the Workers AI dashboard, or queried later with a token that has the required billing read permission.

Sources:

- https://blog.cloudflare.com/clef-decision-models/
- https://developers.cloudflare.com/changelog/post/2026-10-01-clef-workers-ai/
- https://developers.cloudflare.com/workers-ai/models/clef/
- https://developers.cloudflare.com/workers-ai/platform/pricing/

## Latency from this machine in Singapore

cf ai run smoke calls were ~1.7 s end-to-end because CLI startup/auth dominates:

| Model | CLI smoke |
| --- | ---: |
| Clef-flash | 1,755 ms |
| Clef | 1,724 ms |

For application-relevant latency, bench.py calls the REST API over one reused HTTP/2 connection. It alternates models for 12 rounds and excludes round 1 as warm-up. All requests in this run hit Cloudflare's SIN edge (from cf-ray).

| Model | n | median | mean | min | p95 | max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Clef-flash | 11 | **388 ms** | 441 ms | 326 ms | 706 ms | 706 ms |
| Clef | 11 | **622 ms** | 632 ms | 365 ms | 819 ms | 819 ms |

Cloudflare's launch benchmark reports model medians of 38.8 ms for Clef-flash and 209.3 ms for Clef. Those appear to be model-serving latency rather than the full public REST round trip; the observed end-to-end numbers above are the more relevant ones for use from this machine.

Raw data: `bench.csv`.

## Run it

Simplest from this machine, using the existing cf OAuth login:

~~~bash
cf ai run @cf/cloudflare/clef-flash --body @payload.json
cf ai run @cf/cloudflare/clef --body @payload.json
~~~

For direct REST benchmarking:

~~~bash
./bench.py
~~~

bench.py reads the existing OAuth token from ~/.config/cloudflare/config/default.json; it never prints or stores the token.

For a deployed Cloudflare Worker, prefer a Workers AI binding and call:

~~~js
const result = await env.AI.run("@cf/cloudflare/clef-flash", {
  model: "clef-flash",
  state,
  questions,
});
~~~

For a long-lived local/server REST integration, create a scoped Cloudflare API token rather than depending on the interactive cf OAuth token.

## Files

- `README.md` — findings, pricing, latency, and usage notes
- `payload.json` — small support-triage input used for all tests
- `bench.py` — reusable direct REST latency benchmark
- `bench.csv` — raw latency samples
