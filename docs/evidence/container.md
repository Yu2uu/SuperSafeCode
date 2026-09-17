# Container gate validation

## Baseline preparation

- Added a runnable container using Gunicorn
- Application dependencies are installed from requirements.txt
- Application source is copied explicitly
- Added .dockerignore to exclude Git history, local environments,
  databases, and environment files from the build context
- Existing floating base tag and default root user remain
  for evaluation by the container gate
- Build, runtime checks, and security scan: not yet performed

Added .dockerignore to prevent Git history from entering the
build context. This is preventative hardening

## A — Initial image scan

- Commit: 157894b8069ca660f3a8a02e4cf34ad64bfbd69e
- Workflow run: https://github.com/Yu2uu/SuperSafeCode/actions/runs/34606985097/job/103287708128?pr=5
- Base reference: python:latest
- Reported environment: Debian 13.6; Python 3.14 paths.
- Scanner: Trivy 0.74.0.
- Policy: block HIGH and CRITICAL findings.
- Image scan reported:
  - 553 Debian package vulnerability findings.
  - 2 additional Python package findings involving msgpack
    and setuptools.
  - No findings at the selected severity threshold in the
    Flask, Werkzeug, or Gunicorn metadata entries.
- Scanner warning: third-party SBOM data may affect accuracy.
- Interpretation: the image contains components beyond those
  covered by the application requirements audit.
- Limitations: counts are scanner findings, not a verified count
  of unique exploitable vulnerabilities. The origin of the
  additional Python findings needs investigation.

### Runtime and configuration validation

- Startup: the container health endpoint returned `ok`.
- Runtime identity: `uid=0(root) gid=0(root) groups=0(root)`.
- Dockerfile scan: DS-0002 (HIGH), missing a non-root USER.
- Reported checks: 20 total; 19 successes and 1 failure.
- Conclusion: static analysis identified the missing non-root
  configuration, and runtime inspection confirmed root execution.

  ## B — Non-root remediation

- Commit: `b559c6d80479603b99f3e2a18f6d4051a3f74376`
- Workflow run: https://github.com/Yu2uu/SuperSafeCode/actions/runs/35243040738/job/105276073102?pr=5
- Added a non-root runtime user with UID/GID 10001.
- Configured a writable SQLite directory at /data.
- Runtime inspection confirmed UID 10001.
- Startup: {"status":"ok"}
- Dockerfile scan: Clean - no security findings
- Image vulnerability scan: still failed.
- Conclusion: non-root execution was established; image package
  vulnerabilities remain a separate remediation task.


  ## C — Smaller base image change

- Commit: `471053d86c9e9c0e6f849c341e2d8d2d8330c39e`
- Workflow run: https://github.com/Yu2uu/SuperSafeCode/actions/runs/35244800601/job/105282127057?pr=5
- Changed base from python:latest to python:3.12-slim-bookworm.
- Previous reported total: 649 (593 HIGH, 56 CRITICAL).
- New reported total: 63 (58 HIGH, 5 CRITICAL).
- Reduction: 586 findings, approximately 90%
- Result: image scan still fails the unchanged HIGH/CRITICAL policy
- Interpretation: the smaller base substantially reduced reported
  findings, but further investigation and remediation is required
- Limitation: totals describe scanner findings, not unique exploitable
  vulnerabilities. Image contents and advisory data can change between runs.

  Additionaly \/
### Remaining-finding review

The remaining findings include both available fixes and entries
without a listed fixed version. The next remediation applies
available Debian package updates without changing scan thresholds.

CVE-2023-45853 requires package-specific applicability review:
Debian documents that the affected MiniZip code is not built
into the relevant Bookworm zlib binary packages.

Reference:
https://security-tracker.debian.org/tracker/CVE-2023-45853