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
            GLOBAL.Log(f"Deleted {filename} from release")
        upload_result = subprocess.run(
            f"cd {GLOBAL.Paths.AppsDir} && gh release upload apps {filename}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if upload_result.returncode != 0:
            GLOBAL.Log(f"Error uploading {filename} to release. {upload_result.stderr.decode()}", level="CRITICAL")
        else:
            GLOBAL.Log(f"Uploaded {filename} to release")
        return f"https://github.com/anfreire/UpdateMeData/releases/download/apps/{filename}"

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
        GLOBAL.Log(f"Pushed index.json to Github")