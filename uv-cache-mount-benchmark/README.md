# UV Cache Mount Strategy Benchmark

## Executive Summary

This research quantifies the wall-clock time and storage savings from different `uv` cache mount strategies. Testing was conducted with a realistic Python dependency set (pandas, numpy, fastapi, scikit-learn, etc.) totaling ~310 MB.

### Key Results

| Strategy | Cold Cache | Warm Cache | Time Saved | Savings % | Cache Size |
|----------|-----------|-----------|-----------|-----------|-----------|
| No Cache (baseline) | 11.58s | 11.37s | 0s | 0% | 0 MB |
| Persistent Cache | 11.56s | **1.72s** | **9.84s** | **85.1%** | 310 MB |
| Shared Cache | 11.34s | **1.69s** | **9.66s** | **85.1%** | 310 MB |

**Bottom line**: Cache mount strategies save **~85% of installation time** on subsequent builds, at the cost of **~310 MB** of cache storage for this dependency set.

---

## Methodology

### Environment
- Platform: Linux container
- Python: 3.x with uv package manager
- Test dependencies: 8 packages (pandas, numpy, requests, fastapi, scikit-learn, pillow, sqlalchemy, pydantic)

### Strategies Tested

1. **No Cache (Baseline)**
   - Cache cleared before every installation
   - Simulates Docker builds without cache mounts
   - Every run downloads all packages fresh

2. **Persistent Cache (BuildKit-style)**
   - Cache preserved between runs
   - Simulates `docker buildx build --mount=type=cache,target=/root/.cache/uv`
   - First run populates cache, subsequent runs reuse it

3. **Shared Cache (Volume/Bind Mount)**
   - Cache directory persisted across builds
   - Simulates Docker volume mount or bind mount (`-v ./cache:/root/.cache/uv`)
   - First run populates cache, subsequent runs reuse it

### Metrics Collected
- **Wall-clock time**: Total installation duration (seconds)
- **Cache size**: Disk space used by UV cache (bytes/MB)
- **Downloads**: Number of packages downloaded from PyPI
- **Cache delta**: Change in cache size between runs

---

## Detailed Results

### Strategy 1: No Cache (Baseline)

```
Run 1: 11.580s, 310.24 MB downloaded, 14 packages
Run 2: 11.373s, 310.24 MB downloaded, 14 packages
```

**Analysis**:
- Consistent ~11.5s installation time
- No caching benefit - every run downloads all packages
- Total bandwidth: 620 MB for 2 runs
- Use case: When cache cannot be preserved (e.g., ephemeral CI runners)

### Strategy 2: Persistent Cache (BuildKit-style)

```
Cold cache: 11.565s, 310.24 MB downloaded, 14 packages
Warm cache:  1.720s,   1.6 KB delta,      0 packages
```

**Analysis**:
- **Time savings: 9.84s (85.1% reduction)**
- **Bandwidth savings: 310 MB avoided on warm run**
- Cache overhead: 310.24 MB persistent storage
- Warm run only writes minimal metadata (~1.6 KB)
- Use case: Docker BuildKit builds, modern CI/CD pipelines

### Strategy 3: Shared Cache (Volume/Bind Mount)

```
Cold cache: 11.344s, 310.24 MB downloaded, 14 packages
Warm cache:  1.685s,   1.6 KB delta,      0 packages
```

**Analysis**:
- **Time savings: 9.66s (85.1% reduction)**
- **Bandwidth savings: 310 MB avoided on warm run**
- Cache overhead: 310.24 MB persistent storage
- Nearly identical performance to BuildKit cache
- Use case: Docker volumes, development environments with bind mounts

---

## Comparison Analysis

### Performance Equivalence
Both persistent and shared cache strategies deliver virtually identical performance:
- Cold cache: ~11.4s
- Warm cache: ~1.7s
- Time savings: ~85%

The difference between strategies (0.03s) is within measurement noise.

### Cache Characteristics

**Initial Population** (cold cache):
- All strategies take ~11.5s to download and install packages
- Downloads: 14 packages totaling 310.24 MB
- Cache grows from 0 to 310 MB

