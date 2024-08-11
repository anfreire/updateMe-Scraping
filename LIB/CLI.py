from prompt_toolkit.styles import Style
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import (
    yes_no_dialog,
    message_dialog,
    radiolist_dialog,
    checkboxlist_dialog,
)
from prompt_toolkit import prompt
import enum


class MyCompleter(Completer):
    def __init__(self, words_list: list[str]):
        self.words_list = words_list

    def get_completions(self, document, complete_event):
        current_line = document.current_line_before_cursor.lower()
        suggestions = [
            word for word in self.words_list if word.lower().startswith(current_line)
        ]
        for suggestion in suggestions:
            yield Completion(suggestion, start_position=0)


class StyleType(enum.Enum):
    NONE = None
    INFO = Style.from_dict({"bg": "#00ff00"})
    WARNING = Style.from_dict({"bg": "#ffff00"})
    ERROR = Style.from_dict({"bg": "#ff0000"})
    SUCCESS = Style.from_dict({"bg": "#00ff00"})


class CLI:

    @staticmethod
    def message(
        title: str = "", message: str = "", style: StyleType = StyleType.NONE
    ) -> None:
        message_dialog(
            title=title,
            text=message,
            style=style.value,
        ).run()

    @staticmethod
    def confirm(
        title: str = "",
        message: str = "",
        style: StyleType = StyleType.NONE,
    ) -> bool:
        return yes_no_dialog(
            title=title,
            text=message,
            style=style.value,
        ).run()

    @staticmethod
    def checkbox(
        message: str = "",
        options: list[str] = [],
        title: str = "",
    ) -> list[str]:
        return checkboxlist_dialog(
            title=title,
            text=message,
            values=[(option, option) for option in options],
        ).run()

    @staticmethod
    def select(
        title: str = "",
        message: str = "",
        options: list[str] = [],
    ) -> str:
        return radiolist_dialog(
            title=title,
            text=message,
            values=[(option, option) for option in options],
        ).run()

    @staticmethod
    def input(
        message: str = "",
        suggestions: list[str] = [],
    ) -> str:
        return prompt(
            message=message,
            completer=MyCompleter(suggestions) if len(suggestions) > 0 else None,
        ).strip()

    def multiline_input(
        message: str = "",
        suggestions: list[str] = [],
    ) -> list[str]:
        value: str = prompt(
            message=message,
            completer=MyCompleter(suggestions) if len(suggestions) > 0 else None,
            multiline=True,
        ).strip()
        return [line.strip() for line in value.split("\n") if len(line.strip())]
