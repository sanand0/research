#!/usr/bin/env python3
"""
Polya Heuristics Effectiveness Experiment
==========================================
Empirically measures which Polya "How to Solve It" heuristics work best
across math problem categories (MATH benchmark dataset).

Produces a heuristic × category success-rate matrix.

Usage:
  python3 polya_experiment.py sample  [--n-per-level N] [--seed S]
  python3 polya_experiment.py run     [--models M ...] [--heuristics H ...] \
                                      [--categories C ...] [--levels L ...] \
                                      [--n N] [--workers W]
  python3 polya_experiment.py analyze [--min-samples M]
"""

import argparse
import hashlib
import json
import os

# Load .env from home dir or project dir if present (for API keys)
for _env_path in [os.path.expanduser("~/.env"), os.path.join(os.path.dirname(__file__), ".env")]:
    if os.path.exists(_env_path):
        with open(_env_path) as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _, _v = _line.partition("=")
                    os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
import os
import re
import sqlite3
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from threading import local

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "polya_results"
PROBLEMS_FILE = RESULTS_DIR / "problems.json"
RESULTS_DB = RESULTS_DIR / "results.db"
LOGS_DIR = RESULTS_DIR / "logs"
HEURISTICS_FILE = BASE_DIR / "polya_heuristics.json"

ALL_CATEGORIES = [
    "algebra", "counting_and_probability", "geometry",
    "intermediate_algebra", "number_theory", "prealgebra", "precalculus",
]
# Map from CLI shorthand → HF dataset config name
CATEGORY_MAP = {
    "algebra": "algebra",
    "counting": "counting_and_probability",
    "counting_and_probability": "counting_and_probability",
    "geometry": "geometry",
    "intermediate_algebra": "intermediate_algebra",
    "number_theory": "number_theory",
    "prealgebra": "prealgebra",
    "precalculus": "precalculus",
}

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
_thread_local = local()

