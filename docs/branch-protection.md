# Enforce the security checks on main

Status on 2026-10-18: the public GitHub API reported `main` as unprotected and
no active branch rules. The settings below are prepared instructions; they have
not been applied by this change.

## Configure a branch ruleset

After the pipeline-hardening branch has run once so Gate 7 is available:

1. Open repository **Settings > Rules > Rulesets > New ruleset > New branch ruleset**.
2. Name it `main-security-checks`, select **Active**, and target `main`.
3. Leave the bypass list empty so the maintainer is also subject to the rules.
4. Enable **Require a pull request before merging**. For this solo project,
   leave required approvals at zero unless another reviewer is available.
5. Enable **Require status checks to pass**, and require the branch to be up to
   date before merging.
6. Add each exact check name below. Choose GitHub Actions as the expected source
   where the UI offers that choice.
7. Block force pushes and branch deletion, then save the ruleset.

| Required check |
| --- |
| Gate 1 - secret scanning (Gitleaks) |
| Gate 2 - SAST (Semgrep) |
| Gate 3 - Dependencies (pip-audit) |
| Gate 4 - Container security |
| Gate 5 - Runtime security (ZAP) |
| Gate 6 - Security regression tests |
| Gate 7 - Workflow security (zizmor) |

Requiring checks does not require enabling GitHub's merge queue. If a merge queue
is introduced later, add and validate the appropriate workflow trigger first.
Changing job names requires updating the required checks too.

Reference: [GitHub's ruleset setup instructions](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository).

## Prove that merging is blocked

Once the hardening PR is merged and main is green, create a disposable branch
from main. Change the `X-Content-Type-Options` value in `app/main.py` from
`nosniff` to `invalid`, then open a PR. Gates 5/6 should fail; inspect the PR
merge panel and capture evidence that a required check prevents merging.

Close that PR without merging and delete the disposable branch. Keep its URL
and failing run in the evidence. The routine negative-control tests prove
detection, while this separate exercise proves repository enforcement.

Do not record enforcement as complete until the ruleset is active and the
blocked-merge behavior has been observed.
