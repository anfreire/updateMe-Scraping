import os
import datetime
import subprocess
from GLOBAL import GLOBAL, LogLevel


class Github:

    @staticmethod
    def push_release(path: str) -> str:
        filename = path.split("/")[-1]
        delete_result = subprocess.run(
            f"cd {GLOBAL.Paths.Directories.Apps} && gh release delete-asset apps {filename} -y",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if delete_result.returncode != 0:
            GLOBAL.Log(f"Error deleting {filename} from release", level=LogLevel.ERROR)
        else:
            GLOBAL.Log(f"Deleted {filename} from release")
        upload_result = subprocess.run(
            f"cd {GLOBAL.Paths.Directories.Apps} && gh release upload apps {filename}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if upload_result.returncode != 0:
            GLOBAL.Log(
                f"Error uploading {filename} to release. {upload_result.stderr.decode()}",
                level=LogLevel.CRITICAL,
            )
        else:
            GLOBAL.Log(f"Uploaded {filename} to release")
        return f"https://github.com/anfreire/UpdateMe-Data/releases/download/apps/{filename}"

    @staticmethod
    def push_index(message: str = "") -> None:
        message = (
            "[ "
            + datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
            + " ]"
            + message
        )
        os.system(
            f"cd {GLOBAL.Paths.Directories.Data} && git add index.json && git commit -m '{message}' && git push -f"
        )
        GLOBAL.Log(f"Pushed index.json to Github")

    @staticmethod
    def push_icon(path: str) -> str:
        filename = path.split("/")[-1]
        push_result = subprocess.run(
            f"cd {GLOBAL.Paths.Directories.Icons} && git add {filename} && git commit -m '{filename}' && git push -f",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if push_result.returncode != 0:
            GLOBAL.Log(
                f"Error pushing {filename}. {push_result.stderr.decode()}",
                level=LogLevel.CRITICAL,
            )
        else:
            GLOBAL.Log(f"Pushed {filename} to Github")
        return f"https://raw.githubusercontent.com/anfreire/updateMe-Data/main/icons/{filename}"

    @staticmethod
    def push_categories() -> None:
        os.system(
            f"cd {GLOBAL.Paths.Directories.Data} && git add categories.json && git commit -m 'categories.json' && git push -f"
        )
        GLOBAL.Log(f"Pushed categories.json to Github")