def get_db():
    """Return a thread-local SQLite connection."""
    if not hasattr(_thread_local, "conn"):
        _thread_local.conn = sqlite3.connect(str(RESULTS_DB), check_same_thread=False)
        _thread_local.conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id           TEXT PRIMARY KEY,
                problem_id   TEXT NOT NULL,
                category     TEXT NOT NULL,
                level        INTEGER NOT NULL,
                heuristic_id TEXT NOT NULL,
                trial        INTEGER NOT NULL,
                model        TEXT NOT NULL,
                input_tokens INTEGER,
                output_tokens INTEGER,
                elapsed_s    REAL,
                llm_output   TEXT,
                predicted    TEXT,
                gold         TEXT,
                correct      INTEGER,
                created_at   TEXT DEFAULT (datetime('now'))
            )
        """)
        _thread_local.conn.commit()
    return _thread_local.conn


def make_run_id(problem_id: str, heuristic_id: str, trial: int, model: str) -> str:
    key = f"{problem_id}|{heuristic_id}|{trial}|{model}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def already_done(problem_id: str, heuristic_id: str, trial: int, model: str) -> bool:
    run_id = make_run_id(problem_id, heuristic_id, trial, model)
    conn = get_db()
    row = conn.execute("SELECT id FROM results WHERE id=?", (run_id,)).fetchone()
    return row is not None

# ---------------------------------------------------------------------------
# Answer extraction & evaluation
# ---------------------------------------------------------------------------
def extract_boxed(text: str) -> str | None:
    """Extract the content of the last \\boxed{...} in text, handling nesting."""
    idx = text.rfind(r"\boxed{")
    if idx == -1:
        idx = text.rfind(r"\boxed {")
    if idx == -1:
        return None
    start = text.find("{", idx)
    if start == -1:
        return None
    depth, i = 0, start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i]
        i += 1
    return None


def normalize(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("\\,", " ").replace("\\!", "").replace("\\;", " ")
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\left|\\right", "", s)
    s = s.replace("$", "").strip()
    return s


def is_correct(predicted: str | None, gold: str) -> bool:
    if predicted is None:
        return False
    p = normalize(predicted)
    g = normalize(gold)
    if p == g:
        return True
    # Try float comparison
    try:
        return abs(float(p) - float(g)) < 1e-6
    except ValueError:
        pass
    # Try sympy comparison
    try:
        from sympy import simplify
        from sympy.parsing.latex import parse_latex
        expr_p = parse_latex(p)
        expr_g = parse_latex(g)
        return bool(simplify(expr_p - expr_g) == 0)
    except Exception:
        pass
    return False

# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------
def call_llm(model: str, system_prompt: str, user_message: str,
             timeout: int = 120, max_retries: int = 3) -> dict:
    """Call LLM via CLI with retry on rate limits. Returns dict with output, tokens, elapsed_s."""
    cmd = [
        "llm", "--model", model,
        "--system", system_prompt,
        "--usage",
        user_message,
    ]
    for attempt in range(max_retries):
        start = time.time()
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            elapsed = time.time() - start

            # Check for rate limit or quota errors in stderr
            stderr = result.stderr.strip()
            # Note: stderr may contain normal token usage lines even on success
            is_rate_limited = (result.returncode != 0 and
                               ("quota" in stderr.lower() or "rate" in stderr.lower()
                                or "429" in stderr))
            is_error = result.returncode != 0 and not is_rate_limited

            if is_rate_limited:
                wait = 30 * (attempt + 1)
                print(f"  [rate-limit attempt {attempt+1}] waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            if is_error:
                return {
                    "output": "", "input_tokens": None, "output_tokens": None,
                    "elapsed_s": elapsed, "error": True, "stderr": stderr[:200],
                }

            raw = result.stdout.strip()
            if not raw:
                # Empty output with no error — skip storing (let it retry on next run)
                return {
                    "output": "", "input_tokens": None, "output_tokens": None,
                    "elapsed_s": elapsed, "error": True, "stderr": "empty output",
                }

            # Parse token usage from stderr: "Token usage: N input, M output"
            input_tokens, output_tokens = None, None
            usage_match = re.search(r"Token usage:\s*(\d+) input,\s*(\d+) output",
                                    result.stderr)
            if usage_match:
                input_tokens = int(usage_match.group(1))
                output_tokens = int(usage_match.group(2))

            return {
                "output": raw,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "elapsed_s": elapsed,
                "error": False,
            }
        except subprocess.TimeoutExpired:
            return {
                "output": "", "input_tokens": None, "output_tokens": None,
                "elapsed_s": timeout, "error": True, "stderr": "timeout",
            }
        except Exception as e:
            return {
                "output": "", "input_tokens": None, "output_tokens": None,
                "elapsed_s": time.time() - start, "error": True, "stderr": str(e),
            }
    return {"output": "", "input_tokens": None, "output_tokens": None,
            "elapsed_s": 0, "error": True, "stderr": "max retries exceeded"}

# ---------------------------------------------------------------------------
# Problem format
# ---------------------------------------------------------------------------
USER_PROMPT_TEMPLATE = """\
IMPORTANT: You MUST end your response with your final answer enclosed in a LaTeX box: \\boxed{{answer}}

Solve the following math problem. Show your reasoning step by step.

Problem: {problem}

