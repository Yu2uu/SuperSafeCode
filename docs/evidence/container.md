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