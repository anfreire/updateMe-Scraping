from utils.Index import Index
from utils.AppBase import AppBase
from lib.selenium import Selenium, By
from providers.Github import Github
from providers.Modyolo import Modyolo, Liteapks, Moddroid
from providers.Apkdone import ApkDone
from providers.Revanced import Revanced
from time import sleep
from providers.Aero import Aero
import re


#####################################################################################
# HDO
def hdo():
	# HDO
	def HDO():
		driver = Selenium()
		return driver.downloadFile("https://hdo.app/download")

	app = AppBase("HDO", {"HDO": HDO})
	app.update()


#####################################################################################
# YOUTUBE
def youtube(index: Index):
	# ReVanced
	def revanced():
		revanced = Revanced("youtube-revanced")
		return revanced.getLink()

	# ReVanced Extended
	def revanced_extended():
		gh = Revanced("revanced-youtube-extended")
		return gh.getLink()

	# ReVanced 2
	def revanced2():
		gh = Github("j-hc", "revanced-magisk-module")
		versions = gh.getVersions()
		count = 0
		link = None
		while link is None and count < len(versions):
			links = gh.getLinks(
				versions[count], [".apk", "youtube"], ["extended", "arm-v7a"]
			)
			if len(links) > 0:
				link = links[0]
				break
			count += 1
		return (link, gh.origin)

	# ReVanced Extended 2
	def revanced_extended2():
		gh = Github("j-hc", "revanced-magisk-module")
		versions = gh.getVersions()
		count = 0
		link = None
		while link is None and count < len(versions):
			links = gh.getLinks(
				versions[count], [".apk", "youtube-revanced-extended"], ["arm-v7a"]
			)
			if len(links) > 0:
				link = links[0]
				break
			count += 1
		return (link, gh.origin)

	app = AppBase(
		"YouTube",
		{
			"ReVanced": revanced,
			"ReVanced Extended": revanced_extended,
			"ReVanced (2)": revanced2,
			"ReVanced Extended (2)": revanced_extended2,
		},
	)
	app.update(index)


#####################################################################################
# YOUTUBE MUSIC
def youtube_music(index: Index):
	# ReVanced
	def revanced():
		revanced = Revanced("revanced-youtube-music")
		return revanced.getLink()

	# ReVanced Extended
	def revanced_extended():
		gh = Revanced("revanced-youtube-music-extended")
		return gh.getLink()

	# ReVanced 2
	def revanced2():
		gh = Github("j-hc", "revanced-magisk-module")
		versions = gh.getVersions()
		count = 0
		link = None
		while link is None and count < len(versions):
			links = gh.getLinks(
				versions[count], [".apk", "music"], ["extended", "arm-v7a"]
			)
			if len(links) > 0:
				link = links[0]
				break
			count += 1
		return (link, gh.origin)

	# ReVanced Extended 2
	def revanced_extended2():
		gh = Github("j-hc", "revanced-magisk-module")
		versions = gh.getVersions()
		count = 0
		link = None
		while link is None and count < len(versions):
			links = gh.getLinks(
				versions[count], [".apk", "music-revanced-extended"], ["arm-v7a"]
			)
			if len(links) > 0:
				link = links[0]
				break
			count += 1
		return (link, gh.origin)

	app = AppBase(
		"YouTube Music",
		{
			"ReVanced": revanced,
			"ReVanced Extended": revanced_extended,
			"ReVanced (2)": revanced2,
			"ReVanced Extended (2)": revanced_extended2,
		},
	)
	app.update(index)


#####################################################################################
# TWITCH
def twitch(index: Index):
	# ReVanced
	def revanced():
		revanced = Revanced("revanced-twitch")
		return revanced.getLink()

	app = AppBase("Twitch", {"ReVanced": revanced})
	app.update(index)


#####################################################################################
# REDDIT
def reddit(index: Index):
	# ReVanced Extended
	def revanced_extended():
		revanced = Revanced("revanced-reddit-extended")
		return revanced.getLink()

	app = AppBase(
		"Reddit",
		{"ReVanced": revanced_extended},
	)
	app.update(index)


#####################################################################################
# TIKTOK
def tiktok(index: Index):
	# ReVanced
	def revanced():
		revanced = Revanced("revanced-tiktok")
		return revanced.getLink()

	app = AppBase("TikTok", {"ReVanced": revanced})
	app.update(index)


#####################################################################################
# MICROG
def microg(index: Index):
	def teamvanced():
		gh = Github("ReVanced", "GmsCore")
		latest = gh.getVersions()[0]
		link = gh.getLinks(latest, ["signed", ".apk"], ["hw"])[0]
		return (link, gh.origin)

	app = AppBase("MicroG", {"TeamVanced": teamvanced})
	app.update(index)


