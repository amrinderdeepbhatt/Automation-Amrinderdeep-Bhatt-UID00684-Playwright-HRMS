import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Run BDD scenarios")
    parser.add_argument("--env", default="qa")
    parser.add_argument("--browser", default="chromium")
    parser.add_argument("--headless", default="true", choices=["true", "false"])
    parser.add_argument("--tags", default=None, help="pytest marker expression")
    parser.add_argument("--path", default="steps")
    args = parser.parse_args()

    cmd = ["pytest", args.path, f"--browser={args.browser}"]

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