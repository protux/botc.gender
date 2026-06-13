from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from botc_gender.convert import convert_script
from botc_gender.data import load_data_store
from botc_gender.formats.app_schema import Strategy
from botc_gender.pdf_targets import PDF_TARGET_INFO, PdfTarget, format_pdf_instructions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="botc-gender",
        description="Convert Blood on the Clocktower scripts to gender-inclusive German.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert a script JSON (ID list) to a full gendered German script.",
    )
    convert_parser.add_argument("input", type=Path, help="Input script JSON path")
    convert_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output JSON path (default: stdout)",
    )
    convert_parser.add_argument(
        "--strategy",
        choices=["official-override", "custom-suffix"],
        default="official-override",
        help="ID strategy for output characters",
    )
    convert_parser.add_argument(
        "--suffix",
        default="_de",
        help="Suffix for custom-suffix strategy (default: _de)",
    )
    convert_parser.add_argument(
        "--pdf-target",
        choices=list(PDF_TARGET_INFO.keys()),
        help="Print workflow instructions for a PDF generation tool",
    )
    convert_parser.add_argument(
        "--data-dir",
        type=Path,
        help="Override data directory (default: project data/)",
    )

    subparsers.add_parser(
        "pdf-targets",
        help="List available PDF target workflows",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "pdf-targets":
        for key, info in PDF_TARGET_INFO.items():
            print(f"{key}: {info['title']} ({info['url']})")
        return 0

    if args.command == "convert":
        data_dir = args.data_dir
        store = load_data_store(data_dir) if data_dir else load_data_store()

        raw = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            print("Input must be a JSON array", file=sys.stderr)
            return 1

        result = convert_script(
            store,
            raw,
            strategy=args.strategy,
            suffix=args.suffix,
        )
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"

        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)

        if args.pdf_target:
            print("\n" + format_pdf_instructions(args.pdf_target), file=sys.stderr)

        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
