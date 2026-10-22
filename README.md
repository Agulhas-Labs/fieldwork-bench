# fieldwork-bench

Benchmark corpora for the Fieldwork tools (sift, SimWalk, and the tools that follow them): public Swift
apps pinned at a commit, each with a task file whose answers are checked mechanically.

A tool measured only on its author's own code, or on a private app, gives numbers nobody else can
reproduce. These corpora are public, pinned and large, so a result names the commit it was measured at,
and anyone can rerun it.

## Corpora

| Corpus | Upstream | Licence | Pinned commit | Swift lines |
| --- | --- | --- | --- | --- |

Rows are added as each corpus's task file passes the harness's `validate`, which makes no model calls.

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
