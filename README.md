# fieldwork-bench

Benchmark corpora for the Fieldwork tools (sift, SimWalk, and the tools that follow them): public Swift
apps pinned at a commit, each with a task file whose answers are checked mechanically.

A tool measured only on its author's own code, or on a private app, gives numbers nobody else can
reproduce. These corpora are public, pinned and large, so a result names the commit it was measured at,
and anyone can rerun it.

## Corpora

| Corpus | Upstream | Licence | Pinned commit | Swift lines |
| --- | --- | --- | --- | --- |
| wikipedia-ios | [wikimedia/wikipedia-ios](https://github.com/wikimedia/wikipedia-ios) | MIT | `27a82770` | 229,615, plus 28,215 lines of Objective-C |
| firefox-ios | [mozilla-mobile/firefox-ios](https://github.com/mozilla-mobile/firefox-ios) | MPL-2.0 | `d284ab8e` | 524,909 |

Rows are added as each corpus's task file passes the harness's `validate`, which makes no model calls.
Each file has ten tasks: a definition, two caller sets, two type questions, two UI strings traced to the
code that shows them, two injected one-line bugs, and one chained question. One of wikipedia-ios's
caller sets includes Objective-C files, to show where a Swift-only index stops.

## Running a corpus

Fetch the corpus at its pinned commit (the history since June is enough to check which files changed
recently), then run the harness from a sift checkout, passing the clone with `--corpus`:

```sh
git clone --shallow-since=2026-06-01 https://github.com/wikimedia/wikipedia-ios .build/corpora/wikipedia-ios
git -C .build/corpora/wikipedia-ios checkout 27a82770e40cbe3007dc287e059cc3a6d11b6f77

# from a sift checkout
python3 Benchmarks/bench.py validate --tasks <this repo>/corpora/wikipedia-ios/tasks.json \
  --corpus <this repo>/.build/corpora/wikipedia-ios@27a82770e40cbe3007dc287e059cc3a6d11b6f77
sh Benchmarks/run.sh --tasks <same> --corpus <same> --repeats 3
```

firefox-ios needs a harness with two fixes that land in sift's next release. One lets the hook check
skip a file withheld for its size (its 608 KB `Strings.swift`). The other matches an injected file
whose path holds a space.

## Layout

- `corpora/<name>/tasks.json`: the task file, in the format of sift's `Benchmarks/tasks.example.json`,
  pinned to one upstream commit.
- `.build/corpora/<name>`: the upstream clone (gitignored), fetched at the pinned commit.

## Choosing a corpus

- **Public, active and large.** Pinned at a commit made after the models being measured were trained,
  with lookup tasks aimed at code changed since then, so an answer cannot come from memory. A task built
  on an injected bug can't be answered from memory either, because the bug is new.
- **Buildable for its index** where it can be, with a generic simulator destination, so no simulator is
  created or booted.
- **Not vendored.** The upstream code stays upstream. A task file names its symbols and lines, and
  nothing else of it is copied here.

## Privacy gate

Every pushed commit is public. `githooks/pre-push` runs `Scripts/verify-tree.sh` on each commit a push
publishes. The gate is copied from swift-fieldwork and kept in step with it. Enable the hooks once
per clone:

```sh
git config core.hooksPath githooks
```

A contributor without the maintainer's external lists pushes with `FIELDWORK_PRIVACY_GATE=skip`.

## License

Apache-2.0 for the files in this repository. See [LICENSE](LICENSE). Each corpus keeps its own licence
upstream, named in the table above; none of its code is copied here.
