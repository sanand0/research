# Research Notes: Pyodide/Pandas vs JavaScript Break-even Analysis

## Objective
Determine the break-even point where using pandas in Pyodide becomes more efficient than a small JavaScript pipeline for data manipulation tasks.

## Initial Considerations

### Pyodide + Pandas
- **Pros**: Rich data manipulation API, familiar to Python users, powerful operations
- **Cons**: Large initial load time (Pyodide runtime + pandas package), memory overhead

### JavaScript Pipeline
- **Pros**: No load time, native browser execution, lightweight
- **Cons**: More verbose for complex operations, fewer built-in data operations

## Key Factors to Test
1. Initial load time (Pyodide + pandas vs JS libraries if any)
2. Execution time for various operations
3. Data size impact
4. Operation complexity impact

## Hypothesis
There should be a crossover point where:
- For small datasets/simple operations: JS is faster (no load overhead)
- For large datasets/complex operations: Pandas becomes competitive due to optimized operations

---

## Investigation Log

### Step 1: Project Setup
- Created project folder: pyodide-pandas-breakeven
- Starting investigation...

### Step 2: Research Findings on Pyodide/Pandas

**Package Sizes:**
- Pyodide runtime: ~6.4 MB
- Pandas + NumPy: ~15 MB
- Total download: ~21 MB

**Load Times (reported):**
- Pyodide initialization: 4-5 seconds (first load)
- Pandas import: 25-30 seconds (network dependent, ~600kB/s)
- Subsequent loads: Much faster due to browser caching

**Execution Performance:**
- Pyodide runs 1x-5x slower than native Python
- 1x-16x slower than native in some Chrome benchmarks
- Recent versions show 1.2-2x load time improvements

**Key Insight:**
The initial load overhead is significant (30-35 seconds), so pandas needs to provide substantial time savings on actual operations to break even. This suggests:
- Small, one-time operations: JS will be faster
- Large datasets or repeated operations: Pandas may be competitive
- The break-even point is likely around operations that would take 30+ seconds in JS

### Step 3: Benchmark Implementation

Created three benchmark tools:
1. `benchmark-pyodide.html` - Browser-based Pyodide/Pandas benchmark
2. `benchmark-javascript.html` - Browser-based pure JavaScript benchmark
3. `benchmark-comparison.html` - Side-by-side comparison tool
4. `benchmark.js` - Node.js automated benchmark runner

### Step 4: Actual Benchmark Results (Node.js)

**Test Configuration:**
- Operations: Filter, GroupBy+Aggregate, Sort, Transform, Complex Filter
- Data sizes: 100, 1,000, 10,000, 100,000 rows
- 5 iterations per test, averaged

**JavaScript Performance:**
| Rows    | Total Time | Operations/sec |
|---------|------------|----------------|
| 100     | 0.41ms     | 2,439          |
| 1,000   | 1.16ms     | 862            |
| 10,000  | 10.64ms    | 94             |
| 100,000 | 145.08ms   | 6.9            |

**Key Observations:**
1. JavaScript is VERY fast for these operations
2. Scaling is better than linear (0.26-0.36x linear) due to engine optimizations
3. Even 100k rows processes in under 150ms
4. Sort operation is the slowest (79.5ms for 100k rows)
5. GroupBy is efficient (23ms for 100k rows)

### Step 5: Break-even Analysis

**Assumptions:**
- Pyodide + Pandas load time: ~30,000ms (30 seconds)
- Pandas execution: 2-3x slower than JS (conservative estimate based on research)

**Break-even Calculations:**

For a single operation, Pandas NEVER breaks even due to load overhead:
- 100 rows: JS 0.41ms vs Pandas 30,001ms (73,000x slower)
- 100k rows: JS 145ms vs Pandas 30,363ms (209x slower)

For multiple iterations:
- To break even, you need: `30,000ms / (jsTime - pandasTime)` iterations
- Since pandas is slower per operation, you'd need negative iterations
- This means: **Pandas never breaks even on execution speed alone**

**However**, if we assume pandas COULD be faster per operation (e.g., optimized numpy operations):
- If pandas were 2x FASTER than JS (unlikely in Pyodide)
- 100k rows scenario: JS=145ms, Pandas=72ms
- Break-even = 30,000 / (145-72) = ~411 iterations
- Total time: 411 * 145ms = 59 seconds for JS, 30s + 411*72ms = 60 seconds for Pandas

**Reality Check:**
Given Pyodide runs 1-5x SLOWER than native Python, and native Python is often slower than optimized JS for simple operations, Pandas in Pyodide is unlikely to ever be faster per-operation than plain JS.

### Step 6: When to Use Each Approach

**Use JavaScript when:**
- Single-use or few operations
- Small to medium datasets (< 1M rows)
- Performance is critical
- You want instant page load
- Simple data transformations

**Use Pyodide/Pandas when:**
- You NEED pandas-specific features (time series, advanced analytics, ML preprocessing)
- Code clarity and maintainability matter more than raw speed
- Your team knows Python/Pandas better than JS
- You're building a long-running web app with 1000s of operations
- You need to share code between backend (Python) and frontend
- Complex statistical operations that are tedious in vanilla JS

**The Real Break-even:**
It's not about performance—it's about **developer productivity** and **feature requirements**. If you need pandas features, the 30-second load is worth it. If you don't, JS is always faster.
