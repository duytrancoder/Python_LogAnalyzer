import json
import os
import tempfile
import unittest

from log_analyzer import (
    analyze_log,
    build_parser,
    main,
    parse_log_line,
    save_report,
)


class TestLogAnalyzer(unittest.TestCase):
    def test_parse_valid_lines(self):
        info_line = "2026-09-29T09:00:00Z INFO api started"
        res = parse_log_line(info_line)
        self.assertIsNotNone(res)
        self.assertEqual(res["level"], "INFO")
        self.assertEqual(res["timestamp"], "2026-09-29T09:00:00Z")
        self.assertEqual(res["message"], "api started")

        warn_line = "2026-09-29T09:02:00Z WARNING disk usage reached 82 percent"
        res = parse_log_line(warn_line)
        self.assertIsNotNone(res)
        self.assertEqual(res["level"], "WARNING")
        self.assertEqual(res["message"], "disk usage reached 82 percent")

        err_line = "2026-09-29T09:03:00Z ERROR database connection failed"
        res = parse_log_line(err_line)
        self.assertIsNotNone(res)
        self.assertEqual(res["level"], "ERROR")

    def test_parse_malformed_lines(self):
        # Fewer than 3 parts
        self.assertIsNone(parse_log_line("BROKEN LINE"))
        self.assertIsNone(parse_log_line("SINGLEWORD"))
        self.assertIsNone(parse_log_line(""))

        # Invalid severity level
        self.assertIsNone(
            parse_log_line("2026-09-29T09:00:00Z DEBUG verbose trace")
        )

        # Invalid timestamp format
        self.assertIsNone(
            parse_log_line("INVALID_TIMESTAMP INFO server starting")
        )
        self.assertIsNone(
            parse_log_line("2026-99-99T99:99:99Z INFO invalid date numbers")
        )
        self.assertIsNone(
            parse_log_line("2026/09/29 INFO missing time component")
        )

    def test_analyze_log_with_sample(self):
        report = analyze_log("sample.log")
        self.assertEqual(report["counts"]["INFO"], 2)
        self.assertEqual(report["counts"]["WARNING"], 1)
        self.assertEqual(report["counts"]["ERROR"], 2)
        self.assertEqual(report["malformed_lines"], 1)

    def test_save_report(self):
        report = {
            "source": "sample.log",
            "counts": {"INFO": 2, "WARNING": 1, "ERROR": 2},
            "malformed_lines": 1,
        }
        with tempfile.NamedTemporaryFile("w+", delete=False) as temp:
            temp_path = temp.name

        try:
            save_report(report, temp_path)
            with open(temp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["counts"]["ERROR"], 2)
            self.assertEqual(data["malformed_lines"], 1)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_main_cli_success_and_threshold(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as temp:
            temp_out = temp.name

        try:
            # 1. Normal run within threshold (max 5 errors, sample has 2) -> exit 0
            exit_code = main(["sample.log", "--output", temp_out, "--max-errors", "5"])
            self.assertEqual(exit_code, 0)

            # 2. Threshold exceeded (max 1 error, sample has 2) -> exit 2
            exit_code = main(["sample.log", "--output", temp_out, "--max-errors", "1"])
            self.assertEqual(exit_code, 2)

            # 3. Missing file -> exit 1
            exit_code = main(["non_existent.log", "--output", temp_out])
            self.assertEqual(exit_code, 1)
        finally:
            if os.path.exists(temp_out):
                os.remove(temp_out)


if __name__ == "__main__":
    unittest.main()
