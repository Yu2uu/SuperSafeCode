"""Require zizmor to reject unsafe variants of the real workflow via stdin."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main():
    scanner = shutil.which('zizmor')
    if scanner is None:
        candidate = Path(sys.executable).parent / ('zizmor.exe' if sys.platform == 'win32' else 'zizmor')
        if not candidate.is_file():
            raise SystemExit('Install tools/requirements.txt before running this proof')
        scanner = str(candidate)
    current = (ROOT / '.github/workflows/security.yml').read_text(encoding='utf-8')
    unpinned, count = re.subn(r'actions/checkout@[0-9a-f]{40}', 'actions/checkout@v5', current, count=1)
    if count != 1 or 'permissions:\n  contents: read\n' not in current:
        raise SystemExit('Workflow structure changed; review the negative controls')
    cases = {
        'unpinned-uses': unpinned,
        'excessive-permissions': current.replace('permissions:\n  contents: read\n', 'permissions: write-all\n', 1),
    }
    for expected, source in cases.items():
        result = subprocess.run(
            [scanner, '--offline', '--persona', 'pedantic', '--min-severity', 'low',
             '--strict-collection', '--no-config', '--format', 'json', '-'],
            input=source, text=True, capture_output=True, cwd=ROOT,
        )
        if result.returncode not in {12, 13, 14}:
            raise SystemExit(f'Expected a security finding, got exit {result.returncode}: {result.stderr}')
        findings = json.loads(result.stdout)
        if not any(f['ident'] == expected and not f.get('ignored') for f in findings):
            raise SystemExit(f'Missing expected finding: {expected}')
        print(f'PASS: {expected} rejected (exit {result.returncode})')


if __name__ == '__main__':
    main()
