import os
import datetime
import subprocess
from GLOBAL import GLOBAL

class Github:

    @classmethod
    def push_release(cls, path: str) -> str:
        filename = path.split("/")[-1]
        delete_result = subprocess.run(
            f"cd {GLOBAL.Paths.AppsDir} && gh release delete-asset apps {filename} -y",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if delete_result.returncode != 0:
            GLOBAL.Log(f"Error deleting {filename} from release", level="ERROR")
        else:
            GLOBAL.Log(f"Deleted {filename} from release", level="INFO")
        upload_result = subprocess.run(
            f"cd {GLOBAL.Paths.AppsDir} && gh release upload apps {filename}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if upload_result.returncode != 0:
            GLOBAL.Log(f"Error uploading {filename} to release. {upload_result.stderr.decode()}", level="CRITICAL")
        else:
            GLOBAL.Log(f"Uploaded {filename} to release", level="INFO")
        return f"https://github.com/anfreire/UpdateMe-Data/releases/download/apps/{filename}"

    @classmethod
    def push_index(cls, message: str = "") -> None:
        message = (
            "[ "
            + datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
            + " ]"
            + message
        )
        os.system(
            f"cd {GLOBAL.Paths.DataDir} && git add index.json && git commit -m '{message}' && git push -f"
        )
        GLOBAL.Log(f"Pushed index.json to Github", level="INFO")

    @classmethod
    def push_icon(cls, path: str) -> str:
        filename = path.split("/")[-1]
        push_result = subprocess.run(
            f"cd {GLOBAL.Paths.IconsDir} && git add {filename} && git commit -m '{filename}' && git push -f",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if push_result.returncode != 0:
            GLOBAL.Log(f"Error pushing {filename}. {push_result.stderr.decode()}", level="CRITICAL")
        else:
            GLOBAL.Log(f"Pushed {filename} to Github", level="INFO")
        return f"https://raw.githubusercontent.com/anfreire/updateMe-Data/main/icons/{filename}"