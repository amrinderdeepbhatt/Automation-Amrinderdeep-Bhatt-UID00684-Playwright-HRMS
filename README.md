# HRMS BDD Automation

This repository contains UI automation for HRMS flows, written with Playwright + Pytest-BDD.

The goal is simple: keep scenarios readable, steps maintainable, and failures easy to debug.

## Tech Stack

- `pytest`
- `pytest-bdd`
- `playwright`
- `poetry` (dependency management option)

## Folder Guide

```text
config/      App/test configuration loading
data/        YAML test data
features/    Gherkin feature files
pages/       Page Object classes
runner/      Test runner script
steps/       BDD step definitions
utils/       Shared helpers (retry, logger, factories, credentials)
artifacts/   Logs + screenshots from executions
```

## Getting Started

### 1) Set up your environment

Using `pip` + `venv`:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

Using Poetry:

```powershell
poetry install
poetry run playwright install chromium
```

### 2) Add credentials

Credentials are read from environment variables referenced in `data/login.yaml`.
Put them in `.env` (or export them in your shell) before running tests.

## Running Tests

Run the whole suite:

```powershell
python runner/run_bdd.py --headless false
```

With Poetry:

```powershell
poetry run python runner/run_bdd.py --headless false
```

Run one step file:

```powershell
python runner/run_bdd.py --headless false --path steps/test_tc01_login_steps.py
```

With Poetry:

```powershell
poetry run python runner/run_bdd.py --headless false --path steps/test_tc01_login_steps.py
```

Run by marker:

```powershell
python runner/run_bdd.py --headless true --tags smoke
```

## Runner Options

- `--env` environment key (default: `qa`)
- `--browser` browser name (default: `chromium`)
- `--headless` `true` or `false`
- `--tags` pytest marker expression
- `--path` target path (default: `steps`)

## Parallel Execution

Run tests in parallel using `pytest-xdist` by specifying workers. Examples:

```bash
# automatic worker count
python runner/run_bdd.py --workers auto

# two workers
python runner/run_bdd.py --workers 2

# or via pytest directly
pytest -n auto steps
```

Notes:
- Each pytest-xdist worker writes logs to `artifacts/logs/test-<worker>.log` and
	screenshots to `artifacts/screenshots/<worker>/` to avoid file contention.
- Test data generators mix the xdist worker id into seeds to reduce duplicate
	generated values between parallel workers.

## Debug Artifacts

- Failure screenshots: `artifacts/screenshots/`
- Logs: `artifacts/logs/`

## Practical Notes

- This framework follows a Page Object Model pattern.
- Shared date/popup utilities are in `pages/base_page.py`.
- Retry behavior is centralized in `utils/retry.py`.
