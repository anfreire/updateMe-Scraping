import blessed
from typing import List, TypedDict

SHORTCUTS_TYPE = TypedDict("SHORTCUTS_TYPE", {"shortcut": str, "action": str})


SHORTCUTS = {
    "submit": SHORTCUTS_TYPE(shortcut="enter", action="Submit"),
    "quit": SHORTCUTS_TYPE(shortcut="!", action="Quit"),
    "autocomplete": SHORTCUTS_TYPE(shortcut="tab", action="Autocomplete"),
}


class CLI:
    def __init__(self) -> None:
        self.term = blessed.Terminal()

    def print_footer(self, shortcuts: List[SHORTCUTS_TYPE] = []) -> None:
        if not len(shortcuts):
            return
        with self.term.location(0, self.term.height - 1):
            for shortcut in shortcuts:
                print(
                    f"{self.term.on_snow1(self.term.black(self.term.bold(' ' + shortcut['shortcut'] + ' ')))} {shortcut['action']}",
                    end="    ",
                )
        print(flush=True)

    def show_message(self, message: str, error: bool = False) -> None:
        if error:
            message = self.term.red(message)
        with self.term.cbreak(), self.term.hidden_cursor():
            print(
                self.term.clear + self.term.move_xy(0, 0) + message, end="", flush=True
            )
            print(
                self.term.move_xy(0, 2) + "Press any key to continue...",
                end="",
                flush=True,
            )
            self.term.inkey()

    def select(
        self,
        prompt: str,
        options: List[str],
        multiple: bool = False,
        check: bool = False,
    ) -> str | List[str]:
        selected = [] if multiple else [0]
        current = 0
        shortcuts = [
            SHORTCUTS_TYPE(shortcut="▲", action="Previous"),
            SHORTCUTS_TYPE(shortcut="▼", action="Next"),
            SHORTCUTS["submit"],
        ]
        if multiple:
            shortcuts.append(SHORTCUTS_TYPE(shortcut="space", action="Select"))
        with self.term.cbreak(), self.term.hidden_cursor():
            while True:
                print(
                    self.term.clear + self.term.move_xy(0, 0) + prompt,
                    end="",
                    flush=True,
                )
                print(self.term.move_xy(0, 2), end="", flush=True)
                for idx, option in enumerate(options):
                    curr_option = (
                        self.term.bold(f"[X] {option}")
                        if idx in selected
                        else f"[ ] {option}"
                    )
                    if idx == current:
                        print(self.term.on_snow3(curr_option))
                    else:
                        print(curr_option)
                self.print_footer(shortcuts)
                val = self.term.inkey()
                if val == "\n":
                    confirm_options = (
                        options[current]
                        if not multiple
                        else [options[i] for i in selected]
                    )
                    if check and (
                        self.select(
                            f"Is this correct? {self.term.bold(str(confirm_options))}",
                            ["Yes", "No"],
                        )
                        != "Yes"
                    ):
                        continue
                    return confirm_options
                elif val.code == self.term.KEY_DOWN:
                    current = (current + 1) % len(options)
                    if not multiple:
                        selected = [current]
                elif val.code == self.term.KEY_UP:
                    current = (current - 1) % len(options)
                    if not multiple:
                        selected = [current]
                elif val == " " and multiple:
                    if current in selected:
                        selected.remove(current)
                    else:
                        selected.append(current)

    def simple_input(self, prompt: str) -> str:
        while True:
            print(self.term.clear, end="", flush=True)
            input_entered = input(self.term.bold(prompt))
            if (
                self.select(
                    f"Is this correct? {self.term.bold(input_entered)}", ["Yes", "No"]
                )
                == "Yes"
            ):
                return input_entered

    def input(
        self,
        prompt: str,
        initial_value: str = "",
        autocomplete: List[str] = [],
        multiple: bool = False,
    ) -> str | List[str]:
        if initial_value == "" and not multiple and not len(autocomplete):
            return self.simple_input(prompt)
        shortcuts = [SHORTCUTS["submit"]]
        if len(autocomplete):
            shortcuts.append(SHORTCUTS["autocomplete"])
        if multiple:
            shortcuts.append(SHORTCUTS["quit"])
        input_str = initial_value
        inputed = [] if multiple else None
        while True:
            with self.term.cbreak(), self.term.hidden_cursor():
                print(self.term.clear, end="", flush=True)
                self.print_footer(shortcuts)

                autocompleteIdx = -1

                if len(input_str):
                    for feature in autocomplete:
                        if feature.lower().startswith(input_str.lower()):
                            autocompleteIdx = autocomplete.index(feature)
                            break
                    print(
                        self.term.move_xy(0, 0)
                        + f'{prompt}: {input_str + (self.term.gray25(autocomplete[autocompleteIdx][len(input_str):]) if autocompleteIdx != -1 else "")}'
                    )
                else:
                    print(self.term.move_xy(0, 0) + f"{self.term.bold(prompt)} ")

                if multiple and len(inputed):
                    print(self.term.move_xy(0, 2) + self.term.bold("Inputed:"))
                    for feature in inputed:
                        print(f"- {feature}")

                val = self.term.inkey()
                if val == "\n":
                    if len(input_str):
                        correct = (
                            self.select(
                                f"Is this correct? {self.term.bold(input_str)}",
                                ["Yes", "No"],
                            )
                            == "Yes"
                        )
                        if not correct:
                            continue
                        if multiple:
                            inputed.append(input_str)
                            input_str = ""
                        else:
                            return input_str
                elif val == "\t" and len(autocomplete):
                    if autocompleteIdx != -1:
                        input_str = autocomplete[autocompleteIdx]
                elif val == "!" and multiple:
                    break
                elif val.code == self.term.KEY_BACKSPACE:
                    input_str = input_str[:-1]
                elif val.isprintable():
                    input_str += val
        return inputed
