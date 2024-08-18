from typing import Literal, Union
import re
import os
from GLOBAL import GLOBAL, IndexApp, IndexProvider, LogLevel, Provider, App
from dataclasses import dataclass


@dataclass
class GithubProvider:
    origin: str
    user: str
    repo: str
    include_words: list[str]
    exclude_words: list[str]

    def build_provider(self) -> Provider:
        return Provider(
            class_name="Github",
            init_args=[self.user, self.repo],
            call_args=[self.include_words, self.exclude_words],
        )


@dataclass
class LinkSuffixProvider:
    origin: str
    provider_name: str
    provider: Literal["MODYOLO", "LITEAPKS", "APKDONE", "MODZOCO"]
    suffix: str

    def build_provider(self) -> Provider:
        match self.provider:
            case "MODYOLO":
                class_name = "Modyolo"
            case "LITEAPKS":
                class_name = "Liteapks"
            case "APKDONE":
                class_name = "ApkDone"
            case "MODZOCO":
                class_name = "ModZoco"
        return Provider(
            class_name=class_name,
            init_args=[self.suffix],
            call_args=[],
        )


@dataclass
class HrefFinderProvider:
    origin: str
    provider_name: str
    link: str
    include_words: list[str]
    exclude_words: list[str]

    def build_provider(self) -> Provider:
        return Provider(
            class_name="HrefFinder",
            init_args=[],
            call_args=[self.link, self.include_words, self.exclude_words],
        )


@dataclass
class DirectLinkProvider:
    origin: str
    provider_name: str
    link: str

    def build_provider(self) -> Provider:
        return Provider(
            class_name="DirectLink",
            init_args=[],
            call_args=[self.link],
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

    def write_apps(self) -> None:
        providers = {p.provider_name: p.build_provider() for p in self.providers}
        GLOBAL.Apps[self.app_name] = App(
            self.app_name,
            providers,
        )
        GLOBAL.Apps.write()

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
