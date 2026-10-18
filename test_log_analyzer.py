import json
import os

import pytest

from log_analyzer import (
    analyze_log,
    build_parser,
    main,
    parse_log_line,
    print_summary,
    save_report,
)


@pytest.mark.parametrize(
    "line, expected_level, expected_message, expected_ts",
    [
        (
            "2026-09-29T09:00:00Z INFO api started",
            "INFO",
            "api started",
            "2026-09-29T09:00:00Z",
        ),
        (
            "2026-09-29T09:02:00Z WARNING disk usage reached 82 percent",
            "WARNING",
            "disk usage reached 82 percent",
            "2026-09-29T09:02:00Z",
        ),
        (
            "2026-09-29T09:03:00Z ERROR database connection failed",
            "ERROR",
            "database connection failed",
            "2026-09-29T09:03:00Z",
        ),
    ],
)
def test_parse_valid_lines(line, expected_level, expected_message, expected_ts):
    result = parse_log_line(line)
    assert result is not None
    assert result["level"] == expected_level
    assert result["message"] == expected_message
    assert result["timestamp"] == expected_ts


@pytest.mark.parametrize(
    "line",
    [
        "BROKEN LINE",
        "SINGLEWORD",
        "",
        "   ",
        "2026-09-29T09:00:00Z DEBUG verbose trace",
        "INVALID_TIMESTAMP INFO server starting",
        "2026-99-99T99:99:99Z INFO invalid date numbers",
        "2026/09/29 INFO missing time component",
    ],
)
def test_parse_malformed_lines(line):
    assert parse_log_line(line) is None


def test_analyze_log_with_sample():
    report = analyze_log("sample.log")
    assert report["counts"]["INFO"] == 2
    assert report["counts"]["WARNING"] == 1
    assert report["counts"]["ERROR"] == 2
    assert report["malformed_lines"] == 1


def test_analyze_empty_file(tmp_path):
    empty_file = tmp_path / "empty.log"
    empty_file.write_text("", encoding="utf-8")

    report = analyze_log(str(empty_file))
    assert report["counts"]["INFO"] == 0
    assert report["counts"]["WARNING"] == 0
    assert report["counts"]["ERROR"] == 0
    assert report["malformed_lines"] == 0


def test_analyze_all_malformed_file(tmp_path):
    malformed_file = tmp_path / "corrupted.log"
    content = "BROKEN LINE 1\nINVALID_LEVEL\nBAD_TIMESTAMP INFO test\n"
    malformed_file.write_text(content, encoding="utf-8")

    report = analyze_log(str(malformed_file))
    assert report["counts"]["INFO"] == 0
    assert report["counts"]["WARNING"] == 0
    assert report["counts"]["ERROR"] == 0
    assert report["malformed_lines"] == 3


def test_print_summary(capsys):
    report = {
        "source": "dummy.log",
        "counts": {"INFO": 5, "WARNING": 2, "ERROR": 1},
        "malformed_lines": 3,
    }
    print_summary(report)
    captured = capsys.readouterr()

    assert "Log summary" in captured.out
    assert "INFO: 5" in captured.out
    assert "WARNING: 2" in captured.out
    assert "ERROR: 1" in captured.out
    assert "Malformed lines: 3" in captured.out


def test_save_report(tmp_path):
    report = {
        "source": "sample.log",
        "counts": {"INFO": 2, "WARNING": 1, "ERROR": 2},
        "malformed_lines": 1,
    }
    output_path = tmp_path / "report.json"
    save_report(report, str(output_path))

    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["source"] == "sample.log"
    assert data["counts"]["ERROR"] == 2
    assert data["malformed_lines"] == 1


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["app.log"])
    assert args.log_file == "app.log"
    assert args.output == "report.json"
    assert args.max_errors is None


def test_main_cli_success(tmp_path):
    output_path = tmp_path / "out.json"
    exit_code = main(["sample.log", "--output", str(output_path), "--max-errors", "5"])
    assert exit_code == 0
    assert output_path.exists()


def test_main_cli_threshold_exceeded(tmp_path):
    output_path = tmp_path / "out.json"
    # sample.log has 2 errors; threshold is 1 -> exit 2
    exit_code = main(["sample.log", "--output", str(output_path), "--max-errors", "1"])
    assert exit_code == 2


def test_main_cli_missing_file(tmp_path):
    output_path = tmp_path / "out.json"
    exit_code = main(["non_existent_file.log", "--output", str(output_path)])
    assert exit_code == 1


def test_main_cli_permission_denied(tmp_path):
    no_perm_file = tmp_path / "no_perm.log"
    no_perm_file.write_text("2026-09-29T09:00:00Z INFO test\n", encoding="utf-8")
    os.chmod(str(no_perm_file), 0)

    try:
        exit_code = main([str(no_perm_file), "--output", str(tmp_path / "out.json")])
        assert exit_code == 1
    finally:
        os.chmod(str(no_perm_file), 0o644)
