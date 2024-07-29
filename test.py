from GLOBAL import GLOBAL
from lib.virustotal import VirusTotal
from utils.Index import Index
from utils.AppManager import AppManager
from utils.newApp import NewApp
from lib.github import Github
from pyvirtualdisplay import Display
import sys
import os

###############
GLOBAL()  #####
VirusTotal()  #
Index()  ######
###############
import inspect
import apps

from providers.Mobilism import Mobilism
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 600))
display.start()
mob = Mobilism()
print(mob.extract_filename("https://www.up-4ever.net/qwfh1essshmw"))
display.stop()