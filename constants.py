class PATHS:
    VENV: str = "/home/anfreire/Documents/Scripts/UpdateMeScrapping/.venv"
    VT_KEY: str = "/home/anfreire/Documents/Scripts/UpdateMeScrapping/virustotal.json"
    INDEX_DIR: str = "/home/anfreire/Documents/Data/UpdateMeData"
    INDEX: str = "/home/anfreire/Documents/Data/UpdateMeData/index.json"
    APPS_DIR: str = "/home/anfreire/Documents/Data/UpdateMeData/apps"
    LOGS: str = "/home/anfreire/Documents/Scripts/UpdateMeScrapping/logs"


class LINKS:
    APPS_RELEASE = (
        lambda filename: f"https://github.com/anfreire/UpdateMeData/releases/download/apps/{filename}"
    )
