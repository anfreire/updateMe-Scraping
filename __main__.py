from GLOBAL import GLOBAL
from Modules.NewApp import NewApp
from Modules.NewProvider import main as NewProvider
from LIB.Github import Github
from pyvirtualdisplay import Display
from LIB.AppUtils import AppUtils


if __name__ == "__main__":
    if not GLOBAL.Args.xhost:
        display = Display(visible=0, size=(800, 600))
        display.start()

    update = True

    if GLOBAL.Args.new_app or GLOBAL.Args.new_provider:
        NewApp()() if GLOBAL.Args.new_app else NewProvider()
        update = False

    if GLOBAL.Args.rm_assets:
        Github.remove_unused_assests()
        update = False

    if GLOBAL.Args.rm_icons:
        Github.remove_unused_icons()
        update = False

    if update:
        # AppUtils.clean_directory(GLOBAL.Paths.Directories.Apps)

        if GLOBAL.Args.app and len(GLOBAL.Args.app):
            for app in GLOBAL.Args.app:
                if app in GLOBAL.Apps.keys():
                    GLOBAL.Apps[app](GLOBAL.Args.provider)
                else:
                    GLOBAL.Log(f"App {app} not found", level="ERROR")
        else:
            for app in GLOBAL.Apps:
                GLOBAL.Apps[app](GLOBAL.Args.provider)

        for analysis in GLOBAL.VirusTotal.wait_queue():
            GLOBAL.Index[analysis.appname]["providers"][analysis.provider]["safe"] = (
                False if analysis.infected else True
            )
            GLOBAL.Index.write()

        GLOBAL.Index.write()
        Github.push_index()

    if not GLOBAL.Args.xhost:
        display.stop()
