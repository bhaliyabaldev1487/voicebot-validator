"""
cli.py

Command-line entry point for Voicebot Order Flow validation.

Example:
    python cli.py \
      --transcript sample_order_call.json \
      --caller-phone 9876543210 \
      --conversation-id call_001 \
      --output-dir reports

Environment:
    DB connection can be provided either:
    1. via --db-url argument
    2. or via environment variable VOICEBOT_DB_URL
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from runner.order_validation_runner import OrderValidationRunner


DEFAULT_OUTPUT_DIR = "reports"
ENV_DB_URL = "VOICEBOT_DB_URL"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate voicebot order-flow transcript against database records."
    )

    parser.add_argument(
        "--transcript",
        required=True,
        help="Path to transcript JSON file.",
    )

    parser.add_argument(
        "--caller-phone",
        required=False,
        default=None,
        help="Actual customer phone number from call metadata.",
    )

    parser.add_argument(
        "--conversation-id",
        required=False,
        default=None,
        help="Optional conversation/call ID for report naming.",
    )

    parser.add_argument(
        "--output-dir",
        required=False,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory where JSON/HTML reports will be written. Default: {DEFAULT_OUTPUT_DIR}",
    )

    parser.add_argument(
        "--db-url",
        required=False,
        default=None,
        help=(
            "SQLAlchemy DB connection URL. "
            f"If omitted, env var {ENV_DB_URL} will be used."
        ),
    )

    parser.add_argument(
        "--db-echo",
        action="store_true",
        help="Enable SQLAlchemy echo/debug logging.",
    )

    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print full result JSON to stdout after validation.",
    )

    return parser


def resolve_db_url(cli_value: Optional[str]) -> str:
    """
    Resolve DB URL from CLI or environment variable.
    """
    db_url = cli_value or os.getenv(ENV_DB_URL)
    if not db_url:
        raise ValueError(
            "Database URL not provided. Pass --db-url or set environment variable "
            f"{ENV_DB_URL}."
        )
    return db_url


def validate_transcript_file(path: str) -> str:
    """
    Validate transcript path exists.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Transcript file not found: {path}")
    if not p.is_file():
        raise ValueError(f"Transcript path is not a file: {path}")
    return str(p)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        transcript_file = validate_transcript_file(args.transcript)
        db_url = resolve_db_url(args.db_url)

        runner = OrderValidationRunner(
            db_connection_url=db_url,
            db_echo=args.db_echo,
        )

        result = runner.run_and_write_reports(
            transcript_file=transcript_file,
            caller_phone=args.caller_phone,
            conversation_id=args.conversation_id,
            output_dir=args.output_dir,
        )

        print("\n=== Voicebot Order Validation Completed ===")
        print(f"Transcript : {transcript_file}")
        print(f"Success    : {result['validation']['success']}")
        print(f"Summary    : {result['validation']['summary']}")

        report_files = result.get("report_files", {})
        if report_files:
            print(f"JSON Report: {report_files.get('json')}")
            print(f"HTML Report: {report_files.get('html')}")

        print("\nChecks:")
        for check in result["validation"]["checks"]:
            status = "PASS" if check["passed"] else "FAIL"
            print(f" - [{status}] {check['name']}")
            if check.get("expected"):
                print(f"     expected: {check['expected']}")
            if check.get("actual"):
                print(f"     actual  : {check['actual']}")
            if check.get("details"):
                print(f"     details : {check['details']}")

        if args.print_json:
            print("\nFull JSON Result:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        return 0

    except Exception as exc:
        print("\n[ERROR] Voicebot validation failed.")
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())