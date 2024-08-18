import re
import string
import os
from GLOBAL import GLOBAL, IndexProvider
from enum import Enum
from LIB.Apk import Apk


class AnalysisStatus(Enum):
    PENDING = 1
    SAFE = 2
    INFECTED = 3


class AppDiff(Enum):
    NONE = 1
    SHA256 = 2
    VERSION = 3
    PACKAGE_NAME = 4


class AppUtils:
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
            name = name.translate(AppUtils.DIGITS_TRANSLATIONS)
        return name.lower()

    @staticmethod
    def move_file(path: str, new_file_name: str) -> str:
        new_path = os.path.join(GLOBAL.Paths.Directories.Apps, new_file_name)
        if os.path.exists(new_path) and path != new_path:
            os.remove(new_path)
        os.rename(path, new_path)
        return new_path

    @staticmethod
    def get_analysis_status(path: str, apk: Apk) -> AnalysisStatus:
        file_submited = GLOBAL.VirusTotal.check_previous_submissions(path, apk.sha256)
        if file_submited is None:
            return AnalysisStatus.PENDING
        elif file_submited == True:
            return AnalysisStatus.INFECTED
        else:
            return AnalysisStatus.SAFE

    @staticmethod
    def get_app_status(provider: IndexProvider, apk: Apk) -> AppDiff:
        if apk.packageName != provider.packageName:
            return AppDiff.PACKAGE_NAME
        if apk.version != provider.version:
            return AppDiff.VERSION
        if apk.sha256 != provider.sha256:
            return AppDiff.SHA256
        return AppDiff.NONE

    @staticmethod
    def clean_directory(directory: str) -> None:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                GLOBAL.Log(
                    f"Failed to delete {file_path}\n{e.__class__.__name__}: {e.args}",
                    level="ERROR",
                    exception=GLOBAL.Args.debug,
                )
