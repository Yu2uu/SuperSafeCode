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