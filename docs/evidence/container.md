# Gate 4: container security

## Outcome

Gate 4 passed in [PR #6 run 38598774956](https://github.com/Yu2uu/SuperSafeCode/actions/runs/38598774956)
at commit `e4fec44ccc0639fae1b0dd1188f1cf8c94296a39`, verified through the GitHub
API on 2026-10-18.
The policy still blocks unsuppressed HIGH and CRITICAL findings. Passing
includes the reviewed, package-scoped exceptions in [.trivyignore.yaml](../../.trivyignore.yaml);
it does not mean every installed package is patched or the image is suitable
for production. The later main run failed the image scan; see the review below.

## Evidence of improvement

| Checkpoint | Observation | Evidence |
| --- | --- | --- |
| Initial runnable image | Root execution; Dockerfile finding DS-0002. Image scan reported 553 Debian findings and two additional Python findings. | Commit `157894b8069ca660f3a8a02e4cf34ad64bfbd69e`, [Actions run](https://github.com/Yu2uu/SuperSafeCode/actions/runs/34606985097/job/103287708128?pr=5) |
| Non-root execution | UID/GID 10001, health check passed, Dockerfile scan clean; image vulnerability scan still failed. | Commit `b559c6d80479603b99f3e2a18f6d4051a3f74376`, [Actions run](https://github.com/Yu2uu/SuperSafeCode/actions/runs/35243040738/job/105276073102?pr=5) |
| Smaller base | A later comparison fell from 649 findings (593 HIGH, 56 CRITICAL) to 63 (58 HIGH, 5 CRITICAL) with Python 3.12 slim Bookworm. | Commit `471053d86c9e9c0e6f849c341e2d8d2d8330c39e`, [Actions run](https://github.com/Yu2uu/SuperSafeCode/actions/runs/35244800601/job/105282127057?pr=5) |
| Final remediation and review | Updated Debian packages, moved to slim Trixie, removed unused entry points, and reviewed remaining findings. Gate 4 passed in PR #6. | Commit `e4fec44ccc0639fae1b0dd1188f1cf8c94296a39`, [Actions run](https://github.com/Yu2uu/SuperSafeCode/actions/runs/38598774956) |

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

The `systemd-homed` and `Archive::Tar` exceptions were re-reviewed on 2026-10-18
and now expire on **2026-11-17**; the other six expire on **2026-11-05**.
Recheck upstream fixes and applicability
before expiry. Remove exceptions when resolved; any renewal requires a fresh
documented review. CI must continue to fail if an asserted-absent component returns.

The [subsequent main run](https://github.com/Yu2uu/SuperSafeCode/actions/runs/39096484471/job/117583902938)
at commit `ae20791922223ca4152ed1a0c99b7c2e0b9b622a` passed startup, non-root,
component-absence, and Dockerfile checks, but failed the image scan. The maintainer
provided the scan output dated 2026-10-18: three HIGH findings, zero CRITICAL,
and 37 suppressed findings. The three blockers correspond exactly to the two
exceptions that expired on October 17:

| CVE | Packages | Blocking findings |
| --- | --- | --- |
| CVE-2026-16742 | `libsystemd0`, `libudev1` | 2 |
| CVE-2026-9538 | `perl-base` | 1 |

No additional unsuppressed findings were reported in that scan, including in
the Python package entries at the configured HIGH/CRITICAL threshold. This
demonstrates that expired exceptions stop suppressing otherwise blocking findings.

The October 18 review found that Debian still lists the Trixie source packages
as vulnerable for [CVE-2026-16742](https://security-tracker.debian.org/tracker/CVE-2026-16742)
and [CVE-2026-9538](https://security-tracker.debian.org/tracker/CVE-2026-9538).
No fixed Trixie version was listed. The latest successful component-absence
assertions support a 30-day renewal of the same binary-package scope for local/CI
use. This is a renewed applicability decision, not a patch or proof that the
whole scan now passes. Every new build must still pass those assertions and the
vulnerability policy. With identical findings and the renewed exceptions loaded,
the expected result is zero unsuppressed findings and 40 suppressed findings.
That is an expectation, not a new scan result; CI validation remains pending.
