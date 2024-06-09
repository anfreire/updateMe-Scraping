from utils.Index import Index
from utils.AppBase import AppBase
from lib.selenium import Selenium, By
from providers.Github import Github
from providers.Modyolo import Modyolo, Liteapks
from providers.Apkdone import ApkDone
from providers.Revanced import Revanced
from time import sleep
from providers.Aero import Aero


#####################################################################################
# HDO
def hdo():
    # HDO
    def HDO():
        return Selenium().downloadFile("https://hdo.app/download")

    app = AppBase("HDO", {"HDO": HDO})
    app.update()


#####################################################################################
# YOUTUBE
def youtube():
    # ReVanced
    def revanced():
        return Revanced("youtube-revanced")()

    # ReVanced Extended
    def revanced_extended():
        return Revanced("revanced-youtube-extended")()

    # ReVanced 2
    def revanced2():
        return Github("j-hc", "revanced-magisk-module")(
            [".apk", "youtube"], ["extended", "arm-v7a"]
        )

    # ReVanced Extended 2
    def revanced_extended2():
        return Github("j-hc", "revanced-magisk-module")(
            [".apk", "youtube-revanced-extended"], ["arm-v7a"]
        )

    app = AppBase(
        "YouTube",
        {
            "ReVanced": revanced,
            "ReVanced Extended": revanced_extended,
            "ReVanced (2)": revanced2,
            "ReVanced Extended (2)": revanced_extended2,
        },
    )
    app.update()


#####################################################################################
# YOUTUBE MUSIC
def youtube_music():
    # ReVanced
    def revanced():
        return Revanced("revanced-youtube-music")()

    # ReVanced Extended
    def revanced_extended():
        return Revanced("revanced-youtube-music-extended")()

    # ReVanced 2
    def revanced2():
        return Github("j-hc", "revanced-magisk-module")(
            [".apk", "music"], ["extended", "arm-v7a"]
        )

    # ReVanced Extended 2
    def revanced_extended2():
        return Github("j-hc", "revanced-magisk-module")(
            [".apk", "music-revanced-extended"], ["arm-v7a"]
        )

    app = AppBase(
        "YouTube Music",
        {
            "ReVanced": revanced,
            "ReVanced Extended": revanced_extended,
            "ReVanced (2)": revanced2,
            "ReVanced Extended (2)": revanced_extended2,
        },
    )
    app.update()


#####################################################################################
# TWITCH
def twitch():
    # ReVanced
    def revanced():
        return Revanced("revanced-twitch")()

    # ReVanced (2)
    def revanced2():
        return Github("j-hc", "revanced-magisk-module")(
            [".apk", "twitch", "all"], ["arm-v7a"]
        )

    app = AppBase("Twitch", {"ReVanced": revanced, "ReVanced (2)": revanced2})
    app.update()


#####################################################################################
# REDDIT
def reddit():
    # ReVanced Extended
    def revanced_extended():
        return Revanced("revanced-reddit-extended")()

    app = AppBase(
        "Reddit",
        {"ReVanced": revanced_extended},
    )
    app.update()


#####################################################################################
# TIKTOK
def tiktok():
    def revanced():
        return Github("j-hc", "revanced-magisk-module")(
            [".apk", "tiktok", "all"], ["arm-v7a"]
        )

    app = AppBase("TikTok", {"ReVanced": revanced})
    app.update()


#####################################################################################
# MICROG
def microg():
    def teamvanced():
        return Github("ReVanced", "GmsCore")(["signed", ".apk"], ["hw"])

    app = AppBase("MicroG", {"TeamVanced": teamvanced})
    app.update()


#####################################################################################
# SPOTIFY
def spotify():

    # MODYOLO
    def modyolo():
        return Modyolo("spotify-music-24463")()

    # LITEAPKS
    def liteapks():
        return Liteapks("spotify-music-98")()

    # APKDONE
    def apkdone():
        return ApkDone("spotify-mod")()

    app = AppBase(
        "Spotify",
        {
            "MODYOLO": modyolo,
            "LITEAPKS": liteapks,
            "APKDONE": apkdone,
        },
    )
    app.update()


#####################################################################################
# PHOTO EDITOR PRO
def photo_editor_pro():

    # MODYOLO
    def modyolo():
        return Modyolo("polish-photo-editor-pro-2578")()

    # LITEAPKS
    def liteapks():
        return Liteapks("polish-photo-editor-pro-491")()

    # APKDONE
    def apkdone():
        return ApkDone("photo-editor-pro-apk")()

    app = AppBase(
        "Photo Editor Pro",
        {
            "MODYOLO": modyolo,
            "LITEAPKS": liteapks,
            "APKDONE": apkdone,
        },
    )
    app.update()


#####################################################################################
# PHOTOSHOP EXPRESS
def photoshop_express():

    # MODYOLO
    def modyolo():
        return Modyolo("photoshop-express-12281")()

    # LITEAPKS
    def liteapks():
        return Liteapks("photoshop-express-570")()

    # APKDONE
    def apkdone():
        return ApkDone("adobe-photoshop-express")()

    app = AppBase(
        "Photoshop Express",
        {
            "MODYOLO": modyolo,
            "LITEAPKS": liteapks,
            "APKDONE": apkdone,
        },
    )
    app.update()


