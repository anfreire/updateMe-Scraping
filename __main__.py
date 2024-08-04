from GLOBAL import GLOBAL
from utils.newApp import NewApp
from LIB.Github import Github
from pyvirtualdisplay import Display
import os
import inspect
import apps

funs = {
    name: function
    for name, function in [
        o for o in inspect.getmembers(apps) if inspect.isfunction(o[1])
    ]
}

if __name__ == "__main__":
    display = None
    pushChanges = True

    if GLOBAL.Args.new:
        pushChanges = NewApp()()

    else:
        if not GLOBAL.Args.xhost:
            display = Display(visible=0, size=(800, 600))
            display.start()
        if GLOBAL.Args.app and len(GLOBAL.Args.app):
            for app in GLOBAL.Args.app:
                app_name = app.lower()
                if app_name in funs:
                    funs[app_name]()
                else:
                    app_name = app_name.replace(" ", "_")
                    if app_name in funs:
                        funs[app_name]()
                    else:
                        GLOBAL.Log(f"App {app} not found", level="ERROR")
        else:
            for app in funs:
                funs[app]()
        for analysis in GLOBAL.VirusTotal.wait_queue():
            if analysis.infected:
                GLOBAL.Index[analysis.appname]["providers"][analysis.provider][
                    "safe"
                ] = False
                GLOBAL.Index.write()

    if pushChanges:
        GLOBAL.Index.write()
        Github.push_index()
        for file in os.listdir(GLOBAL.Paths.AppsDir):
            os.remove(os.path.join(GLOBAL.Paths.AppsDir, file))
    if display is not None:
        display.stop()
