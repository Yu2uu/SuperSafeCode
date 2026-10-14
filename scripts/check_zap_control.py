"""A red ZAP run counts only if it reported the expected missing-header alert."""

import json
from pathlib import Path
import sys


report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
alerts = [alert for site in report.get("site", []) for alert in site.get("alerts", [])]
if not any(str(alert.get("pluginid")) == "10021" for alert in alerts):
    raise SystemExit("ZAP negative control did not report missing X-Content-Type-Options (10021)")
print("PASS: ZAP reported missing X-Content-Type-Options on the negative control")
