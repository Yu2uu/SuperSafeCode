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