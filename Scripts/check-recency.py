#!/usr/bin/env python3
"""Check that every lookup task's answer rests on lines changed after a boundary date.

A model trained before the boundary may know an answer from memory if the lines it rests on are older,
even when the file around them changed since. So each task not built on an injected bug names those lines
in `check.pinned_lines` (the declaration, each call site, each conformance, the function a string is shown
from), and this script blames each one at the corpus's pinned commit. A line blamed on the shallow clone's
boundary commit predates the clone's history and counts as old. A task built on an injected bug is exempt:
the bug is new.

Usage: python3 Scripts/check-recency.py corpora/<name>/tasks.json .build/corpora/<name> [--since 2026-07-01]
"""

import argparse
import datetime
import json
import os
import subprocess
import sys

ENV = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def git(clone, *arguments):
    return subprocess.run(["git", "-C", clone, *arguments], env=ENV, capture_output=True, text=True,
                          check=True).stdout


def problem(clone, commit, pin, since):
    lines = git(clone, "show", "%s:%s" % (commit, pin["file"])).splitlines()
    where = "%s:%d" % (pin["file"], pin["line"])
    if len(lines) < pin["line"] or pin["contains"] not in lines[pin["line"] - 1]:
        return "%s does not hold %r" % (where, pin["contains"])
    # A user's blame.showRoot would hide the boundary marker that says a line predates the clone.
    blame = git(clone, "-c", "blame.showRoot=false", "blame", "--porcelain", "-L", "%d,%d" % (pin["line"], pin["line"]),
                commit, "--", pin["file"]).splitlines()
    if "boundary" in blame:
        return "%s predates the clone" % where
    time = next(int(line.split()[1]) for line in blame if line.startswith("committer-time "))
    if time < since:
        return "%s last changed %s" % (where, datetime.date.fromtimestamp(time).isoformat())
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tasks")
    parser.add_argument("clone")
    parser.add_argument("--since", default="2026-07-01")
    options = parser.parse_args()
    with open(options.tasks) as handle:
        tasks = json.load(handle)
    commit = tasks["corpus"]["commit"]
    since = datetime.datetime.fromisoformat(options.since).replace(tzinfo=datetime.timezone.utc).timestamp()
    lookups = [task for task in tasks["tasks"] if "inject" not in task]
    failed = 0
    for task in lookups:
        pins = task["check"].get("pinned_lines", [])
        problems = [found for found in (problem(options.clone, commit, pin, since) for pin in pins) if found]
        if not pins:
            problems = ["no pinned_lines name the lines its answer rests on"]
        if problems:
            failed += 1
            print("%s: FAILED %s" % (task["id"], "; ".join(problems)))
        else:
            print("%s: ok (%d lines)" % (task["id"], len(pins)))
    exempt = len(tasks["tasks"]) - len(lookups)
    print("recent since %s: %d/%d lookup tasks (%d injected-bug tasks exempt)"
          % (options.since, len(lookups) - failed, len(lookups), exempt))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