#####################################################################################
# SPOTIFY
def spotify(index: Index):

	# MODYOLO
	def modyolo():
		driver = Modyolo("spotify-music-24463")
		try:
			link = driver.getLink()
		except:
			link = driver.getLink_alt()
		return link

	# LITEAPKS
	def liteapks():
		driver = Liteapks("spotify-music-98")
		return (driver.getLink(), driver.origin)

	# APKDONE
	def apkdone():
		driver = ApkDone("spotify-mod")
		link = driver.getLink()
		return link

	app = AppBase(
		"Spotify",
		{
			"MODYOLO": modyolo,
			"LITEAPKS": liteapks,
			"APKDONE": apkdone,
		},
	)
	app.update(index)


#####################################################################################
# PHOTO EDITOR PRO
def photo_editor_pro(index: Index):

	# MODYOLO
	def modyolo():
		driver = Modyolo("polish-photo-editor-pro-2578")
		link = driver.getLink()
		return (link, driver.origin)

	# LITEAPKS
	def liteapks():
		driver = Liteapks("polish-photo-editor-pro-491")
		link = driver.getLink()
		return (link, driver.origin)

	# APKDONE
	def apkdone():
		driver = ApkDone("photo-editor-pro-apk")
		link = driver.getLink()
		return link

	app = AppBase(
		"Photo Editor Pro",
		{
			"MODYOLO": modyolo,
			"LITEAPKS": liteapks,
			"APKDONE": apkdone,
		},
	)
	app.update(index)


#####################################################################################
# PHOTOSHOP EXPRESS
def photoshop_express(index: Index):

	# MODYOLO
	def modyolo():
		driver = Modyolo("photoshop-express-12281")
		link = driver.getLink()
		return (link, driver.origin)

	# LITEAPKS
	def liteapks():
		driver = Liteapks("photoshop-express-570")
		link = driver.getLink()
		return (link, driver.origin)

	# APKDONE
	def apkdone():
		driver = ApkDone("adobe-photoshop-express")
		link = driver.getLink()
		return link

	app = AppBase(
		"Photoshop Express",
		{
			"MODYOLO": modyolo,
			"LITEAPKS": liteapks,
			"APKDONE": apkdone,
		},
	)
	app.update(index)


#####################################################################################
# CAPCUT
def capcut(index: Index):

	# MODYOLO
	def modyolo():
		driver = Modyolo("capcut-video-editor-29058")
		link = driver.getLink()
		return (link, driver.origin)

	# LITEAPKS
	def liteapks():
		driver = Liteapks("capcut-311")
		link = driver.getLink()
		return (link, driver.origin)

	# APKDONE
	def apkdone():
		driver = ApkDone("capcut-mod-apk")
		link = driver.getLink()
		return link

	app = AppBase(
		"CapCut",
		{
			"MODYOLO": modyolo,
			"LITEAPKS": liteapks,
			"APKDONE": apkdone,
		},
	)
	app.update(index)


#####################################################################################
# INSHOT
def inshot(index: Index):

	def modyolo():
		driver = Modyolo("inshot-2257")
		link = driver.getLink()
		return (link, driver.origin)

	# LITEAPKS
	def liteapks():
		driver = Liteapks("inshot-pro-107")
		link = driver.getLink()
		return (link, driver.origin)

	# APKDONE
	def apkdone():
		driver = ApkDone("inshot")
		link = driver.getLink()
		return link

	app = AppBase(
		"InShot",
		{
			"MODYOLO": modyolo,
			"LITEAPKS": liteapks,
			"APKDONE": apkdone,
		},
	)
	app.update(index)


#####################################################################################
# INSTAGRAM
def instagram(index: Index):

	# Instander
	def instander():
		driver = Selenium()
		driver.openLink("https://thedise.me/instander/repo/")
		a_tags = driver.getElements(By.XPATH, "//a")
		for a in a_tags:
			if a.text == "Clone":
				a.click()
				break
		elements = driver.getElements(By.XPATH, "//a[@href]")
		link = None
		for element in elements:
			if (
				element.get_attribute("href")
				and element.get_attribute("href").endswith(".apk")
				and element.text.endswith("Clone")
			):
				link = element.get_attribute("href")
				break
		return link
	
	# HONINSTA
	def honinsta():
		driver = Selenium()
		driver.openLink("https://honista.com/en/download.html")
		elements = driver.getElements(By.XPATH, "//a[@href]")
		link = None
		for element in elements:
			if (
				element.get_attribute("href")
				and element.get_attribute("href").endswith(".apk")
			):
				link = element.get_attribute("href")
				break
		return link

	# AeroInsta
	def aeroinsta():
		driver = Aero()
		driver.open("https://aeroinsta.com/download-insta-aero/package-2/?lang=en")
		driver.open(driver.get_href_by_text("Download via AeroMods.app (suggested)"))
		sleep(8)
		driver.click_span("checkbox-custom")
		origin = driver.get_href_by_text("Redirect Me!")
		driver.open(origin)
		link = driver.get_href_by_ending_link(".apk")
		return link

	app = AppBase(
		"Instagram",
		{
			"Instander": instander,
			"Honinsta": honinsta,
			"AeroInsta": aeroinsta,
		},
	)
	app.update(index)


