from typing import Dict
import json
from copy import deepcopy
from GLOBAL import GLOBAL


class Provider:
    def __init__(
        self,
        raw: dict,
    ) -> None:
        self.source = raw["source"]
        self.version = raw["version"]
        self.packageName = raw["packageName"]
        self.download = raw["download"] if "download" in raw else ""
        self.safe = raw["safe"] if "safe" in raw else True
        self.sha256 = raw["sha256"] if "sha256" in raw else ""

    def __getitem__(self, key: str) -> str:
        return getattr(self, key)

    def __setitem__(self, key: str, value: str) -> None:
        setattr(self, key, value)

    def __dict__(self) -> dict:
        return {
            "source": self.source,
            "version": self.version,
            "packageName": self.packageName,
            "download": self.download,
            "safe": self.safe,
            "sha256": self.sha256,
        }


class Providers:
    def __init__(self, **kwargs) -> None:
        self.providers: Dict[str, dict] = {}
        for provider in kwargs.keys():
            self.providers[provider] = Provider(kwargs[provider])

    def __getitem__(self, provider: str) -> Provider:
        return self.providers[provider]

    def __setitem__(self, provider: str, value: Provider) -> None:
        self.providers[provider] = value

    def __dict__(self) -> dict:
        return {
            title: provider.__dict__()
            for title, provider in self.providers.items()
        }


class App:
    def __init__(
        self,
        raw: dict,
    ) -> None:
        self.icon = raw["icon"]
        self.depends = raw["depends"] if "depends" in raw else []
        self.complements = raw["complements"] if "complements" in raw else []
        self.features = raw["features"] if "features" in raw else []
        self.providers = Providers(**raw["providers"])

    def __getitem__(self, key: str) -> str:
        return getattr(self, key)

    def __setitem__(self, key: str, value: str) -> None:
        setattr(self, key, value)

    def __dict__(self) -> dict:
        return {
            "icon": self.icon,
            "depends": self.depends,
            "complements": self.complements,
            "features": self.features,
            "providers": self.providers.__dict__(),
        }


class Index:
    instance = None
    index = {}

    def __new__(cls):
        if not cls.instance:
            cls.instance = super(Index, cls).__new__(cls)
            cls.read()
        return cls.instance
    
    @classmethod
    def toDict(cls) -> dict:
        return {app: cls.index[app].__dict__() for app in cls.index.keys()}

    @classmethod
    def read(cls) -> None:
        rawIndex = None
        with open(GLOBAL.Paths.IndexFile, "r") as index_file:
            rawIndex: dict = json.load(index_file)
        index: Dict[str, App] = {}
        for appTitle in rawIndex.keys():
            index[appTitle] = App(rawIndex[appTitle])
        cls.index = index

    @classmethod
    def write(cls) -> None:
        with open(GLOBAL.Paths.IndexFile, "w") as index_file:
            json.dump(
                cls.toDict(),
                index_file,
                indent=4,
            )
