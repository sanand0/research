"""Compact Differential Evolution strategy candidates."""

from __future__ import annotations

import numpy as np


def _integers(rng, high: int) -> int:
    return int(rng.integers(high) if hasattr(rng, "integers") else rng.randint(high))


class BalancedAntitheticBest1:
    """Best/1/bin with balanced, sign-paired donor differences per generation.

    Requires SciPy Differential Evolution with ``updating='deferred'`` so every
    candidate in a generation sees the same population. For each adjacent pair
    of targets, the same donor pair is used in opposite order. For even-sized
    populations this makes each population member appear exactly twice as a
    difference-vector donor per generation.
    """

    def __init__(self, mutation=(0.5, 1.0), recombination: float = 0.7) -> None:
        self.mutation = mutation
        self.recombination = float(recombination)
        self._schedule: list[tuple[int, int]] = []
        self._scale = float(np.mean(mutation)) if isinstance(mutation, tuple) else float(mutation)
        self.generations = 0
        self.schedule_fallbacks = 0

    def _new_schedule(self, population_size: int, rng) -> None:
        self.generations += 1
        if isinstance(self.mutation, tuple):
            self._scale = float(rng.uniform(*self.mutation))
        else:
            self._scale = float(self.mutation)

        n_pairs = population_size // 2
        targets = [(2 * k, 2 * k + 1) for k in range(n_pairs)]
        donor_pairs: list[tuple[int, int]] | None = None
        for _ in range(256):
            perm = list(map(int, rng.permutation(population_size)))
            trial = [(perm[2 * k], perm[2 * k + 1]) for k in range(n_pairs)]
            if all(a not in t and b not in t for t, (a, b) in zip(targets, trial, strict=True)):
                donor_pairs = trial
                break
        if donor_pairs is None:
            # Very unlikely for the population sizes used here; keep correctness
            # without making schedule construction part of the scientific claim.
            self.schedule_fallbacks += 1
            donor_pairs = []
            for t0, t1 in targets:
                eligible = [j for j in range(population_size) if j not in (t0, t1)]
                a, b = rng.choice(eligible, size=2, replace=False)
                donor_pairs.append((int(a), int(b)))

        schedule: list[tuple[int, int]] = [(-1, -1)] * population_size
        for (t0, t1), (a, b) in zip(targets, donor_pairs, strict=True):
            schedule[t0] = (a, b)
            schedule[t1] = (b, a)
        if population_size % 2:
            target = population_size - 1
            eligible = [j for j in range(population_size) if j != target]
            a, b = rng.choice(eligible, size=2, replace=False)
            schedule[target] = (int(a), int(b))
        self._schedule = schedule

    def __call__(self, candidate: int, population: np.ndarray, rng=None) -> np.ndarray:
        if rng is None:
            rng = np.random.default_rng()
        if candidate == 0 or len(self._schedule) != len(population):
            self._new_schedule(len(population), rng)
        a, b = self._schedule[candidate]
        donor = population[0] + self._scale * (population[a] - population[b])
        mask = rng.uniform(size=population.shape[1]) < self.recombination
        mask[_integers(rng, population.shape[1])] = True
        return np.where(mask, donor, population[candidate])


def rejection_whitening_transform(steps: np.ndarray, rejected: np.ndarray) -> np.ndarray:
    """Contract directions rejected more often than their proposal frequency predicts.

    Steps are normalized to isolate direction from step length. Proposal whitening
    removes anisotropy DE already gets from its population before rejection
    frequencies are measured. A d-unit identity prior regularizes one generation
    of evidence. The determinant-one normalization changes shape, not global scale.
    """
    steps = np.asarray(steps, dtype=float)
    rejected = np.asarray(rejected, dtype=bool)
    d = steps.shape[1]
    norms = np.linalg.norm(steps, axis=1)
    keep = norms > 1e-14
    steps, rejected, norms = steps[keep], rejected[keep], norms[keep]
    if len(steps) < 2 or rejected.sum() < 2:
        return np.eye(d)
    u = steps / norms[:, None]
    proposal = d * (u.T @ u) / len(u) + 1e-8 * np.eye(d)
    evals, evecs = np.linalg.eigh(proposal)
    whitener = evecs @ np.diag(evals ** -0.5) @ evecs.T
    color = evecs @ np.diag(evals ** 0.5) @ evecs.T
    y = u @ whitener.T
    n_rejected = int(rejected.sum())
    rejection_cov = d * (y[rejected].T @ y[rejected]) / n_rejected
    regularized = (d * np.eye(d) + n_rejected * rejection_cov) / (d + n_rejected)
    revals, revecs = np.linalg.eigh(regularized)
    gains = revals ** -0.5
    gains /= np.exp(np.mean(np.log(gains)))
    correction = revecs @ np.diag(gains) @ revecs.T
    return color @ correction @ whitener