**Subsequent Runs** (warm cache):
- Installation time drops to ~1.7s (85% reduction)
- No network downloads (0 packages)
- Cache delta: only ~1.6 KB of metadata updates
- Cache size remains stable at 310 MB

### Cost-Benefit Analysis

**Benefits**:
- ⏱️ **Time**: 9.8s saved per build (85% reduction)
- 🌐 **Bandwidth**: 310 MB network transfer avoided
- 💰 **Cost**: Reduced CI/CD minutes, faster developer feedback

**Costs**:
- 💾 **Storage**: 310 MB persistent cache (for this dependency set)
- 🔧 **Complexity**: Minimal (native Docker BuildKit support)

**ROI**: For projects with frequent builds, cache mounts pay for themselves after the first cached build.

---

## Recommendations

### 1. Use Cache Mounts in Docker Builds

**Recommended Dockerfile pattern**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml .

# Install with cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_LINK_MODE=copy uv pip install --system -r pyproject.toml

# Copy application code
COPY . .
```

### 2. Choose Strategy Based on Use Case

| Scenario | Recommended Strategy | Rationale |
|----------|---------------------|-----------|
| Modern CI/CD (GitHub Actions, GitLab CI) | BuildKit cache mount | Native support, no setup needed |
| Local development | Bind mount | Easy inspection, shared across projects |
| Legacy Docker | Volume mount | Works without BuildKit |
| Ephemeral environments | No cache | Only if cache cannot persist |

### 3. Optimize Cache Configuration

```bash
# Set environment variables for optimal performance
ENV UV_LINK_MODE=copy              # Avoid hardlink warnings
ENV UV_CACHE_DIR=/root/.cache/uv   # Explicit cache location
```

### 4. Monitor Cache Size

- This test used 310 MB for 8 common packages
- Larger projects may use 500 MB - 2 GB of cache
- Periodically clean cache in long-running environments
- Use cache mount to share across builds without polluting images

---

## Technical Notes

### Why the 85% Speedup?

With warm cache, uv:
- **Skips downloading** packages from PyPI (network I/O eliminated)
- **Reuses wheels** already built and cached (compilation skipped)
- **Only copies** from cache to venv (fast local I/O)

The remaining 1.7s is spent:
- Creating virtual environment
- Verifying cached packages
- Copying files from cache to installation location
- Writing metadata

### Cache Invalidation

The cache remains valid as long as:
- Package versions don't change (use lock files!)
- Python version remains compatible
- Platform/architecture matches

When dependencies change:
- Only new/updated packages are downloaded
- Unchanged packages remain cached
- Partial cache hit provides intermediate speedup

### Measurement Accuracy

- Each run performed in fresh virtual environment
- Cache directories isolated per strategy
- Wall-clock time measured with Python's `time.time()`
- Small variance (~0.2s) observed between runs due to system load

---

## Conclusions

1. **Cache mounts are highly effective**: 85% time reduction is substantial and consistent across strategies.

2. **Minimal overhead**: 310 MB cache storage is reasonable for the time savings gained.

3. **Strategy choice doesn't matter much**: Persistent cache and shared cache perform identically. Choose based on tooling and workflow.

4. **Strong recommendation**: All Docker-based Python projects using `uv` should implement cache mounts.

5. **Best practice**: Use BuildKit cache mounts (`--mount=type=cache`) as the default strategy in 2025.

---

## Reproduction

To reproduce this benchmark:

```bash
cd uv-cache-mount-benchmark
python3 benchmark_direct.py
```

Results will be saved to `benchmark_results.json` with detailed timing and cache size data.

---

## References

- [UV Documentation: Docker Integration](https://docs.astral.sh/uv/guides/integration/docker/)
- [Docker BuildKit Cache Mounts](https://docs.docker.com/build/cache/)
- Test dependencies: pandas, numpy, requests, fastapi, scikit-learn, pillow, sqlalchemy, pydantic
- Benchmark date: 2025-11-10
