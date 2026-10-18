# Gates 5 and 6: runtime scanning and security regression

## Scope and implementation

This batch adds a bounded ZAP baseline scan and seven security regression tests.
The same tests run through Flask's test client and against the running container
over HTTP. Local tests use an isolated temporary SQLite database. HTTP tests write
fixture notes and must only target a disposable test instance.

The tests cover:

- Public health checks and authenticated note creation/retrieval.
- Rejection of missing, empty, and incorrect API keys for reading and writing.
- SQL injection payloads failing to retrieve a seeded note.
- Security headers on successful responses, authentication failures, and 404s.
- Rejection of malformed JSON payload shapes and invalid field types.

The application now authenticates both note routes, sets response security
headers, validates submitted field types, returns JSON for unknown routes, and
closes database connections after each operation. SQL remains parameterized.
The shared API key grants access to all notes; per-user authorization is outside
this portfolio implementation.

## Evidence that the tests detect failures

`scripts/verify_security_controls.py` tests deliberately weakened temporary source copies without
changing the working tree. It requires assertion failures rather than treating
an import failure or other test error as success.

| Deliberately failing case | Expected detection |
| --- | --- |
| Historical application at commit `4c39f1c`, unauthenticated read | Authentication test fails |
| Historical application at commit `4c39f1c`, missing response headers | Header test fails |
| Current application with GET authentication removed | Authentication test fails |
| Current application with an invalid `nosniff` value | Header test fails |
| Current application with SQL interpolation reintroduced | Injection test fails |

Local validation on 2026-10-12/13: all seven application tests passed, including
over a local HTTP connection, and all five negative cases above were rejected.
These are local results, not a claim of a passing GitHub Actions run. Gate 6
repeats the seven application tests and the three mutations of current code.
The historical comparison was a local evidence check; CI does not depend on
an old branch commit remaining reachable after a squash merge.

## Gate 5 policy and its limits

[ZAP baseline scanning](https://www.zaproxy.org/docs/docker/baseline-scan/)
spiders the target and passively examines responses; it does not perform an
active exploitation scan. The initial target is `/healthz` and any paths the
spider discovers. This does not establish authenticated API coverage. The HTTP
regression tests explicitly exercise the protected note routes separately.

[Rule 10021](https://www.zaproxy.org/docs/alerts/10021/), missing
`X-Content-Type-Options`, is blocking in [.zap/rules.tsv](../../.zap/rules.tsv).
Other baseline alerts remain visible as warnings; `-I` makes those warnings
advisory. Passing this initial policy is not a claim that every ZAP warning
has been fixed.

Before scanning the application, CI scans a local fixture deliberately missing
the header. The workflow requires exit code 1 and rule 10021 in the JSON report.
It then requires the application scan to succeed under the same policy. The
fixture is excluded from the application image.

Download `runtime-security-reports` from the Actions run for the negative-control
and application JSON/HTML reports. Reports are retained for 14 days. The workflow
also prints the ZAP image digest for reproducibility of the evidence.

## Reproduce and finish

From the repository root with project dependencies installed:

```shell
python -m unittest discover -s tests -v
python scripts/verify_security_controls.py
```

Docker/ZAP execution is pending GitHub Actions validation because Docker is not
installed in the local environment. After pushing this batch:

1. Confirm all six jobs pass, including the intentional-failure proofs.
2. Inspect the ZAP reports and triage any advisory findings.
3. Record the Actions URL, exact commit SHA, and observed results here.
4. Configure the new jobs as required PR checks when ready to enforce them.

The remaining pipeline-hardening work is a separate batch. These changes do not
claim production readiness or replace the existing dependency/container gates.
