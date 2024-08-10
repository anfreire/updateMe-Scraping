from typing import Literal, Union
import re
import os
from GLOBAL import GLOBAL, IndexApp, IndexProvider, LogLevel
from dataclasses import dataclass

TAB = "    "


def build_list(lst: list[str]) -> str:
    return "[" + ", ".join([f"'{item}'" for item in lst]) + "]"


def build_provider_function_base(provider: str, lines: list[str]) -> str:
    return (
        f'\n{TAB}# {provider}\n    def {provider.replace(" ", "").lower()}():\n{TAB * 2}'
        + f"\n{TAB * 2}".join(lines)
    )


class ProviderBase:
    origin: str
    provider_name: str

    def build_function(self) -> str:
        pass


@dataclass
class GithubProvider(ProviderBase):
    origin: str
    provider_name: str
    user: str
    repo: str
    include_words: list[str]
    exclude_words: list[str]

    def build_function(self) -> str:
        return build_provider_function_base(
            self.user,
            [
                f'return Github("{self.user}", "{self.repo}")({build_list(self.include_words)}, {build_list(self.exclude_words)})'
            ],
        )


@dataclass
class LinkSuffixProvider(ProviderBase):
    origin: str
    provider_name: str
    provider: Literal["MODYOLO", "LITEAPKS", "APKDONE"]
    suffix: str

    def build_function(self) -> str:
        match self.provider:
            case "MODYOLO":
                class_name = "Modyolo"
            case "LITEAPKS":
                class_name = "Liteapks"
            case "APKDONE":
                class_name = "ApkDone"
        return build_provider_function_base(
            self.provider,
            [f'return {class_name}("{self.suffix}")()'],
        )


@dataclass
class HrefFinderProvider(ProviderBase):
    origin: str
    provider_name: str
    link: str
    include_words: list[str]
    exclude_words: list[str]

    def build_function(self) -> str:
        return build_provider_function_base(
            self.provider_name,
            [
                "return HrefFinder()(",
                f'    "{self.link}",',
                f"    include={build_list(self.include_words)},",
                f"    exclude={build_list(self.exclude_words)})" ")",
            ],
        )


@dataclass
class DirectLinkProvider(ProviderBase):
    origin: str
    provider_name: str
    link: str

    def build_function(self) -> str:
        return build_provider_function_base(
            self.provider_name, [f'return DirectLink()("{self.link}")']
        )


class Writter:
    def __init__(
        self,
        app_name: str,
        app_icon: str,
        depends: list[str],
        complements: list[str],
        features: list[str],
        providers: list[
            Union[
                GithubProvider,
                LinkSuffixProvider,
                HrefFinderProvider,
                DirectLinkProvider,
            ]
        ],
    ):
        self.app_name = app_name
        self.app_icon = app_icon
        self.depends = depends
        self.complements = complements
        self.features = features
        self.providers = providers

    @staticmethod
    def make_fun_name(name: str) -> str:
        name = re.sub(r"[^a-zA-Z0-9_]", "", name.replace(" ", "_"))
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

    def write_apps(self) -> None:
        lines = [
            "#####################################################################################",
            f"# {self.app_name.upper()}",
            f"def {self.make_fun_name(self.app_name)}():",
            "",
            *[p.build_function() for p in self.providers],
            "",
            f"{TAB}app = AppBase(",
            f'{TAB * 2}"{self.app_name}",',
            TAB * 2 + "{",
            *[
                f'{TAB * 3}"{provider.provider_name}": {provider.provider_name.replace(" ", "").lower()}'
                for provider in self.providers
            ],
            TAB * 2 + "}",
            TAB + ")",
            TAB + "app.update()",
        ]
        os.system(
            f" echo '\n\n\n{os.linesep.join(lines)}' >> {GLOBAL.Paths.Files.AppsScript}"
        )

    def write_index(self) -> None:
        providers = {
            p.provider_name: {
                "source": p.origin,
                "version": "",
                "packageName": "",
                "download": "",
                "safe": True,
                "sha256": "",
            }
            for p in self.providers
        }
        GLOBAL.Index[self.app_name] = IndexApp(
            icon=self.app_icon,
            depends=self.depends,
            complements=self.complements,
            features=self.features,
            providers=providers,
        )
        GLOBAL.Index.write()
