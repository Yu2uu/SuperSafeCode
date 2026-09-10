# SAST gate validation

## A — Registry-rule coverage

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