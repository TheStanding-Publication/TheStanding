---
name: issue-to-entry
description: Convert a specific Standing monitoring issue into a recorded entry — research, validate-and-correct, build, and open a pull request. Use when manually processing one issue instead of waiting for the scheduled entry-recorder.
disable-model-invocation: true
---

# Issue to Entry

Convert one Standing monitoring issue into a recorded entry and open its
pull request.

## Run it

Fetch and execute the canonical workflow spec:

https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/docs/specs/ISSUE_TO_ENTRY_SPEC.md

Run it in **manual mode** (`--issue N`) — see the spec's "Modes"
section. The spec is the source of truth — follow its Steps 1-12
exactly; do not work from memory or a remembered older version.

## Input

A GitHub issue number, provided by the operator with this invocation.
The skill still runs the spec's full Step 1 eligibility check on that
issue (open, authored by `thestanding`, no `invalid` label, no open PR
referencing it) and refuses with a clear error if it is not eligible.

## Output

An entry pull request against `TheStanding-Publication/TheStanding`,
with corrections-in-flight documented in the PR body — or a skip-flag
(`invalid` label + comment) if the issue cannot be made into a valid
entry. See the spec for the exact behavior.

This skill has side effects (it pushes a branch and opens a PR), so it
is user-invoked only — it does not auto-trigger. The scheduled
`standing-entry-recorder` task handles batch processing separately.
