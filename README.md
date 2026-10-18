# DevOps Log Analyzer with Python

[![CI Pipeline](https://github.com/duytrancoder/Python_LogAnalyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/duytrancoder/Python_LogAnalyzer/actions/workflows/ci.yml)

A resilient Python CLI tool that parses application logs into structured severity metrics, gracefully handles malformed records, and exports machine-readable JSON reports for CI/CD automation.

## Features

- **Robust Log Parsing**: Validates timestamps, severity levels (`INFO`, `WARNING`, `ERROR`), and arbitrary log messages.
- **Resilience Against Malformed Logs**: Skips unparseable lines without crashing and tallies `malformed_lines`.
- **JSON Report Export**: Automatically saves structured summaries formatted for downstream automations.
- **CI/CD Quality Gate**: Configurable `--max-errors` threshold returning pipeline-friendly exit status codes.
- **Zero Third-Party Dependencies**: Built entirely using Python standard libraries (`argparse`, `json`, `sys`, `unittest`).

---

## Getting Started

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/duytrancoder/Python_LogAnalyzer.git
cd Python_LogAnalyzer

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
```

---

## Usage

### Basic Execution

Analyze a log file and write the report to the default `report.json`:

```bash
python3 log_analyzer.py sample.log
```

### Specify Custom Output File

```bash
python3 log_analyzer.py sample.log --output custom_report.json
```

### Enforce CI/CD Error Threshold

Fail the job (exit status code `2`) if the number of `ERROR` lines exceeds your maximum allowed limit:

```bash
# Example: Allow up to 1 error (fails if > 1)
python3 log_analyzer.py sample.log --max-errors 1
```

---

## Running with Docker (Zero Host Dependencies)

Run the analyzer anywhere without requiring Python installed:

### Option A: Using Pre-built Image from GHCR (No Build Required)

```bash
docker run --rm -v "$(pwd)":/data:ro ghcr.io/duytrancoder/python_loganalyzer:latest /data/sample.log
```

### Option B: Build & Run Locally

```bash
# 1. Build the lightweight image
docker build -t log-analyzer .

# 2. Run analysis by mounting your log file directory
docker run --rm -v "$(pwd)":/data:ro log-analyzer /data/sample.log

# 3. Enforce CI threshold inside Docker
docker run --rm -v "$(pwd)":/data:ro log-analyzer /data/sample.log --max-errors 1
```

---

## Exit Status Codes

| Code | Meaning | Description |
|:---:|:---|:---|
| **`0`** | **Success** | Analysis completed successfully within acceptable thresholds. |
| **`1`** | **File Error** | Missing file, permission denied, or OS I/O failure. |
| **`2`** | **Threshold Failed** | `ERROR` count exceeded the `--max-errors` threshold in CI check. |

---

## Code Quality & Testing

### 1. Run Linter (Ruff)

```bash
ruff check .
```

### 2. Run Tests with Code Coverage (Pytest)

```bash
pytest --cov=log_analyzer --cov-report=term-missing
```

---

## Automated Release (CD)

To publish a new Docker image release to GitHub Container Registry (GHCR):

```bash
git tag v1.0.0
git push origin v1.0.0
```
This automatically triggers the `.github/workflows/release.yml` pipeline.
