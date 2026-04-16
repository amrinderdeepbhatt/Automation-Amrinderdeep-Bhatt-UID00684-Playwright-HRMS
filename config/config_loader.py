"""Configuration loader for environment and browser settings."""

from dotenv import load_dotenv
import yaml


class ConfigLoader:
    """
    Loads config values from a YAML file and provides simple getters
    for commonly used settings like env, url, and browser options.
    """

    def __init__(self, env=None, path="config/config.yaml"):
        """
        Initialize the loader.

        Args:
            env (str, optional): Override environment from config.
            path (str): Path to the YAML config file.
        """

        load_dotenv()

        with open(path, "r") as file:
            self.config = yaml.safe_load(file)

        if env:
            self.config["env"] = env

    def get(self, key):
        """Return a value from config by key.

        Args:
            key: Configuration key name.
        """
        return self.config.get(key)

    def get_url(self):
        """Return base URL for the current environment."""
        env = self.config["env"]
        return self.config["urls"][env]

    def get_browser(self):
        """Return configured browser name."""
        return self.config["browser"]["name"]

    def is_headless(self):
        """Return whether browser should run in headless mode."""
        return self.config["browser"]["headless"]
    