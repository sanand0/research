# How small can a useful execution environment be?

Source: https://chatgpt.com/share/6acb871f-fda4-83ec-a419-a2991d7047a5 <!-- https://chatgpt.com/c/6acb304c-095c-83ec-9496-073470c6dc09 -->

11 October 2026. Inspired by [Geoffrey Huntley's unikernel argument](https://ghuntley.com/unikernels/) and the question "Does a useful `FROM scratch` container lead naturally to unikernels?"

## Question

Build **one useful HTTP application** with the same contract in four environments: Linux native/`FROM scratch` Docker, Docker with gVisor, Unikraft ELF-loader microVM, and WASI HTTP. Separate three choices often confused: **packaging** (OCI/native ELF/Wasm), **execution** (Linux kernel, compatibility unikernel, Wasm runtime), and **isolation** (namespaces, gVisor user-space kernel, virtualization, capabilities). Test actual behavior and deployment friction, not just image size. Use the same source logic and deterministic probes.

This is a proof-of-concept and **not a security or throughput benchmark**.

## Application and reproducible commands

`POST /inspect` accepts a JSON document (maximum 1 MiB) and returns JSON with `bytes` (original UTF-8 request byte count), `sha256` (hex hash of the exact request bytes), `type` (`object`, `array`, `string`, `number`, `boolean`, `null`), and `items` (number of top-level object keys or array elements; zero for scalar values). `GET /health` returns `{"status":"ok"}`. Errors: malformed JSON => 400, excessive body => 413, unknown route => 404. No authentication, TLS, persistence or outbound connections; bind only to localhost for tests.

Example (key order is JSON-semantic, not guaranteed):

```sh
curl -sS -X POST http://127.0.0.1:18765/inspect \
  -H 'content-type: application/json' --data-binary '{"a":1}'
# {"bytes":7,"items":1,"sha256":"...64 hex chars...","type":"object"}
```

Run within this directory. Requirements: Rust, Cargo, `rustup`, `just`, `docker` (for Docker/gVisor), `curl`, `jaq`, `sha256sum`, and `file`. The `just` targets use separate ephemeral servers/containers and clean them up; port `18765` is used locally and can be changed using `PORT_TEST=...`.

```sh
just --list
just test-unit
just test-native        # Compiles x86_64-unknown-linux-musl static PIE; starts it; probes HTTP
just test-docker        # FROM scratch, nonroot, readonly FS, no Linux distribution
just setup-tools        # Downloads pinned Wasmtime 49.0.2 and KraftKit 0.12.16 into ignored .tools/
just test-wasi          # Compiles wasm32-wasip2 and serves through Wasmtime WASI HTTP
just test-gvisor        # Needs host Docker runtime `runsc`: read below
just test-unikraft      # Needs host QEMU (and ideally /dev/kvm): read below
just sizes
just benchmark          # Five launches each of native, Docker, WASI; results/ ignored
```

**Implementation:** [`src/lib.rs`](src/lib.rs) is the shared, runtime-agnostic JSON/hash logic and unit tests; [`src/bin/server.rs`](src/bin/server.rs) is the Linux HTTP adapter (`tiny_http`); [`wasi/src/lib.rs`](wasi/src/lib.rs) is the WASI HTTP P2 adapter (`wstd`). Both adapters bound the accumulated request body to 1 MiB plus a sentinel byte. `Cargo.lock` and `wasi/Cargo.lock` are committed, compiled outputs are ignored. The static ELF is position-independent and musl-linked; confirmed with `file`. The [Dockerfile](Dockerfile) copies **only** that ELF into an otherwise empty filesystem and sets uid/gid `65532:65532`. `.dockerignore` sends only the staged executable; the Docker build context is about 632 KB, not a whole Rust `target/` tree.

### 1. Native Linux and scratch Docker — tested

`just test-native` runs the ELF directly. `just test-docker` builds a `FROM scratch` image (no base-image layers) and runs it with `--read-only --cap-drop ALL --security-opt no-new-privileges`, exposed only via `127.0.0.1:18765:8080`. The image still **uses the host's Linux kernel**. No extra OS files, dynamic loader or CA certificates are shipped. Thus no interactive shell, and do not use `docker exec ... sh` to debug it.

### 2. gVisor — requires Docker host change

gVisor's `runsc` must be installed on the **Docker daemon host**, registered as a runtime, and Docker reloaded/restarted. This is deliberately **not** done from the LocalMCP2 container because it would modify the host's daemon and potentially interrupt existing containers. Follow the [official install guide](https://gvisor.dev/docs/user_guide/install/) and [Docker setup](https://gvisor.dev/docs/user_guide/quick_start/docker/). On the machine running Docker:

```sh
# Review the instructions first. This changes the Docker host configuration.
# After installing runsc on the Docker host:
sudo runsc install
sudo systemctl reload docker   # may need restart, depending on daemon

docker info | grep Runtimes   # should contain runsc
just test-gvisor              # exactly the same scratch image with --runtime=runsc
```

The recipe explicitly refuses to use regular `runc` if `runsc` is unavailable. A successful HTTP test would confirm behavior on gVisor, not prove security or syscall compatibility in general.

### 3. Unikraft — user must run on a host with QEMU

The first practical path uses Unikraft's **prebuilt ELF compatibility loader** around our static PIE Linux executable:

```sh
just setup-tools            # KraftKit CLI into local .tools/bin
# On Ubuntu host, if required: sudo apt install qemu-system-x86
just test-unikraft
```

The [Unikraft CLI docs](https://unikraft.org/docs/cli/running) explicitly support `kraft run BINARY` through a downloaded ELF loader. `tests/with-server.sh` uses `kraft run --port 18765:8080 ...`, with acceleration if `/dev/kvm` is readable or slower TCG emulation otherwise. QEMU must be present on the **host executing `kraft`**. If the loader cannot run the Rust binary's syscalls or network setup, capture the error; we have **not established compatibility**. The recipe stops and removes only its own VM (`inspect-test-unikraft`). **Check KraftKit port exposure/firewall behavior before trying this on a public host**; port binding to localhost has not been verified for this VM path.

Optional [`Kraftfile`](Kraftfile) instead declares `runtime: base:latest`, `rootfs: ./Dockerfile` and `cmd`. It follows Unikraft's [catalog example](https://unikraft.org/guides/catalog-behind-the-scenes), but needs a BuildKit setup and was **not built or validated here**. The straightforward ELF loader recipe above should be tried first.

**Important distinction:** loading an ordinary Linux ELF on a prebuilt Unikraft loader is *not* a tailor-made native unikernel compiled from our application. That deeper step needs an actual Unikraft library-OS port/build and should only be claimed after it's built and run.

### 4. WASI — tested

`just build-wasi` creates a `wasm32-wasip2` component that exports the WASI HTTP interface. `just test-wasi` uses `wasmtime serve -S cli -S http` to provide the component's host imports. Without these switches, current Wasmtime gave an import-linker error for `wasi:cli/environment@0.2.12`. It uses the same `inspect_core::handle` source as native/Docker, not a reimplementation. Wasmtime is an OS process and **not** a unikernel or VM. This example deliberately doesn't grant directory access or outbound networking. `wasmtime serve` is intended for development and needs a front proxy / rate limiting for production.

## Results: measured in LocalMCP2 (11 Oct 2026)

| Path | Build | Contract probe | Artifact size | Runtime support |
|---|---|---|---:|---|
| Native Linux musl static PIE | PASS | PASS | **627,488 B** | Available |
| Scratch Docker (`runc`) | PASS | PASS | **332,741 B** Docker reported `image inspect .Size` | Available |
| Docker + gVisor (`runsc`) | same image | **BLOCKED** | same image | No registered `runsc` Docker runtime |
| Unikraft + ELF loader | PIE ready, Kraft CLI downloaded | **BLOCKED** | VM bundle not measured | QEMU and `/dev/kvm` absent; no VM boot attempted |
| WASI/Wasmtime P2 HTTP | PASS | PASS | **~283 KB** component | Wasmtime 49.0.2 downloaded locally |

All tested environments passed **health, exact hash/size/type, invalid JSON, 404, and 413 excessive payload**. Three core Rust unit tests passed. Native and Wasm use identical core logic. Docker image reported size is a storage-accounting value and is **not directly comparable** to an executable's on-disk byte count (compression / metadata differ).

**Noisy launch-to-health trial, 5 runs each, ms:** native `13,14,13,12,13` (median **13**); scratch Docker `245,251,234,224,254` (median **245**); WASI `129,128,128,128,128` (median **128**). These include process/container startup and polling until HTTP health is reachable but exclude compilation; 100 ms poll intervals give imprecise measurements. All conducted inside LocalMCP2; not controlled cold start, CPU/RSS, throughput, or a reliable basis for ranking runtimes. Full local logs in ignored `results/bench.txt`.

## What we learned

1. **Scratch containers are easy once the executable is self-contained.** The image is an empty filesystem plus executable and OCI metadata, while the host kernel does the heavy lifting.
2. **The barrier moves to the runtime boundary.** Native and Docker share Linux interfaces; Wasmtime needed explicit WASI CLI/HTTP host-import configuration; Unikraft needs a VM runner; gVisor needs host runtime registration.
3. **Images are not a fair proxy for total footprint.** Binary size and OCI image size say nothing about VM memory, resident runtime, available kernel services, cache, or security guarantees.
4. **AI can lower porting effort, but deterministic tests are what make it safe to iterate.** Our shared response contract and cross-runtime probes catch silent divergences; remaining VM tests must not be called complete.

Next: run `just test-gvisor` and `just test-unikraft` on a Linux **host** with the required runtime infrastructure, keep their exact stdout/stderr, then add measured memory and cold-start using the same instrumentation. For Unikraft, distinguish ELF compatibility from the next genuinely interesting experiment: building a native specialized unikernel around the app.

Sources: [Docker scratch base images](https://docs.docker.com/build/building/base-images/), [gVisor Docker Quick Start](https://gvisor.dev/docs/user_guide/quick_start/docker/), [Unikraft ELF loader](https://unikraft.org/docs/cli/running), [Wasmtime CLI serve](https://docs.wasmtime.dev/cli-options.html), [WASI Rust sample](https://github.com/bytecodealliance/sample-wasi-http-rust).
