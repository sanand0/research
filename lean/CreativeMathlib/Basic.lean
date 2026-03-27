import Mathlib

/-- The staircase of odd numbers `1 + 3 + 5 + ...` lands exactly on perfect squares. -/
theorem sum_first_odds_eq_square (n : ℕ) :
    (Finset.range n).sum (fun i => 2 * i + 1) = n ^ 2 := by
  induction n with
  | zero =>
      simp
  | succ n ih =>
      calc
        (Finset.range (n + 1)).sum (fun i => 2 * i + 1)
            = (Finset.range n).sum (fun i => 2 * i + 1) + (2 * n + 1) := by
                rw [Finset.sum_range_succ]
        _ = n ^ 2 + (2 * n + 1) := by rw [ih]
        _ = (n + 1) ^ 2 := by
              nlinarith
