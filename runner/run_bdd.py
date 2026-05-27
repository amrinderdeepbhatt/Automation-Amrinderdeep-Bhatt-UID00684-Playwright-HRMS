"""CLI entry point to run BDD tests with environment options."""

import argparse
import os
import subprocess
import sys

def main():
    """Parse CLI flags and invoke pytest from the project root."""
    parser = argparse.ArgumentParser(description="Run BDD scenarios")
    parser.add_argument("--env", default="qa")
    parser.add_argument("--browser", default="chromium")
    parser.add_argument("--headless", default="true", choices=["true", "false"])
    parser.add_argument("--tags", default=None, help="pytest marker expression")
    parser.add_argument("--path", default="steps")
    parser.add_argument("--workers", default=None, help="Number of pytest-xdist workers (e.g. 2 or 'auto')")
    args = parser.parse_args()

    cmd = [sys.executable, "-m", "pytest", args.path, f"--browser={args.browser}"]

    if args.workers:
        cmd.extend(["-n", str(args.workers)])

    if args.headless.lower() == "false":
        cmd.append("--headed")

    if args.tags:
        cmd.extend(["-m", args.tags])

    env_vars = os.environ.copy()
    env_vars["TEST_ENV"] = args.env

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    subprocess.run(
        cmd,
        check=True,
        env=env_vars,
        cwd=project_root
    )


if __name__ == "__main__":
    main()
