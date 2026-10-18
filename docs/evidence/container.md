# Gate 4: container security

## Outcome

On 2026-10-12 the maintainer reported that the latest Gate 4 run passed.
The policy still blocks unsuppressed HIGH and CRITICAL findings. Passing
includes the reviewed, package-scoped exceptions in [.trivyignore.yaml](../../.trivyignore.yaml);
it does not mean every installed package is patched or the image is suitable
for production. The final passing run URL and commit remain to be recorded.

## Evidence of improvement

| Checkpoint | Observation | Evidence |
| --- | --- | --- |
| Initial runnable image | Root execution; Dockerfile finding DS-0002. Image scan reported 553 Debian findings and two additional Python findings. | Commit `157894b8069ca660f3a8a02e4cf34ad64bfbd69e`, [Actions run](https://github.com/Yu2uu/SuperSafeCode/actions/runs/34606985097/job/103287708128?pr=5) |
| Non-root execution | UID/GID 10001, health check passed, Dockerfile scan clean; image vulnerability scan still failed. | Commit `b559c6d80479603b99f3e2a18f6d4051a3f74376`, [Actions run](https://github.com/Yu2uu/SuperSafeCode/actions/runs/35243040738/job/105276073102?pr=5) |
| Smaller base | A later comparison fell from 649 findings (593 HIGH, 56 CRITICAL) to 63 (58 HIGH, 5 CRITICAL) with Python 3.12 slim Bookworm. | Commit `471053d86c9e9c0e6f849c341e2d8d2d8330c39e`, [Actions run](https://github.com/Yu2uu/SuperSafeCode/actions/runs/35244800601/job/105282127057?pr=5) |
| Final remediation and review | Updated Debian packages, moved to slim Trixie, removed unused entry points, and reviewed remaining findings. Latest gate passed according to the maintainer. | Current Dockerfile, workflow assertions, and exception file; final run link pending. |

These are observations from separate runs. Counts represent package/advisory
findings, not unique exploitable vulnerabilities. Image contents and advisory
data can change between scans; the counts alone do not isolate each change's effect.

## Final controls

- Python 3.12 slim Trixie base; available Debian updates applied during build.
- Gunicorn runs the application as UID/GID 10001; SQLite writes to `/data`.
- The `mount` package is removed. `infocmp` and `nsenter` executables are removed;
  their package records remain visible to vulnerability auditing.
- CI checks startup, non-root execution, absence of `/app/.git`, and absence of
  `mount`, `infocmp`, `nsenter`, `systemd-homed`, and `Archive/Tar.pm`.
- `.dockerignore` excludes Git metadata, local environments, databases, and
  environment files from the build context. This is preventive: the original
  Dockerfile contained only `FROM`, so no earlier Git-history exposure is claimed.
- Trivy scans both Dockerfile configuration and the built image. Suppressed
  findings remain visible through `--show-suppressed`.

## Residual risk and review dates

Eight CVE exceptions are scoped to named packages and local/CI portfolio use.
The exception file records component-absence evidence or explicit residual-risk
acceptance. Non-root execution and executable removal are not proof that every
related library is unexploitable. No live deployment is covered by this decision.

The `systemd-homed` and `Archive::Tar` exceptions expire on **2026-10-17**;
the other six expire on **2026-11-05**. Recheck upstream fixes and applicability
before expiry. Remove exceptions when resolved; any renewal requires a fresh
documented review. CI must continue to fail if an asserted-absent component returns.

Before closing this checkpoint, add the final passing Actions URL and its exact
commit SHA. Use that run's totals if recording final counts; do not infer them
from earlier scans.
