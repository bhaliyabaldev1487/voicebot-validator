from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILE = ROOT / "config.yaml"


class Settings:

    def __init__(self):

        with open(CONFIG_FILE, "r") as fp:
            self.config = yaml.safe_load(fp)

    @property
    def database(self):
        return self.config["database"]

    @property
    def logging(self):
        return self.config["logging"]

    @property
    def app(self):
        return self.config["app"]


settings = Settings()
