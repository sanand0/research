Go 1.21 is released! - The Go Programming Language





[![Go](/images/go-logo-white.svg)](/)

[Skip to Main Content](#main-content)

* [Why Go *arrow\_drop\_down*](#)

  Press Enter to activate/deactivate dropdown

  + [Case Studies](/solutions/case-studies)

    Common problems companies solve with Go
  + [Use Cases](/solutions/use-cases)

    Stories about how and why companies use Go
  + [Security](/security/)

    How Go can help keep you secure by default
* [Learn](/learn/)

  Press Enter to activate/deactivate dropdown
* [Docs *arrow\_drop\_down*](#)

  Press Enter to activate/deactivate dropdown

  + [Go Spec](/ref/spec)

    The official Go language specification
  + [Go User Manual](/doc)

    A complete introduction to building software with Go
  + [Standard library](https://pkg.go.dev/std)

    Reference documentation for Go's standard library
  + [Release Notes](/doc/devel/release)

    Learn what's new in each Go release
  + [Effective Go](/doc/effective_go)

    Tips for writing clear, performant, and idiomatic Go code
* [Packages](https://pkg.go.dev)

  Press Enter to activate/deactivate dropdown
* [Community *arrow\_drop\_down*](#)

  Press Enter to activate/deactivate dropdown

  + [Recorded Talks](/talks/)

    Videos from prior events
  + [Meetups
    *open\_in\_new*](https://www.meetup.com/pro/go)

    Meet other local Go developers
  + [Conferences
    *open\_in\_new*](/wiki/Conferences)

    Learn and network with Go developers from around the world
  + [Go blog](/blog)

    The Go project's official blog.
  + [Go project](/help)

    Get help and stay informed from Go
  + Get connected

    [![](/images/logos/social/google-groups.svg)](https://groups.google.com/g/golang-nuts)
    [![](/images/logos/social/github.svg)](https://github.com/golang)
    [![](/images/logos/social/twitter.svg)](https://twitter.com/golang)
    [![](/images/logos/social/reddit.svg)](https://www.reddit.com/r/golang/)
    [![](/images/logos/social/slack.svg)](https://invite.slack.golangbridge.org/)
    [![](/images/logos/social/stack-overflow.svg)](https://stackoverflow.com/tags/go)




[![Go.](/images/go-logo-blue.svg)](/)

* [Why Go *navigate\_next*](#)

  [*navigate\_before*Why Go](#)

  + [Case Studies](/solutions/case-studies)
  + [Use Cases](/solutions/use-cases)
  + [Security](/security/)
* [Learn](/learn/)
* [Docs *navigate\_next*](#)

  [*navigate\_before*Docs](#)

  + [Go Spec](/ref/spec)
  + [Go User Manual](/doc)
  + [Standard library](https://pkg.go.dev/std)
  + [Release Notes](/doc/devel/release)
  + [Effective Go](/doc/effective_go)
* [Packages](https://pkg.go.dev)
* [Community *navigate\_next*](#)

  [*navigate\_before*Community](#)

  + [Recorded Talks](/talks/)
  + [Meetups
    *open\_in\_new*](https://www.meetup.com/pro/go)
  + [Conferences
    *open\_in\_new*](/wiki/Conferences)
  + [Go blog](/blog)
  + [Go project](/help)
  + Get connected

    [![](/images/logos/social/google-groups.svg)](https://groups.google.com/g/golang-nuts)
    [![](/images/logos/social/github.svg)](https://github.com/golang)
    [![](/images/logos/social/twitter.svg)](https://twitter.com/golang)
    [![](/images/logos/social/reddit.svg)](https://www.reddit.com/r/golang/)
    [![](/images/logos/social/slack.svg)](https://invite.slack.golangbridge.org/)
    [![](/images/logos/social/stack-overflow.svg)](https://stackoverflow.com/tags/go)

# [The Go Blog](/blog/)

# Go 1.21 is released!

Eli Bendersky, on behalf of the Go team  
8 August 2023

Today the Go team is thrilled to release Go 1.21,
which you can get by visiting the [download page](/dl/).

Go 1.21 is packed with new features and improvements. Here are some of the
notable changes; for the full list, refer to the
[release notes](/doc/go1.21).

## Tool improvements

* The Profile Guided Optimization (PGO) feature we [announced for preview in
  1.20](/blog/pgo-preview) is now generally available! If a file named
  `default.pgo` is present in the main package’s directory, the `go` command
  will use it to enable a PGO build. See the [PGO documentation](/doc/pgo) for
  more details. We’ve measured the impact of PGO on a wide set of Go programs and
  see performance improvements of 2-7%.
* The [`go` tool](/cmd/go) now supports [backward](/doc/godebug)
  and [forward](/doc/toolchain) language compatibility.

## Language changes

* New built-in functions: [min, max](/ref/spec#Min_and_max)
  and [clear](/ref/spec#Clear).
* Several improvements to type inference for generic functions. The description of
  [type inference in the spec](/ref/spec#Type_inference)
  has been expanded and clarified.
* In a future version of Go we’re planning to address one of the most common
  gotchas of Go programming:
  [loop variable capture](/wiki/CommonMistakes).
  Go 1.21 comes with a preview of this feature that you can enable in your code
  using an environment variable. See [the LoopvarExperiment wiki
  page](/wiki/LoopvarExperiment) for more details.

## Standard library additions

* New [log/slog](/pkg/log/slog) package for structured logging.
* New [slices](/pkg/slices) package for common operations
  on slices of any element type. This includes sorting functions that are generally
  faster and more ergonomic than the [sort](/pkg/sort) package.
* New [maps](/pkg/maps) package for common operations on maps
  of any key or element type.
* New [cmp](/pkg/cmp) package with new utilities for comparing
  ordered values.

## Improved performance

In addition to the performance improvements when enabling PGO:

* The Go compiler itself has been rebuilt with PGO enabled for 1.21, and as a
  result it builds Go programs 2-4% faster, depending on the host architecture.
* Due to tuning of the garbage collector, some applications may see up to a 40%
  reduction in tail latency.
* Collecting traces with [runtime/trace](/pkg/runtime/trace) now
  incurs a substantially smaller CPU cost on amd64 and arm64.

## A new port to WASI

Go 1.21 adds an experimental port for [WebAssembly System Interface (WASI)](https://wasi.dev/),
Preview 1 (`GOOS=wasip1`, `GOARCH=wasm`).

To facilitate writing more general WebAssembly (Wasm) code, the compiler also
supports a new directive for importing functions from the Wasm host:
`go:wasmimport`.

---

Thanks to everyone who contributed to this release by writing code, filing bugs,
sharing feedback, and testing the release candidates. Your efforts helped
to ensure that Go 1.21 is as stable as possible.
As always, if you notice any problems, please [file an issue](/issue/new).

Enjoy Go 1.21!

**Next article:** [Backward Compatibility, Go 1.21, and Go 2](/blog/compat)  
**Previous article:** [Experimenting with project templates](/blog/gonew)  
**[Blog Index](/blog/all)**



[Why Go](/solutions/)
[Use Cases](/solutions/use-cases)
[Case Studies](/solutions/case-studies)

[Get Started](/learn/)
[Playground](/play)
[Tour](/tour/)
[Stack Overflow](https://stackoverflow.com/questions/tagged/go?tab=Newest)
[Help](/help/)

[Packages](https://pkg.go.dev)
[Standard Library](/pkg/)
[About Go Packages](https://pkg.go.dev/about)

[About](/project)
[Download](/dl/)
[Blog](/blog/)
[Issue Tracker](https://github.com/golang/go/issues)
[Release Notes](/doc/devel/release)
[Brand Guidelines](/brand)
[Code of Conduct](/conduct)

[Connect](https://www.twitter.com/golang)
[Twitter](https://www.twitter.com/golang)
[GitHub](https://github.com/golang)
[Slack](https://invite.slack.golangbridge.org/)
[r/golang](https://reddit.com/r/golang)
[Meetup](https://www.meetup.com/pro/go)
[Golang Weekly](https://golangweekly.com/)

Opens in new window.

![The Go Gopher](/images/gophers/pilot-bust.svg)

* [Copyright](/copyright)
* [Terms of Service](/tos)
* [Privacy Policy](http://www.google.com/intl/en/policies/privacy/)
* [Report an Issue](/s/website-issue)
* ![System theme](/images/icons/brightness_6_gm_grey_24dp.svg)
  ![Dark theme](/images/icons/brightness_2_gm_grey_24dp.svg)
  ![Light theme](/images/icons/light_mode_gm_grey_24dp.svg)

[![Google logo](/images/google-white.png)](https://google.com)

go.dev uses cookies from Google to deliver and enhance the quality of its services and to
analyze traffic. [Learn more.](https://policies.google.com/technologies/cookies)

Okay