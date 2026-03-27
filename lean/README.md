# CreativeMathlib

This is a tiny Lean 4 project built with Lake's `math` template, so it uses
[`mathlib`](https://github.com/leanprover-community/mathlib4).

The main example lives in `CreativeMathlib/Basic.lean`. It proves a classic
visual identity:

`1 + 3 + 5 + ... + (2n - 1) = n^2`

In Lean, the theorem is stated as:

```lean
theorem sum_first_odds_eq_square (n : ℕ) :
    (Finset.range n).sum (fun i => 2 * i + 1) = n ^ 2
```

The proof uses:

- `Finset.range` and finite sums from mathlib
- induction on `n`
- `nlinarith` to close the arithmetic step cleanly

## Verify it

From this directory, run:

```bash
lake build
```

The first build may take a while because Lake fetches mathlib dependencies and
their build cache.

If you want to inspect just the theorem file, open:

```text
CreativeMathlib/Basic.lean
```
