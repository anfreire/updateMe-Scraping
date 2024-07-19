import blessed
from GLOBAL import GLOBAL
from utils.Index import Provider, Providers, App, Index
from lib.github import Github
import os
import requests
import pickle
from typing import TypedDict, Literal

GITHUB_PROVIDER_TYPE = TypedDict(
    "github",
    {
        "user": str,
        "repo": str,
        "include_words": list[str],
        "exclude_words": list[str],
    },
)

DEFINED_PROVIDER_TYPE = TypedDict(
    "defined",
    {
        "provider": Literal["modyolo", "liteapks", "apkdone", "revanced"],
        "tag": str,
    },
)

CUSTOM_FIND_PROVIDER_TYPE = TypedDict(
    "custom",
    {
        "link": str,
        "include_words": list[str],
        "exclude_words": list[str],
    },
)

CUSTOM_DIRECT_PROVIDER_TYPE = TypedDict(
    "custom_direct",
    {
        "link": str,
    },
)


class AppManager:
    def __init__(self) -> None:
        self.term = blessed.Terminal()
        self.variables = {}

    def getName(self) -> str | None:
        appname = input(self.term.move_xy(0, 0) + "Enter the name of the app: ").strip()
        error = False
        if len(appname) == 0:
            print(
                self.term.move_xy(0, 2)
                + self.term.red
                + "App name cannot be empty!"
                + self.term.normal
            )
            error = True
        elif any(appname == app for app in Index.index.keys()):
            print(
                self.term.move_xy(0, 2)
                + self.term.red
                + "App already exists!"
                + self.term.normal
            )
            error = True
        if error:
            print(self.term.move_xy(0, 4) + "Press any key to continue...")
            with self.term.cbreak():
                self.term.inkey()
                return None
        print(self.term.clear)
        print(
            self.term.move_xy(0, 0)
            + f"Is the app's name '{self.term.bold + appname + self.term.normal}' correct? [Y/n] "
        )
        with self.term.cbreak():
            answer = self.term.inkey()
            if answer.lower() != "y":
                return None
            else:
                GLOBAL.Log(f"App's name set to {appname}", level="INFO")
        return appname

    def getIcon(self) -> str | None:
        icon = input(
            self.term.move_xy(0, 0) + "Enter the url of the app's icon: "
        ).strip()
        error = False
        if len(icon) == 0:
            print(
                self.term.move_xy(0, 2)
                + self.term.red
                + "Icon url cannot be empty!"
                + self.term.normal
            )
            error = True
        elif os.path.exists(
            iconPath := os.path.join(
                GLOBAL.Paths.IconsDir,
                iconName := self.variables["name"].replace(" ", "_").lower() + ".png",
            )
        ):
            print(
                self.term.move_xy(0, 2)
                + self.term.red
                + "Icon already exists!"
                + self.term.normal
            )
            error = True
        else:
            response = requests.get(icon)
            if response.status_code != 200:
                print(
                    self.term.move_xy(0, 2)
                    + self.term.red
                    + "Icon url is invalid!"
                    + self.term.normal
                )
                error = True
        if error:
            print(self.term.move_xy(0, 4) + "Press any key to continue...")
            with self.term.cbreak():
                self.term.inkey()
                return None
        with open(iconPath, "wb") as file:
            file.write(response.content)
        print(self.term.clear)
        print(self.term.move_xy(0, 0) + f"Icon saved as {iconPath}")
        print(self.term.move_xy(0, 2) + "Press any key to continue...")
        with self.term.cbreak():
            self.term.inkey()
        return Github.push_icon(iconPath)

    def checkbox(self, property: str, items: list) -> list[str]:
        selected = set()
        cursorPos = 0
        with self.term.cbreak(), self.term.hidden_cursor():
            val = None
            while val not in ("q", "Q"):
                print(self.term.clear)
                print(self.term.move_xy(0, 0) + f"Select the {property}")
                for ids, item in enumerate(items):
                    item = "[X] " + item if ids in selected else "[ ] " + item
                    if cursorPos == ids:
                        print(self.term.reverse + item + self.term.normal)
                    else:
                        print(item)
                print(
                    self.term.move_down
                    + "Use arrow keys to navigate, space to select, 'q' to quit."
                )
                val = self.term.inkey()
                if val.code == self.term.KEY_UP:
                    if cursorPos > 0:
                        cursorPos -= 1
                elif val.code == self.term.KEY_DOWN:
                    if cursorPos < len(items) - 1:
                        cursorPos += 1
                elif val == " ":
                    if cursorPos in selected:
                        selected.remove(cursorPos)
                    else:
                        selected.add(cursorPos)
                elif val in ("q", "Q"):
                    break
        print(self.term.clear)
        print(self.term.move_xy(0, 0) + f"Selected {property}:")
        for idx in selected:
            print(self.term.move_down + "'" + items[idx] + "'")
        print(
            self.term.move_down
            + "Press 'r' to reset selection, any other key to continue..."
        )
        with self.term.cbreak():
            if self.term.inkey() == "r":
                return self.checkbox(property, items)
        GLOBAL.Log(
            f"Selected {property}: {' '.join([items[idx] for idx in selected])}",
            level="INFO",
        )
        return [items[idx] for idx in selected]

    def inputList(self, property: str, autocomplete: list) -> list[str]:
        inputStr = ""
        inputed = []
        with self.term.cbreak(), self.term.hidden_cursor():
            while True:
                autocompleteIdx = -1
                print(self.term.clear + self.term.move_xy(0, 0))
                print(
                    "Press 'enter' to add feature, 'tab' to autocomplete and '!' to quit."
                    + self.term.move_down
                )
                if len(inputed):
                    print(f"Selected {property}:")
                    for feature in inputed:
                        print(self.term.move_down + "'" + feature + "'")
                    print(self.term.move_down)
                if len(inputStr):
                    for feature in autocomplete:
                        if feature.startswith(inputStr):
                            autocompleteIdx = autocomplete.index(feature)
                            break
                    print(
                        f'{property}: {inputStr + (self.term.gray25(autocomplete[autocompleteIdx][len(inputStr):]) if autocompleteIdx != -1 else "")}'
                    )
                else:
                    print(f"{property}: ")
                val = self.term.inkey()
                if val == "\n":
                    if len(inputStr):
                        inputed.append(inputStr)
                        inputStr = ""
                elif val == "\t":
                    if autocompleteIdx != -1:
                        inputStr = autocomplete[autocompleteIdx]
                elif val == "!":
                    break
                elif val.code == self.term.KEY_BACKSPACE:
                    inputStr = inputStr[:-1]
                elif val.isprintable():
                    inputStr += val
        print(self.term.clear)
        print(self.term.move_xy(0, 0) + f"Selected {property}:")
        for feature in inputed:
            print(self.term.move_down + "'" + feature + "'")
        print(
            self.term.move_down
            + "Press 'r' to reset selection, any other key to continue..."
        )
        with self.term.cbreak():
            if self.term.inkey() == "r":
                return self.inputList(property, autocomplete)
        GLOBAL.Log(f"Selected {property}: {' '.join(inputed)}", level="INFO")
        return inputed

    def addApp(self) -> bool:
        if os.path.exists(GLOBAL.Paths.NewAppBackupFile):
            GLOBAL.Log(
                "Found a backup of a new app creation",
                level="INFO",
            )
            with open(GLOBAL.Paths.NewAppBackupFile, "rb") as file:
                self.variables = pickle.load(file)
            with self.term.fullscreen():
                print(self.term.clear)
                print(self.term.move_xy(0, 0) + "Found a backup of a new app creation.")
                print(
                    self.term.move_xy(0, 2)
                    + "Do you want to continue the creation of the app?"
                )
                print(
                    self.term.move_down
                    + "Press 'y' to continue, any other key to start over..."
                )
                with self.term.cbreak():
                    if self.term.inkey().lower() != "y":
                        self.variables = {}
                        GLOBAL.Log(
                            "Discarding backup of a new app creation", level="INFO"
                        )
                    else:
                        print(self.term.clear)
                        print(
                            self.term.move_xy(0, 0)
                            + "Continuing the creation of the app..."
                        )
                        GLOBAL.Log(
                            "Continuing the creation of the app from backup",
                            level="INFO",
                        )
        apps = list(Index.index.keys())
        features = list(
            {feature for app in Index.index.values() for feature in app.features}
        )
        providers = list(
            {
                provider
                for app in Index.index.values()
                for provider in app.providers.providers.keys()
            }
        )
        ASSIGNMENTS = {
            "name": self.getName,
            "icon": self.getIcon,
            "dependencies": lambda: self.checkbox("dependencies", apps),
            "complements": lambda: self.checkbox("complements", apps),
            "features": lambda: self.inputList("features", features),
            "providers": lambda: self.inputList("providers", providers),
        }
        try:
            with self.term.fullscreen():
                for key, value in ASSIGNMENTS.items():
                    while self.variables.get(key) is None:
                        print(self.term.clear)
                        self.variables[key] = value()
                        with open(GLOBAL.Paths.NewAppBackupFile, "wb") as file:
                            pickle.dump(self.variables, file)
                print(self.term.clear)
                providers = {}
                for provider in self.variables["providers"]:
                    source = None
                    while source is None:
                        source = input(
                            self.term.move_xy(0, 0)
                            + f"Enter the source of the {provider} provider: "
                        ).strip()
                        print(self.term.clear)
                        print(
                            self.term.move_xy(0, 0)
                            + f"Is the source '{self.term.bold + source + self.term.normal}' correct? [Y/n] "
                        )
                        with self.term.cbreak():
                            answer = self.term.inkey()
                            if answer.lower() != "y":
                                source = None
                            else:
                                GLOBAL.Log(
                                    f"Source of {provider} set to {source}",
                                    level="INFO",
                                )
                    providers[provider] = {
                        "source": source,
                        "version": "",
                        "packageName": "",
                        "download": "",
                        "safe": True,
                        "sha256": "",
                    }
                Index.index[self.variables["name"]] = App(
                    {
                        "icon": self.variables["icon"],
                        "depends": self.variables["dependencies"],
                        "complements": self.variables["complements"],
                        "features": self.variables["features"],
                        "providers": providers,
                    }
                )
                os.system(
                    f'echo \'\n\n\n#####################################################################################\n# {self.variables["name"].upper()}\ndef {self.variables["name"].replace(" ", "").lower()}():\n'
                    + "\n".join(
                        [
                            f'\n\t# {providerName}\n\tdef {providerName.replace(" ", "").lower()}():\n\t\treturn None'
                            for providerName in self.variables["providers"]
                        ]
                    )
                    + f'\n\n\tapp = AppBase("{self.variables["name"]}", '
                    + "{"
                    + ", ".join(
                        [
                            f'"{providerName}": {providerName.replace(" ", "").lower()}'
                            for providerName in self.variables["providers"]
                        ]
                    )
                    + "})\n"
                    + f"\tapp.update()' >> {GLOBAL.Paths.AppsScriptFile}"
                )

        except KeyboardInterrupt:
            print(self.term.clear)
            print(self.term.move_xy(0, 0) + self.term.red + "Aborting app creation...")
            GLOBAL.Log("Aborting app creation...", level="INFO")
            return False
        os.remove(GLOBAL.Paths.NewAppBackupFile)
        return True