Remember: Your last line MUST be \\boxed{{your_final_answer}}"""


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------
def cmd_sample(args):
    """Download and cache problems from MATH dataset."""
    from datasets import load_dataset

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    import random
    random.seed(args.seed)

    problems = []
    for cat in ALL_CATEGORIES:
        print(f"Loading {cat}...")
        try:
            ds = load_dataset("EleutherAI/hendrycks_math", cat,
                              split="test", trust_remote_code=True)
        except Exception as e:
            print(f"  SKIP {cat}: {e}")
            continue

        # Group by level
        by_level = {}
        for ex in ds:
            lvl = int(re.search(r"Level (\d)", ex["level"]).group(1))
            by_level.setdefault(lvl, []).append(ex)

        for level in sorted(by_level):
            pool = by_level[level]
            random.shuffle(pool)
            n = min(args.n_per_level, len(pool))
            for ex in pool[:n]:
                # Extract gold answer from solution
                gold = extract_boxed(ex["solution"]) or ex["solution"][:100]
                problems.append({
                    "id": f"{cat}_L{level}_{hashlib.sha256(ex['problem'].encode()).hexdigest()[:8]}",
                    "category": cat,
                    "level": level,
                    "problem": ex["problem"],
                    "solution": ex["solution"],
                    "gold": gold,
                })
        print(f"  Collected {sum(1 for p in problems if p['category']==cat)} problems for {cat}")

    with open(PROBLEMS_FILE, "w") as f:
        json.dump(problems, f, indent=2)
    print(f"\nSaved {len(problems)} problems to {PROBLEMS_FILE}")

    # Summary
    from collections import Counter
    by_cat_level = Counter((p["category"], p["level"]) for p in problems)
    for (cat, level), count in sorted(by_cat_level.items()):
        print(f"  {cat:35s} L{level}: {count}")


# ---------------------------------------------------------------------------
# Run experiment
# ---------------------------------------------------------------------------
def load_problems(categories, levels, limit_per_cell=None):
    """Load filtered problems from problems file."""
    with open(PROBLEMS_FILE) as f:
        all_problems = json.load(f)

    result = []
    from collections import Counter
    cell_counts = Counter()

    for p in all_problems:
        cat = p["category"]
        # Map short names
        if cat not in categories and cat.split("_")[0] not in categories:
            skip = True
            for c in categories:
                if c == "all" or c in cat or cat in c:
                    skip = False
                    break
            if skip:
                continue
        if p["level"] not in levels:
            continue
        cell = (p["category"], p["level"])
        if limit_per_cell and cell_counts[cell] >= limit_per_cell:
            continue
        cell_counts[cell] += 1
        result.append(p)

    return result


def run_single(problem, heuristic, trial, model, heuristics_map, log_path):
    """Run one LLM call, store result in DB, log to JSONL.
    Returns None if skipped (already done) or on error (allows retry on next run).
    """
    run_id = make_run_id(problem["id"], heuristic["id"], trial, model)

    # Skip if already done (resumable)
    conn = get_db()
    if conn.execute("SELECT 1 FROM results WHERE id=?", (run_id,)).fetchone():
        return None  # already exists

    system_prompt = heuristic["prompt"]
    user_message = USER_PROMPT_TEMPLATE.format(problem=problem["problem"])

    resp = call_llm(model, system_prompt, user_message)

    # Don't store empty/error results — let them be retried on next run
    if resp["error"] or not resp["output"]:
        return {"_error": True, "problem_id": problem["id"], "model": model,
                "heuristic_id": heuristic["id"], "stderr": resp.get("stderr", "")}

    predicted = extract_boxed(resp["output"])
    correct = int(is_correct(predicted, problem["gold"]))

    row = {
        "id": run_id,
        "problem_id": problem["id"],
        "category": problem["category"],
        "level": problem["level"],
        "heuristic_id": heuristic["id"],
        "trial": trial,
        "model": model,
        "input_tokens": resp["input_tokens"],
        "output_tokens": resp["output_tokens"],
        "elapsed_s": round(resp["elapsed_s"], 2),
        "llm_output": resp["output"][:4000],  # cap storage
        "predicted": predicted,
        "gold": problem["gold"],
        "correct": correct,
    }

    conn.execute("""
        INSERT OR IGNORE INTO results
        (id, problem_id, category, level, heuristic_id, trial, model,
         input_tokens, output_tokens, elapsed_s, llm_output, predicted, gold, correct)
        VALUES (:id,:problem_id,:category,:level,:heuristic_id,:trial,:model,
                :input_tokens,:output_tokens,:elapsed_s,:llm_output,:predicted,:gold,:correct)
    """, row)
    conn.commit()

    # Append to JSONL log
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        json.dump(row, f)
        f.write("\n")

    return row


def cmd_run(args):
    """Run the experiment."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if not PROBLEMS_FILE.exists():
        print(f"ERROR: {PROBLEMS_FILE} not found. Run 'sample' first.")
        sys.exit(1)

    if not HEURISTICS_FILE.exists():
        print(f"ERROR: {HEURISTICS_FILE} not found.")
        sys.exit(1)

    with open(HEURISTICS_FILE) as f:
        all_heuristics = json.load(f)
    heuristics_map = {h["id"]: h for h in all_heuristics}

    # Filter heuristics
    if "all" in args.heuristics:
        heuristics = all_heuristics
    else:
        heuristics = [heuristics_map[h] for h in args.heuristics if h in heuristics_map]
        missing = [h for h in args.heuristics if h not in heuristics_map]
        if missing:
            print(f"WARNING: Unknown heuristics: {missing}")

    # Filter categories
    categories = args.categories if "all" not in args.categories else ALL_CATEGORIES

    # Filter levels
    levels = [int(l) for l in args.levels]

    # Load problems
    problems = load_problems(categories, levels, limit_per_cell=args.n_per_cell)
    print(f"Problems: {len(problems)}, Heuristics: {len(heuristics)}, "
          f"Trials: {args.n}, Models: {args.models}")

    # Build task list
    tasks = []
    for model in args.models:
        for problem in problems:
            for heuristic in heuristics:
                for trial in range(args.n):
                    run_id = make_run_id(problem["id"], heuristic["id"], trial, model)
                    tasks.append((problem, heuristic, trial, model, run_id))

    # Check which are already done
    conn = get_db()
    done_ids = set(
        row[0] for row in conn.execute("SELECT id FROM results").fetchall()
    )
    pending = [t for t in tasks if t[4] not in done_ids]

    total = len(tasks)
    already = total - len(pending)
    print(f"Total tasks: {total}  |  Already done: {already}  |  Pending: {len(pending)}")

    if not pending:
        print("Nothing to do!")
        return

    log_path = LOGS_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    saved = 0
    errors = 0
    start_time = time.time()

    def do_task(task):
        if getattr(args, 'delay', 0) > 0:
            time.sleep(args.delay)
        problem, heuristic, trial, model, _ = task
        return run_single(problem, heuristic, trial, model, heuristics_map, log_path)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(do_task, t): t for t in pending}
        done_count = already
        for fut in as_completed(futures):
            done_count += 1
            result = fut.result()
            if result and not result.get("_error"):
                saved += 1
                status = "✓" if result["correct"] else "✗"
                elapsed_total = time.time() - start_time
                rate = saved / elapsed_total if elapsed_total > 0 else 0
                remaining = len(pending) - saved - errors
                eta = remaining / rate if rate > 0 else 0
                print(
                    f"[{done_count}/{total}] {status} "
                    f"{result['model'][:20]} | {result['category'][:12]} "
                    f"L{result['level']} | {result['heuristic_id'][:15]} "
                    f"| pred={str(result['predicted'])[:10]} gold={str(result['gold'])[:10]}"
                    f" | {result['elapsed_s']:.1f}s | ETA {eta:.0f}s",
                    flush=True
                )
            elif result and result.get("_error"):
                errors += 1
                print(f"[{done_count}/{total}] ERROR {result['model'][:20]} "
                      f"{result['problem_id']} {result.get('stderr','')[:60]}", flush=True)

    print(f"\nDone. Saved: {saved}, Errors: {errors}, Already done: {already}. Log: {log_path}")
    cmd_analyze(args)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
