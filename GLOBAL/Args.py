from dataclasses import dataclass, field
import argparse
from typing import List, TypeVar, Generic, Literal


@dataclass
class BaseArgs:
    debug: bool = False
    xhost: bool = False

    @staticmethod
    def parse(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-d", "--debug", action="store_true", help="Debug mode")
        parser.add_argument(
            "-x", "--xhost", action="store_true", help="Use xhost: Display"
        )


@dataclass
class UpdateArgs(BaseArgs):
    github: bool = False
    virustotal: bool = False
    apps: List[str] = field(default_factory=list)
    providers: List[str] = field(default_factory=list)

    @staticmethod
    def parse(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
        update_parser = subparsers.add_parser(
            "update", help="Update apps and providers"
        )
        update_parser.add_argument(
            "-g", "--github", action="store_true", help="Force Github push"
        )
        update_parser.add_argument(
            "-v", "--virustotal", action="store_true", help="Force VirusTotal analysis"
        )
        update_parser.add_argument("-a", "--apps", nargs="+", help="App name(s)")
        update_parser.add_argument(
            "-p", "--providers", nargs="+", help="Provider name(s)"
        )


@dataclass
class NewArgs(BaseArgs):
    app: bool = False
    provider: bool = False

    def parse(parser: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
        new_parser = parser.add_parser("new", help="Add new app or provider")
        new_parser.add_argument("-a", "--app", action="store_true", help="Add new app")
        new_parser.add_argument(
            "-p", "--provider", action="store_true", help="Add new provider"
        )


@dataclass
class RemoveArgs(BaseArgs):
    icons: bool = False
    assets: bool = False

    def parse(parser: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
        remove_parser = parser.add_parser(
            "remove", help="Remove unused icons or assets"
        )
        remove_parser.add_argument(
            "-i", "--icons", action="store_true", help="Remove unused icons"
        )
        remove_parser.add_argument(
            "-a", "--assets", action="store_true", help="Remove unused assets"
        )


T = TypeVar("T", UpdateArgs, NewArgs, RemoveArgs)

Command = Literal["update", "new", "remove"]


@dataclass
class Args(Generic[T]):
    command: Command
    args: T

    @classmethod
    def parse_args(cls) -> "Args":
        parser = argparse.ArgumentParser(description="Application argument parser")

        BaseArgs.parse(parser)

        subparsers = parser.add_subparsers(dest="command")

        UpdateArgs.parse(subparsers)

        NewArgs.parse(subparsers)

        RemoveArgs.parse(subparsers)

        args = parser.parse_args()

        return cls(args.command, args)


if __name__ == "__main__":
    args = Args.parse_args()
    print(args)
