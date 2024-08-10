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

    @staticmethod
    def remove_unused_assests() -> None:
        command = f"cd {GLOBAL.Paths.Directories.Apps} && gh release view apps | awk '{{print $2}}'"
        uploaded_files = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        uploaded_files = [
            file.strip()
            for file in uploaded_files.stdout.decode().split("\n")
            if file.strip().endswith(".apk")
        ]
        used_files = []
        for app in GLOBAL.Index.values():
            for provider in app.providers.values():
                download = provider["download"]
                filename = download.split("/")[-1]
                used_files.append(filename)
        diff = set(uploaded_files) - set(used_files)
        if len(diff) == 0:
            return
        for file in diff:
            delete_result = subprocess.run(
                f"cd {GLOBAL.Paths.Directories.Apps} && gh release delete-asset apps '{file}' -y",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if delete_result.returncode != 0:
                GLOBAL.Log(f"Error deleting {file} from release", level=LogLevel.ERROR)
            else:
                GLOBAL.Log(f"Deleted {file} from release")

    def remove_unused_icons() -> None:
        command = f"cd {GLOBAL.Paths.Directories.Icons} && git ls-files"
        uploaded_files = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        uploaded_files = [
            file.strip()
            for file in uploaded_files.stdout.decode().split("\n")
            if file.strip().endswith(".png")
        ]
        used_files = []
        for app in GLOBAL.Index.values():
            filename = app.icon.split("/")[-1]
            used_files.append(filename)
        diff = set(uploaded_files) - set(used_files)
        if len(diff) == 0:
            return
        for file in diff:
            delete_result = subprocess.run(
                f"cd {GLOBAL.Paths.Directories.Icons} && git rm {file}; rm {file}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if delete_result.returncode != 0:
                GLOBAL.Log(f"Error deleting {file} from release", level=LogLevel.ERROR)
            else:
                GLOBAL.Log(f"Deleted {file} from release")
                os.system(
                    f"cd {GLOBAL.Paths.Directories.Icons} && git commit -m 'Removed unused icons' && git push -f"
                )
                GLOBAL.Log(f"Removed unused icons from Github")
