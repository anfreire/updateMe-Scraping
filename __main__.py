from GLOBAL import GLOBAL
from utils.newApp import NewApp
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


if __name__ == "__main__":
    display = None
    functions = get_functions()

    if GLOBAL.Args.new:
        NewApp()()

    else:
        if not GLOBAL.Args.xhost:
            display = Display(visible=0, size=(800, 600))
            display.start()
        if GLOBAL.Args.app and len(GLOBAL.Args.app):
            for app in GLOBAL.Args.app:
                app_name = app.lower()
                if app_name in functions:
                    functions[app_name]()
                else:
                    app_name = app_name.replace(" ", "_")
                    if app_name in functions:
                        functions[app_name]()
                    else:
                        GLOBAL.Log(f"App {app} not found", level="ERROR")
        else:
            for app in functions:
                functions[app]()
        for analysis in GLOBAL.VirusTotal.wait_queue():
            if analysis.infected:
                GLOBAL.Index[analysis.appname]["providers"][analysis.provider][
                    "safe"
                ] = False
                GLOBAL.Index.write()

    GLOBAL.Index.write()
    Github.push_index()
    for file in os.listdir(GLOBAL.Paths.Directories.Apps):
        os.remove(os.path.join(GLOBAL.Paths.Directories.Apps, file))
    if display is not None:
        display.stop()
