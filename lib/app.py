import re
import string


class App:
    DIGITS_TRANSLATIONS = str.maketrans(
        {
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
    )

    @staticmethod
    def filter_name(name: str) -> str:
        name = re.sub(r"[^\w]", "", name)
        if name and name[0] in string.digits:
            name = name.translate(App.DIGITS_TRANSLATIONS)
        return name.lower()
