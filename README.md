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

Two harness changes are still pending in sift, and until they land, numbers from these corpora are not
comparable:

- **wikipedia-ios:** its two fix tasks edit files whose paths hold a space. The current harness doesn't
  recognise such a file as restored, so a correct fix scores as a failure. `validate` passes regardless.
- **firefox-ios:** `validate` stops at its hook check, because the corpus's largest file (the 608 KB
  `Strings.swift`) is withheld for its size. The benchmark and a direct replay also judge that file
  differently, so firefox-ios numbers wait until that is understood.

## Layout

- `corpora/<name>/tasks.json`: the task file, in the format of sift's `Benchmarks/tasks.example.json`,
  pinned to one upstream commit.
- `.build/corpora/<name>`: the upstream clone (gitignored), fetched at the pinned commit.
- `Scripts/check-recency.py`: checks that each lookup task's answer rests on lines changed after a date.

## Choosing a corpus

- **Public, active and large.** Pinned at a commit made after the models being measured were trained,
  with lookup tasks aimed at code changed since then, so an answer cannot come from memory. A task built
  on an injected bug can't be answered from memory either, because the bug is new. A recently changed
  file isn't enough on its own: each lookup task lists every line its answer rests on as `pinned_lines`,
  and `python3 Scripts/check-recency.py corpora/<name>/tasks.json .build/corpora/<name>` blames each one
  at the pinned commit. Every pinned line must have changed after 2026-07-01 (`--since`).
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
