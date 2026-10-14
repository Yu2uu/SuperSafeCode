# SuperSafeCode
A Flask/SQLite notes API used to demonstrate security gates in GitHub Actions.
This is a portfolio project for local and CI use.

The pipeline includes secret scanning, static analysis, dependency auditing,
container scanning, a ZAP baseline scan, and security regression tests.
The runtime and regression gates are awaiting their first CI validation;
pipeline hardening remains a separate step.

Evidence: [SAST](docs/evidence/sast.md),
[dependencies](docs/evidence/dependencies.md),
[container security](docs/evidence/container.md), and
[runtime and regression tests](docs/evidence/runtime.md).

## Run locally on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:NOTES_API_KEY = "local-demo-only"
.\.venv\Scripts\python.exe -m flask --app app.main run --host 127.0.0.1 --port 8000
```

Use the development server only for local practice. `/healthz` is public;
`POST /notes` and `GET /notes/<id>` require `X-API-Key`. Creating a note requires
a JSON object with nonempty string `owner` and `body` fields. The shared key
grants access to all notes. SQLite defaults to `notes.db`; set `NOTES_DB_PATH`
to use another path. The container runs Gunicorn on port 8000 as a non-root user.

## Run security tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/verify_security_controls.py
```

The first command uses an isolated temporary database. The second proves that
selected tests reject deliberately reintroduced weaknesses.
CI also runs the tests over HTTP against a disposable container.
