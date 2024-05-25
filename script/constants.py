import os


class PATHS:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR: str = os.path.join(SCRIPT_DIR, "../data")
    APPS_DIR: str = os.path.join(DATA_DIR, "apps")
    ENV: str = os.path.join(SCRIPT_DIR, ".env.json")
    INDEX: str = os.path.join(DATA_DIR, "index.json")


class LINKS:
    APPS_RELEASE = (
        lambda filename: f"https://github.com/anfreire/UpdateMeData/releases/download/apps/{filename}"
    )
