"""Credential loaders backed by YAML profiles and environment variables."""

import os
from pathlib import Path

import yaml

def _load_login_data(path="data/login.yaml"):
    """Read login profile data from disk.

    Args:
        path: Path to the login YAML test data file.
    """
    data_path = Path(path)
    with data_path.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}
    
def load_login_credentials(profile="valid"):
    """Resolve username and password for a given profile.

    Args:
        profile: Credential profile key in login test data.
    """
    data = _load_login_data()
    profile_data = data.get(profile, {})

    username = None
    password = None

    username_env = profile_data.get("username_env")
    password_env = profile_data.get("password_env")

    if username_env:
        username = os.getenv(username_env)
    if password_env:
        password = os.getenv(password_env)

    if not username or not password:
        raise RuntimeError(
            f"Missing credentials for {profile}. Set env variables for {username_env} and {password_env}"
        )
    
    return {"username": username, "password": password}
