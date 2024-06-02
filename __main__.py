from GLOBAL import GLOBAL
from lib.virustotal import VirusTotal
from utils.Index import Index
from lib.github import Github
from pyvirtualdisplay import Display
#############|
GLOBAL()#####|
VirusTotal()#|
Index()######|
#############|
import inspect
import apps

funs = {name: function for name, function in [o for o in inspect.getmembers(apps) if inspect.isfunction(o[1])]}

if __name__ == "__main__":
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
    for analysis in VirusTotal.wait_queue():
        if analysis.infected:
            Index.index[analysis.appname]["providers"][analysis.provider]["infected"] = True
            Index.write()
    Index.write()
    Github.push_index()
    if not GLOBAL.Args.xhost:
        display.stop()