def cmd_analyze(args):
    """Print success-rate heatmap to terminal."""
    if not RESULTS_DB.exists():
        print("No results yet.")
        return

    conn = sqlite3.connect(str(RESULTS_DB))

    print("\n" + "="*80)
    print("POLYA HEURISTICS EFFECTIVENESS MATRIX")
    print("="*80)

    # Overall stats
    total, correct = conn.execute(
        "SELECT COUNT(*), SUM(correct) FROM results"
    ).fetchone()
    print(f"Total runs: {total}  |  Overall accuracy: {correct/total*100:.1f}%\n")

    # Per model
    for (model,) in conn.execute("SELECT DISTINCT model FROM results ORDER BY model"):
        print(f"\nModel: {model}")
        print("-" * 60)

        # Get heuristics present in data
        heuristics = [r[0] for r in conn.execute(
            "SELECT DISTINCT heuristic_id FROM results WHERE model=? ORDER BY heuristic_id",
            (model,)
        ).fetchall()]

        # Get categories present
        categories = [r[0] for r in conn.execute(
            "SELECT DISTINCT category FROM results WHERE model=? ORDER BY category",
            (model,)
        ).fetchall()]

        if not heuristics or not categories:
            continue

        # Build matrix
        col_w = 10
        header = f"{'category':25s}" + "".join(f"{h[:col_w]:>{col_w}}" for h in heuristics)
        print(header)
        print("-" * len(header))

        for cat in categories:
            row_vals = []
            for h in heuristics:
                n, c = conn.execute(
                    "SELECT COUNT(*), SUM(correct) FROM results "
                    "WHERE model=? AND category=? AND heuristic_id=?",
                    (model, cat, h)
                ).fetchone()
                if n and n >= getattr(args, 'min_samples', 1):
                    pct = c / n * 100
                    row_vals.append(f"{pct:.0f}%")
                else:
                    row_vals.append("  -")
            print(f"{cat[:25]:25s}" + "".join(f"{v:>{col_w}}" for v in row_vals))

        # By level
        print(f"\n  By difficulty level:")
        for (lvl,) in conn.execute(
            "SELECT DISTINCT level FROM results WHERE model=? ORDER BY level", (model,)
        ).fetchall():
            n, c = conn.execute(
                "SELECT COUNT(*), SUM(correct) FROM results WHERE model=? AND level=?",
                (model, lvl)
            ).fetchone()
            print(f"    Level {lvl}: {c}/{n} = {c/n*100:.1f}%")

    # Top surprises: heuristics that beat baseline by most
    print("\n" + "="*80)
    print("TOP SURPRISES (heuristic vs baseline, per category)")
    print("="*80)
    try:
        rows = conn.execute("""
            WITH base AS (
                SELECT model, category, 1.0*SUM(correct)/COUNT(*) AS base_rate
                FROM results WHERE heuristic_id='baseline'
                GROUP BY model, category
            ),
            heur AS (
                SELECT model, category, heuristic_id, 1.0*SUM(correct)/COUNT(*) AS rate
                FROM results WHERE heuristic_id != 'baseline'
                GROUP BY model, category, heuristic_id
                HAVING COUNT(*) >= 3
            )
            SELECT h.model, h.category, h.heuristic_id,
                   ROUND(h.rate*100,1) AS heur_pct,
                   ROUND(b.base_rate*100,1) AS base_pct,
                   ROUND((h.rate - b.base_rate)*100,1) AS delta
            FROM heur h JOIN base b USING (model, category)
            ORDER BY delta DESC
            LIMIT 15
        """).fetchall()
        print(f"{'Model':20} {'Category':20} {'Heuristic':20} {'Heur%':>6} {'Base%':>6} {'Delta':>6}")
        print("-" * 80)
        for row in rows:
            print(f"{row[0][:20]:20} {row[1][:20]:20} {row[2][:20]:20} "
                  f"{row[3]:>6} {row[4]:>6} {row[5]:>+6}")
    except Exception as e:
        print(f"(surprises query failed: {e})")

    conn.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Polya Heuristics Effectiveness Experiment")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # --- sample ---
    p_sample = sub.add_parser("sample", help="Sample problems from MATH dataset")
    p_sample.add_argument("--n-per-level", type=int, default=50,
                          help="Max problems per category×level (default 50)")
    p_sample.add_argument("--seed", type=int, default=42, help="Random seed")

    # --- run ---
    p_run = sub.add_parser("run", help="Run experiment")
    p_run.add_argument("--models", nargs="+",
                       default=["gpt-5.4-nano"],
                       help="LLM model IDs (space-separated)")
    p_run.add_argument("--heuristics", nargs="+", default=["all"],
                       help="Heuristic IDs or 'all'")
    p_run.add_argument("--categories", nargs="+", default=["all"],
                       help="Category names or 'all'")
    p_run.add_argument("--levels", nargs="+", default=["3", "4", "5"],
                       help="Difficulty levels (1-5)")
    p_run.add_argument("--n", type=int, default=1, help="Trials per problem (default 1)")
    p_run.add_argument("--n-per-cell", type=int, default=None,
                       help="Max problems per category×level (None=all)")
    p_run.add_argument("--workers", type=int, default=8, help="Parallel workers")
    p_run.add_argument("--delay", type=float, default=0,
                       help="Seconds to sleep between calls per worker (for rate limiting)")
    p_run.add_argument("--min-samples", type=int, default=1,
                       help="Min samples to show in heatmap")

    # --- analyze ---
    p_analyze = sub.add_parser("analyze", help="Print heatmap from existing results")
    p_analyze.add_argument("--min-samples", type=int, default=3)

    args = parser.parse_args()

    if args.cmd == "sample":
        cmd_sample(args)
    elif args.cmd == "run":
        cmd_run(args)
    elif args.cmd == "analyze":
        cmd_analyze(args)


if __name__ == "__main__":
    main()
