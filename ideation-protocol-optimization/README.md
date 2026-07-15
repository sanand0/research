# Ideation Protocol Optimization

To test if my [ideation protocol skill](protocols/v1.md) really works, I created an [evaluation](evaluate2.md) and benchmarked it against variations.

I finally ended with a [revised version](protocols/v4.md) that's likely to be more creative, practical, and correct.

## Generate output

I ran this script to create the ideation prompts:

```bash
uv run prompt.py generate.md --protocol protocols/v1.md --task tasks/t1.md
```

... for each version of `--protocol protocols/*.md` across six different `--task tasks/*.md`.

I copy-pasted them into different environments:

- `chatgpt-gpt-5.6-sol-high`
- `claude-sonnet-5-medium`

... and saved the results in `output/${environment}/${protocol_name}_${task_name}.md`. For example: `output/chatgpt-gpt-5.6-sol-high/v1_t1.md`

For second, third, ... attempts, I plan to name them `output/${environment}/${protocol_name}_${task_name}_2.md`, `output/${environment}/${protocol_name}_${task_name}_3.md`, etc.

## Evaluate output

I ran this script:

```bash
uv run prompt.py evaluate.md --task tasks/t1.md --p output/chatgpt-gpt-5.6-sol-high/v1_t1.md --q output/chatgpt-gpt-5.6-sol-high/v2_t1.md
uv run prompt.py evaluate.md --task tasks/t1.md --p output/chatgpt-gpt-5.6-sol-high/v2_t1.md --q output/chatgpt-gpt-5.6-sol-high/v1_t1.md
```

... with each combination of output files per task as `--p` and `--q` (in both orders), copy-pasted and ran it on a smart judge models:

- `chatgpt-gpt-5.6-sol-high`
- `gemini-3.5-flash-thinking`

... and saved as `judge/${judge}/${environment}/${task_name}_${p_version}_${q_version}.json`. For example: `judge/chatgpt-gpt-5.6-sol-high/chatgpt-gpt-5.6-sol-high/t1_v1_v2.json`

Here are evaluations I have so far:

- [Evaluation prompt](evaluate2.md) run with:
  - judge = `chatgpt-gpt-5.6-sol-high`
    - generator = `chatgpt-gpt-5.6-sol-high`
      - prompt = `v1` | `v2`. v2 beats v1
    - prompt = `v2`
      - generator = `chatgpt-gpt-5.6-sol-high` | `claude-sonnet-5-medium`. ChatGPT rated whichever ouput was first as better!
  - judge = `gemini-3.5-flash-thinking`
    - prompt = `v2`
      - generator = `chatgpt-gpt-5.6-sol-high` | `claude-sonnet-5-medium`. ChatGPT (obviously) beats Claude with this model + settings.
    - prompt = `v3`
      - generator = `chatgpt-gpt-5.6-sol-high` | `claude-sonnet-5-medium`. ChatGPT (obviously) beats Claude with this model + settings.
- I also ran an [old evaluation prompt](evaluate.md), which didn't quite evaluate what I wanted, but I ran it with:
  - judge = `chatgpt-gpt-5.6-sol-high`
    - generator = `chatgpt-gpt-5.6-sol-high`
      - prompt = `v0` | `v1`. v1 beats v0
      - prompt = `v1` | `v2`. v2 beats v1
      - prompt = `v2` | `v3`. v3 and v2 are on par. v3 is more practical (and concise), v2 is more creative.

## Results

[Claude conversation discussing results](https://claude.ai/share/1f12542b-6eb3-4b3c-a272-90c82d326b00). But mainly:

- [v1](protocols/v1.md) is better in every respect than [v0](protocols/v0.md).
- [v2](protocols/v2.md) is better in every respect than [v1](protocols/v1.md).
- [v3](protocols/v3.md) is more practical and concise than [v2](protocols/v2.md) but less creative.
- [v4](protocols/v4.md) is an untested synthesis of v2 and v3, that can be practical or creative based on the need.

## Lessons

Here are my takeaways: <!-- https://claude.ai/chat/8e13e695-564c-47f2-8446-747a714d3e89 -->

1. Once you know the rubric, models can easily create a good prompt to optimize for it. So rubric design matters more.
2. ⭐ Rubric design is really knowing what you want/need. To do this, iterating on output matters.
3. Position bias is real. Always check if an (P, Q) comparison matches a (Q, P) comparison.
4. Models are still biased towards longer content, and potentially towards their own output.
5. A 20-word prompt tied the full skill on selection, so most of a protocol's words are scaffolding.
6. Convergence is the weakest step across every version and the likeliest place the next real gain hides.

**Takeaway**: Figure out what you _really_ want, first. Then, ask a smart model for a prompt that optimizes for it. Benchmark if you'll use it a lot.
