import os
import configparser
import logging
import argparse
from typing import Literal
import re
import string


class Paths:
    ScriptDir: str = os.path.dirname(os.path.realpath(__file__))
    DataDir: str = os.path.join(ScriptDir, "..", "Data")
    AppsDir: str = os.path.join(DataDir, "apps")
    IconsDir: str = os.path.join(DataDir, "icons")
    IndexFile: str = os.path.join(DataDir, "index.json")
    LogFile: str = os.path.join(ScriptDir, ".log")
    ConfigFile: str = os.path.join(ScriptDir, ".ini")
    AppsScriptFile: str = os.path.join(ScriptDir, "apps.py")
    NewAppBackupFile: str = os.path.join(ScriptDir, "new_app.pkl")
    CategoriesFile: str = os.path.join(DataDir, "categories.json")


class Log:
    def __init__(self, debug: bool):
        self.clean()
        logging.basicConfig(
            filename=Paths.LogFile,
            level=logging.INFO if not debug else logging.DEBUG,
            format="\n[ %(levelname)s ] [ %(asctime)s ]\n%(message)s",
            datefmt="%m/%d/%Y - %H:%M:%S",
        )

    def clean(self):
        open(Paths.LogFile, "w").close()

    def log(
        self,
        message: str,
        level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
        exception: bool = False,
    ):
        if exception:
            getattr(logging, level.lower())(message, exc_info=True, stack_info=True)
        else:
            getattr(logging, level.lower())(message)
        print(f"[ {level} ]\n{message}\n\n")

    def __call__(
        self,
        message: str,
        level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
        exception: bool = False,
    ):
        self.log(message, level, exception)


class Args:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-a", "--app", "--apps", nargs="+", help="App name")
        self.parser.add_argument(
            "-g", "--github", help="Force Github push", action="store_true"
        )
        self.parser.add_argument(
            "-v", "--virustotal", help="Force VirusTotal analysis", action="store_true"
        )
        self.parser.add_argument(
            "-c", "--config", help="Edit config file", action="store_true"
        )
        self.parser.add_argument(
            "-d", "--debug", help="Debug mode", action="store_true"
        )
        self.parser.add_argument(
            "-x", "--xhost", help="Use xhost: Display", action="store_true"
        )
        self.parser.add_argument("-n", "--new", help="Add new app", action="store_true")
        self.args = self.parser.parse_args()

    @property
    def app(self):
        return self.args.app

    @property
    def github(self):
        return self.args.github

    @property
    def virustotal(self):
        return self.args.virustotal

    @property
    def config(self):
        return self.args.config

    @property
    def debug(self):
        return self.args.debug

    @property
    def xhost(self):
        return self.args.xhost

    @property
    def new(self):
        return self.args.new


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(Paths.ConfigFile)

    def __getitem__(self, section: str):
        return self.config[section]

    def get(self, section: str, key: str):
        try:
            return self.config[section][key]
        except KeyError:
            return None

    def set(self, section: str, key: str, value: str):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        with open(Paths.ConfigFile, "w") as file:
            self.config.write(file)

    def setup(self):
        while True:
            section = input("Enter section name (or 'quit' to finish): ")
            if section.lower() == "quit":
                break

            if section not in self.config:
                self.config[section] = {}

            while True:
                key = input(
                    "Enter key for section '{}' (or 'done' to finish section): ".format(
                        section
                    )
                )
                if key.lower() == "done":
                    break

                value = input("Enter value for key '{}': ".format(key))
                self.config[section][key] = value

        with open(Paths.ConfigFile, "w") as file:
            self.config.write(file)


class GLOBAL:
    istance = None
    Paths = None
    Log = None
    Args = None
    Config = None

    def __new__(cls):
        if not cls.istance:
            cls.istance = super(GLOBAL, cls).__new__(cls)
            cls.Paths = Paths()
            cls.Args = Args()
            cls.Log = Log(cls.Args.debug)
            cls.Config = Config()
            cls.Log("Global instance created")
            cls.Log(f"Args: {cls.Args.args}")
        return cls.istance