#####################################################################################
# CAPCUT
def capcut():

    # MODYOLO
    def modyolo():
        return Modyolo("capcut-video-editor-29058")()

    # LITEAPKS
    def liteapks():
        return Liteapks("capcut-311")()

    # APKDONE
    def apkdone():
        return ApkDone("capcut-mod-apk")()

    app = AppBase(
        "CapCut",
        {
            "MODYOLO": modyolo,
            "LITEAPKS": liteapks,
            "APKDONE": apkdone,
        },
    )
    app.update()


#####################################################################################
# INSHOT
def inshot():

    def modyolo():
        return Modyolo("inshot-2257")()

    # LITEAPKS
    def liteapks():
        return Liteapks("inshot-pro-107")()

    # APKDONE
    def apkdone():
        return ApkDone("inshot")()

    app = AppBase(
        "InShot",
        {
            "MODYOLO": modyolo,
            "LITEAPKS": liteapks,
            "APKDONE": apkdone,
        },
    )
    app.update()


#####################################################################################
# INSTAGRAM
def instagram():

    # Instander
    def instander():
        driver = Selenium()
        driver.get("https://thedise.me/instander/repo/")
        a_tags = driver.find_elements(By.XPATH, "//a")
        for a in a_tags:
            if a.text == "Clone":
                a.click()
                break
        elements = driver.find_elements(By.XPATH, "//a[@href]")
        link = None
        for element in elements:
            if (
                element.get_attribute("href")
                and element.get_attribute("href").endswith(".apk")
                and element.text.endswith("Clone")
            ):
                link = element.get_attribute("href")
                break
        return driver.downloadFile(link)

    # HONINSTA
    def honinsta():
        driver = Selenium()
        driver.get("https://honista.com/en/download.html")
        elements = driver.find_elements(By.XPATH, "//a[@href]")
        link = None
        for element in elements:
            if element.get_attribute("href") and element.get_attribute("href").endswith(
                ".apk"
            ):
                link = element.get_attribute("href")
                break
        return driver.downloadFile(link)

    app = AppBase(
        "Instagram",
        {
            "Instander": instander,
            "Honinsta": honinsta,
        },
    )
    app.update()


# #####################################################################################
# # TWITTER
# def twitter():
#     # AeroWitter
#     def aeroWitter():
#         driver = Aero()
#         driver.open("https://aerowitter.com/download-aero-twitter/package-2/?lang=en")
#         driver.open(
#             driver.get_href_by_text("Download Button 1 - AeroMods.app (Recommended)")
#         )
#         sleep(8)
#         driver.click_span("checkbox-custom")
#         origin = driver.get_href_by_text("Redirect Me!")
#         driver.open(origin)
#         return driver.downloadFile(driver.get_href_by_ending_link(".apk"))

#     app = AppBase(
#         "Twitter",
#         {
#             "AeroWitter": aeroWitter,
#         },
#     )
#     app.update()


#####################################################################################
# NEWPIPE
def newpipe():

    def teamnewpipe():
        return Github("TeamNewPipe", "NewPipe")([".apk"])

    app = AppBase("NewPipe", {"TeamNewPipe": teamnewpipe})
    app.update()


#####################################################################################
# SEAL
def seal():

    def junkfood02():
        return Github("JunkFood02", "Seal")(["universal", ".apk"])

    app = AppBase("Seal", {"JunkFood02": junkfood02})
    app.update()


#####################################################################################
# SMARTLAUNCHER
def smartlauncher():

    def modyolo():
        return Modyolo("smart-launcher-6-27413")()

    # LITEAPKS
    def liteapks():
        return Liteapks("smart-launcher-6-184")()

    # APKDONE
    def apkdone():
        return ApkDone("smart-launcher-5")()

    app = AppBase(
        "Smart Launcher 6",
        {
            "MODYOLO": modyolo,
            "LITEAPKS": liteapks,
            "APKDONE": apkdone,
        },
    )
    app.update()


def niagaralauncher():

    def modyolo():
        return Modyolo("niagara-launcher-63941")()

    # LITEAPKS
    def liteapks():
        return Liteapks("niagara-launcher-75423")()

    # APKDONE
    def apkdone():
        return ApkDone("niagara-launcher")()

    app = AppBase(
        "Niagara Launcher",
        {
            "MODYOLO": modyolo,
            "LITEAPKS": liteapks,
            "APKDONE": apkdone,
        },
    )
    app.update()


#####################################################################################
# REVANCED MANAGER
def revancedManager():

    def ReVanced():
        return Github("ReVanced", "revanced-manager")([".apk"])

    app = AppBase("ReVanced Manager", {"ReVanced": ReVanced})
    app.update()


#####################################################################################
# YTDLNIS
def ytdlnis():
    def ytdlnis():
        return Github("deniscerri", "ytdlnis")([".apk", "universal"])

    app = AppBase("YTDLnis", {"deniscerr": ytdlnis})
    app.update()


#####################################################################################
# NEVER HAVE I EVER
def neverhaveiever():
    # LiteApks
    def liteapks():
        return Liteapks("never-have-i-ever-194362")()

    app = AppBase("Never Have I Ever", {"LiteApks": liteapks})
    app.update()


#####################################################################################
# LAWNCHAIR
def lawnchair():

    # LawnchairLauncher
    def lawnchairlauncher():
        return Github("LawnchairLauncher", "Lawnchair")(["Lawnchair", ".apk"])

    app = AppBase("Lawnchair", {"LawnchairLauncher": lawnchairlauncher})
    app.update()
