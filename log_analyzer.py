import argparse
from datetime import datetime
import json
import sys

LEVELS = ("INFO", "WARNING", "ERROR")


def parse_log_line(line):
    parts = line.strip().split(maxsplit=2)

    if len(parts) != 3:
        return None

    timestamp, level, message = parts

    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None

    if level not in LEVELS:
        return None

    return {
        "timestamp": timestamp,
        "level": level,
        "message": message,
    }


def analyze_log(log_file):
    counts = {level: 0 for level in LEVELS}
    malformed_lines = 0

    with open(log_file, encoding="utf-8") as file:
        for line in file:
            entry = parse_log_line(line)

            if entry is None:
                malformed_lines += 1
                continue

            counts[entry["level"]] += 1

    return {
        "source": log_file,
        "counts": counts,
        "malformed_lines": malformed_lines,
    }


def print_summary(report):
    print("Log summary")

    for level in LEVELS:
        print(f"{level}: {report['counts'][level]}")

    print(f"Malformed lines: {report['malformed_lines']}")


def save_report(report, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Analyze a simple application log."
    )
    parser.add_argument(
        "log_file",
        help="Path to the log file to analyze.",
    )
    parser.add_argument(
        "--output",
        default="report.json",
        help="Path for the JSON report (default: report.json).",
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=None,
        help="Maximum allowed ERROR count before failing the CI check.",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        report = analyze_log(args.log_file)
        save_report(report, args.output)
    except OSError as error:
        print(f"Could not process a file: {error}")
        return 1

    print_summary(report)
    print(f"JSON report written to {args.output}")

    if args.max_errors is not None and report["counts"]["ERROR"] > args.max_errors:
        print(
            f"CI check failed: ERROR count ({report['counts']['ERROR']}) "
            f"exceeds maximum threshold of {args.max_errors}."
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
