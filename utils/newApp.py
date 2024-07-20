from lib.cli import CLI
from GLOBAL import GLOBAL
from utils.Index import Provider, Providers, App, Index
from utils.searcher import Searcher
from lib.github import Github
import pickle
import os
import requests
from typing import TypedDict, Literal, List, Tuple
from copy import deepcopy
import json
import pyvirtualdisplay
import re


def make_fun_name(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)
    if name[0].isdigit():
        DIGITS = {
            "0": "zero",
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
            "7": "seven",
            "8": "eight",
            "9": "nine",
        }
        name = DIGITS[name[0]] + name[1:]
    return name.lower()


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


list_to_str = lambda x: str([f'"{word}"' for word in x])


class NewApp(CLI):
    def __init__(self):
        super().__init__()
        self.existing_apps = list(Index.index.keys())
        self.features = list(
            {feature for app in Index.index.values() for feature in app.features}
        )
        self.variables = {}
        self.sources = {}

    def get_name(self):
        name = ""
        while True:
            name = self.input("Enter the name of the app:", name).strip()
            if len(name) == 0:
                self.show_message("Name cannot be empty", error=True)
                continue
            if any(name == app for app in self.existing_apps):
                self.show_message("App already exists", error=True)
                continue
            return name

    def get_icon(self):
        while True:
            icon = self.input("Enter the icon of the app:").strip()
            if len(icon) == 0:
                self.show_message("Icon cannot be empty", error=True)
                continue
            if os.path.exists(
                iconPath := os.path.join(
                    GLOBAL.Paths.IconsDir,
                    self.variables["name"].replace(" ", "_").lower() + ".png",
                )
            ):
                self.show_message(f"Icon already exists at {iconPath}", error=True)
                continue
            response = requests.get(icon)
            if response.status_code != 200:
                self.show_message("Invalid icon url", error=True)
                continue
            with open(iconPath, "wb") as file:
                file.write(response.content)
            return Github.push_icon(iconPath)

    def restore_config(self):
        if not os.path.exists(GLOBAL.Paths.NewAppBackupFile):
            return
        if (
            self.select(
                "Do you want to restore the backup of a new app creation?",
                ["Yes", "No"],
            )
            == "No"
        ):
            return
        with open(GLOBAL.Paths.NewAppBackupFile, "rb") as file:
            self.variables = pickle.load(file)

    def save_config(self):
        with open(GLOBAL.Paths.NewAppBackupFile, "wb") as file:
            pickle.dump(self.variables, file)

    def remove_config(self):
        if os.path.exists(GLOBAL.Paths.NewAppBackupFile):
            os.remove(GLOBAL.Paths.NewAppBackupFile)

    def build_provider_scrapper(self, provider: str, lines: List[str]) -> str:
        return (
            f'\n    # {provider}\n    def {provider.replace(" ", "").lower()}():\n        '
            + "\n        ".join(lines)
        )

    def build_github_scrapper(self) -> Tuple[str, str]:
        user = self.input("Enter the github user:")
        repo = self.input("Enter the github repo:")
        include_words = self.input("Enter the include words", multiple=True)
        exclude_words = self.input("Enter the exclude words", multiple=True)
        self.sources["Github"] = f"https://github.com/{user}/{repo}"
        return (
            user,
            self.build_provider_scrapper(
                user,
                [
                    f'return Github("{user}", "{repo}")({list_to_str(include_words)}, {list_to_str(exclude_words)})',
                ],
            ),
        )

    def build_defined_scrapper(self, provider: str) -> Tuple[str, str]:
        if provider == "ReVanced":
            tag = self.input(f"Enter the tag for {provider}:")
        else:
            if not GLOBAL.Args.xhost:
                display = pyvirtualdisplay.Display(visible=0, size=(800, 600))
                display.start()
            searcher = Searcher(provider)
            searcher.search(self.variables["name"])
            results = searcher.get_results()
            for title, href in results.items():
                name_words = [word.lower() for word in self.variables["name"].split()]
                if all(word in title.lower() for word in name_words):
                    try:
                        tag = searcher.get_tag(href)
                    except Exception as e:
                        continue
                    self.sources[provider] = href
                    break
            if not GLOBAL.Args.xhost:
                display.stop()
            if "tag" not in locals():
                tag = self.input(f"Enter the tag for {provider}:")
        match provider:
            case "MODYOLO":
                class_name = "Modyolo"
            case "LITEAPKS":
                class_name = "Liteapks"
            case "APKDONE":
                class_name = "ApkDone"
            case "ReVanced":
                class_name = "Revanced"
        return (
            provider,
            self.build_provider_scrapper(provider, [f'return {class_name}("{tag}")()']),
        )

    def build_custom_find_scrapper(self) -> Tuple[str, str]:
        link = self.input("Enter the link for the href finder:")
        include_words = self.input("Enter the include words:", multiple=True)
        exclude_words = self.input("Enter the exclude words:", multiple=True)
        return (
            link,
            self.build_provider_scrapper(
                link,
                [
                    "return Simple()(",
                    f'    "{link}",',
                    f"    include={list_to_str(include_words)},",
                    f"    exclude={list_to_str(exclude_words)},",
                    ")",
                ],
            ),
        )

    def build_custom_direct_scrapper(self) -> Tuple[str, str]:
        link = self.input("Enter the link for the direct link:")
        return (
            link,
            self.build_provider_scrapper(
                link,
                [
                    f'return Simple()("{link}")',
                ],
            ),
        )

    def build_provider_scrappers(self) -> str:
        PROVIDERS_MAP = {
            "Github": lambda x: self.build_github_scrapper(),
            "MODYOLO": lambda x: self.build_defined_scrapper(x),
            "LITEAPKS": lambda x: self.build_defined_scrapper(x),
            "APKDONE": lambda x: self.build_defined_scrapper(x),
            "ReVanced": lambda x: self.build_defined_scrapper(x),
            "Direct Link": lambda x: self.build_custom_direct_scrapper,
            "href finder": lambda x: self.build_custom_find_scrapper,
        }
        providers_copy = deepcopy(self.variables["providers"])
        self.variables["providers"] = []
        scrappers = []
        for provider in providers_copy:
            new_name, scrapper = PROVIDERS_MAP[provider](provider)
            self.variables["providers"].append(new_name)
            scrappers.append(scrapper)
        return "\n\n".join(scrappers)

    def write_scrapper(self):
        os.system(
            f'echo \'\n\n\n#####################################################################################\n# {self.variables["name"].upper()}\ndef {make_fun_name(self.variables["name"])}():\n'
            + self.build_provider_scrappers()
            + f'\n\n    app = AppBase("{self.variables["name"]}", '
            + "{"
            + ", ".join(
                [
                    f'"{providerName}": {providerName.replace(" ", "").lower()}'
                    for providerName in self.variables["providers"]
                ]
            )
            + "})\n"
            + f"    app.update()' >> {GLOBAL.Paths.AppsScriptFile}"
        )

    def add_index(self):
        providers = {}
        for provider in self.variables["providers"]:
            source = None if provider not in self.sources else self.sources[provider]
            while source is None:
                source = self.input(f"Enter the source of {provider}:")
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
        Index.write()

    def add_category(self):
        categories = {}
        with open(GLOBAL.Paths.CategoriesFile, "r") as file:
            categories = json.load(file)
        if (
            self.select(
                "Is the category in the list? ",
                ["Yes", "No"],
            )
            == "No"
        ):
            while True:
                category = self.input("Enter the category:")
                if category in categories.keys():
                    self.show_message("Category already exists", error=True)
                    break
                icon = self.input("Enter the icon for the category:")
                categories[category] = {"apps": [self.variables["name"]], "icon": icon}
                break
        else:
            category = self.select("Select the category", list(categories.keys()))
            categories[category]["apps"].append(self.variables["name"])
        with open(GLOBAL.Paths.CategoriesFile, "w") as file:
            json.dump(categories, file, indent=4)
        Github.push_categories()

    def __call__(self):
        self.restore_config()
        ASSIGNMENTS = {
            "name": self.get_name,
            "icon": self.get_icon,
            "dependencies": lambda: self.select(
                "Select dependencies", self.existing_apps, multiple=True
            ),
            "complements": lambda: self.select(
                "Select complements", self.existing_apps, multiple=True
            ),
            "features": lambda: self.input(
                "Enter the app features:", autocomplete=self.features, multiple=True
            ),
            "providers": lambda: self.select(
                "Select providers",
                [
                    "Github",
                    "MODYOLO",
                    "LITEAPKS",
                    "APKDONE",
                    "ReVanced",
                    "Direct Link",
                    "href finder",
                ],
                multiple=True,
            ),
        }

        for key, fun in ASSIGNMENTS.items():
            while self.variables.get(key) is None:
                self.variables[key] = fun()
                self.save_config()

        self.write_scrapper()

        self.add_index()

        self.add_category()

        self.remove_config()
