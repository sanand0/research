# Experiment design

I asked Claude and ChatGPT how to design an experiment to test: "Does telling AI agents to write in simple language worsen their thinking quality?"

<!-- https://chatgpt.com/c/6a6d770d-9d68-83ec-b544-84a7aa1ecdc6 + https://claude.ai/chat/7788dcc8-dd41-4605-843b-7c418d675b8a -->

Here is the prompt I added to tell agents to write in simple language:

> Answer in ASD-STE100

I tested these tasks on ChatGPT with GPT 5.6 Sol:

1. [Model benchmarking](question/1.md)
2. [Causal diagnosis](question/1.md)
3. [Decision under uncertainty](question/1.md)
4. [Experimental design](question/1.md)
5. [Evidence and judgment](question/1.md)
6. [Adversarial system design](question/1.md)

The results, without (-) and with (+) the simplified language prompts, are below:

- Task 1 - prompt: [result-1a.md](result-1a.md): 66 sources, 1m 31s
- Task 1 + prompt: [result-1b.md](result-1b.md): 44 sources, 41s
- Task 2 - prompt: [result-2a.md](result-2a.md)
- Task 2 + prompt: [result-2b.md](result-2b.md)
- Task 3 - prompt: [result-3a.md](result-3a.md)
- Task 3 + prompt: [result-3b.md](result-3b.md)
- Task 4 - prompt: [result-4a.md](result-4a.md)
- Task 4 + prompt: [result-4b.md](result-4b.md)
- Task 5 - prompt: [result-5a.md](result-5a.md): 123 sources, 2m 4s
- Task 5 + prompt: [result-5b.md](result-5b.md): 84 sources, 5m 4s
- Task 6 - prompt: [result-6a.md](result-6a.md): 97 sources, 2m 20s
- Task 6 + prompt: [result-6b.md](result-6b.md): 26 sources, 3m 44s, wrote code

I used this [rubric](rubric.md) on ChatGPT with GPT 5.6 Sol to compare each pair twice - in both orders (A, B) and (B, A) - to reduce position bias.

Here are the results. 🟢 = Simple prompt won. 🟡 = Tie. 🔴 = Without simple prompt won.

| Task | Order | Winner | Correctness | Key drivers | Mechanism | Caveats | Calibration | Actionability | Eval                 |
| ---: | ----- | :----: | :---------: | :---------: | :-------: | :-----: | :---------: | :-----------: | -------------------- |
|    1 | A, B  |   🔴   |     🔴      |     🔴      |    🔴     |   🔴    |     🔴      |      🔴       | [Eval](evals/1ab.md) |
|    1 | B, A  |   🔴   |     🔴      |     🔴      |    🔴     |   🔴    |     🔴      |      🔴       | [Eval](evals/1ba.md) |
|    2 | A, B  |   🔴   |     🔴      |     🔴      |    🔴     |   🔴    |     🔴      |      🔴       | [Eval](evals/2ab.md) |
|    2 | B, A  |   🔴   |     🟡      |     🔴      |    🔴     |   🔴    |     🔴      |      🔴       | [Eval](evals/2ba.md) |
|    3 | A, B  |   🔴   |     🟡      |     🔴      |    🔴     |   🔴    |     🔴      |      🔴       | [Eval](evals/3ab.md) |
|    3 | B, A  |   🔴   |     🟡      |     🔴      |    🔴     |   🔴    |     🔴      |      🔴       | [Eval](evals/3ba.md) |
|    4 | A, B  |   🔴   |     🔴      |     🔴      |    🔴     |   🔴    |     🔴      |      🔴       | [Eval](evals/4ab.md) |
|    4 | B, A  |   🔴   |     🟢      |     🔴      |    🔴     |   🔴    |     🟡      |      🔴       | [Eval](evals/4ba.md) |
|    5 | A, B  |   🔴   |     🔴      |     🔴      |    🟡     |   🔴    |     🔴      |      🔴       | [Eval](evals/5ab.md) |
|    5 | B, A  |   🔴   |     🔴      |     🔴      |    🔴     |   🔴    |     🟢      |      🔴       | [Eval](evals/5ba.md) |
|    6 | A, B  |   🔴   |     🔴      |     🔴      |    🔴     |   🔴    |     🔴      |      🔴       | [Eval](evals/6ab.md) |
|    6 | B, A  |   🔴   |     🔴      |     🔴      |    🔴     |   🔴    |     🔴      |      🔴       | [Eval](evals/6ba.md) |

In short, asking a model to "Answer in ASD-STE100" consistently reduces its thinking quality.
