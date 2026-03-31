import yaml


class ConfigLoader:
    def __init__(self, env=None, path="config/config.yaml"):
        with open(path, "r") as file:
            self.config = yaml.safe_load(file)

        if env:
            self.config["env"] = env

    def get(self, key):
        return self.config.get(key)

    def get_url(self):
        env = self.config["env"]
        return self.config["urls"][env]

    def get_browser(self):
        return self.config["browser"]["name"]

    def is_headless(self):
        return self.config["browser"]["headless"]
