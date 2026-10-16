# DevOps Log Analyzer with Python

A command-line tool built with Python to parse application logs into structured severity counts, resiliently handle malformed records, and output machine-readable JSON summaries for CI/CD automation.

## Project Objectives

- **Raw Log Reading**: Parse log files line-by-line safely using Python context managers.
- **Resilient Parsing**: Handle malformed log lines gracefully without crashing the analyzer.
- **Severity Aggregation**: Count occurrences of `INFO`, `WARNING`, and `ERROR` records.
- **CLI & Automation**: Provide flexible command-line arguments and structured JSON output.
- **CI/CD Integration**: Return actionable exit codes based on error thresholds.

## Setup

1. **Activate Virtual Environment**:
   ```bash
   source .venv/bin/activate
   ```
2. **Verify Python Environment**:
   ```bash
   which python3
   ```
