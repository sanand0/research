# Running experiment log

## 11 Oct 2026

Goal: Implement the same deterministic HTTP contract across native Linux / scratch Docker, gVisor, Unikraft (ELF compatibility loader), and WASI HTTP components. Measure behavior, footprint and tooling friction. No privileged host configuration changes or permanent servers.

Initial environment: Remote shell runs inside a Docker container on graphene (Ubuntu Linux 6.17). Rust 1.99, Cargo, Docker 29, just available; `runsc`, `kraft`, `wasmtime`, `go`, and `/dev/kvm` initially absent. Docker daemon reachable but no `runsc` runtime registered. Tool-specific setup and tests recorded below.

Architectural caveat: Unikraft ELF loader is binary compatibility on a prebuilt unikernel—not compiling our Rust application *into* a purpose-built unikernel. Native port of the app to Unikraft would be a separate fifth experiment.

### Builds, repairs, findings

1. Created common Rust inspect function with SHA-256 and JSON shape, native `tiny_http` adapter, WASI `wstd` adapter, reproducible `just` tests and an empty `FROM scratch` Dockerfile.
2. `cargo test` initially failed compiling native header construction (`tiny_http::Header::from_bytes` returns `Result<_, ()>`). Fixed static header with `expect`. Retested: all three tests pass.
3. Installed Rust musl target. Compiled static PIE Linux ELF, verified with `file` (627,488 bytes). `just test-native`: passed all HTTP probes.
4. Initially Docker build context was 119 MB because of the Rust `target` tree. Switched to staged `.build/inspect-server` and tightened `.dockerignore`; new context ~632 KB. Rebuilt and retested: HTTP probes passed. `docker image inspect .Size` = 332,732 bytes; not necessarily uncompressed executable+image size.
5. `just test-gvisor` deliberately refuses fallback to runc; blocked because Docker host has no `runsc` runtime configured. Avoided modifying Docker daemon from inside LocalMCP2.
6. Installed wasm32-wasip2 Rust target; WASI component compiled. Downloaded Wasmtime v49.0.2 to ignored `.tools/bin`. First serve attempt failed with `wasi:cli/environment@0.2.12` import missing; adding `-S cli -S http` resolved it. `just test-wasi` passed. Improved WASI adapter to stop buffering at 1 MiB+1 byte; tested 413 response.
7. Downloaded KraftKit v0.12.16 to ignored `.tools/bin`. `just test-unikraft` blocked: QEMU missing; `/dev/kvm` absent. Source static PIE is prepared, not verified in Unikraft. An optional `Kraftfile` was written following official examples, but not built.
8. Re-ran all three available end-to-end runtimes with 1 MiB oversized body test: native, Docker and WASI all passed. 5 repeated start-to-health (including polling) tests: medians native 13 ms, Docker 245 ms, WASI 128 ms. Not a controlled performance comparison.
9. Local generated binaries, downloads, build roots, VM images, benchmarks and logs are ignored. No host Docker daemon or privilege settings changed.

Final re-run after adjusting the common maximum-body guard: all 3 core unit tests and all native/Docker/WASI HTTP probes pass; Docker image inspect Size is now 332,741 B; WASI file size 282,629 B.