class RejectionWhitenedBest1:
    """Best/1/bin with one-generation active correction from rejected trials."""

    def __init__(
        self,
        dimension: int,
        span: np.ndarray,
        mutation=(0.5, 1.0),
        recombination: float = 0.7,
        active: bool = True,
    ) -> None:
        self.active = bool(active)
        self.dimension = int(dimension)
        self.span = np.asarray(span, dtype=float)
        self.mutation = mutation
        self.recombination = float(recombination)
        self.transform = np.eye(self.dimension)
        self._scale = float(np.mean(mutation)) if isinstance(mutation, tuple) else float(mutation)
        self.pending_parents: list[np.ndarray] = []
        self.generations = 0
        self.last_reject_rate = float("nan")

    def __call__(self, candidate: int, population: np.ndarray, rng=None) -> np.ndarray:
        if rng is None:
            rng = np.random.default_rng()
        if candidate == 0:
            self.generations += 1
            self.pending_parents = []
            self._scale = float(rng.uniform(*self.mutation)) if isinstance(self.mutation, tuple) else float(self.mutation)
        eligible = np.delete(np.arange(len(population)), candidate)
        a, b = rng.choice(eligible, size=2, replace=False)
        difference = self.transform @ (population[int(a)] - population[int(b)])
        donor = population[0] + self._scale * difference
        mask = rng.uniform(size=self.dimension) < self.recombination
        mask[_integers(rng, self.dimension)] = True
        trial = np.where(mask, donor, population[candidate])
        self.pending_parents.append(np.asarray(population[candidate], dtype=float).copy())
        return trial

    def observe_batch(self, trials: np.ndarray, values: np.ndarray, parent_values: np.ndarray) -> None:
        trials = np.asarray(trials, dtype=float)
        values = np.asarray(values, dtype=float)
        parent_values = np.asarray(parent_values, dtype=float)
        parents = np.asarray(self.pending_parents, dtype=float)
        if len(trials) != len(parents):
            raise RuntimeError(f"trial/parent mismatch: {len(trials)} != {len(parents)}")
        rejected = values > parent_values
        self.last_reject_rate = float(rejected.mean())
        if not self.active or rejected.sum() < self.dimension:
            self.transform = np.eye(self.dimension)
            return
        steps = (trials - parents) / self.span
        self.transform = rejection_whitening_transform(steps, rejected)


def run_sequential_best1(
    obj,
    seed: int,
    pop_per_d: int = 2,
    mutation: tuple[float, float] = (0.5, 1.0),
    recombination: float = 0.7,
    active: bool = True,
    abort_fraction: float = 0.25,
) -> dict[str, int]:
    """Immediate best/1/bin with revocable generation-level F dithering.

    Standard mode samples one F per complete population pass. Active mode treats
    that draw as provisional: after a fixed prefix, if no trial has been
    accepted, it abandons the remaining targets and starts a fresh pass with a
    newly sampled F. Evaluated prefix trials still count against the budget.
    """
    from math import ceil
    from scipy.stats import qmc

    d = int(obj.dimension)
    n = max(4, int(pop_per_d * d))
    rng = np.random.default_rng(seed)
    pop = qmc.scale(qmc.Halton(d, scramble=True, seed=seed).random(n), obj.lb, obj.ub)
    vals = np.array([obj(x) for x in pop], dtype=float)
    cutoff = max(2, ceil(n * abort_fraction))
    aborts = 0
    passes = 0

    while obj.nfev < obj.budget:
        passes += 1
        scale = float(rng.uniform(*mutation)) if isinstance(mutation, tuple) else float(mutation)
        accepted = 0
        for i in range(n):
            if obj.nfev >= obj.budget:
                break
            eligible = np.delete(np.arange(n), i)
            a, b = rng.choice(eligible, 2, replace=False)
            best = pop[int(np.argmin(vals))]
            donor = best + scale * (pop[int(a)] - pop[int(b)])
            mask = rng.random(d) < recombination
            mask[rng.integers(d)] = True
            trial = np.where(mask, donor, pop[i]).copy()
            bad = (trial < obj.lb) | (trial > obj.ub)
            if bad.any():
                trial[bad] = rng.uniform(obj.lb[bad], obj.ub[bad])
            parent_y = float(vals[i])
            y = float(obj(trial))
            if y <= parent_y:
                pop[i] = trial
                vals[i] = y
                accepted += 1
            if active and i + 1 == cutoff and accepted == 0:
                aborts += 1
                break

    return {"aborts": aborts, "passes": passes}


