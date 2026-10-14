"""Prove selected tests reject known-bad code, without editing the working tree."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def expect_failure(source, test_name, folder):
    target = folder / "main.py"
    target.write_text(source, encoding="utf-8")
    env = dict(os.environ)
    env.pop("NOTES_TEST_URL", None)
    env["NOTES_TEST_SOURCE"] = str(target)
    env["PYTHONPATH"] = str(ROOT / "tests")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "unittest", f"test_security.SecurityTests.{test_name}", "-v"],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    output = result.stdout + result.stderr
    # An import failure or infrastructure error is not proof that a control worked.
    if result.returncode != 1 or f"FAIL: {test_name}" not in output or "ERROR:" in output:
        print(output)
        raise SystemExit(f"Control validation failed: {test_name}")
    print(f"PASS: {test_name} rejected known-bad code (exit 1)")


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise SystemExit("Mutation target changed; review the proof rather than skipping it")
    return source.replace(old, new, 1)


def main():
    current = (ROOT / "app/main.py").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        cases = [
            ("test_get_requires_authentication", 'if request.endpoint in {"get_note", "create_note"}:',
             'if request.endpoint in {"create_note"}:'),
            ("test_headers_on_success_and_errors", 'response.headers["X-Content-Type-Options"] = "nosniff"',
             'response.headers["X-Content-Type-Options"] = "invalid"'),
            ("test_injection_cannot_select_existing_note",
             'query = "SELECT id, owner, body FROM notes WHERE id = ?"\n        row = conn.execute(query, (note_id,)).fetchone()',
             'query = f"SELECT id, owner, body FROM notes WHERE id = {note_id}"\n        row = conn.execute(query).fetchone()'),
        ]
        for name, old, new in cases:
            expect_failure(replace_once(current, old, new), name, folder)


if __name__ == "__main__":
    main()
