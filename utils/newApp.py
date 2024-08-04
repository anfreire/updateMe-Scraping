from LIB.CLI import CLI
from GLOBAL import GLOBAL, IndexApp, IndexProvider
from utils.searcher import Searcher
from LIB.Github import Github
import pickle
import os
import requests
from typing import TypedDict, Literal, List, Tuple
from copy import deepcopy
import json
import pyvirtualdisplay
import re

TAB = "    "


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


class NewApp(CLI):
    def __init__(self):
        super().__init__()
        self.existing_apps = list(GLOBAL.Index.keys())
        self.features = list(
            {feature for app in GLOBAL.Index.values() for feature in app.features}
        )
        self._variables = {}
        self.sources = {}
        self.__restore_config()

    def __restore_config(self):
        if not os.path.exists(GLOBAL.Paths.Files.NewAppBackup):
            return
        if self.message(
            "Do you want to restore the backup of a new app creation?", prompt=True
        ):
            return
        with open(GLOBAL.Paths.Files.NewAppBackup, "rb") as file:
            self._variables = pickle.load(file)

    def __save_config(self):
        with open(GLOBAL.Paths.Files.NewAppBackup, "wb") as file:
            pickle.dump(self.variables, file)

    def __remove_config(self):
        if os.path.exists(GLOBAL.Paths.Files.NewAppBackup):
            os.remove(GLOBAL.Paths.Files.NewAppBackup)

    @property
    def variables(self):
        return self._variables

    @variables.setter
    def variables(self, value):
        self._variables = value
        self.__save_config()

    def __build_provider_fun(self, provider: str, lines: List[str]) -> str:
        return (
            f'\n    # {provider}\n    def {provider.replace(" ", "").lower()}():\n        '
            + "\n        ".join(lines)
        )

    def __build_github_scrapper(self) -> Tuple[str, str]:
        user = self.input("Github User")
        repo = self.input("Github Repo")
        include_words: list[str] = self.input(
            "Github Include Search Words", multiple=True
        )
        exclude_words = self.input("Github Exclude Search Words", multiple=True)
        self.sources["Github"] = f"https://github.com/{user}/{repo}"
        return (
            user,
            self.__build_provider_fun(
                user,
                [
                    f'return Github("{user}", "{repo}")({repr(include_words)}, {repr(exclude_words)})',
                ],
            ),
        )

    def __build_defined_scrapper(self, provider: str) -> Tuple[str, str]:
        tag = None
        if provider == "ReVanced":
            tag = self.input(f"{provider} Tag")
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
            if not tag:
                tag = self.input(f"{provider} Tag")
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
            self.__build_provider_fun(provider, [f'return {class_name}("{tag}")()']),
        )

    def __build_unkown_scrapper(self) -> Tuple[str, str]:
        link = self.input("Unkown Link")
        include_words = self.input(
            "Unkown Provider Include Search Words", multiple=True
        )
        exclude_words = self.input("Unkown Provider Search Words", multiple=True)
        return (
            link,
            self.__build_provider_fun(
                link,
                [
                    "return Simple()(",
                    f'    "{link}",',
                    f"    include={repr(include_words)},",
                    f"    exclude={repr(exclude_words)},",
                    ")",
                ],
            ),
        )

    def __build_mobilism_scrapper(self) -> Tuple[str, str]:
        search = self.input("Mobilism Search Query")
        user = self.input("Mobilism Author")
        include_words_search = self.input(
            "Mobilism Include Search Words", multiple=True
        )
        exclude_words_search = self.input(
            "Mobilism Exclude Search Words", multiple=True
        )
        include_words_filename = self.input(
            "Mobilism Include Filename Words", multiple=True
        )
        exclude_words_filename = self.input(
            "Mobilism Exclude Filename Words", multiple=True
        )
        return (
            user,
            self.__build_provider_fun(
                user,
                [
                    f"return Mobilism()(",
                    f'    "{self.variables["name"]}",',
                    f'    "{search}",',
                    f'    "{user}",',
                    f"    include_words_search={repr(include_words_search)},",
                    f"    exclude_words_search={repr(exclude_words_search)},",
                    f"    include_words_filename={repr(include_words_filename)},",
                    f"    exclude_words_filename={repr(exclude_words_filename)},",
                    ")",
                ],
            ),
        )

    def __build_direct_scrapper(self) -> Tuple[str, str]:
        name = self.input("Direct Provider Name")
        link = self.input("Direct Provider URL")
        return (
            name,
            self.__build_provider_fun(
                name,
                [
                    f'return Simple()("{link}")',
                ],
            ),
        )

    def build_provider_scrappers(self) -> str:
        PROVIDERS_MAP = {
            "Github": lambda x: self.__build_github_scrapper(),
            "MODYOLO": lambda x: self.__build_defined_scrapper(x),
            "LITEAPKS": lambda x: self.__build_defined_scrapper(x),
            "APKDONE": lambda x: self.__build_defined_scrapper(x),
            "ReVanced": lambda x: self.__build_defined_scrapper(x),
            "Direct Link": lambda x: self.__build_direct_scrapper(),
            "HREF finder": lambda x: self.__build_unkown_scrapper(),
            "Mobilism": lambda x: self.__build_mobilism_scrapper(),
        }
        providers_copy = deepcopy(self.variables["providers"])
        self.variables["providers"] = []
        scrappers = []
        for provider in providers_copy:
            new_name, scrapper = PROVIDERS_MAP[provider](provider)
            self.variables["providers"].append(new_name)
            scrappers.append(scrapper)
        return "\n\n".join(scrappers)

    def __get_name(self) -> None:
        value = ""
        while True:
            value = self.input("App Name", value).strip()
            if len(value) == 0:
                self.message("Name cannot be empty", "error")
                continue
            if any(value == app for app in self.existing_apps):
                self.message("App already exists", "error")
                continue
            self.variables["name"] = value
            break

    def __get_icon(self) -> None:
        while True:
            icon = self.input("App Icon URL").strip()
            if len(icon) == 0:
                self.message("Icon cannot be empty", "error")
                continue
            if os.path.exists(
                iconPath := os.path.join(
                    GLOBAL.Paths.Directories.Icons,
                    re.sub(r"[^a-zA-Z0-9_]", "", self.variables["name"]) + ".png",
                )
            ):
                if not self.message(
                    "Icon already exists, do you want to use it?", prompt=True
                ):
                    if self.message(
                        "Do you want to remove the existing icon?", prompt=True
                    ):
                        os.remove(iconPath)
                    else:
                        continue
            else:
                response = requests.get(icon)
                if response.status_code != 200:
                    self.message("Invalid icon url", "error")
                    continue
                with open(iconPath, "wb") as file:
                    file.write(response.content)
            self.variables["icon"] = iconPath
            Github.push_icon(iconPath)
            break

    def __get_providers(self) -> None:
        providers = {
            "Github": 0,
            "MODYOLO": 0,
            "LITEAPKS": 0,
            "APKDONE": 0,
            "ReVanced": 0,
            "Direct Link": 0,
            "HREF finder": 0,
            "Mobilism": 0,
        }
        while True:
            providers = self.form("App Providers", providers)
            for provider, value in providers.items():
                for _ in range((int(value) if value else 0)):
                    self.variables["providers"].append(provider)
            if len(self.variables["providers"]) == 0:
                self.message("At least one provider is required", "error")
                continue

    def __get_dependencies(self) -> None:
        self.variables["dependencies"] = self.checkbox(
            "App Dependencies", self.existing_apps
        )

    def __get_complements(self) -> None:
        self.variables["complements"] = self.checkbox(
            "App Complements", self.existing_apps
        )

    def __get_features(self) -> None:
        self.variables["features"] = self.input(
            "Enter the app features:", autocomplete=self.features, multiple=True
        )

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
            + f"    app.update()' >> {GLOBAL.Paths.Files.AppsScript}"
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
        GLOBAL.Index[self.variables["name"]] = IndexApp(
            {
                "icon": self.variables["icon"],
                "depends": self.variables["dependencies"],
                "complements": self.variables["complements"],
                "features": self.variables["features"],
                "providers": providers,
            }
        )
        GLOBAL.Index.write()

    def add_category(self):
        categories = {}
        with open(GLOBAL.Paths.Files.Categories, "r") as file:
            categories = json.load(file)
        category = self.select("App Category", list(categories.keys()))
        if category is None:
            while True:
                category = self.input("App Category")
                if category in categories.keys():
                    self.message("Category already exists", "error")
                    break
                icon = self.input(f"{category} Icon")
                categories[category] = {"apps": [self.variables["name"]], "icon": icon}
                break
        else:
            categories[category]["apps"].append(self.variables["name"])
        with open(GLOBAL.Paths.Files.Categories, "w") as file:
            json.dump(categories, file, indent=4)
        Github.push_categories()

    def __call__(self):
        ASSIGNMENTS = {
            "name": self.__get_name,
            "icon": self.__get_icon,
            "dependencies": self.__get_dependencies,
            "complements": self.__get_complements,
            "features": self.__get_features,
            "providers": self.__get_providers,
        }

        for key, fun in ASSIGNMENTS.items():
            while self.variables.get(key) is None:
                fun()
                self.__save_config()

        self.write_scrapper()

        self.add_index()

        self.add_category()

        self.__remove_config()
