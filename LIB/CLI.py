import blessed
from copy import deepcopy
from enum import Enum
from typing import Literal
from pyperclip import paste


class Shortcuts(Enum):
    """Shortcuts for the CLI.

    Attributes:
        - EXIT (tuple[tuple[str, str], str]): The shortcut to exit the CLI.
        - SELECT (tuple[str, str]): The shortcut to select an option.
        - SAVE (tuple[tuple[str, str], str]): The shortcut to save the current state.
        - MOVE_UP (tuple[str, str]): The shortcut to move up.
        - MOVE_DOWN (tuple[str, str]): The shortcut to move down
    """

    EXIT = (("Ctrl", "C"), "Exit")
    SELECT = ("Enter", "Select")
    SUBMIT = ("Enter", "Submit")
    CHECK = ("Space", "Check/Uncheck")
    PASTE = (("Ctrl", "V"), "Paste")
    SAVE = (("Ctrl", "S"), "Save")
    MOVE_UP = ("↑", "Move Up")
    MOVE_DOWN = ("↓", "Move Down")


class Signals:
    class Exited(Exception):
        def __init__(self, message: str = "") -> None:
            super().__init__(message)

    class Selected(Exception):
        def __init__(self, message: str = "") -> None:
            super().__init__(message)

    class Saved(Exception):
        def __init__(self, message: str = "") -> None:
            super().__init__(message)