class PrefixResampleBest1:
    """Best/1/bin that revokes a generation-level F after a failed prefix.

    Uses only SciPy's public callable-strategy inputs. With immediate updating,
    a successful prior trial changes the population seen by the next strategy
    call. After the first quarter of a generation, if none changed the
    population, a fresh F is sampled for the remaining targets.
    """

    def __init__(
        self,
        mutation: tuple[float, float] = (0.5, 1.0),
        recombination: float = 0.7,
        active: bool = True,
        switch_fraction: float = 0.25,
    ) -> None:
        from math import ceil
        self.mutation = mutation
        self.recombination = float(recombination)
        self.active = bool(active)
        self.switch_fraction = float(switch_fraction)
        self._ceil = ceil
        self._scale = float(np.mean(mutation))
        self._previous_population: np.ndarray | None = None
        self._prefix_successes = 0
        self.resamples = 0
        self.generations = 0

    def _sample_scale(self, rng) -> None:
        self._scale = float(rng.uniform(*self.mutation)) if isinstance(self.mutation, tuple) else float(self.mutation)

    def __call__(self, candidate: int, population: np.ndarray, rng=None) -> np.ndarray:
        if rng is None:
            rng = np.random.default_rng()
        n, d = population.shape
        cutoff = max(2, self._ceil(n * self.switch_fraction))

        if candidate == 0:
            self.generations += 1
            self._prefix_successes = 0
            self._sample_scale(rng)
        elif self._previous_population is not None and not np.array_equal(population, self._previous_population):
            if candidate <= cutoff:
                self._prefix_successes += 1

        if self.active and candidate == cutoff and self._prefix_successes == 0:
            self._sample_scale(rng)
            self.resamples += 1

        eligible = np.delete(np.arange(n), candidate)
        a, b = rng.choice(eligible, size=2, replace=False)
        donor = population[0] + self._scale * (population[int(a)] - population[int(b)])
        mask = rng.uniform(size=d) < self.recombination
        mask[_integers(rng, d)] = True
        trial = np.where(mask, donor, population[candidate])
        self._previous_population = np.asarray(population, dtype=float).copy()
        return trial


def conditioned_halton_population(
    dimension: int,
    lb: np.ndarray,
    ub: np.ndarray,
    seed: int,
    condition_limit: float = 20.0,
    max_per_d: int = 4,
) -> np.ndarray:
    """Shortest Halton prefix with a numerically stable centered design.

    Population size is chosen without objective values. The covariance
    condition number is invariant to a common scalar rescaling, so the check is
    performed in the unit cube before scaling to the user bounds.
    """
    from scipy.stats import qmc

    d = int(dimension)
    nmax = max(d + 1, int(max_per_d * d))
    x = qmc.Halton(d, scramble=True, seed=seed).random(nmax)
    chosen = nmax
    for n in range(max(5, d + 1), nmax + 1):
        z = x[:n] - x[:n].mean(axis=0)
        singular = np.linalg.svd(z, compute_uv=False)
        if singular[-1] <= 1e-14:
            continue
        covariance_condition = float((singular[0] / singular[-1]) ** 2)
        if covariance_condition <= condition_limit:
            chosen = n
            break
    return qmc.scale(x[:chosen], np.asarray(lb, float), np.asarray(ub, float))
