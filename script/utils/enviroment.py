from abstract.singleton import SingletonMeta
import json
from constants import PATHS
import os
class Environment(metaclass=SingletonMeta):
    def __init__(self):
        self.gh_key = json.load(open(PATHS.ENV))["gh"]
        self.export_env("GH_KEY", self.gh_key)
        self.clone("UpdateMe-Data", PATHS.DATA_DIR)

    def export_env(self, env: str, value: str) -> None:
        export = f"export {env}={value}"
        os.system(export)
        if export in open("/root/.bashrc").read():
            return
        os.system(f"echo '{export}' >> /root/.bashrc")
        os.system(f"source /root/.bashrc")

    def clone(self, repo: str, path: str) -> None:
        os.system(f"git clone git@github.com:anfreire/{repo}.git {path}")