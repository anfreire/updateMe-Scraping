from typing import Any, Dict, Type
import json
import importlib

DynamicClass = Type[Any]


def get_dynamic_class(module_path: str, class_name: str) -> DynamicClass:
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class Provider:
    class_name: str
    init_args: list
    call_args: list

    def __init__(self, class_name: str, init_args: list, call_args: list):
        self.class_name = class_name
        self.init_args = init_args
        self.call_args = call_args

    def __call__(self) -> str | None:
        dynamic_class = get_dynamic_class(
            f"Providers.{self.class_name}", self.class_name
        )
        return dynamic_class(*self.init_args)(*self.call_args)


class App:
    name: str
    providers: Dict[str, Provider]

    def __init__(self, name: str, providers: Dict[str, Provider]):
        self.name = name
        self.providers = providers

    def __call__(self):
        dynamic_class = get_dynamic_class("LIB.AppBase", "AppBase")
        app = dynamic_class(self.name, self.providers)
        app.update()


class Apps:
    def __init__(self, apps_json: str):
        self.apps: Dict[str, App] = {}
        self.__read(apps_json)

    def __getitem__(self, key: str) -> Any:
        return self.apps[key]

    def __setitem__(self, key: str, value: Any) -> None:
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

    def __read(self, apps_json: str) -> None:
        with open(apps_json, "r") as file:
            apps = json.load(file)
        self.apps = {
            app: App(
                app,
                {
                    provider: Provider(
                        provider_info["class"],
                        provider_info["init_args"],
                        provider_info["call_args"],
                    )
                    for provider, provider_info in providers.items()
                },
            )
            for app, providers in apps.items()
        }