class CLI:
    def __init__(self) -> None:
        self.term = blessed.Terminal()

    def __del__(self) -> None:
        self.show_cursor()

    def __call__(self) -> None:
        try:
            self.__hide_cursor()
            self.__clear()
            while True:
                self.__print(self.term.move_xy(0, 0))
                with self.term.cbreak():
                    val = self.term.inkey()
                    self.__clear()
                    self.__print_header("Keyboard Input")
                    self.__print(
                        f"""- {self.term.bold("repr(val):")} {repr(val)}
- {self.term.bold("val.code:")} '{val.code}'
- {self.term.bold("val.name:")} '{val.name}'
- {self.term.bold("val.is_sequence:")} '{val.is_sequence}'

Press a key to see the output...
"""
                    )
        except KeyboardInterrupt:
            return

    ############################################################################
    #   UTILS

    def __print(self, text: str) -> None:
        """Print text to the terminal.

        Args:
            - text (str): The text to print to the terminal.
        """
        print(text, end="", flush=True)

    def __clear(self) -> None:
        """Clear the terminal.

        Returns:
            None
        """
        self.__print(self.term.clear + self.term.home)

    def __hide_cursor(self) -> None:
        """Hide the cursor.

        Returns:
            None
        """
        self.__print(self.term.hide_cursor)

    def show_cursor(self) -> None:
        """Show the cursor.

        Returns:
            None
        """
        self.__print(self.term.normal_cursor)

    ############################################################################
    #   HEADER

    def __print_header(self, title: str) -> None:
        """Print the header of the CLI.

        Args:
            - title (str): The title of the CLI.
        """
        spacing = self.term.on_black((len(title) + 4) * " ") + "\n"
        self.__print(
            spacing
            + self.term.on_black(self.term.white(self.term.bold(f"  {title}  ")))
            + "\n"
            + spacing
            + "\n"
        )

    ############################################################################
    #   FOOTER

    def __print_shortcuts(self, shortcuts: list[Shortcuts]) -> None:
        """Print the shortcuts of the CLI.

        Args:
            - shortcuts (list[Shortcuts]): The shortcuts to print to the terminal.
        """
        to_print = self.term.move_xy(0, self.term.height - 1)
        for i, shortcut in enumerate(shortcuts):
            (shortcut, description) = shortcut.value
            if type(shortcut) == tuple:
                shortcut = (
                    self.term.bold(shortcut[0]) + " + " + self.term.bold(shortcut[1])
                )
            else:
                shortcut = self.term.bold(shortcut)

            to_print += f"{self.term.on_snow3(f' {shortcut} ')} {description}"

            if i != len(shortcuts) - 1:
                to_print += "    "
        self.__print(to_print)

    ################################################################################
    #   SELECT

    def __print_select(self, options: list[str], selected: str) -> None:
        """Prints the options with the selected option highlighted

        Args:
            - options (list[str]): The options to print.
            - selected (str): The selected option.
        """
        term_height = self.term.height - 6
        if len(options) > term_height:
            start = max(0, options.index(selected) - term_height // 2)
            end = min(len(options), start + term_height)
            options = options[start:end]
        to_print = ""
        for option in options:
            to_print += self.term.on_snow3(option) if option == selected else option
            to_print += "\n"
        self.__print(to_print)

    def __input_select(self, options: list[str], selected: str) -> str:
        """Input for the select options

        Args:
            - options (list[str]): The options to choose from.
            - selected (str): The selected option.

        Returns:
            str: The selected option.

        Raises:
            Signals.Selected: If the user submits the selected option.
        """
        try:
            with self.term.cbreak():
                val = self.term.inkey()
                match val.code:
                    case 343:
                        self.__clear()
                        raise Signals.Selected(selected)
                    case 259:
                        return options[(options.index(selected) - 1) % len(options)]
                    case 258:
                        return options[(options.index(selected) + 1) % len(options)]
                return selected
        except KeyboardInterrupt:
            self.__clear()
            raise Signals.Exited("Exited")

    def select(self, title: str, options: list[str]) -> str | None:
        """Select an option from a list of options.

        Args:
            - title (str): The title of the select menu.
            - options (list[str]): The options to choose from.

        Returns:
            str: The selected option.
        """
        selected = options[0]
        while True:
            try:
                self.__hide_cursor()
                self.__clear()
                self.__print_header(title)
                self.__print_select(options, selected)
                self.__print_shortcuts(
                    [
                        Shortcuts.EXIT,
                        Shortcuts.MOVE_UP,
                        Shortcuts.MOVE_DOWN,
                        Shortcuts.SELECT,
                    ]
                )
                selected = self.__input_select(options, selected)
            except (Signals.Selected, Signals.Exited) as e:
                if type(e) == Signals.Selected:
                    return selected
                return None

    ################################################################################
    #   CHECKBOX

    def __print_checkbox(
        self, options: list[str], chosen: list[str], selected: str
    ) -> None:
        """Prints the options with checkboxes

        Args:
            - options (list[str]): The options to print.
            - chosen (list[str]): The options that are chosen.
            - selected (str): The selected option.
        """
        term_height = self.term.height - 6
        if len(options) > term_height:
            start = max(0, options.index(selected) - term_height // 2)
            end = min(len(options), start + term_height)
            options = options[start:end]
        to_print = ""
        for option in options:
            line = ("[X] " if option in chosen else "[ ] ") + option
            to_print += (
                self.term.on_snow3(line) if option == selected else line
            ) + "\n"
        self.__print(to_print)

    def __input_checkbox(
        self, options: list[str], chosen: list[str], selected: str
    ) -> tuple[list[str], str]:
        """Input for the checkbox options

        Args:
            - options (list[str]): The options to choose from.
            - chosen (list[str]): The options that are chosen.
            - selected (str): The selected option.

        Returns:
            tuple[list[str], str]: The chosen options and the selected option.

        Raises:
            Signals.Selected: If the user submits the selected option.
        """
        try:
            with self.term.cbreak():
                val = self.term.inkey()

                match val.code:
                    case 343:
                        self.__clear()
                        raise Signals.Selected(selected)
                    case 259:
                        return (
                            chosen,
                            options[(options.index(selected) - 1) % len(options)],
                        )
                    case 258:
                        return (
                            chosen,
                            options[(options.index(selected) + 1) % len(options)],
                        )
                    case _:
                        if val == " ":
                            if selected in chosen:
                                chosen.remove(selected)
                            else:
                                chosen.append(selected)

                return chosen, selected
        except KeyboardInterrupt:
            self.__clear()
            raise Signals.Exited("Exited")

    def checkbox(self, title: str, options: list[str]) -> list[str] | None:
        """Select multiple options from a list of options.

        Args:
            - title (str): The title of the checkbox menu.
            - options (list[str]): The options to choose from.

        Returns:
            list[str]: The selected options.

        Raises:
            Signals.Exited: If the user exits the checkbox menu.
        """
        selected = options[0]
        chosen = []
        while True:
            try:
                self.__hide_cursor()
                self.__clear()
                self.__print_header(title)
                self.__print_checkbox(options, chosen, selected)
                self.__print_shortcuts(
                    [
                        Shortcuts.EXIT,
                        Shortcuts.MOVE_UP,
                        Shortcuts.MOVE_DOWN,
                        Shortcuts.CHECK,
                        Shortcuts.SUBMIT,
                    ]
                )
                chosen, selected = self.__input_checkbox(options, chosen, selected)
            except (Signals.Selected, Signals.Exited) as e:
                return chosen if type(e) == Signals.Selected else None

    ############################################################################
    #   FORM

    def __print_form(
        self, props: dict[str, str], value_index: int, selected: str
    ) -> None:
        term_height = self.term.height - 6
        if len(props) > term_height:
            keys = list(props.keys())
            start = max(0, keys.index(selected) - term_height // 2)
            end = min(len(keys), start + term_height)
            props = {key: props[key] for key in keys[start:end]}
        to_print = ""
        for field, value in props.items():
            if selected == field:
                if value_index == len(value):
                    value += " "
                value = (
                    value[:value_index]
                    + self.term.on_skyblue3(value[value_index])
                    + value[value_index + 1 :]
                )
            to_print += f"{self.term.bold(field)}: {value}\n"
        self.__print(to_print)

    def __input_form(
        self, props: dict[str, str], value_index: int, selected: str
    ) -> tuple[dict[str, str], int, str]:
        try:
            with self.term.cbreak():
                val = self.term.inkey()

                if val == "\x13":
                    self.__clear()
                    raise Signals.Saved("Saved")

                match val.code:
                    case 259:
                        selected = list(props.keys())[
                            (list(props.keys()).index(selected) - 1) % len(props)
                        ]
                        value_index = min(len(props[selected]), value_index)
                    case 258:
                        selected = list(props.keys())[
                            (list(props.keys()).index(selected) + 1) % len(props)
                        ]
                        value_index = min(len(props[selected]), value_index)
                    case 260:
                        value_index = max(0, value_index - 1)
                    case 261:
                        value_index = min(len(props[selected]), value_index + 1)
                    case _:
                        old_value = props[selected]

                        if val == "\x16":
                            new_value = (
                                old_value[:value_index]
                                + paste()
                                + old_value[value_index:]
                            )
                            props[selected] = new_value
                            value_index = value_index + len(paste())
                        elif val.code == 263:
                            new_value = (
                                old_value[: value_index - 1] + old_value[value_index:]
                            )
                            props[selected] = new_value
                            value_index = max(0, value_index - 1)
                        elif not val.is_sequence and val.isprintable():
                            new_value = (
                                old_value[:value_index] + val + old_value[value_index:]
                            )
                            props[selected] = new_value
                            value_index = value_index + 1

                return props, value_index, selected

        except KeyboardInterrupt:
            self.__clear()
            raise Signals.Exited

    def form(self, title: str, props: dict[str, str | None]) -> dict[str, str]:
        selected = list(props.keys())[0]
        value_index = len(props[selected])
        while True:
            try:
                self.__hide_cursor()
                self.__clear()
                self.__print_header(title)
                self.__print_form(props, value_index, selected)
                self.__print_shortcuts(
                    [Shortcuts.EXIT, Shortcuts.PASTE, Shortcuts.SAVE]
                )
                props, value_index, selected = self.__input_form(
                    props, value_index, selected
                )
            except (Signals.Saved, Signals.Exited) as e:
                if type(e) == Signals.Exited:
                    return None
                return props

    ############################################################################
    #   INPUT

    def __print_input_input(
        self,
        value: str,
        index: int,
        suggested: str | None,
    ) -> None:
        value

        if suggested and len(suggested) > len(value):
            to_suggest = suggested[len(value) :]
            to_print = (
                value
                + self.term.on_skyblue3(to_suggest[0])
                + self.term.gray50(to_suggest[1:])
            )
        else:
            if index >= len(value):
                to_print = value + self.term.on_skyblue3(" ")
            else:
                to_print = (
                    value[:index]
                    + self.term.on_skyblue3(value[index])
                    + value[index + 1 :]
                )
        self.__print(to_print + "\n\n")

    def __print_input_inputed(self, inputed: list[str]) -> None:
        to_print = f"{self.term.bold('Inputed:')}\n"
        for value in inputed:
            to_print += f"- {value}\n"
        self.__print(to_print)

    def __print_input(
        self, value: str, index: int, suggested: str | None, inputed: list[str]
    ) -> None:
        term_height = self.term.height - 6
        term_height -= 2  # input
        self.__print_input_input(value, index, suggested)
        if len(inputed) and term_height > 0:
            term_height -= 1  # inputed title
            self.__print_input_inputed(inputed[-term_height:])

    def __input_input(
        self,
        value: str,
        index: int,
        suggested: str | None,
        autocomplete: list[str],
        multiple: bool = False,
        inputed: list[str] = [],
    ) -> tuple[str, int, str | None, list[str]]:
        try:
            with self.term.cbreak():
                val = self.term.inkey()

                match val.code:
                    case 343:  # Enter
                        if multiple:
                            inputed.append(value)
                    case 260:  # Left
                        index = max(0, index - 1)
                    case 261:  # Right
                        index = min(len(value), index + 1)
                    case 512:  # TAB
                        if suggested:
                            value = suggested
                            index = len(value)
                            suggested = None
                    case 263:  # Backspace
                        value = value[: index - 1] + value[index:]
                        index = max(0, index - 1)
                    case _:
                        old_value = value

                        if val == "\x16":  # Ctrl + V
                            new_value = old_value[:index] + paste() + old_value[index:]
                            value = new_value
                            index = index + len(paste())

                        elif val == "\x13":  # Ctrl + S
                            raise Signals.Saved

                        elif not val.is_sequence and val.isprintable():
                            new_value = old_value[:index] + val + old_value[index:]
                            value = new_value
                            index += 1

                if len(autocomplete):
                    suggestions = [
                        word
                        for word in autocomplete
                        if word.lower().startswith(value.lower())
                    ]
                    if len(suggestions) == 0:
                        suggested = None
                    else:
                        suggested = suggestions[0]

                return value, index, suggested, inputed
        except KeyboardInterrupt:
            self.__clear()
            raise Signals.Exited

    def input(
        self,
        title: str,
        value: str = "",
        autocomplete: list[str] = [],
        multiple: bool = False,
    ) -> str | list[str] | None:
        index = len(value)
        suggested = None
        inputed = []
        while True:
            try:
                self.__hide_cursor()
                self.__clear()
                self.__print_header(title)
                self.__print_input(value, index, suggested, inputed)
                shortcuts = [Shortcuts.EXIT, Shortcuts.PASTE]
                if multiple:
                    shortcuts.append(Shortcuts.SUBMIT)
                shortcuts.append(Shortcuts.SAVE)
                self.__print_shortcuts(shortcuts)
                value, index, suggested, inputed = self.__input_input(
                    value, index, suggested, autocomplete, multiple, inputed
                )
            except (Signals.Exited, Signals.Selected, Signals.Saved) as e:
                if type(e) == Signals.Exited:
                    return None
                return value if not multiple else inputed

    ############################################################################
    #   MESSAGE

    def message(
        self,
        message: str,
        type: 'Literal["error", "info", "success", "warning", None]' = None,
        prompt: bool = False,
    ) -> bool | None:
        """Print a message to the terminal.

        Args:
            - message (str): The message to print to the terminal.
            - type (Literal["error", "info", "success"]): The type of message to print.

        Returns:
            None
        """
        color = {
            "None": lambda x: x,
            "error": lambda x: self.term.red(self.term.bold(x)),
            "info": lambda x: self.term.blue(self.term.bold(x)),
            "success": lambda x: self.term.green(self.term.bold(x)),
            "warning": lambda x: self.term.yellow(self.term.bold(x)),
        }
        self.__hide_cursor() if not prompt else self.show_cursor()
        self.__clear()
        self.__print(color[str(type)](message))
        try:
            if not prompt:
                self.__print("\n\nPress any key to continue...")
                with self.term.cbreak():
                    self.term.inkey()
                    return None
            self.__print(" (y/n)")
            with self.term.cbreak():
                return self.term.inkey().lower() == "y"
        except KeyboardInterrupt:
            return None if not prompt else False


if __name__ == "__main__":
    CLI()()