#####################################################################################
# TWITTER
def twitter(index: Index):
	# AeroWitter
	def aeroWitter():
		driver = Aero()
		driver.open("https://aerowitter.com/download-aero-twitter/package-2/?lang=en")
		driver.open(
			driver.get_href_by_text("Download Button 1 - AeroMods.app (Recommended)")
		)
		sleep(8)
		driver.click_span("checkbox-custom")
		origin = driver.get_href_by_text("Redirect Me!")
		driver.open(origin)
		return driver.get_href_by_ending_link(".apk")

	app = AppBase(
		"Twitter",
		{
			"AeroWitter": aeroWitter,
		},
	)
	app.update(index)


#####################################################################################
# WHATSAPP
def whatsapp(index: Index):

	# FMWhatsApp
	def fmwhatsapp():
		driver = Selenium()
		driver.openLink("https://fmmods.com/fouad-whatsapp/")
		links = driver.getElements(By.XPATH, "//a[@href]")
		links = [link for link in links if link.get_attribute("href").endswith(".apk")]
		link = None
		for l in links:
			tag = l.get_attribute("href").split("/")[-1]
			if tag.startswith("FMWA"):
				link = l.get_attribute("href")
				break
		return link

	# YMWhatsApp
	def ymwhatsapp():
		driver = Selenium()
		driver.openLink("https://ymmods.net/download-ymwa-clone/")
		# get all script tags
		scripts = driver.getElements(By.XPATH, "//script")
		link = None
		for script in scripts:
			pattern = re.compile(r"'(https://[^']+.apk)'")
			links = pattern.findall(script.get_attribute("innerHTML"))
			if len(links) > 0 and "YMWhatsApp" in links[0] and "Clone" in links[0]:
				link = links[0]
				break
		return link

	app = AppBase(
		"WhatsApp",
		{
			"FMWhatsApp": fmwhatsapp,
			"YMWhatsApp": ymwhatsapp,
		},
	)
	app.update(index)


#####################################################################################
# NEWPIPE
def newpipe(index: Index):

	def teamnewpipe():
		gh = Github("TeamNewPipe", "NewPipe")
		latest = gh.getVersions()[0]
		link = gh.getLinks(latest, [".apk"])[0]
		return (link, gh.origin)

	app = AppBase("NewPipe", {"TeamNewPipe": teamnewpipe})
	app.update(index)


#####################################################################################
# SEAL
def seal(index: Index):

	def junkfood02():
		gh = Github("JunkFood02", "Seal")
		versions = gh.getVersions()
		for version in versions:
			link = gh.getLinks(version, ["universal", ".apk"])
			if len(link):
				return (link[0], gh.origin)

	app = AppBase("Seal", {"JunkFood02": junkfood02})
	app.update(index)


#####################################################################################
# SMARTLAUNCHER
def smartlauncher(index: Index):

	def modyolo():
		driver = Modyolo("smart-launcher-6-27413")
		link = driver.getLink()
		return (link, driver.origin)

	# LITEAPKS
	def liteapks():
		driver = Liteapks("smart-launcher-6-184")
		link = driver.getLink()
		return (link, driver.origin)

	# APKDONE
	def apkdone():
		driver = ApkDone("smart-launcher-5")
		link = driver.getLink()
		return link

	app = AppBase(
		"Smart Launcher 6",
		{
			"MODYOLO": modyolo,
			"LITEAPKS": liteapks,
			"APKDONE": apkdone,
		},
	)
	app.update(index)


def niagaralauncher(index: Index):

	def modyolo():
		driver = Modyolo("niagara-launcher-63941")
		link = driver.getLink()
		return (link, driver.origin)

	# LITEAPKS
	def liteapks():
		driver = Liteapks("niagara-launcher-75423")
		link = driver.getLink()
		return (link, driver.origin)

	# APKDONE
	def apkdone():
		driver = ApkDone("niagara-launcher")
		link = driver.getLink()
		return link

	app = AppBase(
		"Niagara Launcher",
		{
			"MODYOLO": modyolo,
			"LITEAPKS": liteapks,
			"APKDONE": apkdone,
		},
	)
	app.update(index)


#####################################################################################
# REVANCED MANAGER
def revancedManager(index: Index):

	def ReVanced():
		gh = Github("ReVanced", "revanced-manager")
		latest = gh.getVersions()[0]
		link = gh.getLinks(latest, [".apk"])[0]
		return (link, gh.origin)

	app = AppBase("ReVanced Manager", {"ReVanced": ReVanced})
	app.update(index)


#####################################################################################
# YTDLNIS
def ytdlnis(index: Index):
	def ytdlnis():
		gh = Github("deniscerri", "ytdlnis")
		latest = gh.getVersions()[0]
		link = gh.getLinks(latest, [".apk", "universal"])[0]
		return (link, gh.origin)

	app = AppBase("YTDLnis", {"deniscerr": ytdlnis})
	app.update(index)


#####################################################################################
# NEVER HAVE I EVER
def neverhaveiever(index: Index):
	# LiteApks
	def liteapks():
		driver = Liteapks("never-have-i-ever-194362")
		return (driver.getLink(), driver.origin)
	
	app = AppBase("Never Have I Ever", {"LiteApks": liteapks})
	app.update(index)