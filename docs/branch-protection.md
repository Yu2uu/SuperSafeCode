# Enforce the security checks on main

As of 19 October 2026, the `main-security-checks` ruleset (ID `25427133`)
requires a pull request, all seven security checks, and an up-to-date branch
before merging into `main`. Required approvals are set to zero for this solo
project. Force pushes and branch deletion are restricted.

All seven jobs passed on main at `cd635acac40f55de30d565d9056d406709576199` in
[run 39307160136](https://github.com/Yu2uu/SuperSafeCode/actions/runs/39307160136).
The steps below describe how to reproduce these settings.

## Configure a branch ruleset

After the pipeline-hardening branch has run once so Gate 7 is available:

1. Open repository **Settings > Rules > Rulesets > New ruleset > New branch ruleset**.
2. Name it `main-security-checks`, select **Active**, and target `main`.
3. Leave the bypass list empty.
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

## Verification

The October 18–19 checks used GitHub's REST API to read branch rules and workflow
job results. Those results are linked throughout the evidence documents.

A separate blocked-merge test was not performed. The automated negative controls
check that scanners and tests reject unsafe changes; they do not test the PR
merge controls.
