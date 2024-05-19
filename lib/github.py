import os
from constants import PATHS, LINKS
from base.config import Config
import datetime

config = Config()

class Github:

    @classmethod
    def push_release(cls, path: str) -> str:
        filename = path.split("/")[-1]
        os.system(
            f"cd {PATHS.APPS_DIR} && \
			gh release delete-asset apps {filename} -y"
        )
        os.system(
            f"cd {PATHS.APPS_DIR} && \
			gh release upload apps {filename} --clobber {filename}"
        )
        return LINKS.APPS_RELEASE(filename)

    @classmethod
    def push_index(cls, message: str = "") -> str:
        message = (
            "[ "
            + datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
            + " ]"
            + message
        )
        os.system(
            f"cd {PATHS.INDEX_DIR} && git add index.json && git commit -m '{message}' && git push -f"
        )
        print("Pushed index to git")