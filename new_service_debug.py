#new service tests

from systray import SysTrayIcon as tray
import sys
import ctypes, platform

if int(platform.release()) >= 8:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)


import random


bundle_dir = ""

def quits(s):
    print("randomize")
    menu = ((str(random.randrange(1000)), None, quits),
        ((str(random.randrange(1000)), None, quits)))
    s.update(menu_options=menu)
    #print("kill", s)
    #s.shutdown()
    #sys.exit()

menu = (("Quit", None, quits),
        ("Quit", None, quits))

systray = tray(bundle_dir + "\\assets\\" + "icon.ico", "hi", menu, default_menu_index=0)
systray.start()

            
