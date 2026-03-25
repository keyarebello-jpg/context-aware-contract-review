#!/usr/bin/env python3
"""
main.py
-------
Entry point for the Contract Compliance Graph system.

Usage:
    python main.py                          # Use default data files
    python main.py --output report.json     # Also save JSON report
    python main.py --format json            # Print JSON only
    python main.py --contract path/to/contract.json  # Custom contract
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure src/ is importable from the project root
sys.path.insert(0, str(Path(__file__).parent))

from src.compliance_checker import run_compliance_check, format_report_text


DATA_DIR = Path(__file__).parent / "data"


def main():
    parser = argparse.ArgumentParser(
        description="Contract Compliance Graph — Regulatory Gap Analyser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --format json --output report.json
  python main.py --contract data/contract.json
        """
    )
    parser.add_argument(
        "--contract",
        default=DATA_DIR / "contract.json",
        help="Path to contract JSON file"
    )
    parser.add_argument(
        "--company",
        default=DATA_DIR / "company_profile.json",
        help="Path to company profile JSON file"
    )
    parser.add_argument(
        "--regulations",
        default=DATA_DIR / "regulations.json",
        help="Path to regulations JSON file"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output",
        help="Save report to this file path (optional)"
    )
    args = parser.parse_args()

    print("\n⚙️  Running compliance analysis...\n", file=sys.stderr)

    try:
        report = run_compliance_check(
            contract_path=args.contract,
            company_profile_path=args.company,
            regulations_path=args.regulations,
        )
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Output ---
    if args.format == "json":
        output_str = json.dumps(report, indent=2)
    else:
        output_str = format_report_text(report)

    print(output_str)

    # --- Optionally save ---
    if args.output:
        out_path = Path(args.output)
        with open(out_path, "w", encoding="utf-8") as f:
            if args.format == "json":
                f.write(output_str)
            else:
                # Always save JSON when writing to file for programmatic use
                f.write(json.dumps(report, indent=2))
        print(f"\n📄 Report saved to: {out_path}", file=sys.stderr)

    # Exit with non-zero if critical gaps found
    critical_gaps = [
        g for g in report["compliance_gaps"]
        if g["severity"] == "critical"
    ]
    if critical_gaps:
        sys.exit(2)


if __name__ == "__main__":
    main()
