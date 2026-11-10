# Prompts

## Initial Research, 10 Nov 2026

<!-- Claude Codex Set Usage Limits: https://chatgpt.com/c/6af27d4b-c36c-83ec-9007-ed5d8fd7a655 (2026-11-10T13:01:21+08:00) -->

I think it should be possible to set up codex as well as Claude Code in a way that they will stop running a session if the usage or number of tokens exceeds a specific amount. For example, I might be able to say, execute this prompt in this directory, making sure that it does not consume more than 2% of my five-hour limit or 100,000 tokens or the equivalent of 10 cents in API cost, factoring in the cached costs as well. Are any these possible? Or are there better ways? Can you check if the use of hooks or plugins or whatever is the simplest mechanism to achieve this will allow me to do the job? You may test this on @LocalMCP2 if possible, keeping the consumption really low and only using Luna and Haiku models. Use relevant skills.

---

How much usage does Claude Code's --max-budget-usd 0.10 consume from the 5-hour limit and the 7-day limit? You might be able to answer this from your earlier calculation. If not, feel free to run another experiment with enough granularity to get as good a result as you can without consuming more than 5% of my 5-hour limit (and ideally a lot less than that if you can get good accuracy).

Ultimately, I want to know: 1% of my Claude Code 5-hour limit = how many dollars, for a typical query, and what cache and input/output mix?

---

Based on this, what's your assessment of the total value of the twenty-dollar plan that I have in terms of API cost? I mean for this twenty dollars, how many dollars of API cost am I actually able to spend approximately? I know this varies a lot, but give me the range and, for different scenarios. Keep in mind that Graphene is no longer available

---

Can I disable cache writes in Claude Code and will that save cost for single one-off requests?

Can I use Claude Code with a lighter harness like Pi as of today, consuming from the subscription rather than paid credits?

---

@LocalMCP2 is now available. I installed pi-claude-subscription. Check if it works, and how much fewer tokens and % of 5-h limit it consumes vs Claude Code with caching disabled vs Claude Code without caching disabled on the same task (you pick the task).

I'm planning to ask students to submit prompts for a one-off exercise, e.g. create a single-page HTML to render an impressive animation, which is budget constrained (e.g. 3 cents) and want to see if I should use Claude Code with caching disabled, or enabled, or Pi with pi-claude-subscription. If it should be the last, also see how I can run it with a budget limit enabled.

I'm OK with you consuming up to 25% of my 5 hour limit - but try and consume as little as you can while still running a robust set of experiments. Think carefully, use relevant skills, pilot before scaling if required.

---

Move this to ~/code/research/claude-pi-tokens/ and document it, including a README.md (ASD-STE100). Make sure it's perfectly clear to a first-time reader what we found and how. Update ~/code/research/README.md and commit but do not push.

---

Compress the PNGs to WebP maximally to compress space, update required files, and amend the earlier commit - and also commit the prompts.md I added.
