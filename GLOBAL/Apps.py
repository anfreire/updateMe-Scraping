from typing import Any, Dict, Type, Protocol, List
import json
import importlib
from dataclasses import dataclass

class DynamicProviderClass(Protocol):
    def __init__(self, *args: Any): ...
    def __call__(self, *args: Any) -> str | None: ...

@dataclass
class Provider:
    class_name: str
    init_args: List[Any]
    call_args: List[Any]

    def get_dynamic_class(self) -> Type[DynamicProviderClass]:
        module = importlib.import_module(f"Providers.{self.class_name}")
        return getattr(module, self.class_name)

    def __call__(self) -> str | None:
        dynamic_class = self.get_dynamic_class()
        return dynamic_class(*self.init_args)(*self.call_args)

@dataclass
class App:
    name: str
    providers: Dict[str, Provider]

    def __call__(self, providers: List[str] | None = None) -> None:
        from LIB.AppBase import AppBase
        app = AppBase(self.name, self.providers)
        app.update(providers)

class Apps:
    def __init__(self, apps_json: str):
        self.apps: Dict[str, App] = {}
        self.apps_json = apps_json
        self.__read()

    def __getitem__(self, key: str) -> App:
        return self.apps[key]

    def __setitem__(self, key: str, value: App) -> None:
        self.apps[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.apps

    def __iter__(self):
        return iter(self.apps)

    def __len__(self) -> int:
        return len(self.apps)

    def keys(self):
        return self.apps.keys()

    def values(self):
        return self.apps.values()

    def items(self):
        return self.apps.items()

    def __read(self) -> None:
        with open(self.apps_json, "r") as file:
            apps_data = json.load(file)
            self.apps = {
                app_name: App(
                    app_name,
                    {
                        provider_name: Provider(
                            provider_info["class"],
                            provider_info["init_args"],
                            provider_info["call_args"],
                        )
                        for provider_name, provider_info in providers.items()
                    },
                )
                for app_name, providers in apps_data.items()
            }

    def write(self) -> None:
        with open(self.apps_json, "w") as file:
            json.dump(
                {
                    app_name: {
                        provider_name: {
                            "class": provider.class_name,
                            "init_args": provider.init_args,
                            "call_args": provider.call_args,
                        }
                        for provider_name, provider in app.providers.items()
                    }
                    for app_name, app in self.apps.items()
                },
                file,
                indent=4,
            )