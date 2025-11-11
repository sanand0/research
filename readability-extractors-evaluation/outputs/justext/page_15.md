Go 1.21 is released!

Today the Go team is thrilled to release Go 1.21,
which you can get by visiting the download page.

Go 1.21 is packed with new features and improvements. Here are some of the
notable changes; for the full list, refer to the
release notes.

Tool improvements

The Profile Guided Optimization (PGO) feature we announced for preview in
1.20 is now generally available! If a file named
default.pgo is present in the main package’s directory, the go command
will use it to enable a PGO build. See the PGO documentation for
more details. We’ve measured the impact of PGO on a wide set of Go programs and
see performance improvements of 2-7%.

Language changes

Several improvements to type inference for generic functions. The description of
type inference in the spec
has been expanded and clarified.

In a future version of Go we’re planning to address one of the most common
gotchas of Go programming:
loop variable capture.
Go 1.21 comes with a preview of this feature that you can enable in your code
using an environment variable. See the LoopvarExperiment wiki
page for more details.

A new port to WASI

To facilitate writing more general WebAssembly (Wasm) code, the compiler also
supports a new directive for importing functions from the Wasm host:
go:wasmimport.

Thanks to everyone who contributed to this release by writing code, filing bugs,
sharing feedback, and testing the release candidates. Your efforts helped
to ensure that Go 1.21 is as stable as possible.
As always, if you notice any problems, please file an issue.