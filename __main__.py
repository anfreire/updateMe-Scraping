from GLOBAL import GLOBAL
from Modules.NewApp import NewApp
from Modules.NewProvider import main as NewProvider
from LIB.Github import Github
from pyvirtualdisplay import Display
import os
import json
from LIB.AppBase import AppBase
from Providers.HrefFinder import HrefFinder
from Providers.Github import Github
from Providers.Modyolo import Modyolo
from Providers.Liteapks import Liteapks
from Providers.Apkdone import ApkDone
from Providers.DirectLink import DirectLink

CLASS_MAP = {
    "HrefFinder": HrefFinder,
    "Github": Github,
    "Modyolo": Modyolo,
    "Liteapks": Liteapks,
    "ApkDone": ApkDone,
    "DirectLink": DirectLink,
}


def get_functions() -> dict[str, callable]:
    with open(os.path.join(GLOBAL.Paths.Files.AppsJson), "r") as file:
        return {
            app: lambda: AppBase(
                app,
                {
                    provider: lambda: CLASS_MAP[info["class"]](*info["init_args"])(
                        *info["call_args"]
                    )
                    for provider, info in providers.items()
                },
            ).update()
            for app, providers in json.load(file).items()
        }


def clean() -> None:
    for directory in [
        os.path.join(os.path.expanduser("~"), "Downloads"),
        GLOBAL.Paths.Directories.Apps,
    ]:
        if not os.path.exists(directory):
            continue

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                GLOBAL.Log(f"Failed to delete {file_path}. Reason: {e}", level="ERROR")


if __name__ == "__main__":
    display = None
    functions = get_functions()

    if GLOBAL.Args.new_app or GLOBAL.Args.new_provider:
        NewApp()() if GLOBAL.Args.new_app else NewProvider()
        exit()
    else:

        clean()
        if not GLOBAL.Args.xhost:
            display = Display(visible=0, size=(800, 600))
            display.start()

        if GLOBAL.Args.app and len(GLOBAL.Args.app):
            for app in GLOBAL.Args.app:
                app_name = app.lower()
                if app_name in functions:
                    functions[app_name]()
                else:
                    GLOBAL.Log(f"App {app} not found", level="ERROR")
        else:
            for app in functions:
                functions[app]()

        for analysis in GLOBAL.VirusTotal.wait_queue():
            GLOBAL.Index[analysis.appname]["providers"][analysis.provider]["safe"] = (
                False if analysis.infected else True
            )
            GLOBAL.Index.write()

    GLOBAL.Index.write()
    Github.push_index()
    if display is not None:
        display.stop()
    Github.remove_unused_icons()
    Github.remove_unused_assests()
