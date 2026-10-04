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

The original smoke + baseline benchmark made 13 requests/model at 248 input tokens/request = 6,448 input tokens total, about **96.7 neurons**. Including the later HTTP/1.1 vs HTTP/2 and Worker-binding latency experiments, this investigation used roughly **500 neurons** in total — about 5% of one day's free allocation, or about **$0.0055** if it had all been billable.

cf billing usage get-v1 returned HTTP 403 because the current OAuth token lacks billing-usage permission. That is not required for inference. The exact day's account-wide neuron consumption can still be checked in the Workers AI dashboard, or queried later with a token that has the required billing read permission.

Sources:

- https://blog.cloudflare.com/clef-decision-models/
- https://developers.cloudflare.com/changelog/post/2026-10-01-clef-workers-ai/
- https://developers.cloudflare.com/workers-ai/models/clef/
- https://developers.cloudflare.com/workers-ai/platform/pricing/
- https://developers.cloudflare.com/workers-ai/configuration/bindings/
- https://developers.cloudflare.com/workers/reference/protocols/

## Latency from Singapore

The practical result: **for lowest latency, put a tiny Worker in front of Clef and call it through a Workers AI binding (`env.AI.run()`); if you use the public REST API directly, keep the connection alive. HTTP/3 by itself did not materially reduce steady-state latency.** Model execution / scheduling is a much larger component than the transport protocol.

### Baseline: direct REST over a reused HTTP/2 connection

`bench.py` calls `api.cloudflare.com` over one reused HTTP/2 connection, alternates models for 12 rounds, and excludes round 1 as warm-up. The current committed `bench.csv`, run on this machine, gives:

| Model | n | median | mean | min | p95 | max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Clef-flash | 11 | **409 ms** | 389 ms | 332 ms | 447 ms | 447 ms |
| Clef | 11 | **680 ms** | 665 ms | 481 ms | 896 ms | 896 ms |

All requests hit Cloudflare's `SIN` edge. The earlier `cf ai run` smoke calls were ~1.7 s because CLI startup/auth dominates, so the direct REST benchmark is much more representative.

### HTTP/1.1 vs HTTP/2: reuse matters more than protocol

A second exploratory run compared fresh and reused HTTP/1.1 and HTTP/2 connections. It was noisy enough that there is no credible HTTP/2-vs-HTTP/1.1 winner, but creating a fresh connection for each inference was consistently worse, especially in the tail.

| Model | H1 reused median | H2 reused median | H1 fresh median | H2 fresh median |
| --- | ---: | ---: | ---: | ---: |
| Clef-flash | 527 ms | 621 ms | 844 ms | 715 ms |
| Clef | 660 ms | 777 ms | 819 ms | 1,018 ms |

The H2 medians differ substantially between this run and the baseline above, showing that backend/model variance is larger than any protocol effect in these small samples. The reliable optimization is **connection reuse**, not choosing H1 or H2.

### Workers AI binding: the biggest win

I deployed a temporary Worker using `env.AI.run()` so the Worker could call Clef through a Workers AI binding rather than the public REST API. Over a reused HTTP/2 connection from Singapore, 12 runs/model gave:

| Model | End-to-end median | `AI.run()` median | Network/Worker overhead median | End-to-end min |
| --- | ---: | ---: | ---: | ---: |
| Clef-flash | **273 ms** | 215 ms | 53 ms | **223 ms** |
| Clef | **417 ms** | 326 ms | 51 ms | **333 ms** |

That is roughly **33% lower median latency for Clef-flash** and **39% lower for Clef** than the current direct-REST baseline. The temporary Worker was deleted after the benchmark.

### HTTP/3

`api.cloudflare.com` did not advertise HTTP/3 in its response headers, and a direct QUIC/H3 handshake from this machine failed. By contrast, the temporary `workers.dev` endpoint advertised `alt-svc: h3=":443"`, and Chrome did switch to HTTP/3 after learning the Alt-Svc route.

Warm browser navigation timings over H3 were (the first Clef-flash H3 navigation was excluded as connection setup; Clef ran afterward on the already-warm H3 connection):

| Model | n | median | mean | min | max |
| --- | ---: | ---: | ---: | ---: | ---: |
| Clef-flash | 7 | **303 ms** | 330 ms | 239 ms | 429 ms |
| Clef | 8 | **473 ms** | 522 ms | 325 ms | 849 ms |

Those are not better than the H2 Worker-binding medians. This is not a perfectly controlled H2-vs-H3 comparison — Chrome and `httpx` are different clients and model latency varies substantially — but it is enough to say **H3 is not the lever worth chasing here**. H3 can reduce connection-establishment cost and help under packet loss, but once a connection is warm, inference dominates.

The lowest end-to-end observations in these tests were about **223 ms for Clef-flash** and **325 ms for Clef** through the Worker-binding path. The lowest measured `AI.run()` times were **178 ms** and **300 ms** respectively, which is a useful practical floor for this prompt from Singapore.

Cloudflare's launch benchmark reports median model latencies of 38.8 ms for Clef-flash and 209.3 ms for Clef across its benchmark suite. Those numbers are not directly comparable with this 248-token prompt and public end-to-end measurements, but they confirm that Clef-flash itself can execute much faster under favorable conditions.

Raw reproducible baseline data is in `bench.csv`. The protocol, Worker-binding, and H3 tests were one-off exploratory measurements; their aggregate results are preserved above rather than as extra benchmark files.

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

- `README.md` — findings, pricing, latency, and recommendations
- `prompts.md` — prompts / ideas for evaluating Clef
- `payload.json` — small support-triage input used for all tests
- `bench.py`, `bench.csv` — reusable direct REST HTTP/2 baseline benchmark
