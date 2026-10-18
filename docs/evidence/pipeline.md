# Gate 7: workflow security and supply-chain hardening

## Finding and change

The application security checks could pass while the workflow itself still used
mutable action tags, broad token permissions, and persisted checkout credentials.
This was a configuration weakness, not evidence of an actual compromise.

Reviewed on 2026-10-18 against merge commit
`ae20791922223ca4152ed1a0c99b7c2e0b9b622a`. A local zizmor 1.31.1 audit found:

| Finding | Count | Remediation |
| --- | --- | --- |
| `unpinned-uses` | 12 | Resolve official action releases to full commit SHAs |
| `excessive-permissions` | 2 | Default to `contents: read`; allow SARIF writes only in Gates 1 and 2 |
| `artipacked` | 1 | Disable checkout credential persistence in Gate 1 |
| `undocumented-permissions` | 1 | Remove unused PR write permission; explain necessary write grants |
| `concurrency-limits` | 1 | Cancel superseded PR runs; serialize runs on the same ref |

All actions now use verified commit SHAs with release comments. Gitleaks,
Semgrep, Trivy, ZAP, and the Python base image use registry-verified SHA-256
digests. The previously floating Gitleaks and Semgrep images were resolved to
v8.30.1 and 1.181.0. Version-labelled Trivy 0.74.0 and ZAP 2.17.0 were retained.
The Python base digest matches the previously observed image; Debian upgrades
still run at build time.

## Gate behavior

Gate 7 installs zizmor from [tools/requirements.txt](../../tools/requirements.txt)
using pip hash checking and binary wheels only. Hashes cover Linux x86_64 CI and
Windows x86_64 local review. The scanner has no Python runtime dependencies.

The audit uses offline mode, the pedantic persona, strict input collection,
and a LOW-or-higher blocking threshold. It checks workflow and Dependabot files
under `.github/`. There are no repository-specific exclusions. The ordinary
output mode retains finding-based exit codes; SARIF mode alone would not enforce
that behavior. See [zizmor usage](https://docs.zizmor.sh/usage/).

`scripts/verify_workflow_gate.py` sends two modified copies of the real workflow
to zizmor through stdin. It verifies that a mutable checkout tag triggers
`unpinned-uses`, and `permissions: write-all` triggers `excessive-permissions`.
Both must return a finding exit code and the expected non-ignored rule. Parsing
errors, scanner failures, and zero findings are rejected as invalid proof.
The unsafe copies are never installed as executable GitHub workflows.

## Maintenance

[Dependabot](../../.github/dependabot.yml) checks weekly for action, application
dependency, workflow-scanner, and Dockerfile base-image updates. Version updates
have a seven-day cooldown; security updates are not subject to this setting.
See [the Dependabot reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#cooldown).

Scanner image references inside shell scripts and environment values need manual
review; this configuration does not claim Dependabot updates them. For each
scanner update, select an official release, resolve its registry digest, replace
the tag and digest together, and rerun the gate and its failure proof. Update both
Semgrep occurrences together. For zizmor, review the wheel hashes alongside the
version. Review emergency fixes promptly rather than waiting for a version-update
cooldown.

## Validation and remaining limits

Local validation: the hardened workflow and Dependabot configuration produce no
findings under the configured zizmor policy. Both negative controls are rejected.
GitHub validation of this new batch is pending; Docker is unavailable locally.

Digest pinning fixes the selected image content, not the entire build. Hosted
runners, Python setup downloads, pip transitive resolution, Debian package
updates, Semgrep registry rules, and vulnerability databases remain external
inputs. Offline zizmor cannot perform its online advisory or repository audits,
and it does not prove the security of arbitrary shell scripts or dependencies.
These boundaries are retained explicitly rather than claiming a hermetic build.

GitHub API inspection on 2026-10-18 reported `main` as unprotected and returned
no active rules for that branch. A green scanner job therefore did not establish
merge enforcement. Follow [the branch-protection instructions](../branch-protection.md)
and capture a blocked PR before recording that requirement as complete.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m pip install --require-hashes --only-binary=:all: -r tools/requirements.txt
.\.venv\Scripts\zizmor.exe --offline --persona pedantic --min-severity low --strict-collection --no-config .github/
.\.venv\Scripts\python.exe scripts/verify_workflow_gate.py
```

CI uses the same options with `python` and `zizmor` on PATH. Expected results:
audit exit 0 for the hardened workflow; two printed PASS messages confirming
that the deliberately weakened variants produced blocking findings.

After pushing, record the seven-job Actions run and exact commit here. Preserve
the distinction between scanner success, the expired-exception review in
[Gate 4](container.md), and repository merge enforcement.
