#!/usr/bin/env python3
# scripts/parse_batch.py

import re
import json
from pathlib import Path

# ---------- config ----------
BATCH_DIR = Path("./batches")                 # where batch_result_###.txt live
OUTPUT    = Path("./parsed/companyReports.json")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
# -----------------------------

block_regex = re.compile(
    r"### BEGIN COMPANY REPORT([\s\S]*?)### END COMPANY REPORT",
    re.MULTILINE
)

overall_regex = re.compile(
    r"\*\*?Overall AI-Readiness Score:\*?\*\s*([\d.]+)",  # tolerate one or two * on each side
    re.I,
)

def _get(pattern: str, block: str, flags=0, default=""):
    m = re.search(pattern, block, flags)
    return m.group(1).strip() if m else default

def parse_block(block: str) -> dict:
    return {
        "company":   _get(r"Company:\s*([^\n]+)", block, re.I),
        "sector":    _get(r"Sector:\s*([^\n]+)", block, re.I),
        "industry":  _get(r"Industry:\s*([^\n]+)", block, re.I),

        "dim1": int(_get(r"Strategy.*?:\s*(\d)/5", block, re.I, "0")),
        "dim2": int(_get(r"Analytics.*?:\s*(\d)/5", block, re.I, "0")),
        "dim3": int(_get(r"Capabilities.*?:\s*(\d)/5", block, re.I, "0")),
        "dim4": int(_get(r"Skills.*?:\s*(\d)/5", block, re.I, "0")),
        "dim5": int(_get(r"Implementation.*?:\s*(\d)/5", block, re.I, "0")),

        "overall": float(overall_regex.search(block).group(1)) if overall_regex.search(block) else 0.0,
        "evidence":  _get(r"Key Evidence Summary:\s*([\s\S]*?)\n\n\*\*Strategic AI", block, re.I),
        "strategic": _get(r"Strategic AI Positioning:\s*([\s\S]*?)\n\n\*\*Contextual", block, re.I),
        "context":   _get(r"Contextual Considerations:\s*([\s\S]*?)\n\n\*\*Confidence", block, re.I),
        "confidence":_get(r"Confidence Level:\s*([^\n]+)", block, re.I),
    }

def main() -> None:
    reports = []

    for txt_file in sorted(BATCH_DIR.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8")
        for m in block_regex.finditer(text):
            reports.append(parse_block(m.group(1)))

    OUTPUT.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(f"✓ parsed {len(reports)} company reports → {OUTPUT}")

if __name__ == "__main__":
    main()
