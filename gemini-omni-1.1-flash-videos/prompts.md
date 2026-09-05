# Prompts

# Initial research, 31 Aug 2026

<!--

v1: Gemini Omni 1.1 Flash Features: https://chatgpt.com/c/6a94e0ad-08d0-83ec-8f8e-4d9e3240da64
v2: Use cases: https://chatgpt.com/c/6a94e67e-42b8-83ec-a29d-bc69a6fcd509
v3: Run the experiments below: thttps://chatgpt.com/c/6a94ec56-9118-83ec-996a-691a3283cf61

-->

What are people reporting consistently as the most noteworthy features of Gemini Omni 1.1 Flash? Research extensively, share a prioritized list.

---

Based on video generation discussions - see emails, chat, transcripts, etc. on @LocalMCP - who would be interested and what specific use cases could they try out? Share a prioritized list.

---

I'd like to run create a few self-explanatory feature videos, i.e. just watching / hearing the videos, people will understand the feature it showcases. These should be the most noteworthy features and the video should instantly and visually (as well as narratively) them understand why this was hard. It should also be relevant to the above audience. Ideate using relevant skills on @LocalMCP and research as required to suggest the most effective steps + prompts for each video.

---

The GEMINI_API_KEY in ~/code/research/gemini-omni-1.1-flash-videos/.env can create videos using the Omni 1.1 Flash model. A pipeline exists under `~/code/research/gemini-omni-1.1-flash-videos/`:

-`generate.py` — one executable Python script using the official `google-genai` SDK via `uv`; loads `.env`, generates video, saves metadata and estimates actual API cost. -`README.md`— usage, smoke-test result, pricing, and experiment budget. -`.gitignore` — ignores `.env`, `output/`, and Python cache. -`output/sample.mp4`— generated smoke test. -`output/sample.json`— model/request/usage/cost metadata.

For the five proposed experiments, assuming 3 exploratory 360p candidates for experiments 1–4, six candidates for “Fail cheaply,” then rerunning the chosen sequences at 720p, the costs are likely to be:

| Experiment                                  |    Estimate |
| ------------------------------------------- | ----------: |
| Fix ONE thing: 8s base + edit               |      ~$2.72 |
| Still me at 30 seconds: base + 2 extensions |      ~$4.75 |
| First + last frame interpolation            |      ~$1.64 |
| Video-reference motion                      |      ~$1.64 |
| Fail cheaply: six 5s variants + final       |      ~$1.55 |
| **Total**                                   | **~$12.30** |

Run the first experiment.

I want this structured so that each experiment is a separate uv Python script that can be run independently, will resume from where it stopped, is agent friendly (see the skill), logs progress and errors, and organizes output in a comparable way.

---

Impressive! Proceed with the next. Clean up unnecessary files.

---

Proceed with the next two.

Document all the API costs so far. Even experiments and failures, itemized.

---

Compress final videos into webm using libav1. Here's my preferred command and settings:

```
bash
ffmpeg -i input.mp4 -c:v av1_nvenc -preset p6 -tune uhq -rc vbr -cq 55 -b:v 0 -spatial-aq 1 -temporal-aq 1 -c:a libopus -b:a 24k -vbr on -compression_level 10 output.webm
```

Create a single page`index.html`that explains what we did (including prompts, API parameters), why that's relevant, what it costs, what we learnt, what to be careful about, and embeds the .webm videos as proof. Link EXTENSIVELY to sources, references, etc. Use anand-writing-style skill.

Create a justfile so that`just build`will create the video outputs (including .webm, re-creating only what's required)`just deploy`should copy the required videos into ~/r2/media/ e.g. 2026-08-31-gemini-omni-1.1-flash/01-fix-one-thing/base.mp4 etc. as well as index.html into 2026-08-31-gemini-omni-1.1-flash/

~/r2/media/ is synced with media.s-anand.net/ - use absolute URLs in index.html so that it can be viewed from anywhere (e.g. via Github Pages - https://sanand0.github.io/research/2026-08-31-gemini-omni-1.1-flash/ as well as https://media.s-anand.net/2026-08-31-gemini-omni-1.1-flash/)

git add the relevant files. Ideally`git add gemini-omni-1.1-flash-videos/` should do this - update .gitignore accordingly and delete unnecessary files IF REQUIRED.

---

I deployed the videos.

A few changes: Round off costs to the nearest cent (or 2 significant digits if it's less than 10 cents).
Change headings to action titles where relevant. For example: "Can I fix ONE thing?" -> "It can make SPECIFIC changes" (or something better). "It can extend videos from 10s to 30s".
Make the caveats like 2 seconds of silence around the video and other gotchas stand out.
Improve the design. The font feels plain. Think about the best way to design this page, making it more attractive functionally - not just aesthetics for its own sake, but rather for better readability, comprehension, etc. - and apply it.
