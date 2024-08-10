from GLOBAL import GLOBAL
from Modules.NewApp import NewApp
from LIB.Github import Github
from pyvirtualdisplay import Display
import os
import inspect
import apps


def get_functions() -> dict[str, callable]:
    return {
        name: function
        for name, function in [
            o for o in inspect.getmembers(apps) if inspect.isfunction(o[1])
        ]
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

    if GLOBAL.Args.new:
        NewApp()()
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
