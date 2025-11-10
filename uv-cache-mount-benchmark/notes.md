# UV Cache Mount Benchmark - Research Notes

## Objective
Investigate and benchmark different `uv` cache mount strategies to measure:
- Wall-clock time savings
- Bytes/storage savings

## Research Phase

### Background on UV
- `uv` is a fast Python package installer written in Rust
- Uses caching to speed up repeated installations
- Common in Docker builds to speed up dependency installation

### Cache Mount Strategies to Test
1. **No cache** - Baseline, no caching at all
2. **Volume mount** - Docker volume for cache persistence
3. **Bind mount** - Host directory bind mount
4. **BuildKit cache mount** - Docker BuildKit's `--mount=type=cache`

## Investigation Started
Starting research on uv cache mechanisms...

### Key Findings from Research

**UV Cache Location**: `/root/.cache/uv` (default)

**Cache Mount Strategies Identified**:
1. **No cache** - Baseline, fresh install every time
2. **BuildKit cache mount** - `--mount=type=cache,target=/root/.cache/uv`
   - Docker BuildKit's built-in caching mechanism
   - Persists between builds
   - Most recommended approach in 2025
3. **Volume mount** - Traditional Docker volume
   - `docker volume create uv-cache`
   - Mounted at runtime
4. **Bind mount** - Host directory mounted
   - `-v ./cache:/root/.cache/uv`
   - Cache stored on host filesystem

**Best Practices Found**:
- Use `UV_LINK_MODE=copy` to avoid hardlink warnings
- Separate dependency installation from project installation
- Use `--frozen` flag to ensure reproducible builds
- Cache mounts work best with layered Dockerfile approach

### Benchmark Design

**Test Scenarios**:
1. Cold cache (first run) - measure baseline
2. Warm cache (second run) - measure savings
3. Cache invalidation (dependency change) - partial cache hit

**Metrics to Collect**:
- Wall-clock time (seconds)
- Download size (bytes)
- Cache size (bytes)
- Build time comparison

**Test Dependencies**:
Using a realistic Python project with common heavy dependencies:
- pandas
- numpy
- requests
- fastapi
- scikit-learn

## Implementation Notes

### Environment Constraints
- Docker not available in this environment
- Pivoting to direct uv benchmark approach
- Will simulate different cache strategies using:
  1. No cache (clear before each run)
  2. Local cache (persistent across runs)
  3. Shared cache directory
  4. Different cache locations to test filesystem impact

### Revised Benchmark Approach
Instead of Docker builds, will benchmark:
1. Fresh install with no cache (baseline)
2. Second install with warm cache (measure savings)
3. Cache size analysis
4. Different uv cache configurations

## Benchmark Execution

### Test Setup
- Environment: Linux container
- Python: 3.x with uv installed
- Test packages: pandas, numpy, requests, fastapi, scikit-learn, pillow, sqlalchemy, pydantic
- Method: Direct uv pip install with controlled UV_CACHE_DIR

### Strategies Tested
1. **No Cache**: Cache cleared before every install (baseline)
2. **Persistent Cache**: BuildKit-style, cache preserved between runs
3. **Shared Cache**: Volume/bind mount style, cache preserved between runs

### Results Summary

**No Cache (Baseline)**:
- Run 1: 11.58s, 310.24 MB downloaded
- Run 2: 11.37s, 310.24 MB downloaded
- Consistent performance, no savings

**Persistent Cache (BuildKit-style)**:
- Cold cache: 11.56s, 310.24 MB
- Warm cache: 1.72s, ~1.6 KB delta
- **Time saved: 9.84s (85.1%)**
- **Cache size: 310.24 MB**

**Shared Cache (Volume/bind mount)**:
- Cold cache: 11.34s, 310.24 MB
- Warm cache: 1.69s, ~1.6 KB delta
- **Time saved: 9.66s (85.1%)**
- **Cache size: 310.24 MB**

### Key Findings
- Persistent and shared cache strategies perform nearly identically
- ~85% time reduction with warm cache
- Cache overhead: ~310 MB for these dependencies
- No downloads on warm cache runs (0 downloads vs 14 on cold)
- Minimal cache delta on warm runs (~1.6 KB vs 310 MB initial)
