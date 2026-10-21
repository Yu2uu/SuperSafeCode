# SAST gate validation

## A - Registry-rule coverage

- Commit: `bb5a0f7d384e71472f356dac946e8851c44f5e99`
- Workflow run: https://github.com/Yu2uu/SuperSafeCode/actions/runs/34467633038?pr=3
- Rule packs: p/security-audit, p/python, p/flask
- Findings:
  - python.flask.security.audit.debug-enabled.debug-enabled
  - python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host
- Result: failed with two Flask configuration findings.
- Coverage gap: the interpolated SQLite query in app/main.py
  was not reported.
- Conclusion: this rule selection did not detect this SQL pattern.

## B - Expanded SQL-pattern coverage

- Commit: `cec88d774d44d5bdafde98f526f0277c10d60be6`
- Workflow run: https://github.com/Yu2uu/SuperSafeCode/actions/runs/34481135508/job/102883935640?pr=3
- Change: added a custom rule for f-strings passed directly
  or through a local variable into execute().
- Application finding: `semgrep.interpolated-sql-execute`
- Location: `app/main.py`, query execution in `get_note`.
- Result: the unchanged vulnerable query is now reported.
- Conclusion: the custom rule closes the demonstrated
  detection gap for this SQL construction pattern.
- Limitation: this is syntactic detection, not universal SQL
  injection coverage or proof that input is attacker-controlled.

## C - Remediation and final validation

The application now uses SQLite placeholders and passes values separately for
reads and writes. It runs under Gunicorn in the container. Custom rule fixtures
exercise unsafe and safe SQL patterns, and behavioral tests reject the tested
SQL injection payloads.

Gate 2 passed in [main run 39307160136](https://github.com/Yu2uu/SuperSafeCode/actions/runs/39307160136)
at `cd635acac40f55de30d565d9056d406709576199`, checked on 2026-10-19.
This closes the demonstrated pattern-specific gap; it does not
establish universal SQL injection detection.
