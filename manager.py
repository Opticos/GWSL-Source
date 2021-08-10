# GWSL Dashboard *lets do this again*

# Copyright Paul-E/Opticos Studios 2021
# https://sites.google.com/bartimee.com/opticos-studios/home

# Dedicated to the Sacred Heart of Jesus

#                #########
#       #      #############
#       ~       #########
#   #########     ####
#      \@/
#       |
#       #
#    O  #.
#    |> #
#   _#  #

import time
import os
import sys
import win32
import subprocess
import threading
import iset
import re
import pymsgbox
import random
import winshell
from win32com.client import Dispatch
import winreg
from winreg import *
from exe_layer import cmd
import logging
import ipaddress

BUILD_MODE = "MSIX"  # MSIX or WIN32

version = "1.4.0"

lc_name = "Licenses138.txt"

show_ad = False

debug = False

args = sys.argv

frozen = 'not'
if getattr(sys, 'frozen', False):
    # we are running in a bundle
    frozen = 'ever so'
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

if debug == True:
    print("debug mode")
    print('we are', frozen, 'frozen')
    print('bundle dir is', bundle_dir)
    print('sys.argv[0] is', sys.argv[0])
    print('sys.executable is', sys.executable)
    print('os.getcwd is', os.getcwd())

asset_dir = bundle_dir + "\\assets\\"

app_path = os.getenv('APPDATA') + "\\GWSL\\"

if os.path.isdir(app_path) == False:
    # os.mkdir(app_path)
    print(subprocess.getoutput('mkdir "' + app_path + '"'))
    print("creating appdata directory")

# EMERGENCY LOG DELETER FOR 1.3.6. Delete in 1.3.8
"""
try:
    if os.path.exists(app_path + "GWSL_helper.sh") == True:
        scr = open(app_path + "GWSL_helper.sh", "r")
        lines = scr.read()
        if "v3" not in lines:
            print("Cleaning Logs...")
            os.remove(app_path + 'dashboard.log')
            os.remove(app_path + 'settings.json')
except:
    pass
"""

class DuplicateFilter(logging.Filter):

    def filter(self, record):
        # add other fields if you need more granular comparison, depends on your app
        current_log = (record.module, record.levelno, record.msg)
        if current_log != getattr(self, "last_log", None):
            self.last_log = current_log
            return True
        return False


logger = logging.Logger("GWSL " + version, level=0)
# logger = logging.getLogger("GWSL " + version)
# Create handlers
f_handler = logging.FileHandler(app_path + 'dashboard.log')

# f_handler.setLevel(10)

f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(f_handler)
logger.addFilter(DuplicateFilter())

updated = False


try:
    iset.path = app_path + "settings.json"

    if os.path.exists(app_path + "\\settings.json") == False:
        iset.create(app_path + "\\settings.json")
        print("creating settings")
    else:
        sett = iset.read()
        if "conf_ver" not in sett:
            iset.create(app_path + "\\settings.json")
            print("Updating settings")
        else:
            if sett["conf_ver"] >= 6:
                if debug == True:
                    print("Settings up to date")
                try:
                    v = sett["gwsl_ver"]
                    if v != version:
                        updated = True
                        sett["gwsl_ver"] = version
                        iset.set(sett)
                except:
                    updated = True
                    print("Updating settings")
                    old_iset = iset.read()
                    iset.create(app_path + "\\settings.json")
                    new_iset = iset.read()

                    #migrate user settings
                    new_iset["putty"]["ip"] = old_iset["putty"]["ip"]
                    new_iset["distro_blacklist"] = old_iset["distro_blacklist"]
                    new_iset["app_blacklist"] = old_iset["app_blacklist"]
                    new_iset["xserver_profiles"] = old_iset["xserver_profiles"]
                    try:
                        new_iset["general"]["acrylic_enabled"] = old_iset["general"]["acrylic_enabled"]
                    except:
                        pass
                    try:
                        new_iset["general"]["clipboard"] = old_iset["general"]["clipboard"]
                    except:
                        pass
                    try:
                        new_iset["general"]["start_menu_mode"] = old_iset["general"]["start_menu_mode"]
                    except:
                        pass
                    try:
                        new_iset["general"]["shell_gui"] = old_iset["general"]["shell_gui"]
                    except:
                        pass
                    
                    try:
                        new_iset["graphics"]["hidpi"] = old_iset["graphics"]["hidpi"]
                    except:
                        pass
                    try:
                        new_iset["putty"]["ssh_key"] = old_iset["putty"]["ssh_key"]
                    except:
                        pass
                    iset.set(new_iset)
                        
            else:
                updated = True
                print("Updating settings")
                old_iset = iset.read()
                iset.create(app_path + "\\settings.json")
                new_iset = iset.read()

                #migrate user settings
                new_iset["putty"]["ip"] = old_iset["putty"]["ip"]
                new_iset["distro_blacklist"] = old_iset["distro_blacklist"]
                new_iset["app_blacklist"] = old_iset["app_blacklist"]
                new_iset["xserver_profiles"] = old_iset["xserver_profiles"]
                try:
                    new_iset["general"]["acrylic_enabled"] = old_iset["general"]["acrylic_enabled"]
                except:
                    pass
                try:
                    new_iset["general"]["clipboard"] = old_iset["general"]["clipboard"]
                except:
                    pass
                try:
                    new_iset["general"]["start_menu_mode"] = old_iset["general"]["start_menu_mode"]
                except:
                    pass
                try:
                    new_iset["general"]["shell_gui"] = old_iset["general"]["shell_gui"]
                except:
                    pass
                
                try:
                    new_iset["graphics"]["hidpi"] = old_iset["graphics"]["hidpi"]
                except:
                    pass
                try:
                    new_iset["putty"]["ssh_key"] = old_iset["putty"]["ssh_key"]
                except:
                    pass
                iset.set(new_iset)
                

    # Get the script ready
    import wsl_tools as tools

    if os.path.exists(app_path + "GWSL_helper.sh") == False:
        # print("Moving helper script")
        print(subprocess.getoutput('copy "' + bundle_dir + "\\assets\GWSL_helper.sh" + '" "' + app_path + '"'))

    if os.path.exists(app_path + "oiw_update.txt") == False:
        print("show ad")
        #with open(app_path + "oiw_update.txt", "w") as filer:
        #    filer.write("Delete this file to get the OpenInWSL Ad on startup again")
        #    filer.close()
        show_ad = True
        

        
    else:
        # make sure the script is up to date
        scr = open(app_path + "GWSL_helper.sh", "r")
        lines = scr.read()
        if "v4" in lines:
            if debug == True:
                print("Script is up to date")
        else:
            print("Updating Script")
            print(subprocess.getoutput('copy "' + bundle_dir + "\\assets\GWSL_helper.sh" + '" "' + app_path + '"'))

    if os.path.exists(app_path + lc_name) == False:
        # print("Moving Licenses")
        print(subprocess.getoutput('copy "' + bundle_dir + "\\assets\\" + lc_name + '" "' + app_path + '"'))
except Exception as e:
    logger.exception("Exception occurred - Config generation")
    sys.exit()

tools.script = app_path + "\\GWSL_helper.sh"




try:
    import ctypes
    import platform

    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
except Exception as e:
    logger.exception("Exception occurred - Cannot set dpi aware")

import tkinter as tk

from tkinter import *
from tkinter import ttk

root = None  # tk.Tk() #this is intensive... import as needed?
# root.withdraw()
from PIL import Image, ImageTk
import PIL
import win32gui
import PIL.ImageTk

import win32con
import win32api
import keyboard

def get_system_light():
    """
    Sets color of white based on Windows registry theme setting
    :return:
    """
    global light, white, accent
    try:
        registry = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        key_value = QueryValueEx(key, 'SystemUsesLightTheme')
        k = int(key_value[0])
        light = False
        white = [255, 255, 255]
        if k == 1:
            light = True
            white = [0, 0, 0]
            for i in range(3):
                if accent[i] > 50:
                    accent[i] -= 50
    except:
        white = [255, 255, 255]
        light = False

def raise_windows(*args):
    hwnd = HWND
    
    SetWindowPos = windll.user32.SetWindowPos
    
    if pos_config == "bottom":
        w, h = winpos, screensize[1] - taskbar - int(HEIGHT)
    elif pos_config == "top":
        w, h =  winpos, taskbar
    elif pos_config == "right":
        w, h = winpos - taskbar, screensize[1] - HEIGHT
    elif pos_config == "left":
        w, h = taskbar, screensize[1] - HEIGHT
    
    SetWindowPos(hwnd, -1, w, h, 0, 0, 0x0001)
    """
    try:
        win32gui.ShowWindow(HWND, 5)
        win32gui.SetForegroundWindow(HWND)
    except Exception as e:
        logger.exception("Exception occurred - cannot raise window")
    """

# import gettext
# zh = gettext.translation('manager', localedir='locale', languages=['zh'])
# zh.install()
# _ = #zh.gettext
_ = lambda s: s

default_font = asset_dir + "SegUIVar.ttf"#"segoeui.ttf"

# default_font = asset_dir + "NotoSans-Regular.ttf"#"msyh.ttc"


if "--r" not in args:
    os.environ["PBR_VERSION"] = "4.0.2"

    import singleton

    try:
        instance = singleton.SingleInstance()
    except singleton.SingleInstanceException:
        print("quit")
        try:
            def windowEnumerationHandler(hwnd, top_windows):
                top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


            results = []
            top_windows = []
            win32gui.EnumWindows(windowEnumerationHandler, top_windows)
            for i in top_windows:
                if "gwsl dashboard" in i[1].lower():
                    win32gui.ShowWindow(i[0], 5)
                    win32gui.SetForegroundWindow(i[0])
                    break
        except Exception as e:
            logger.exception("Exception occurred - cannot raise window")

        sys.exit()
    except PermissionError:
        print("quit")
        try:
            def windowEnumerationHandler(hwnd, top_windows):
                top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


            results = []
            top_windows = []
            win32gui.EnumWindows(windowEnumerationHandler, top_windows)
            for i in top_windows:
                if "gwsl dashboard" in i[1].lower():
                    win32gui.ShowWindow(i[0], 5)
                    win32gui.SetForegroundWindow(i[0])
                    break
        except Exception as e:
            logger.exception("Exception occurred - cannot raise window")
            pass

        sys.exit()

    try:

        from win10toast import ToastNotifier

        toaster = ToastNotifier()

        dd = [random.randrange(0, 8), random.randrange(0, 8), random.randrange(0, 8)]  # pick a random date to ask for donations

        # DISPLAY ones
        import OpticUI as ui

        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "4.0.2"

        import pygame, webbrowser
        # print("whoops")

        import animator as anima

        from pygame.locals import *

        t = time.perf_counter()
        import pygame.gfxdraw

        ui.init("dpi")  # , tk, root)
        from ctypes import wintypes, windll

        if int(platform.release()) >= 8:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)

        from win32api import GetMonitorInfo, MonitorFromPoint
        from pathlib import Path

        monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
        monitor_area = monitor_info.get("Monitor")
        work_area = monitor_info.get("Work")
        taskbar = int(monitor_area[3] - work_area[3])

        pos_config = "bottom"  # loc of taskbar

        if work_area[1] != 0:
            taskbar = work_area[1]
            pos_config = "top"

        elif work_area[0] != 0:
            taskbar = work_area[0]
            pos_config = "left"

        elif work_area[2] != monitor_area[2]:
            taskbar = monitor_area[2] - work_area[2]
            pos_config = "right"

        else:
            taskbar = int(monitor_area[3] - work_area[3])
            pos_config = "bottom"

        ui.set_scale(1)

        # pygame init takes a long time...
        # pygame.display.init()

        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        WIDTH, HEIGHT = ui.inch2pix(3.8), ui.inch2pix(5.7)  ##ui.inch2pix(7.9), ui.inch2pix(5)
        if pos_config == "top":
            winpos = screensize[0] - WIDTH
            winh = taskbar - HEIGHT
        elif pos_config == "bottom":
            winpos = screensize[0] - WIDTH
            winh = screensize[1]
        elif pos_config == "right":
            winpos = screensize[0] - WIDTH
            winh = screensize[1]
        elif pos_config == "left":
            winpos = taskbar
            winh = screensize[1]

        sett = iset.read()
        try:
            start_menu = sett["general"]["start_menu_mode"]
        except:
            start_menu = False

        if start_menu == True:
            if pos_config == "top":
                winpos = 0
                winh = taskbar - HEIGHT
            elif pos_config == "bottom":
                winpos = 0
                winh = screensize[1]
            elif pos_config == "right":
                winpos = screensize[0] - WIDTH
                winh = screensize[1]
            elif pos_config == "left":
                winpos = taskbar
                winh = screensize[1]

        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (winpos, winh)  # screensize[1] - taskbar)

        py_root = pygame.display.set_mode([WIDTH, HEIGHT], NOFRAME)

        HWND = pygame.display.get_wm_info()["window"]
        
        keyboard.add_hotkey('alt+ctrl+g', raise_windows)#, args=HWND)

        
        
        # win32gui.MoveWindow(HWND, screensize[0] - WIDTH, screensize[1] - taskbar - HEIGHT, WIDTH, HEIGHT, True)

        canvas = pygame.Surface([WIDTH, HEIGHT])  # , pygame.SRCALPHA)
        try:
            win32gui.ShowWindow(HWND, 5)
            win32gui.SetForegroundWindow(HWND)
        except:
            pass
                    
        ui.set_size([WIDTH, HEIGHT])
        pygame.display.set_caption("GWSL Dashboard")
        ui.start_graphics(pygame, asset_dir)
        ico = pygame.image.load(asset_dir + "icon.png").convert_alpha()
        pygame.display.set_icon(ico)
        fpsClock = pygame.time.Clock()
        lumen_opac = 6
        # light_source = pygame.image.load(asset_dir + "lumens/7.png").convert_alpha()
        #sync, clock, link, laptop, invalid/failed circle, 
        icons_old = {"refresh":"", "clock":"", "link":"",
                 "laptop":"", "error":"", "settings":"", "app_list":"",
                 "shell":"", "network":"", "heart":"", "question":"",
                 "plus":"", "minus":"", "x":"", "check":"", "dbus_config":"",
                 "theme":"", "discord":"", "export":"", "folder":""}
        
        #these are all 24 weight
        icons = {"refresh":"", "clock":"", "link":"",
                 "laptop":"", "error":"", "settings":"", "app_list":"",
                 "shell":"", "network":"", "heart":"", "question":"",#oldshell 
                 "plus":"", "minus":"", "x":"", "check":"", "dbus_config":"",
                 "theme":"", "discord":"", "export":"", "folder":""}


        
        ico_font = asset_dir + "SEGMDL2.TTF"
        modern = True
        
        if modern == True:
            ico_font = asset_dir + "segoefluent.ttf"#"SEGMDL2.TTF"

        if "fluent" not in ico_font:
            icons = icons_old
        # lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
        # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
        # mask.fill([255, 0, 0])
        # pay = pygame.image.load(asset_dir + "paypal.png").convert_alpha()
        # pay = pygame.transform.smoothscale(pay, [ui.inch2pix(1), int((pay.get_height() / pay.get_width()) * ui.inch2pix(1))])
        
        back = pygame.Surface([WIDTH, HEIGHT])  # mini1.copy()


        def get_pos():
            rect = win32gui.GetWindowRect(HWND)
            return [int(rect[0]), int(rect[1])]


        poser = get_pos()
        back = pygame.transform.scale(back, screensize)

        accent = ui.get_color()

        get_system_light()

        fuchsia = [12, 222, 123]

        # Set window transparency color
        hwnd = HWND
        long = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               long | win32con.WS_EX_LAYERED)
        #win32con.WS_BORDER

        #win32gui.SetLayeredWindowAttributes(HWND, win32api.RGB(*[100, 100, 100]), int(255), win32con.LWA_COLORKEY)
        
        #region = win32gui.CreateRoundRectRgn(0, 0, WIDTH, HEIGHT, 20, 20)
        #win32gui.SetWindowRgn(hwnd, region, True)
        import rounder
        if rounder.round(HWND) == True:
            pad = ui.inch2pix(0.14)
            fade = False
        else:
            pad = 0
            fade = True
        
        if start_menu == True:
            padx = -1 * pad
        else:
            padx = pad
        sett = iset.read()
        try:
            acrylic = sett["general"]["acrylic_enabled"]
        except Exception as e:
            logger.exception("Exception occurred - Please reset settings")
            acrylic = True


        if acrylic == True:
            import blur
            blur.blur(HWND)
        else:
            try:
                mini1 = pygame.image.load(os.getenv('APPDATA') + r"\Microsoft\Windows\Themes\TranscodedWallpaper").convert()
            except:
                bak = asset_dir + random.choice(["1", "2", "3"]) + ".jpg"
                mini1 = pygame.image.load(bak).convert()
            back = mini1.copy()#
            back = pygame.transform.scale(back, screensize)

    except Exception as e:
        logger.exception("Exception occurred - Cannot Init Display")


def get_version(machine):
    try:
        machines = os.popen("wsl.exe -l -v").read()  # lines()
        machines = re.sub(r'[^a-z A-Z0-9./\n-]', r'', machines).splitlines()
        #machines = machines.splitlines()
        machines2 = []
        wsl_1 = True
        for i in machines:
            b = ''.join(i).split()
            if 'VERSION' in b:
                wsl_1 = False
            if 'NAME' not in b and b != [] and b != None:
                machines2.append(b)
        if wsl_1 == True:
            print("assuming wsl 1")
            return 1
        
        for i in machines2:
            if i[0] == machine:
                return int(i[2])
        return 1
        
    except:
        return 1
    


def reboot(machine):
    """
    Reboots WSL instance
    :param machine:
    :return:
    """
    os.popen("wsl.exe -t " + str(machine))
    time.sleep(1)
    os.popen("wsl.exe -d " + str(machine))


def helper(topic):
    """
    Build URL for specified topic
    :param topic:
    :return:
    """
    if topic == "machine chooser":
        url = "the-gwsl-user-interface"
    elif topic == "configure":
        url = "configuring-a-wsl-distro-for-use-with-gwsl"
    elif topic == "theme":
        url = "configuring-a-wsl-distro-for-use-with-gwsl"
    elif topic == "launcher":
        url = "using-the-integrated-linux-app-launcher"
    webbrowser.get('windows-default').open("https://opticos.github.io/gwsl/tutorials/manual.html#" + str(url))


def help_short():
    """
    Open help page on shortcut creator in browser
    :return:
    """
    webbrowser.get('windows-default').open(
        "https://opticos.github.io/gwsl/tutorials/manual.html#using-the-gwsl-shortcut-creator")


def help_ssh():
    """
    Open help page on using GWSL with SSH
    :return:
    """
    webbrowser.get('windows-default').open("https://opticos.github.io/gwsl/tutorials/manual.html#using-gwsl-with-ssh")


def wsl_run(distro, command, caller, nolog=False):
    """
    One Run to Rule Them All... nvm
    """
    cmd = "wsl.exe ~ -d " + str(distro) + " . ~/.profile;nohup /bin/sh -c " + '"' + str(command) + '&"'
    
    if nolog == False:
        logger.info(f"(runos) WSL SHELL $ {cmd}")
        #logger.info(f"WSL OUTPUT > {out}")
        
    #subprocess.Popen(cmd, shell=True)
    #print(caller, cmd)
    run = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            universal_newlines=True
    )
    out = str(run.stdout.read().rstrip())
    #print(out)
    return out
    
    #return out


def runs(distro, command, nolog=False):
    
    cmd = "wsl.exe ~ -d " + str(distro) + " . ~/.profile;nohup /bin/sh -c " + '"' + str(command) + '&"'
    if nolog == False:
        logger.info(f"(runos) WSL SHELL $ {cmd}")
    subprocess.Popen(cmd,
                     shell=True)  # .readlines()
    #print("runs. it would be", cmd)
    return None
    
    
    #return wsl_run(distro, command, "runs")


def run(distro, command, nolog=False):
    #"""
    cmd = "wsl.exe ~ -d " + str(distro) + " . ~/.profile;nohup /bin/sh -c " + '"' + str(command) + '&"'
    #old out = subprocess.getoutput(cmd)  # .readlines()
    out = subprocess.check_output(cmd, shell=True, errors="ignore")
    if nolog == False:
        logger.info(f"(run) WSL SHELL $ {cmd}")
        logger.info(f"WSL OUTPUT > {out}")
    #print("run. it would be", cmd)
    return out
    #"""
    #return wsl_run(distro, command, "run")


def start_dbus(distro):
    command = "/etc/init.d/dbus start"
    cmd = "wsl.exe ~ -d " + str(distro) + " /bin/sh -c " + '"' + str(command) + '"'
    try:
        out = subprocess.getoutput(cmd)
    except:
        out = ""
    return out
   

def runo3(distro, command, nolog=False):
    #"""
    cmd = "wsl.exe ~ -d " + str(distro) + " . ~/.profile;/bin/sh -c " + '"' + str(command) + '"'
    out = subprocess.getoutput(cmd)  # .readlines()
    if nolog == False:
        logger.info(f"(runo3) WSL SHELL $ {cmd}")
        logger.info(f"WSL OUTPUT > {out}")
    #print("runo3. it would be", cmd)
    return out
    #"""
    #return wsl_run(distro, command, "runo3")


def runo2(distro, command, nolog=False):
    #"""
    cmd = "wsl.exe -d " + str(distro) + ' ' + "/bin/sh -c " + '"' + str(command) + '"'
    out = os.popen(cmd).readlines()
    if nolog == False:
        logger.info(f"(runo2) WSL SHELL $ {cmd}")
        logger.info(f"WSL OUTPUT > {out}")
    #print("runo2. it would be", cmd)
    return out
    #"""
    #return wsl_run(distro, command, "runo2")

""" obselete
def runo(distro, command):
    cmd = "wsl.exe -d " + str(distro) + " /bin/sh -c " + '"' + str(command) + '"'
    out = os.popen(cmd).readlines()
    logger.info(f"(runo) WSL SHELL $ {cmd}")
    logger.info(f"WSL OUTPUT > {out}")
    return out


"""
def get_ip(machine):
    """
    Get IP of select WSL instance
    :return:
    """
    #print("get_ip")
    cmd = "wsl.exe -d " + str(machine) + ' ' + "/bin/sh -c " + '"' + """(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit;}')""" + '"'

    
    #print(cmd)
    result = os.popen(cmd).readlines()[0]

    try:
        result = result.rstrip()
    except:
        pass
    if "nameserver" in result:
        result = result[len("nameserver") + 1:]
        
    try:
        ipa = ipaddress.ip_address(result)
    except:
        cmd = "wsl.exe -d " + str(machine) + ' ' + "/bin/sh -c " + '"' + """echo $(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit;}')""" + '"'
        result = os.popen(cmd).readlines()[0]
        #result = "localhost"
    
        
    #print("ipa", ipa, "ipd")

    
    #result = runo3(machine, """echo $(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit;}')""")
    #print("ip", result, "done")
    return result  # [0][:-1]


def test_x():
    """
    Test the VCXSRV config by launching xclock
    :return:
    """
    subprocess.Popen("VCXSRV/xclock -display localhost:0")


def choose_machine():
    """
    Builds the choose machine menu
    :return:
    """
    global selected, canvas, WIDTH, HEIGHT, mini, back, lumen, mask
    machines = os.popen("wsl.exe -l -q").read()  # lines()
    machines = re.sub(r'[^a-zA-Z0-9./\n-]', r'', machines).splitlines()
    machines[:] = (value for value in machines if value != "")

    
    sett = iset.read()

    avoid = sett["distro_blacklist"]
    docker_blacklist = []
    for i in machines:
        for a in avoid:
            if str(a).lower() in str(i).lower():
                docker_blacklist.append(i)
        

    for i in docker_blacklist:
        machines.remove(i)
    
    if len(machines) == 1:
        return machines[0]
    elif len(machines) > 7:
        if len(machines) != 23:
            return pymsgbox.confirm(text=_('Select a WSL Machine'), title=_('Choose WSL Machine'), buttons=machines)
        else:
            machines = []

    animator.animate("choose", [100, 0])
    machine = False

    b = pygame.Surface([WIDTH, HEIGHT])
    draw(b)

    while True:
        mouse = False
        if win32gui.GetFocus() != HWND:
            if animator.get("start")[0] == 100:
                animator.animate("start", [0, 0])
                animator.animate("start2", [0, 0])
                break
        # if animator.get("start")[0] == 0:
        #    pygame.quit()
        #    sys.exit()

        for event in pygame.event.get():
            if event.type == QUIT:
                # subprocess.getoutput('taskkill /F /IM GWSL_service.exe')
                # subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                mouse = event.pos
            elif event.type == VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                if WIDTH < ui.inch2pix(7.9):
                    WIDTH = ui.inch2pix(7.9)
                if HEIGHT < ui.inch2pix(5):
                    HEIGHT = ui.inch2pix(5)

                canvas = pygame.display.set_mode([WIDTH, HEIGHT], RESIZABLE)
                # ui.set_size([WIDTH, HEIGHT])
                # mini = pygame.image.load(bak).convert()
                back = mini.copy()
                back = pygame.transform.scale(back, [WIDTH, HEIGHT])
                ui.iris2(back, [0, 0],
                         [WIDTH, HEIGHT],
                         [0, 0, 0], radius=10, shadow_enabled=False, resolution=50)
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])

                b = pygame.Surface([WIDTH, HEIGHT])
                draw(b)
                lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask.fill([255, 0, 0])

        canvas.blit(b, [0, 0])

        v = animator.get("choose")[0] / 100

        # canvas.fill([0, 0, 0, int((1 - v) * 255)])
        ui.iris2(canvas, [0, 0],
                 [WIDTH, HEIGHT],
                 False, radius=10, shadow_enabled=False, resolution=30, alpha=int(v * 255))

        if light == False:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, int(v*100)])
        else:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, int(v*80)])
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, int(v*80)])

        # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0] + [int(v * 180)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))
        if len(machines) != 0:
            txt = title_font.render(_("Choose A WSL Distro:"), True, white)
        else:
            txt = title_font.render(_("No WSL Distros Installed."), True, white)

        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * (v))])

        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        txt = title_font.render("?", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt,
                    [WIDTH - txt.get_width() - ui.inch2pix(0.3), ui.inch2pix(0.2) - int(ui.inch2pix(0.1) * (1 - v))])
        hover = pygame.mouse.get_pos()
        if hover[0] > WIDTH - txt.get_width() - ui.inch2pix(0.4) and hover[0] < WIDTH - ui.inch2pix(0.1):
            if hover[1] > ui.inch2pix(0.1) and hover[1] < ui.inch2pix(0.3) + txt.get_height() - int(
                    ui.inch2pix(0.1) * (1 - v)):
                if mouse != False:
                    helper("machine chooser")

        d = ui.inch2pix(0.2)
        h = ui.inch2pix(0.8) + txt.get_height() + ui.inch2pix(0.25)
        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        # title_font.bold = True
        selected = False
        if len(machines) != 0:
            for i in machines:
                s2 = False
                ni = i[0].upper() + i[1:]
                ni = ni.replace("-", " ")
                txt = title_font.render(ni, True, white)

                if hover[0] > (WIDTH / 2) - (txt.get_width() / 2) - ui.inch2pix(0.2) and hover[0] < (WIDTH / 2) - (
                        txt.get_width() / 2) + txt.get_width() + ui.inch2pix(0.2):
                    if hover[1] > h - ui.inch2pix(0.1) - int(v * d) + 1 and hover[
                        1] < h + txt.get_height() + ui.inch2pix(0.1) - int(v * d):
                        if mouse != False:
                            machine = i
                            animator.animate("choose", [0, 0])
                        selected = True
                        s2 = True

                s = animator.get("select")[0] / 100

                if s2 == False:
                    txt.set_alpha(int(v * 255))
                else:
                    txt.set_alpha(int((1 - s) * v * 255))

                canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, h - int(v * d)])
                if s2 == True:
                    txt = title_font.render(ni, True, accent)
                    txt.set_alpha(int((s) * v * 255))
                    canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, h - int(v * d)])

                h += ui.inch2pix(0.3) + txt.get_height()
                d += ui.inch2pix(0.1)

        if selected == True:
            animator.animate("select", [100, 0])
        else:
            animator.animate("select", [0, 0])

        txt = title_font.render(_("Cancel"), True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, HEIGHT - ui.inch2pix(0.2) - txt.get_height() - int(v * d)])
        if mouse != False:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT - ui.inch2pix(0.2) - txt.get_height() - ui.inch2pix(0.1) - int(v * d) and mouse[
                    1] < HEIGHT - ui.inch2pix(0.2) - txt.get_height() + txt.get_height() + ui.inch2pix(0.1) - int(
                        v * d):
                    machine = None
                    animator.animate("choose", [0, 0])

        fpsClock.tick(60)
        animator.update()

        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=(pygame.BLEND_RGBA_ADD))

        pygame.display.update()
        if machine != False and animator.get("choose")[0] <= 1:
            return machine


def about():
    """
    Handles building and displaying the about window
    :return:
    """
    global selected, canvas, WIDTH, HEIGHT, mini, back, lumen, mask

    animator.animate("choose", [100, 0])
    machine = False

    b = pygame.Surface([WIDTH, HEIGHT])
    draw(b)

    while True:
        mouse = False
        if win32gui.GetFocus() != HWND:
            if animator.get("start")[0] == 100:
                animator.animate("start", [0, 0])
                animator.animate("start2", [0, 0])
                break
        # if animator.get("start")[0] == 0:
        #    pygame.quit()
        #    sys.exit()

        for event in pygame.event.get():
            if event.type == QUIT:
                # subprocess.getoutput('taskkill /F /IM GWSL_service.exe')
                # subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                mouse = event.pos
            elif event.type == VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                if WIDTH < ui.inch2pix(7.9):
                    WIDTH = ui.inch2pix(7.9)
                if HEIGHT < ui.inch2pix(5):
                    HEIGHT = ui.inch2pix(5)

                canvas = pygame.display.set_mode([WIDTH, HEIGHT], RESIZABLE)
                # ui.set_size([WIDTH, HEIGHT])
                # mini = pygame.image.load(bak).convert()
                back = mini.copy()
                back = pygame.transform.scale(back, [WIDTH, HEIGHT])
                ui.iris2(back, [0, 0],
                         [WIDTH, HEIGHT],
                         [0, 0, 0], radius=10, shadow_enabled=False, resolution=50)
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])

                b = pygame.Surface([WIDTH, HEIGHT])
                draw(b)
                lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask.fill([255, 0, 0])

        canvas.blit(b, [0, 0])

        v = animator.get("choose")[0] / 100

        ui.iris2(canvas, [0, 0],
                 [WIDTH, HEIGHT],
                 [0, 0, 0], radius=10, shadow_enabled=False, resolution=30, alpha=int(v * 255))

        if light == False:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, int(100 * v)])
        else:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, int(80 * v)])
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, int(80 * v)])

        # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0] + [int(v * 180)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))
        txt = title_font.render(_("About GWSL"), True, white)

        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * v)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.15)))  # used to be 0.17
        title_font.italic = False

        icon_font = ui.font(ico_font, int(ui.inch2pix(0.16)))

        sett = icon_font.render(icons["clock"], True, white)  # 
        sett.set_alpha(int(v * 255))
        canvas.blit(sett, [WIDTH - sett.get_width() - ui.inch2pix(0.3), ui.inch2pix(0.395) - int(ui.inch2pix(0.1) * v)])

        txt = title_font.render(_("XClock"), True, white)

        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH - sett.get_width() - ui.inch2pix(0.37) - txt.get_width(),
                          ui.inch2pix(0.36) - int(ui.inch2pix(0.1) * v)])

        if mouse != False:
            if mouse[0] > WIDTH - sett.get_width() - ui.inch2pix(0.39) - txt.get_width() and mouse[
                0] < WIDTH - ui.inch2pix(0.25):
                if mouse[1] > ui.inch2pix(0.38) - int(ui.inch2pix(0.1) * v) and mouse[1] < ui.inch2pix(0.41) - int(
                        ui.inch2pix(0.1) * v) + sett.get_height():
                    test_x()

        d = ui.inch2pix(0.2)
        h = ui.inch2pix(0.8) + txt.get_height() + ui.inch2pix(0)

        machines = ["GWSL Version" + " " + str(version),
                    "© Copyright Paul-E/Opticos Studios 2021",
                    "GWSL Uses:",
                    "Python - Pyinstaller - SDL",
                    "VCXSRV - Putty - Pillow",
                    "Tcl/Tk - Paper Icon Pack",
                    "Pymsgbox - OpticUI - Infi.Systray",
                    "Visit Opticos Studios Website",
                    "More Apps!",
                    "View Licenses",
                    "Edit Configuration",
                    "Allow GWSL Through The Firewall",
                    "GWSL Discord Server",
                    "View Logs"]

        if BUILD_MODE == "WIN32":
            machines[0] = _("GWSL Version ") + str(version) + " (win32)"
        else:
            machines[0] = _("GWSL Version ") + str(version) + _(" (store)")

        if len(machines) != 0:
            for i in machines:
                if i == "View Licenses" or i == "Visit Opticos Studios Website" or i == "Edit Configuration" or \
                        i == "View Logs" or i == "Add to Startup" or i == "Allow GWSL Through The Firewall" or \
                        i == "GWSL Discord Server" or i == "More Apps!":
                    txt = title_font.render(i, True, accent)  # [0, 120, 250])
                else:
                    txt = title_font.render(i, True, white)
                txt.set_alpha(int(v * 255))
                canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, h - int(v * d)])
                if mouse != False:
                    if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                        0] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                        if mouse[1] > h - ui.inch2pix(0.1) - int(v * d) and mouse[
                            1] < h + txt.get_height() + ui.inch2pix(0.1) - int(v * d):
                            if i == "View Licenses":
                                os.popen(app_path + lc_name)
                            elif i == "Visit Opticos Studios Website":
                                webbrowser.get('windows-default').open('https://sites.google.com/bartimee.com/opticos-studios/home')
                            elif i == "View Logs":
                                os.chdir(app_path)
                                os.popen("notepad service.log|notepad dashboard.log")
                            elif i == "Edit Configuration":
                                os.chdir(app_path)
                                os.popen("settings.json")
                            elif i == "More Apps!":
                                animator.animate("choose", [0, 0])
                                machine = "announce"
                                
                            elif i == "Allow GWSL Through The Firewall": #TODO
                                os.popen("control /name Microsoft.WindowsFirewall /page pageConfigureApps")
                                pymsgbox.confirm(text=_('GWSL needs access through the Windows Firewall \
                                                to communicate with WSL version 2. Please allow public access to "GWSL_vcxsrv.exe", \
                                                "GWSL_vcxsrv_lowdpi.exe", and "pulseaudio.exe" for audio. You will need Admin Priviledges to do this.'),
                                                 title=_('Allow GWSL Firewall Access'), buttons=["Ok"])
                            elif i == "GWSL Discord Server":
                                webbrowser.get('windows-default').open("https://discord.com/invite/VkvNgkH")
                                

                h += ui.inch2pix(0.2) + txt.get_height()  # used to be 0.23
                d += ui.inch2pix(0.1)

        txt = title_font.render(_("Cancel"), True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt,
                    [WIDTH / 2 - txt.get_width() / 2, HEIGHT - ui.inch2pix(0.4) - txt.get_height() - int((v - 1) * d)])
        if mouse != False:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT - ui.inch2pix(0.4) - txt.get_height() - int((v - 1) * d) and mouse[
                    1] < HEIGHT - ui.inch2pix(0.4) - txt.get_height() - int(
                        (v - 1) * d) + txt.get_height() + ui.inch2pix(0.1):
                    machine = None
                    animator.animate("choose", [0, 0])

        fpsClock.tick(60)
        animator.update()
        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=(pygame.BLEND_RGBA_ADD))

        pygame.display.update()
        if (machine == None or machine == "announce") and animator.get("choose")[0] <= 1:
            if machine == "announce":
                announce()
            break


def announce():
    """
    Handles building and displaying the announce system
    :return:
    """
    #print("announce")
    global selected, canvas, WIDTH, HEIGHT, mini, back, lumen, mask

    animator.animate("choose", [100, 0])
    machine = False

    b = pygame.Surface([WIDTH, HEIGHT])
    draw(b)

    ann_icon = pygame.image.load(asset_dir + "oiw.png").convert_alpha()
    ico_s = int(WIDTH * 3/8)
    ann_icon = pygame.transform.smoothscale(ann_icon, [ico_s, ico_s])
    
    while True:
        mouse = False
        if win32gui.GetFocus() != HWND:
            if animator.get("start")[0] == 100:
                animator.animate("start", [0, 0])
                animator.animate("start2", [0, 0])
                break
        # if animator.get("start")[0] == 0:
        #    pygame.quit()
        #    sys.exit()

        for event in pygame.event.get():
            if event.type == QUIT:
                # subprocess.getoutput('taskkill /F /IM GWSL_service.exe')
                # subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                mouse = event.pos
            elif event.type == VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                if WIDTH < ui.inch2pix(7.9):
                    WIDTH = ui.inch2pix(7.9)
                if HEIGHT < ui.inch2pix(5):
                    HEIGHT = ui.inch2pix(5)

                canvas = pygame.display.set_mode([WIDTH, HEIGHT], RESIZABLE)
                # ui.set_size([WIDTH, HEIGHT])
                # mini = pygame.image.load(bak).convert()
                back = mini.copy()
                back = pygame.transform.scale(back, [WIDTH, HEIGHT])
                ui.iris2(back, [0, 0],
                         [WIDTH, HEIGHT],
                         [0, 0, 0], radius=10, shadow_enabled=False, resolution=50)
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])

                b = pygame.Surface([WIDTH, HEIGHT])
                draw(b)
                lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask.fill([255, 0, 0])

        canvas.blit(b, [0, 0])

        v = animator.get("choose")[0] / 100

        ui.iris2(canvas, [0, 0],
                 [WIDTH, HEIGHT],
                 [0, 0, 0], radius=10, shadow_enabled=False, resolution=30, alpha=int(v * 255))

        if light == False:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, 100])
        else:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, 80])
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, 80])

        # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0] + [int(v * 180)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))
        txt = title_font.render(_("Check out my new app!"), True, white)

        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * v)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.15)))  # used to be 0.17
        title_font.italic = False

        icon_font = ui.font(ico_font, int(ui.inch2pix(0.16)))


        ann_icon2 = ann_icon.copy()
        ann_icon2.set_alpha(int(v * 255))
        canvas.blit(ann_icon2, [int(WIDTH / 2 - ann_icon.get_width() / 2), int(HEIGHT / 2 - ann_icon.get_height() / 2 - ui.inch2pix(1)) - int(ui.inch2pix(0.1) * v)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.3)))
        txt = title_font.render(_("OpenInWSL"), True, white)

        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, WIDTH / 2 + ui.inch2pix(0.8) - int(ui.inch2pix(0.1) * v)])


        title_font = ui.font(default_font, int(ui.inch2pix(0.15)))
        #title_font.italic = True

        txt = title_font.render(_("Make Linux Apps Windows File Handlers"), True, white)

        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, WIDTH / 2 + ui.inch2pix(1.4) - int(ui.inch2pix(0.1) * v)])


        title_font.italic = False

        title_font = ui.font(default_font, int(ui.inch2pix(0.2)))


        txt = title_font.render(_("Get it on the Microsoft Store"), True, accent)

        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, WIDTH / 2 + ui.inch2pix(2.2) - int(ui.inch2pix(0.1) * v)])

        if mouse != False:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > WIDTH / 2 + ui.inch2pix(2.2) - int(ui.inch2pix(0.1) * v) - ui.inch2pix(0.1) and mouse[
                    1] < WIDTH / 2 + ui.inch2pix(2.2) - int(ui.inch2pix(0.1) * v) + txt.get_height() + ui.inch2pix(0.1):
                    webbrowser.open("ms-windows-store://pdp/?productid=9ngmqpwcg7sf")
                    #animator.animate("choose", [0, 0])

                    
        

        d = ui.inch2pix(0.2)
        h = ui.inch2pix(0.8) + txt.get_height() + ui.inch2pix(0)

        


        
        
        title_font = ui.font(default_font, int(ui.inch2pix(0.15)))
        
        txt = title_font.render(_("Ok"), True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt,
                    [WIDTH / 2 - txt.get_width() / 2, HEIGHT - ui.inch2pix(0.8) - txt.get_height() - int((v - 1) * d)])
        if mouse != False:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT - ui.inch2pix(0.8) - txt.get_height() - int((v - 1) * d) and mouse[
                    1] < HEIGHT - ui.inch2pix(0.8) - txt.get_height() - int(
                        (v - 1) * d) + txt.get_height() + ui.inch2pix(0.1):
                    machine = None
                    animator.animate("choose", [0, 0])


        txt = title_font.render(_("Don't Show Again"), True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt,
                    [WIDTH / 2 - txt.get_width() / 2, HEIGHT - ui.inch2pix(0.4) - txt.get_height() - int((v - 1) * d)])
        if mouse != False:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT - ui.inch2pix(0.4) - txt.get_height() - int((v - 1) * d) and mouse[
                    1] < HEIGHT - ui.inch2pix(0.4) - txt.get_height() - int(
                        (v - 1) * d) + txt.get_height() + ui.inch2pix(0.1):
                    machine = None
                    with open(app_path + "oiw_update.txt", "w") as filer:
                        filer.write("Delete this file to get the OpenInWSL Ad on startup again")
                        filer.close()
                    animator.animate("choose", [0, 0])
                    

        fpsClock.tick(60)
        animator.update()
        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=(pygame.BLEND_RGBA_ADD))

        pygame.display.update()
        if machine == None and animator.get("choose")[0] <= 1:
            break

        
def configure_machine(machine):
    global selected, canvas, WIDTH, HEIGHT, mini, back, lumen, mask
    animator.animate("choose", [100, 0])
    animator.register("loading_c", [0, 0])
    animator.animate("loading_c", [100, 0])

    b = pygame.Surface([WIDTH, HEIGHT])
    draw(b)

    g_button = ""
    q_button = ""
    QT = 1
    GTK = 1
    x_configured = False
    libgl_indirect = False
    loading = True
    loading_angle = 0
    icon_font = ui.font(ico_font, int(ui.inch2pix(1)))  # 0.19
    loader = icon_font.render(icons["refresh"], True, white)#
    them = "Default"
    themes = []
    m_version = ""

    def get():
        nonlocal q_button, g_button, QT, GTK, x_configured, loading, themes, them, m_version, libgl_indirect
        profile = tools.profile(machine)
        m_version = get_version(machine)


        if "QT_SCALE_FACTOR=2" in profile:
            QT = 2
        if "GDK_SCALE=2" in profile:
            GTK = 2

        if QT == 1:
            q_button = "HI-DPI"
        else:
            q_button = "LOW-DPI"

        if GTK == 1:
            g_button = "HI-DPI"
        else:
            g_button = "LOW-DPI"

        ver = get_version(machine)
        if "export DISPLAY=" in profile:
            x_configured = True

        if "export LIBGL_ALWAYS_INDIRECT=1" in profile:
            libgl_indirect = True

        try:
            themes = tools.get_themes(machine)

            def sorter(e):
                return e[0].lower()

            themes.sort(key=sorter)
            them = "Default"
            pl = profile.split("\n")
            for i in pl:
                if "GTK_THEME=" in i:
                    them = i[17:]
        except:
            them = "None"
            themes = []

        loading = False
        animator.animate("loading_c", [0, 0])

    t = threading.Thread(target=get)
    t.daemon = True
    t.start()

    rebooter = False

    

    while True:
        loading_angle -= 10
        mouse = False
        
        if win32gui.GetFocus() != HWND:
            if animator.get("start")[0] == 100:
                animator.animate("start", [0, 0])
                animator.animate("start2", [0, 0])
                break
        
        if animator.get("start")[0] < 100:
            break
        selected = False

        for event in pygame.event.get():

            if event.type == QUIT:
                # subprocess.getoutput('taskkill /F /IM GWSL_service.exe')
                # subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                if loading == False and event.button == 1:
                    mouse = event.pos
            elif event.type == VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                if WIDTH < ui.inch2pix(7.9):
                    WIDTH = ui.inch2pix(7.9)
                if HEIGHT < ui.inch2pix(5):
                    HEIGHT = ui.inch2pix(5)

                canvas = pygame.display.set_mode([WIDTH, HEIGHT], RESIZABLE)
                # ui.set_size([WIDTH, HEIGHT])
                # mini = pygame.image.load(bak).convert()
                back = mini.copy()
                back = pygame.transform.scale(back, [WIDTH, HEIGHT])
                ui.iris2(back, [0, 0],
                         [WIDTH, HEIGHT],
                         [0, 0, 0], radius=10, shadow_enabled=False, resolution=50)
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])

                b = pygame.Surface([WIDTH, HEIGHT])
                draw(b)
                lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask.fill([255, 0, 0])

        canvas.blit(b, [0, 0])

        v = animator.get("choose")[0] / 100

        ui.iris2(canvas, [0, 0],
                 [WIDTH, HEIGHT],
                 [0, 0, 0], radius=10, shadow_enabled=False, resolution=30, alpha=int(v * 255))

        if light == False:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, int(v*100)])
        else:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, int(v*80)])
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, int(v*80)])

        # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0] + [int(v * 180)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))

        ni = str(machine)[0].upper() + str(machine)[1:]
        ni = ni.replace("-", " ")

        txt = title_font.render("Configure " + str(ni), True, white)

        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * v)])
        w = ui.inch2pix(0.5)  # WIDTH / 2 - txt.get_width() / 2 + ui.inch2pix(0.1)
        d = ui.inch2pix(0.2)
        h = ui.inch2pix(0.8) + txt.get_height() + ui.inch2pix(0.1) #last used to be 0.25        
        
        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))

        if "fluent" in ico_font:
            icon_font = ui.font(ico_font, int(ui.inch2pix(0.25))) #for old icons 0.19
        else:
            icon_font = ui.font(ico_font, int(ui.inch2pix(0.19))) #for old icons 0.19

        
        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        txt = title_font.render("?", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt,
                    [WIDTH - txt.get_width() - ui.inch2pix(0.3), ui.inch2pix(0.2) - int(ui.inch2pix(0.1) * (1 - v))])
        hover = pygame.mouse.get_pos()
        if hover[0] > WIDTH - txt.get_width() - ui.inch2pix(0.4) and hover[0] < WIDTH - ui.inch2pix(0.1):
            if hover[1] > ui.inch2pix(0.1) and hover[1] < ui.inch2pix(0.3) + txt.get_height() - int(
                    ui.inch2pix(0.1) * (1 - v)):
                if mouse != False:
                    helper("configure")

        # title_font.bold = True

        def confx():
            nonlocal rebooter, x_configured, machine
            
            # if x_configured == False:
            ver = get_version(machine)

            if ver == 1:
                # WSL1
                tools.export(machine, 1)
                tools.export_audio(machine, 1, shell="bash")
            elif ver == 2:
                # WSL2
                tools.export(machine, 2)
                tools.export_audio(machine, 2, shell="bash")

            x_configured = True
            toaster.show_toast("Display Exported",
                               str(machine) + " is set to forward X through port 0.",
                               icon_path=asset_dir + "icon.ico",
                               duration=5,
                               threaded=True)

            restart = pymsgbox.confirm(text='Restart ' + machine + " To Apply Changes?", title='Restart Machine?',
                                       buttons=["Yes", "No"])
            if restart == "Yes":
                reboot(machine)
                rebooter = True
                machine = None

        def ask_reboot():
            nonlocal rebooter, machine
            restart = pymsgbox.confirm(text='Restart ' + machine + " To Apply Changes?", title='Restart Machine?',
                                       buttons=["Yes", "No"])
            if restart == "Yes":
                reboot(machine)
                rebooter = True
                machine = None
                
        def alternate_conf():
            nonlocal loading
            #loading = True
            options = [["Bash: Display/Audio Export"],
                      ["Bash: Enable LibGL Indirect"],
                      ["Bash: Toggle GTK DPI"],
                      ["Bash: Toggle QT DPI"],
                      
                      ["Zsh: Display/Audio Export"],
                      ["Zsh: Enable LibGL Indirect"],
                      ["Zsh: Toggle GTK DPI"],
                      ["Zsh: Toggle QT DPI"],

                      ["Fish: Display/Audio Export"],
                      ["Fish: Enable LibGL Indirect"],
                      ["Fish: Toggle GTK DPI"],
                      ["Fish: Toggle QT DPI"],
                      ["~Clean GWSL additions"]] #must be alphabetical because of reused chooser code
            icos = []
            s_list = []
            for option in options:
                s_list.append(option[0])
                pass
                #profile = tools.profile(machine, shell=shell_v)
                """
                if "QT_SCALE_FACTOR=2" in profile:
                    QT = 2
                if "GDK_SCALE=2" in profile:
                    GTK = 2

                """
                #if "export DISPLAY=" in profile or "set -gx DISPLAY" in profile:
                #    icos.append("check")
                #else:
                icos.append("shell")
                    
            
            option = chooser(canvas, "More Options", s_list, icon_override=icos)
            print(option)
            
            if option != None:
                if "Bash" in option:
                    shell = "bash"
                elif "Zsh" in option:
                    shell = "zsh"
                elif "Fish" in option:
                    shell = "fish"
                else:
                    shell = "bash"
                    
                profile = tools.profile(machine, shell=shell)
                m_version = get_version(machine)
                
                if "Clean" in option:
                    tools.cleanup(machine)
                    ask_reboot()
                    
                elif "Export" in option:
                    tools.export(machine, m_version, shell=shell)
                    tools.export_audio(machine, m_version, shell=shell)
                    ask_reboot()
                    print("export")
                    
                #elif "Audio" in option:
                #    tools.export_audio(machine, m_version, shell=shell)
                #    ask_reboot()
                #    print("export audio")
                    
                elif "LibGL" in option:
                    tools.export_v(machine, "LIBGL_ALWAYS_INDIRECT", 1, shell=shell)
                    ask_reboot()
                    print("libgl")
                elif "GTK" in option:
                    if shell == "fish":
                        if "GDK_SCALE 2" in profile:
                            print("gtk is 2. changing to 1")
                            tools.gtk(machine, 1, shell="fish")
                        else:
                            print("gtk is 1. changing to 2")
                            tools.gtk(machine, 2, shell="fish")
                    else:
                        if "GDK_SCALE=2" in profile:
                            print("gtk is 2. changing to 1")
                            tools.gtk(machine, 1, shell=shell)
                        else:
                            print("gtk is 1. changing to 2")
                            tools.gtk(machine, 2, shell=shell)
                    ask_reboot()
                    print("gtk")
                elif "QT" in option:
                    if shell == "fish":
                        if "QT_SCALE_FACTOR 2" in profile:
                            print("qt is 2. changing to 1")
                            tools.qt(machine, 1, shell="fish")
                        else:
                            print("qt is 1. changing to 2")
                            tools.qt(machine, 2, shell="fish")
                    else:
                        if "QT_SCALE_FACTOR=2" in profile:
                            print("qt is 2. changing to 1")
                            tools.qt(machine, 1, shell=shell)
                        else:
                            print("qt is 1. changing to 2")
                            tools.qt(machine, 2, shell=shell)
                    ask_reboot()
                    print("qt")
                    

                    

                
            
        def browse_wsl():
            nonlocal machine
            #chooser(canvas, "Alternate Shell Display Export", ["Bash (choose if unsure)", "Zsh", "Fish"], icon_override="shell")
            v = subprocess.getoutput(rf'wsl -d {machine} echo "hi"')
            subprocess.Popen(rf'explorer.exe "\\wsl$\{machine}"', shell=True)# + str(machine))
            
        def indirect_conf():
            nonlocal rebooter, libgl_indirect, machine
            
            # if x_configured == False:
            ver = get_version(machine)

            
            tools.export_v(machine, "LIBGL_ALWAYS_INDIRECT", 1)

            libgl_indirect = True
            

            restart = pymsgbox.confirm(text='Restart ' + str(machine) + " To Apply Changes?", title='Restart Machine?',
                                       buttons=["Yes", "No"])
            if restart == "Yes":
                reboot(machine)
                rebooter = True
                machine = None
                

            
        def conf_dbus():
            code = pymsgbox.password(text='Enter Sudo Password For ' + str(machine.replace("-", " ")) + ":",
                                     title='Authentication', mask='*')
            if code == None:
                return None
            passw = 'echo "' + code + '" | sudo -H -S '
            print("Cheching DBus Install...")
            run(machine, passw + "sudo apt -y install dbus dbus-x11", nolog=True)
            print("Preparing Systemd...")
            run(machine, passw + "sudo systemd-machine-id-setup", nolog=True)
            print("Starting Bus...")
            run(machine, passw + "sudo /etc/init.d/dbus start", nolog=True)
            # print("Injecting into .profile")
            # tools.dbus(machine)
            # print(run(machine, passw + 'echo -e "#!/bin/sh -e \n" >> /etc/rc.local'))
            # run(machine, passw + 'echo -e "/etc/init.d/dbus start \n" >> /etc/rc.local')
            # run(machine, passw + 'echo "exit 0" >> /etc/rc.local')
            print("Complete")

        def scaleg():
            nonlocal GTK, g_button, buttons, rebooter, machine
            if GTK == 2:
                tools.gtk(machine, 1)
            else:
                tools.gtk(machine, 2)

            GTK = 1
            profile = tools.profile(machine)
            if "GDK_SCALE=2" in profile:
                GTK = 2

            if GTK == 1:
                g_button = "HI-DPI"
            else:
                g_button = "LOW-DPI"

            restart = pymsgbox.confirm(text='Restart ' + machine + " To Apply Changes?", title='Restart Machine?',
                                       buttons=["Yes", "No"])
            if restart == "Yes":
                reboot(machine)
                rebooter = True
                machine = None

        def scaleq():
            nonlocal QT, q_button, buttons, rebooter, machine
            if QT == 2:
                tools.qt(machine, 1)
            else:
                tools.qt(machine, 2)

            QT = 1
            profile = tools.profile(machine)
            if "QT_SCALE_FACTOR=2" in profile:
                QT = 2

            if QT == 1:
                q_button = "HI-DPI"
            else:
                q_button = "LOW-DPI"

            restart = pymsgbox.confirm(text='Restart ' + machine + " To Apply Changes?", title='Restart Machine?',
                                       buttons=["Yes", "No"])
            if restart == "Yes":
                reboot(machine)
                rebooter = True
                machine = None

        def reb():
            nonlocal rebooter, machine
            r = threading.Thread(target=reboot, args=[machine])
            r.daemon = True
            r.start()
            rebooter = True
            machine = None

        def theme():
            nonlocal loading, them
            if themes != []:
                s_theme = chooser(canvas, "Choose A GTK Theme:", [" Default Theme"] + themes)
                if s_theme != None:
                    def th():
                        nonlocal them, s_theme
                        if s_theme != " Default Theme":
                            run(machine, """sed -i.bak '/GTK_THEME=/d' ~/.profile""")
                            run(machine, """echo 'export GTK_THEME=""" + str(s_theme) + """' >> ~/.profile""")
                            them = "Default"
                            profile = tools.profile(machine)
                            pl = profile.split("\n")
                            for i in pl:
                                if "GTK_THEME=" in i:
                                    them = i[17:]

                        else:
                            run(machine, """sed -i.bak '/GTK_THEME=/d' ~/.profile""")
                            them = "Default"

                    themer = threading.Thread(target=th)
                    themer.daemon = True
                    themer.start()

        plus = icons["plus"]
        minus = icons["minus"]

        buttons = []
        if x_configured == False:
            buttons.append(["Auto-Export Display/Audio", confx, icons["x"]])
        else:
            buttons.append(["Display/Audio Auto-Exporting", confx, icons["check"]])


        if libgl_indirect == False:
            buttons.append(["Enable LibGL Indirect (optional)", indirect_conf, icons["x"]])
        else:
            buttons.append(["LibGL Indirect is Enabled", indirect_conf, icons["laptop"]])
        
        buttons.append(["More Shells and Options", alternate_conf, icons["shell"]])

        
        if machine != None:
            if "deb" in machine.lower() or "ubuntu" in machine.lower():
                buttons.append(["Configure DBus (optional)", conf_dbus, icons["dbus_config"]])

         

        #if m_version == 2:
        #buttons.append(["Browse Distro Files", browse_wsl, icons["folder"]]) #TODO
        
 
        if "HI" in g_button:
            ico = plus
        else:
            ico = minus
        buttons.append(["Set GTK To: " + g_button, scaleg, ico])
        if "HI" in q_button:
            ico = plus
        else:
            ico = minus

        buttons.append(["Set QT To: " + q_button, scaleq, ico])
        if themes != []:
            buttons.append(["GTK Theme: " + str(them), theme, icons["theme"]])
        else:
            buttons.append(["No GTK Themes Installed", theme, icons["theme"]])

        buttons.append(["Reboot " + ni, ask_reboot, icons["refresh"]])
        click = None
        v5 = (1 - animator.get("loading_c")[0] / 100)

        title_font2 = ui.font(default_font, int(ui.inch2pix(0.13)))
        v_str = ""
        if m_version != "":
            v_str = f"(WSL {m_version})"
        txt3 = title_font2.render(v_str, True, white)
        txt3.set_alpha(int(v5 * 200 * v))
        
        canvas.blit(txt3, [WIDTH / 2 - txt3.get_width() / 2, ui.inch2pix(0.45) + txt.get_height() - int(ui.inch2pix(0.2) * (v - 1))])


        
        hover = pygame.mouse.get_pos()
        selected = False
        for i in buttons:
            s2 = False
            if loading == False:
                txt = title_font.render(i[0], True, white)
                if hover[0] > w and hover[0] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                    if hover[1] > h - ui.inch2pix(0.1) - int(v * d) and hover[1] < h + txt.get_height() + ui.inch2pix(
                            0.1) - int(v * d):
                        if mouse != False:
                            click = i[1]
                        selected = True
                        s2 = True
                        # animator.animate("choose", [0, 0])

                s = animator.get("select")[0] / 100

                txt2 = icon_font.render(i[2], True, white)

                if s2 == False:
                    txt2.set_alpha(int(v5 * int(v * 255)))
                    txt.set_alpha(int(v5 * (int(v * 255))))
                else:
                    txt2.set_alpha(int((1 - s) * v5 * int(v * 255)))
                    txt.set_alpha(int((1 - s) * v5 * (int(v * 255))))

                canvas.blit(txt, [w + ui.inch2pix(0.4), h - int(v5 * d)])

                fluent_ico_offset = 0
                if "fluent" in ico_font:
                    fluent_ico_offset = -0.05

                canvas.blit(txt2, [w, h - int(v5 * d) + ui.inch2pix(0.06 + fluent_ico_offset)])
                

                if s2 == True:
                    txt = title_font.render(i[0], True, accent)
                    txt.set_alpha(int(v5 * (int(v * 255 * s))))
                    canvas.blit(txt, [w + ui.inch2pix(0.4), h - int(v5 * d)])

                    txt2 = icon_font.render(i[2], True, accent)
                    txt2.set_alpha(int(v5 * int(v * 255 * s)))
                    canvas.blit(txt2, [w, h - int(v5 * d) + ui.inch2pix(0.06 + fluent_ico_offset)])

            h += ui.inch2pix(0.34) + txt.get_height() #used to be 0.35
            d += ui.inch2pix(0.1)

        if selected == True:
            animator.animate("select", [100, 0])
        else:
            animator.animate("select", [0, 0])

        txt = title_font.render("Cancel", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, HEIGHT + ui.inch2pix(0.6) - txt.get_height() - int(v * d)])
        
        if mouse != False:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT + ui.inch2pix(0.6) - txt.get_height() - int(v * d) and mouse[
                    1] < HEIGHT + ui.inch2pix(0.6) + txt.get_height() + ui.inch2pix(0.1) - int(v * d):
                    machine = None
                    animator.animate("choose", [0, 0])

        if loading == True:
            # txt2 = pygame.transform.rotozoom(loader, loading_angle, 0.22)
            # txt2.set_alpha(int(255))
            # canvas.blit(txt2, [WIDTH / 2 - txt2.get_width() / 2, HEIGHT / 2 - txt2.get_height() / 2 + ui.inch2pix(0)])
            pass
        v = animator.get("loading_c")[0] / 100
        txt2 = pygame.transform.rotozoom(loader, loading_angle, 0.22)
        txt2.set_alpha(int(v * 255))
        # canvas.blit(txt2, [ui.inch2pix(0.2) - txt2.get_width() / 2, HEIGHT - ui.inch2pix(0.3) - txt2.get_height() \
        # / 2 - int((v - 1) * ui.inch2pix(0.4))])
        canvas.blit(txt2, [WIDTH / 2 - txt2.get_width() / 2,
                           HEIGHT / 2 - ui.inch2pix(0.2) - txt2.get_height() / 2 - int((v - 1) * ui.inch2pix(0.4))])

        if click != None:
            click()

        if rebooter == True:
            animator.animate("choose", [0, 0])

        fpsClock.tick(60)
        animator.update()

        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=(pygame.BLEND_RGBA_ADD))

        pygame.display.update()
        if machine == None and animator.get("choose")[0] <= 1:
            return machine


def app_launcher(machine):
    global selected, canvas, WIDTH, HEIGHT, mini, back, lumen, mask
    animator.animate("choose", [100, 0])
    animator.animate("apps", [0, 0])

    b = pygame.Surface([WIDTH, HEIGHT])
    draw(b)

    apps = {}
    app_list = []
    loading = True
    message = ""
    k = "a"
    alpha = {}

    def get():
        nonlocal apps, loading, list_length, app_list, message, alpha
        read = tools.get_apps(machine, logger=logger)
        ui.set_icons(asset_dir + "Paper/")
        apper = {}
        sett = iset.read()

        avoid = sett["app_blacklist"]
        size = ui.inch2pix(0.4)
        
        for i in read:

            blocker = False
            name = i[0].lower() + i[1:]
            for a in avoid:
                if str(a).lower() in str(name).lower():
                    blocker = True
                    break
            if blocker == True:
                continue

            cmd = read[i]["cmd"]
            #if " " in cmd:
            #    cmd = cmd.split(" ")[0] #Hope this was here for a reason...
            
            if ' ' in cmd and '"' in cmd:
                #print("replace", cmd)
                cmd = cmd.replace('"', "'") #this fixes paths in commands
                ## nope cmd = cmd.replace(" ", "\\ ")

            if  "%" in cmd:
                cmd = cmd[:cmd.index("%")]
            
            #print(cmd)
            #size = ui.inch2pix(0.4)
            ico_name = read[i]["ico"]
            if ico_name == None or "." in ico_name:
                ico_name = name

            icon = pygame.transform.smoothscale(ui.pygame_icon(ico_name, bundle_dir), [size, size])
            apper.update({name: {"icon": icon, "cmd": cmd, "icn": ico_name}})
        apps = apper
        app_list = list(apps)
        app_list.sort()

        old_key = ""
        alpha = {}
        c = 0
        h2 = 0
        for i in app_list:
            if i[0].lower() != old_key:
                new_key = i[0].lower()
                old_key = new_key
                alpha.update({new_key: int(h2)})
            c += 1
            h2 = c * (ui.inch2pix(0.35) + ui.inch2pix(0.28))  # ui.inch2pix(0.35) + txt.get_height()

        animator.animate("apps", [100, 0])
        list_length = len(apps) * (ui.inch2pix(0.35) + ui.inch2pix(0.23))
        #loading = False
        """
        if app_list == []:
            time.sleep(0.5)
            message = "No Graphical Apps Found"
            animator.animate("apps", [0, 0])
            return False

        """
        
        ni = str(machine)[0].upper() + str(machine)[1:]
        ni = ni.replace("-", " ")
        icon_font = ui.font(ico_font, size)

        icon = pygame.transform.smoothscale(ui.pygame_icon("Files", bundle_dir), [size, size])
        
        apps[f"Files on {ni}"] = {"icon":icon, "cmd":"f_manager_gw"}
        apps[f"Terminal on {ni}"] = {"icon":icon, "cmd":"term_gw"}
        app_list = [f"Files on {ni}", f"Terminal on {ni}"] + app_list
        
        ####
        icon_surf3 = pygame.transform.smoothscale(ui.pygame_icon("Nautilus", bundle_dir), [size, size])

        icon_font = ui.font(ico_font, size)
        sett = icon_font.render(icons["folder"], True, white)

        
        icon_surf = pygame.Surface([int(size), int(size)], pygame.SRCALPHA)
        icon_surf.blit(sett, [0, int(-ui.inch2pix(0.03))],
                        special_flags=(pygame.BLEND_RGBA_ADD))

        #####
        icon_surf4 = pygame.transform.smoothscale(ui.pygame_icon("Terminal", bundle_dir), [size, size])

        sett = icon_font.render(icons["shell"], True, white)

        
        icon_surf2 = pygame.Surface([size, size], pygame.SRCALPHA)
        icon_surf2.blit(sett, [0, int(-ui.inch2pix(0.03))],
                        special_flags=(pygame.BLEND_RGBA_ADD))

                    
        apps[f"Files on {ni}"] = {"icon":icon_surf, "cmd":"f_manager_gw"}
        apps[f"Terminal on {ni}"] = {"icon":icon_surf2, "cmd":"term_gw"}

        loading = False
    list_length = 0

    t = threading.Thread(target=get)
    t.daemon = True
    t.start()

    scroll2 = 0
    scroll = 0
    loading_angle = 0
    icon_surf = pygame.Surface([WIDTH, HEIGHT], pygame.SRCALPHA)

    # generate loader
    icon_font = ui.font(ico_font, int(ui.inch2pix(1)))  # 0.19

    loader = icon_font.render(icons["refresh"], True, white)
    # print(txt2.get_size())

    end = False
    touch_scrolling = False
    while True:
        loading_angle -= 10
        mouse = False
        bottom_padding = ui.inch2pix(0.7)
        top_padding = ui.inch2pix(0.6) + ui.inch2pix(0.21) + ui.inch2pix(0.1)

        if win32gui.GetFocus() != HWND:
            if animator.get("start")[0] == 100:
                animator.animate("start", [0, 0])
                animator.animate("start2", [0, 0])
                break

        if animator.get("start")[0] < 100:
            break
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                button = event.button
                if button == 1 and touch_scrolling == False:
                    mouse = event.pos
                if touch_scrolling == True:
                    touch_scrolling = False

            elif event.type == MOUSEBUTTONDOWN:
                button = event.button
                if list_length > HEIGHT - bottom_padding - top_padding:
                    if button == 5:  # down
                        if scroll > -list_length + ui.inch2pix(0.5) - HEIGHT - bottom_padding - top_padding:
                            scroll2 -= ui.inch2pix(0.5)
                    elif button == 4:  # up
                        if scroll < -ui.inch2pix(0.4):
                            scroll2 += ui.inch2pix(0.5)
                            
            elif event.type == MOUSEMOTION:               
                rel = event.rel[1]
                if pygame.mouse.get_pressed()[0] == True:
                    if abs(rel) > 5:
                        touch_scrolling = True
                    if rel < -5:
                        if scroll > -list_length + ui.inch2pix(0.5) - HEIGHT - bottom_padding - top_padding:
                            scroll2 += rel
                    elif rel > 5:
                        if scroll < -ui.inch2pix(0.4):
                            scroll2 += rel
                
            elif event.type == KEYDOWN:
                key = pygame.key.name(event.key)
                if key.lower() in alpha:
                    scroll2 = -1 * alpha[key.lower()]  # - top_padding

            elif event.type == VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                if WIDTH < ui.inch2pix(7.9):
                    WIDTH = ui.inch2pix(7.9)
                if HEIGHT < ui.inch2pix(5):
                    HEIGHT = ui.inch2pix(5)

                canvas = pygame.display.set_mode([WIDTH, HEIGHT], RESIZABLE)
                # ui.set_size([WIDTH, HEIGHT])
                # mini = pygame.image.load(bak).convert()
                back = mini.copy()
                back = pygame.transform.scale(back, [WIDTH, HEIGHT])
                ui.iris2(back, [0, 0],
                         [WIDTH, HEIGHT],
                         [0, 0, 0], radius=10, shadow_enabled=False, resolution=50)
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])

                b = pygame.Surface([WIDTH, HEIGHT])
                draw(b)
                lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask.fill([255, 0, 0])

        v = animator.get("choose")[0] / 100

        # ui.iris2(canvas, [0, ui.inch2pix(0.6) + ui.inch2pix(0.21) + ui.inch2pix(0.25)],
        #     [WIDTH, HEIGHT - (ui.inch2pix(0.8) + ui.inch2pix(0.21) + ui.inch2pix(0.25)) - ui.inch2pix(0.8)],
        #     [0, 0, 0], radius=10, shadow_enabled=False, resolution=30, alpha=int(v * 255))

        # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0] + [int(v * 180)])
        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))

        ni = str(machine)[0].upper() + str(machine)[1:]
        ni = ni.replace("-", " ")
        txt = title_font.render("Apps On " + str(ni), True, white)

        w = ui.inch2pix(0.5)  # WIDTH / 2 - txt.get_width() / 2 + ui.inch2pix(0.1)
        d = ui.inch2pix(0.2)
        h = ui.inch2pix(0.8) + txt.get_height() + ui.inch2pix(0.25)
        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        icon_font = ui.font(ico_font, int(ui.inch2pix(0.19)))

        # title_font.bold = True

        if scroll < scroll2 - int((scroll2 - scroll) / 2):
            scroll += int((scroll2 - scroll) / 2)
        if scroll2 < scroll - int((scroll - scroll2) / 2):
            scroll -= int((scroll - scroll2) / 2)

        # draw top and bottom of background
        icon_surf.fill([0, 0, 0, 0])
        icon_surf.blit(b, [0, 0], [0, 0, WIDTH, top_padding])
        icon_surf.blit(b, [0, HEIGHT - bottom_padding], [0, (HEIGHT - bottom_padding), WIDTH, bottom_padding])

        v3 = animator.get("apps")[0] / 100
        a = int(v3 * 255)
        for a in app_list:
            i = apps[a]

            if h - int((v3 - 1) * d) + scroll > -1 * (ui.inch2pix(0.5)) and h - int((v3 - 1) * d) + scroll < HEIGHT:

                txt = title_font.render(a[0].upper() + a[1:], True, white)
                txt.set_alpha(int(v3 * 255))

                icon = i["icon"]
                icon_surf.blit(icon, [w + ui.inch2pix(0.4) - icon.get_width() - ui.inch2pix(0.1),
                                      h + txt.get_height() / 2 - icon.get_height() / 2 - int(
                                          (v3 - 1) * d) + scroll + ui.inch2pix(0.03)],
                               special_flags=(pygame.BLEND_RGBA_ADD))
        
                txt2 = icon_font.render(icons["link"], True, white)

                txt_width = WIDTH - (w + ui.inch2pix(0.4) + txt2.get_width() + ui.inch2pix(0.6))
                ext = title_font.render("... ", True, white)

                icon_surf.blit(txt, [w + ui.inch2pix(0.4), h - int((v3 - 1) * d) + scroll],
                               [0, 0, txt_width, txt.get_height()], special_flags=(pygame.BLEND_RGBA_ADD))
                if txt.get_width() > txt_width:
                    icon_surf.blit(ext, [w + ui.inch2pix(0.4) + txt_width, h - int((v3 - 1) * d) + scroll],
                                   special_flags=(pygame.BLEND_RGBA_ADD))
                    txt_width += ext.get_width()

                if i["cmd"] != "f_manager_gw" and i["cmd"] != "term_gw":
                    icon_surf.blit(txt2, [WIDTH - txt2.get_width() - ui.inch2pix(0.3),
                                      h - int((v3 - 1) * d) + ui.inch2pix(0.06) + scroll],
                               special_flags=(pygame.BLEND_RGBA_ADD))
                    
                if mouse != False and mouse[1] >= top_padding and mouse[1] <= HEIGHT - bottom_padding:
                    if mouse[1] > h - ui.inch2pix(0.1) - int((v3 - 1) * d) + scroll and mouse[
                        1] < h + txt.get_height() + ui.inch2pix(0.2) - int((v3 - 1) * d) + scroll:
                        if mouse[0] > w + ui.inch2pix(0.4) - icon.get_width() - ui.inch2pix(0.1) and mouse[
                            0] < w + ui.inch2pix(0.4) + txt_width:
                            if i["cmd"] != "f_manager_gw" and i["cmd"] != "term_gw":
                                spawn_n_run(machine, i["cmd"], "Default", "Default", "Default", "Default", "None")
                                if animator.get("start")[0] == 100:
                                    animator.animate("start", [0, 0])
                                    animator.animate("start2", [0, 0])
                                    end = True
                            else:
                                if i["cmd"] == "f_manager_gw":
                                    print("Files")
                                    subprocess.Popen(rf'explorer.exe "\\wsl$\{machine}"', shell=True)# + str(machine))
                                    
                                    
                                elif i["cmd"] == "term_gw":
                                    print("Terminal")
                                    sett = iset.read()
                                    shell_ui = sett["general"]["shell_gui"]
                                    if shell_ui == "cmd":
                                        subprocess.Popen("wsl.exe ~ -d " + str(machine))
                                    else:
                                        subprocess.Popen(f'wt -p "{machine}"')

                                    
                        elif mouse[0] > w + ui.inch2pix(0.4) + txt_width and mouse[0] < WIDTH:
                            if i["cmd"] != "f_manager_gw" and i["cmd"] != "term_gw":
                                shortcut(name=a[0].upper() + a[1:], cmd=i["cmd"], mach=machine, icn=i["icn"])

            h += ui.inch2pix(0.35) + txt.get_height()
            d += ui.inch2pix(0.1)

        # Draw stuff on canvas
        canvas.blit(b, [0, 0])
        # draw top icons and bottom icons
        icon_surf.set_alpha(int(int(v3 * 255) / 4))
        canvas.blit(icon_surf, [0, 0], [0, 0, WIDTH, top_padding])

        canvas.blit(icon_surf, [0, HEIGHT - bottom_padding], [0, (HEIGHT - bottom_padding), WIDTH, bottom_padding])

        # blur
        ui.iris2(canvas, [0, 0],
                 [WIDTH, HEIGHT],
                 [0, 0, 0], radius=10, shadow_enabled=False, resolution=30, alpha=int(v * 255))

        # draw central items
        icon_surf.set_alpha(int(v3 * 255))
        canvas.blit(icon_surf, [0, top_padding], [0, (top_padding), WIDTH, HEIGHT - bottom_padding - top_padding])

        # Top title above blur
        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))

        txt = title_font.render("Apps on " + str(ni), True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * v)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.13)))
        s_str = ""
        if loading == False:
            s_str = "(Type to Search)"
        txt3 = title_font.render(s_str, True, white)
        txt3.set_alpha(int(v * v3 * 200))
        
        canvas.blit(txt3, [WIDTH / 2 - txt3.get_width() / 2, ui.inch2pix(0.45) + txt.get_height() - int(ui.inch2pix(0.2) * (v - 1))])
        

        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        txt = title_font.render("?", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt,
                    [WIDTH - txt.get_width() - ui.inch2pix(0.3), ui.inch2pix(0.2) - int(ui.inch2pix(0.1) * (1 - v))])
        hover = pygame.mouse.get_pos()
        if hover[0] > WIDTH - txt.get_width() - ui.inch2pix(0.4) and hover[0] < WIDTH - ui.inch2pix(0.1):
            if hover[1] > ui.inch2pix(0.1) and hover[1] < ui.inch2pix(0.3) + txt.get_height() - int(
                    ui.inch2pix(0.1) * (1 - v)):
                if mouse != False:
                    helper("launcher")

        # loader
        v2 = 1 - (animator.get("apps")[0] / 100)

        if message == "":
            txt2 = pygame.transform.rotozoom(loader, loading_angle, 0.22)
            txt2.set_alpha(int(v * int(v2 * 255)))

            canvas.blit(txt2, [WIDTH / 2 - txt2.get_width() / 2,
                               HEIGHT / 2 - txt2.get_height() / 2 - int((v2 - 1) * ui.inch2pix(0.4)) + ui.inch2pix(0)])

        # error Message
        title_font = ui.font(default_font, int(ui.inch2pix(0.17)))
        txt = title_font.render(message, True, white)
        txt.set_alpha(int(v * int(v2 * 255)))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2,
                          HEIGHT / 2 - txt.get_height() / 2 - int((v2 - 1) * ui.inch2pix(0.4)) + ui.inch2pix(0)])

        txt = title_font.render("Cancel", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2,
                          HEIGHT - ui.inch2pix(0.3) - txt.get_height() - int((v - 1) * ui.inch2pix(0.4))])
        if mouse != False:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT - ui.inch2pix(0.3) - txt.get_height() - int((v - 1) * ui.inch2pix(0.4)) and mouse[
                    1] < HEIGHT - ui.inch2pix(0.3) - txt.get_height() - int(
                        (v - 1) * ui.inch2pix(0.4)) + txt.get_height() + ui.inch2pix(0.1):
                    machine = None
                    animator.animate("choose", [0, 0])
                    animator.animate("apps", [0, 0])
                    
        
        

        

        if light == False:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, int(v*100)])
        else:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, int(v*80)])
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, int(v*80)])

        fpsClock.tick(60)
        animator.update()

        if end == True:
            break

        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=(pygame.BLEND_RGBA_ADD))

        pygame.display.update()
        if machine == None and animator.get("choose")[0] <= 1:
            return machine


def chooser(backdrop, title, options, icon_override=None):
    global selected, canvas, WIDTH, HEIGHT, mini, back, lumen, mask
    animator.register("choose1", [0, 0])
    animator.animate("choose1", [100, 0])

    options.sort()

    b = pygame.Surface([WIDTH, HEIGHT])
    b = backdrop.copy()

    size = ui.inch2pix(0.4)
    ui.set_icons(asset_dir + "Paper/")

    ico_list = False
    import typing
    
    if isinstance(icon_override, str):
        icon = "paint"
        if icon_override != None:
            icon = icon_override
        iconer = pygame.transform.smoothscale(ui.pygame_icon(icon, bundle_dir), [size, size])
            
    elif isinstance(icon_override, list):
        ico_list = True
        
    icon = "paint"
    iconer = pygame.transform.smoothscale(ui.pygame_icon(icon, bundle_dir), [size, size])

    list_length = 0
    list_length = len(options) * (ui.inch2pix(0.35) + ui.inch2pix(0.25))

    scroll2 = 0
    scroll = 0
    icon_surf = pygame.Surface([WIDTH, HEIGHT], pygame.SRCALPHA)

    choice = False

    end = False

    k = "a"
    alpha = {}
    option_names = {}
    pretty_options = []
    for i in options:
        option_names.update({i[0].upper() + i[1:]: i})

    for i in options:
        pretty_options.append(i[0].upper() + i[1:])
    pretty_options.sort()
    touch_scrolling = False
    while True:
        mouse = False
        bottom_padding = ui.inch2pix(0.7)
        top_padding = ui.inch2pix(0.6) + ui.inch2pix(0.21) + ui.inch2pix(0.1)

        if win32gui.GetFocus() != HWND:
            if animator.get("start")[0] == 100:
                animator.animate("start", [0, 0])
                animator.animate("start2", [0, 0])
                break

        if animator.get("start")[0] < 100:
            break  # pygame.quit()
            # sys.exit()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                button = event.button
                if button == 1 and touch_scrolling == False:
                    mouse = event.pos
                if touch_scrolling == True:
                    touch_scrolling = False

            elif event.type == MOUSEBUTTONDOWN:
                button = event.button
                if list_length > HEIGHT - bottom_padding - top_padding:
                    if button == 5:  # down
                        if scroll > -list_length + ui.inch2pix(
                                0.5) + HEIGHT - top_padding - bottom_padding - ui.inch2pix(5):
                            scroll2 -= ui.inch2pix(0.5)
                    elif button == 4:  # up
                        if scroll < -ui.inch2pix(0.4):
                            scroll2 += ui.inch2pix(0.5)
            elif event.type == MOUSEMOTION:               
                rel = event.rel[1]
                if pygame.mouse.get_pressed()[0] == True:
                    if abs(rel) > 5:
                        touch_scrolling = True
                    if rel < -5:
                        if scroll > -list_length + ui.inch2pix(
                                0.5) + HEIGHT - top_padding - bottom_padding - ui.inch2pix(5):
                            scroll2 += rel
                    elif rel > 5:
                        if scroll < -ui.inch2pix(0.4):
                            scroll2 += rel
            elif event.type == KEYDOWN:
                key = pygame.key.name(event.key)
                if key.lower() in alpha:
                    scroll2 = -1 * alpha[key.lower()]  # - top_padding


            elif event.type == VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                if WIDTH < ui.inch2pix(7.9):
                    WIDTH = ui.inch2pix(7.9)
                if HEIGHT < ui.inch2pix(5):
                    HEIGHT = ui.inch2pix(5)

                canvas = pygame.display.set_mode([WIDTH, HEIGHT], RESIZABLE)
                # ui.set_size([WIDTH, HEIGHT])
                # mini = pygame.image.load(bak).convert()
                back = mini.copy()
                back = pygame.transform.scale(back, [WIDTH, HEIGHT])
                ui.iris2(back, [0, 0],
                         [WIDTH, HEIGHT],
                         [0, 0, 0], radius=10, shadow_enabled=False, resolution=50)
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])

                b = pygame.Surface([WIDTH, HEIGHT])
                draw(b)
                lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask.fill([255, 0, 0])

        v = animator.get("choose1")[0] / 100

        # ui.iris2(canvas, [0, ui.inch2pix(0.6) + ui.inch2pix(0.21) + ui.inch2pix(0.25)],
        #     [WIDTH, HEIGHT - (ui.inch2pix(0.8) + ui.inch2pix(0.21) + ui.inch2pix(0.25)) - ui.inch2pix(0.8)],
        #     [0, 0, 0], radius=10, shadow_enabled=False, resolution=30, alpha=int(v * 255))

        # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0] + [int(v * 180)])
        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))

        txt = title_font.render(title, True, white)

        w = ui.inch2pix(0.5)  # WIDTH / 2 - txt.get_width() / 2 + ui.inch2pix(0.1)
        d = ui.inch2pix(0.2)
        h = ui.inch2pix(0.8) + txt.get_height() + ui.inch2pix(0.25)
        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        icon_font = ui.font(ico_font, int(ui.inch2pix(0.19)))

        # title_font.bold = True

        if scroll < scroll2 - int((scroll2 - scroll) / 2):
            scroll += int((scroll2 - scroll) / 2)
        if scroll2 < scroll - int((scroll - scroll2) / 2):
            scroll -= int((scroll - scroll2) / 2)

        # draw top and bottom of background
        icon_surf.fill([0, 0, 0, 0])
        icon_surf.blit(b, [0, 0], [0, 0, WIDTH, top_padding])
        icon_surf.blit(b, [0, HEIGHT - bottom_padding], [0, (HEIGHT - bottom_padding), WIDTH, bottom_padding])

        v3 = animator.get("choose1")[0] / 100
        a = int(v3 * 255)
        k = "a"
        alpha = {}
        old_key = ""
        alpha = {}
        c = 0
        h2 = 0
        icon_font = ui.font(ico_font, int(ui.inch2pix(0.33)))
        
        for a in pretty_options:
            if option_names[a][0].lower() != old_key:
                new_key = option_names[a][0].lower()
                old_key = new_key
                alpha.update({new_key: int(h2)})
            c += 1
            h2 = c * (ui.inch2pix(0.35) + ui.inch2pix(0.27))  # ui.inch2pix(0.35) + txt.get_height()

            if h - int((v3 - 1) * d) + scroll > -1 * (ui.inch2pix(0.5)) and h - int((v3 - 1) * d) + scroll < HEIGHT:

                txt = title_font.render(a, True, white)
                txt.set_alpha(int(v3 * 255))

                if ico_list == True:
                    sett = icon_font.render(icons[icon_override[pretty_options.index(a)]], True, white)
                    sett.set_alpha(int(v3 * 255))
                    modern_offset = 0
                    if modern == True:
                        modern_offset = ui.inch2pix(0.02)
                
                    icon_surf.blit(sett, [w + ui.inch2pix(0.4) - iconer.get_width() - ui.inch2pix(0.1),
                                       modern_offset + h + txt.get_height() / 2 - iconer.get_height() / 2 - int((v3 - 1) * d) + scroll + ui.inch2pix(0.03)],
                                    special_flags=(pygame.BLEND_RGBA_ADD))
                
                else:
                    icon_surf.blit(iconer, [w + ui.inch2pix(0.4) - iconer.get_width() - ui.inch2pix(0.1),
                                            h + txt.get_height() / 2 - iconer.get_height() / 2 - int(
                                                (v3 - 1) * d) + scroll + ui.inch2pix(0.03)],
                                   special_flags=(pygame.BLEND_RGBA_ADD))

                txt_width = WIDTH - (w + ui.inch2pix(0.4) + ui.inch2pix(0.2) + ui.inch2pix(0.6))
                ext = title_font.render("... ", True, white)
                
                icon_surf.blit(txt, [w + ui.inch2pix(0.4), h - int((v3 - 1) * d) + scroll],
                               [0, 0, txt_width, txt.get_height()], special_flags=(pygame.BLEND_RGBA_ADD))
                if txt.get_width() > txt_width:
                    icon_surf.blit(ext, [w + ui.inch2pix(0.4) + txt_width, h - int((v3 - 1) * d) + scroll],
                                   special_flags=(pygame.BLEND_RGBA_ADD))
                    txt_width += ext.get_width()

                if mouse != False and mouse[1] >= top_padding and mouse[1] <= HEIGHT - bottom_padding:
                    if mouse[1] > h - ui.inch2pix(0.1) - int((v3 - 1) * d) + scroll and mouse[
                        1] < h + txt.get_height() + ui.inch2pix(0.2) - int((v3 - 1) * d) + scroll:
                        if mouse[0] > w + ui.inch2pix(0.4) - iconer.get_width() - ui.inch2pix(0.1) and mouse[
                            0] < w + ui.inch2pix(0.4) + txt_width:
                            choice = option_names[a]
                            animator.animate("choose1", [0, 0])

            h += ui.inch2pix(0.35) + txt.get_height()
            d += ui.inch2pix(0.1)
        # Draw stuff on canvas
        canvas.blit(b, [0, 0])
        # draw top icons and bottom icons
        icon_surf.set_alpha(int(int(v3 * 255) / 4))
        canvas.blit(icon_surf, [0, 0], [0, 0, WIDTH, top_padding])

        canvas.blit(icon_surf, [0, HEIGHT - bottom_padding], [0, (HEIGHT - bottom_padding), WIDTH, bottom_padding])

        # blur
        ui.iris2(canvas, [0, 0],
                 [WIDTH, HEIGHT],
                 [0, 0, 0], radius=10, shadow_enabled=False, resolution=30, alpha=int(v * 255))

        # draw central items
        icon_surf.set_alpha(int(v3 * 255))
        canvas.blit(icon_surf, [0, top_padding], [0, (top_padding), WIDTH, HEIGHT - bottom_padding - top_padding])

        # Top title above blur
        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))

        txt = title_font.render(title, True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * v)])


        title_font = ui.font(default_font, int(ui.inch2pix(0.13)))
        s_str = "(Type to Search)"
        txt3 = title_font.render(s_str, True, white)
        txt3.set_alpha(int(v * v3 * 200))
        
        canvas.blit(txt3, [WIDTH / 2 - txt3.get_width() / 2, ui.inch2pix(0.45) + txt.get_height() - int(ui.inch2pix(0.2) * (v - 1))])

        
        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        txt = title_font.render("?", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt,
                    [WIDTH - txt.get_width() - ui.inch2pix(0.3), ui.inch2pix(0.2) - int(ui.inch2pix(0.1) * (1 - v))])
        hover = pygame.mouse.get_pos()
        if hover[0] > WIDTH - txt.get_width() - ui.inch2pix(0.4) and hover[0] < WIDTH - ui.inch2pix(0.1):
            if hover[1] > ui.inch2pix(0.1) and hover[1] < ui.inch2pix(0.3) + txt.get_height() - int(
                    ui.inch2pix(0.1) * (1 - v)):
                if mouse != False:
                    helper("theme")

        txt = title_font.render("Cancel", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2,
                          HEIGHT - ui.inch2pix(0.3) - txt.get_height() - int((v - 1) * ui.inch2pix(0.4))])
        if mouse != False:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT - ui.inch2pix(0.3) - txt.get_height() - int((v - 1) * ui.inch2pix(0.4)) and mouse[
                    1] < HEIGHT - ui.inch2pix(0.3) - txt.get_height() - int(
                        (v - 1) * ui.inch2pix(0.4)) + txt.get_height() + ui.inch2pix(0.1):
                    choice = None
                    animator.animate("choose1", [0, 0])

        if light == False:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, int(v*100)])
        else:
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, int(v*80)])
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, int(v*80)])

        fpsClock.tick(60)
        animator.update()

        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=(pygame.BLEND_RGBA_ADD))

        pygame.display.update()
        if choice != False and animator.get("choose1")[0] <= 1:
            return choice


# def about():
#    choice = pymsgbox.confirm(text="This is the GWSL2 dashboard. GWSL2 is copyright Paul-E/Opticos Studios 2020.
#       The X-Window backend is VCXSRV.", title="GWSL", buttons=["Sounds Good!"])


def create_shortcut(command, name, icon):
    try:
        args = str(command)
        # winshell.start_menu()
        shortcut_path = os.path.join(app_path, str(str(name) + ".lnk"))
        home = str(Path.home())
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)

        print("attempt create shortcut")
        print("args:", args)
        print("cwd:", home)
        print("in:", shortcut_path)

        if BUILD_MODE == "MSIX":
            CSIDL_COMMON_APPDATA = 28

            _SHGetFolderPath = windll.shell32.SHGetFolderPathW
            _SHGetFolderPath.argtypes = [wintypes.HWND,
                                         ctypes.c_int,
                                         wintypes.HANDLE,
                                         wintypes.DWORD, wintypes.LPCWSTR]

            path_buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            result = _SHGetFolderPath(0, CSIDL_COMMON_APPDATA, 0, 0, path_buf)
            target_loc = path_buf.value + r"\\Microsoft\\WindowsApps\\"
            shortcut.WorkingDirectory = "/"  # home
            shortcut.Targetpath = target_loc + "gwsl.exe"
        else:
            shortcut.Targetpath = sys.executable
            print(sys.executable)
            shortcut.WorkingDirectory = home

        shortcut.Arguments = args

        shortcut.IconLocation = str(icon)
        shortcut.save()

        while os.path.exists(shortcut_path) == False:
            print("waiting")
            pass
        if os.path.exists(shortcut_path) == True:
            print("Shortcut Successfully Created")
        print(subprocess.getoutput('copy "' + shortcut_path + '" "' + winshell.start_menu() + '"'))

    except Exception as e:
        logger.exception("Exception occurred - Cannot Create Shortcut")


def start_server(port, mode, clipboard, extra=None):
    default_arguments = ["-ac", "-wgl", "-compositewm", "-notrayicon", "-dpi", "auto"]
    if mode == "multi":
        default_arguments.append("-multiwindow")
    elif mode == "full":
        default_arguments.append("-fullscreen")
    elif mode == "c" and extra != None:
        default_arguments = extra
    if clipboard == True:
        default_arguments.append("-clipboard")
        default_arguments.append("-primary")
    else:
        default_arguments.append("-noclipboard")
        default_arguments.append("-noprimary")

    sett = iset.read()
    hidpi = sett["graphics"]["hidpi"]
    
    hd = ""
    if hidpi == False:
        hd = "_lowdpi"
    proc = subprocess.Popen([f"VCXSRV/GWSL_vcxsrv{hd}.exe", ":" + str(port)] + default_arguments)
    return proc.pid


def get_light():
    try:
        registry = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        key_value = QueryValueEx(key, 'AppsUseLightTheme')
        k = int(key_value[0])
        return k
    except:
        return 0


def spawn_n_run(machine, command, w_mode, w_clipboard, GTK, QT, appends, cmd=False, theme="Follow Windows",
                root="False", dbus="False", keep="False"):
    ver = get_version(machine)
    if root == "True":
        code = pymsgbox.password(text='Enter Sudo Password For ' + str(machine.replace("-", " ")) + ":",
                                 title='Authentication', mask='*')
        if code == None:
            return None
        passw = "echo '" + code + "' | sudo -H -S "

    else:
        passw = ""
        
    v = ""
    
    if dbus == "True":
        v = start_dbus(machine)
    if dbus == "True" and "system message bus already started" not in v:
        if passw == "":
            code = pymsgbox.password(text="Enter Sudo Password To Start DBus:", title='DBus Not Started.', mask='*')

            runo3(machine, "echo '" + code + "' | sudo -H -S " + "/etc/init.d/dbus start", nolog=True)
        else:
            runo3(machine, passw + "/etc/init.d/dbus start", nolog=True)

    if theme == "Follow Windows":
        k = get_light()
        prof = tools.profile(machine)
        if "GTK_THEME" in prof:
            if k == 1:
                l_mode = "GTK_THEME=$GTK_THEME:light "
            else:
                l_mode = "GTK_THEME=$GTK_THEME:dark "
        else:
            if k == 1:
                l_mode = "GTK_THEME=Adwaita:light "
            else:
                l_mode = "GTK_THEME=Adwaita:dark "

    elif theme == "Light Mode":
        prof = tools.profile(machine)
        if "GTK_THEME" in prof:
            l_mode = "GTK_THEME=$GTK_THEME:light "

        else:
            l_mode = "GTK_THEME=Adwaita:light "

    elif theme == "Dark Mode":
        prof = tools.profile(machine)
        if "GTK_THEME" in prof:
            l_mode = "GTK_THEME=$GTK_THEME:dark "
        else:
            l_mode = "GTK_THEME=Adwaita:dark "

    try:
        if w_mode == "Default" and w_clipboard == "Default":
            # Don't start a new server
            if GTK == "Default":
                gtk = ""
            else:
                gtk = "GDK_SCALE=" + GTK + " "

            if QT == "Default":
                qt = ""
            else:
                qt = "QT_SCALE_FACTOR=" + QT + " "

            if appends == "None":
                append = ""
            else:
                append = " " + appends
            if ver == 1:
                #print("check1")
                runs(machine, passw + l_mode + "DISPLAY=:0 PULSE_SERVER=tcp:localhost " + qt + gtk + command + append, nolog=True)
            else:
                ip = get_ip(machine)
                #print("check2")
                runs(machine, passw + l_mode + "DISPLAY=" + str(ip) + f":0 PULSE_SERVER=tcp:{ip} " + qt + gtk + command + append, nolog=True)

        else:
            # In this case, we need to start a new server, run in a new thread that self closes
            # VCXSRV after command if in multi window mode
            port = str(random.randrange(1000, 9999))
            extra = None
            if w_mode == "Multi Window":
                mode = "multi"
            elif w_mode == "Single Window":
                mode = "single"
            elif w_mode == "Fullscreen":
                mode = "full"
            elif w_mode == "Default":
                sett = iset.read()
                mode = sett["graphics"]["window_mode"]
                if mode != "multi" and mode != "single" and mode != "full":
                    print("custom fallback")
                    sett = iset.read()
                    profile_dict = sett["xserver_profiles"]
                    extra = profile_dict[mode]
                    mode = "c"
                
            else:
                mode = w_mode

            if w_clipboard == "Default":
                sett = iset.read()
                clipboard = sett["general"]["clipboard"]
            elif w_clipboard == "Enabled" or w_clipboard == True:
                clipboard = True
            elif w_clipboard == "Disabled" or w_clipboard == False:
                clipboard = False

            PID = start_server(port, mode, clipboard, extra)
            ver = get_version(machine)

            if GTK == "Default":
                gtk = ""
            else:
                gtk = "GDK_SCALE=" + GTK + " "

            if QT == "Default":
                qt = ""
            else:
                qt = "QT_SCALE_FACTOR=" + QT + " "

            if appends == "None":
                append = ""
            else:
                append = " " + appends

            def threaded():
                print("running in thread")
                # runo2 #runo
                if ver == 1:
                    #print("check3")
                    print(runs(machine, passw + l_mode + "DISPLAY=:" + port + " PULSE_SERVER=tcp:localhost " + qt + gtk + command + append, nolog=True))

                elif ver == 2:
                    ip = get_ip(machine)
                    #print("check4")
                    print(runs(machine,
                               passw + l_mode + "DISPLAY=" + str(ip) + ":" + port + f" PULSE_SERVER=tcp:{ip} " + qt + gtk + command + append, nolog=True))

                while True:
                    time.sleep(2)
                    procs = runo2(machine, "ps -ef")
                    if command in str(procs):
                        time.sleep(1)
                    else:
                        break
                if keep == "False":
                    print(f"All of {command} terminated. Killing Server Instance on port {port}")
                    print(subprocess.getoutput('taskkill /F /PID ' + str(PID)))
                else:
                    print(f"XServer do not kill. Keeping X on port {port}")

            if mode == "single":
                if ver == 1:
                    #print("check5")
                    runs(machine, passw + l_mode + "DISPLAY=:" + port + " PULSE_SERVER=tcp:localhost " + qt + gtk + command + append, nolog=True)

                elif ver == 2:
                    ip = get_ip(machine)
                    #print("check6")
                    runs(machine,
                         passw + l_mode + "DISPLAY=" + str(ip) + ":" + port + f" PULSE_SERVER=tcp:{ip} " + qt + gtk + command + append, nolog=True)

            else:
                if cmd == False:
                    t = threading.Thread(target=threaded)
                    t.daemon = True
                    t.start()
                else:
                    threaded()
    except Exception as e:
        logger.exception("Exception occurred - cannot spawn process")




			
def get_login(machine):
    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)  # , fg="red", bg="black")
        boxRoot.withdraw()
    else:
        boxRoot = tk.Tk()
        boxRoot.withdraw()

    def quitter():
        boxRoot.quit()
        boxRoot.destroy()
        boxRoot.running = False
        return None

    def login(*args):
        nonlocal creds
        passw = link_pass.get()
        user = link_user.get()
        key = link_key.get()
        if user != "" and (passw != "" or key != ""):
            creds = {"user": user, "pass": passw, "key": key}
            sett = iset.read()
            sett["putty"]["ssh_key"] = link_key.get()
            iset.set(sett)
            
            boxRoot.quit()
            boxRoot.destroy()
            # boxRoot.running = False
            

    def browse_key(*args):
        nonlocal creds
        from tkinter.filedialog import askopenfilename
        boxRoot.wm_attributes("-topmost", 0)
        filename = tk.filedialog.askopenfilename(initialdir = "~/", title=f"Select a Valid SSH Private Key (.PPK) for {machine}", \
                                      filetypes=[("PPK Key Files","*.ppk")])
        boxRoot.wm_attributes("-topmost", 1)
        link_key.delete(0,"end")
        link_key.insert(0, filename)
        sett = iset.read()
        sett["putty"]["ssh_key"] = filename
        iset.set(sett)
        

    creds = {}

    boxRoot.title("Login to " + str(machine))
    boxRoot.iconname("Dialog")
    width, height = ui.inch2pix(5), ui.inch2pix(2)
    
    boxRoot.minsize(width, height)
    boxRoot.iconbitmap(asset_dir + "icon.ico")
    boxRoot.geometry('+%d+%d' % (screensize[0] / 2 - width / 2, screensize[1] / 2 - height / 2 - ui.inch2pix(0.5)))
    
    boxRoot.running = True
    boxRoot.protocol("WM_DELETE_WINDOW", quitter)

    lbl = tk.Label(boxRoot, text="Login:", justify=LEFT)  # , font=("Helvetica", 16))
    # lbl.grid(row=0, padx=10, sticky="W")
    boxRoot.grid_rowconfigure(0, weight=0)

    # First frame

    frame_1 = ttk.Frame(boxRoot, padding="0.15i")
    imager = Image.open(asset_dir + "lock2.png")
    img = PIL.ImageTk.PhotoImage(imager.resize([50, 50]))
    labelm = tk.Label(frame_1, image=img)
    labelm.image = img

    labelm.grid(row=0, padx=10, pady=10, sticky="EW", rowspan=2)

    tk.Label(frame_1, text="Username: ").grid(row=0, column=1, padx=10, sticky="W")

    link_user = ttk.Entry(frame_1)

    link_user.grid(row=0, column=2, padx=10, sticky="WE")

    link_user.focus_force()

    tk.Label(frame_1, text="Password: ").grid(row=1, column=1, padx=10, sticky="W")

    link_pass = ttk.Entry(frame_1, show="*")

    link_pass.grid(row=1, column=2, padx=10, sticky="WE")


    tk.Label(frame_1, text="SSH Private PPK Key: ").grid(row=2, column=1, padx=10, sticky="W")

    link_key = ttk.Entry(frame_1)
    link_key.grid(row=2, column=2, padx=10, sticky="WE")

    sett = iset.read()
    k_file = sett["putty"]["ssh_key"]

    if k_file != None:
        link_key.insert(0, k_file)
        

    key_b = ttk.Button(frame_1, text="...", command=browse_key, width=4)
    key_b.grid(row=2, column=3, padx=0, sticky="W")
    
    machines = []

    frame_1.grid(row=1, column=0, padx=20, sticky="SWE", columnspan=2)
    frame_1.grid_columnconfigure(2, weight=1)

    frame_3 = tk.Frame(boxRoot)  # , padding="0.15i")

    close_b = ttk.Button(frame_3, text="Cancel", command=quitter)
    close_b.grid(column=0, row=0, sticky="SW", padx=10)

    test_b = ttk.Button(frame_3, text="Login", command=login)
    test_b.grid(column=2, row=0, sticky="SE", padx=10)

    frame_3.grid(row=3, column=0, padx=20, pady=20, sticky="SWE", columnspan=2)

    frame_3.grid_columnconfigure(2, weight=1)

    frame_3.grid_columnconfigure(1, weight=1)

    frame_3.grid_columnconfigure(0, weight=1)

    boxRoot.grid_rowconfigure(1, weight=0)
    boxRoot.grid_rowconfigure(2, weight=1)

    boxRoot.grid_rowconfigure(3, weight=0)

    boxRoot.bind("<Return>", login)
    boxRoot.grid_columnconfigure(0, weight=1)
    boxRoot.deiconify()
    boxRoot.wm_attributes("-topmost", 1)

    while True:
        # draw(canvas, mouse=False)
        time.sleep(0.05)
        boxRoot.update()
        if boxRoot.running == False:
            break
        if creds != {}:
            return creds

def get_login_old(machine):
    global root
    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)  # , fg="red", bg="black")
        boxRoot.withdraw()
    else:
        root = tk.Tk()
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)
        boxRoot.withdraw()

    def quitter():
        boxRoot.quit()
        boxRoot.destroy()
        boxRoot.running = False
        return None

    def login(*args):
        nonlocal creds
        passw = link_pass.get()
        user = link_user.get()
        if user != "" and passw != "":
            creds = {"user": user, "pass": passw}
            boxRoot.quit()
            boxRoot.destroy()
            # boxRoot.running = False

    creds = {}

    boxRoot.title("Login to " + str(machine))
    boxRoot.iconname("Dialog")
    boxRoot.minsize(300, 120)
    boxRoot.running = True
    boxRoot.protocol("WM_DELETE_WINDOW", quitter)

    lbl = tk.Label(boxRoot, text="Login:", justify=LEFT)  # , font=("Helvetica", 16))
    # lbl.grid(row=0, padx=10, sticky="W")
    boxRoot.grid_rowconfigure(0, weight=0)

    # First frame

    frame_1 = ttk.Frame(boxRoot, padding="0.15i")
    imager = Image.open(asset_dir + "lock.png")
    # imager = imager.resize([48, 48])

    img = PIL.ImageTk.PhotoImage(imager.resize([48, 48]))
    labelm = tk.Label(frame_1, image=img)
    labelm.image = img

    labelm.grid(row=0, padx=10, pady=10, sticky="EW", rowspan=2)

    tk.Label(frame_1, text="Username: ").grid(row=0, column=1, padx=10, sticky="W")

    link_user = ttk.Entry(frame_1)

    link_user.grid(row=0, column=2, padx=10, sticky="WE")

    link_user.focus_force()

    tk.Label(frame_1, text="Password: ").grid(row=1, column=1, padx=10, sticky="W")

    link_pass = ttk.Entry(frame_1, show="*")

    link_pass.grid(row=1, column=2, padx=10, sticky="WE")

    machines = []

    frame_1.grid(row=1, column=0, padx=20, sticky="SWE", columnspan=2)
    frame_1.grid_columnconfigure(2, weight=1)

    frame_3 = tk.Frame(boxRoot)  # , padding="0.15i")

    close_b = ttk.Button(frame_3, text="Cancel", command=quitter)
    close_b.grid(column=0, row=0, sticky="SW", padx=10)

    test_b = ttk.Button(frame_3, text="Login", command=login)
    test_b.grid(column=2, row=0, sticky="SE", padx=10)

    frame_3.grid(row=2, column=0, padx=20, pady=20, sticky="SWE", columnspan=2)

    frame_3.grid_columnconfigure(2, weight=1)

    frame_3.grid_columnconfigure(1, weight=1)

    frame_3.grid_columnconfigure(0, weight=1)

    boxRoot.grid_rowconfigure(1, weight=0)
    boxRoot.grid_rowconfigure(2, weight=1)

    boxRoot.grid_rowconfigure(3, weight=0)

    boxRoot.bind("<Return>", login)
    boxRoot.grid_columnconfigure(0, weight=1)
    boxRoot.deiconify()
    boxRoot.wm_attributes("-topmost", 1)

    while True:
        # draw(canvas, mouse=False)
        time.sleep(0.05)
        boxRoot.update()
        if boxRoot.running == False:
            break
        if creds != {}:
            return creds

#from ttkbootstrap import Style
def shortcut(name=None, cmd=None, mach=None, icn=None):
    ui.set_icons(asset_dir + "Paper/")
    k = get_light()

    global root
    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)  # , fg="red", bg="black")
        boxRoot.withdraw()
    else:
        root = tk.Tk()
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)
        boxRoot.withdraw()

    def quitter():
        boxRoot.quit()
        boxRoot.destroy()
        boxRoot.running = False
        # pygame.quit()
        # sys.exit()
        return None

    #style = Style(theme='superhero')#darkly')
    #boxRoot = style.master
    

    boxRoot.title("Shortcut Creator")
    boxRoot.iconname("Dialog")
    width, height = ui.inch2pix(4.3), ui.inch2pix(4)
    
    boxRoot.minsize(420, 480)
    boxRoot.minsize(width, height)

    boxRoot.iconbitmap(asset_dir + "icon.ico")

    
    boxRoot.running = True
    boxRoot.protocol("WM_DELETE_WINDOW", quitter)

    boxRoot.geometry('+%d+%d' % (screensize[0] / 2 - width / 2, screensize[1] / 2 - height / 2 - ui.inch2pix(0.5)))

    lbl = tk.Label(boxRoot, text="Create a Start Menu Shortcut:", justify=CENTER)  # , font=("Helvetica", 16))
    lbl.grid(row=0, padx=10, pady=10, sticky="EW")
    boxRoot.grid_rowconfigure(0, weight=0)
    

    def test():
        nonlocal machine
        try:
            machine = machine_chooser.get()
        except:
            pass

        command = link_command.get()
        if link_label.get() != "" and command != "":
            spawn_n_run(machine, command, mode_chooser.get(), clip_chooser.get(), GTK_chooser.get(),
                        QT_chooser.get(), append_chooser.get(), theme=color_chooser.get(), root=root_chooser.get(),
                        dbus=dbus_chooser.get(), keep=kill_chooser.get())

    def create():
        nonlocal machine
        try:
            machine = machine_chooser.get()
        except:
            pass

        command = link_command.get()
        if link_label.get() != "" and command != "":
            # --r --wsl_machine="Ubuntu-20.04" --wsl_cmd="gedit" --w_mode="Default" --clip_enabled="Default"
            #   --gtk_scale=1 --qt_scale=1 --append=""
            if append_chooser.get() == "None":
                append = ""
            else:
                append = append_chooser.get()
            command = '--r --wsl_machine="' + str(machine) + '" --wsl_cmd="' + command + '" --w_mode="' + str(
                mode_chooser.get()) + '" --clip_enabled="' + str(clip_chooser.get())
            command += '" --gtk_scale="' + str(GTK_chooser.get()) + '" --qt_scale="' + str(
                QT_chooser.get()) + '" --append="' + str(append) + '"'
            t = color_chooser.get()
            if t == "Follow Windows":
                command += ' --theme="follow"'
            elif t == "Light Mode":
                command += ' --theme="light"'
            elif t == "Dark Mode":
                command += ' --theme="dark"'

            command += ' --root="' + root_chooser.get().lower() + '"'

            command += ' --dbus="' + dbus_chooser.get().lower() + '"'

            command += ' --keep="' + kill_chooser.get().lower() + '"'

            imager.save(app_path + "\\" + str(link_label.get()) + ".ico",
                        sizes=[(24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (255, 255)])
            if root_chooser.get() == "False":
                create_shortcut(command, link_label.get() + " on " + str(machine.replace("-", " ")),
                                app_path + "\\" + str(link_label.get()) + ".ico")
            else:
                create_shortcut(command, "(root) " + link_label.get() + " on " + str(machine.replace("-", " ")),
                                app_path + "\\" + str(link_label.get()) + ".ico")
            quitter()

    def reseticon():
        nonlocal imager
        imager = Image.open(asset_dir + "link.png")
        image2 = imager.resize([48, 48], resample=PIL.Image.ANTIALIAS)
        img = PIL.ImageTk.PhotoImage(image2)
        labelm.configure(image=img)
        labelm.image = img

    # First frame

    frame_1 = ttk.Frame(boxRoot, padding="0.15i")
    imager = Image.open(asset_dir + "link2.png")
    # imager = imager.resize([48, 48])

    img = PIL.ImageTk.PhotoImage(imager.resize([48, 48]))
    labelm = tk.Label(frame_1, image=img)
    labelm.image = img

    if icn != None:
        imager = ui.icon(icn.lower())
        image2 = imager.resize([48, 48], resample=PIL.Image.ANTIALIAS)
        img = PIL.ImageTk.PhotoImage(image2)
        labelm.configure(image=img)
        labelm.image = img
    labelm.grid(row=0, padx=10, pady=10, sticky="EW", rowspan=2)

    tk.Label(frame_1, text="Shortcut Label: ").grid(row=0, column=1, padx=10, sticky="W")

    link_label = ttk.Entry(frame_1)
    if name != None:
        link_label.insert(0, name)
    link_label.grid(row=0, column=2, padx=10, sticky="WE")

    link_label.focus_force()

    tk.Label(frame_1, text="Shortcut Command: ").grid(row=1, column=1, padx=10, sticky="W")

    link_command = ttk.Entry(frame_1)
    if name != None:
        link_command.insert(0, cmd)
    link_command.grid(row=1, column=2, padx=10, sticky="WE")

    tk.Label(frame_1, text="Run In: ").grid(row=2, column=1, padx=10, pady=7, sticky="W")

    machines = os.popen("wsl.exe -l -q").read()
    machines = re.sub(r'[^a-zA-Z0-9./\n-]', r'', machines).splitlines()
    machines[:] = (value for value in machines if value != "")

    if len(machines) == 23:
        machines = []
    sett = iset.read()

    avoid = sett["distro_blacklist"]
    docker_blacklist = []
    for i in machines:
        for a in avoid:
            if str(a).lower() in str(i).lower():
                docker_blacklist.append(i)

    for i in docker_blacklist:
        machines.remove(i)

    if mach == None:
        if len(machines) > 1:
            # animator.animate("start", [0, 0])
            machine_chooser = ttk.Combobox(frame_1, values=machines, state="readonly")
            machine_chooser.current(0)
            machine_chooser.grid(row=2, column=2, padx=10, sticky="WE")
        elif len(machines) == 1:
            # animator.animate("start", [0, 0])
            machine_chooser = ttk.Label(frame_1, text=machines[0])
            machine = machines[0]
            machine_chooser.grid(row=2, column=2, padx=10, sticky="WE")
        else:
            pymsgbox.alert(text='No WSL Distros Found', title='Please Install a WSL Distro', button='OK')
            quitter()
            return None
    else:
        machine_chooser = ttk.Label(frame_1, text=mach)
        machine = mach
        machine_chooser.grid(row=2, column=2, padx=10, sticky="WE")

    reset_b = ttk.Button(frame_1, text="Reset Icon", command=reseticon)

    reset_b.grid(row=3, column=1, padx=10, pady=0, sticky="EW", rowspan=1)

    help_b = ttk.Button(frame_1, text="Help", command=help_short)

    help_b.grid(row=3, column=2, padx=10, pady=0, sticky="W", rowspan=1)

    frame_1.grid_columnconfigure(2, weight=1)

    frame_1.grid(row=1, column=0, padx=20, pady=0, sticky="NEW")

    frame_2 = cpane(frame_1, "Less Options", "More Options")

    tk.Label(frame_2.frame, text="Display Mode: ").grid(row=0, column=0, pady=7, sticky="WN")

    mode_chooser = ttk.Combobox(frame_2.frame, values=["Default", "Multi Window", "Single Window", "Fullscreen"],
                                state="readonly")
    mode_chooser.current(0)
    mode_chooser.grid(row=0, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="GTK Scale Mode: ").grid(row=1, column=0, pady=7, sticky="WN")
    GTK_chooser = ttk.Combobox(frame_2.frame, values=["Default", "1", "2", "3"], state="readonly")
    GTK_chooser.current(0)
    GTK_chooser.grid(row=1, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="QT Scale Mode: ").grid(row=2, column=0, pady=7, sticky="WN")
    QT_chooser = ttk.Combobox(frame_2.frame, values=["Default", "1", "2", "3"], state="readonly")
    QT_chooser.current(0)
    QT_chooser.grid(row=2, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="Shared Clipboard: ").grid(row=3, column=0, pady=7, sticky="WN")
    clip_chooser = ttk.Combobox(frame_2.frame, values=["Default", "Enabled", "Disabled"], state="readonly")
    clip_chooser.current(0)
    clip_chooser.grid(row=3, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="Color Mode: ").grid(row=4, column=0, pady=7, sticky="WN")
    color_chooser = ttk.Combobox(frame_2.frame, values=["Follow Windows", "Light Mode", "Dark Mode"], state="readonly")
    color_chooser.current(0)
    color_chooser.grid(row=4, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text='Run As Root:').grid(row=5, column=0, pady=7, sticky="WN")
    root_chooser = ttk.Combobox(frame_2.frame, values=["True", "False"], state="readonly")
    root_chooser.current(1)
    root_chooser.grid(row=5, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text='Experimental Features:').grid(row=6, column=0, pady=7, sticky="WN")

    tk.Label(frame_2.frame, text='Use DBus (Sudo Required):').grid(row=7, column=0, pady=7, sticky="WN")
    dbus_chooser = ttk.Combobox(frame_2.frame, values=["True", "False"], state="readonly")
    dbus_chooser.current(1)
    dbus_chooser.grid(row=7, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text='Experimental Flags:').grid(row=8, column=0, pady=7, sticky="WN")
    append_chooser = ttk.Combobox(frame_2.frame, values=["None", "--zoom=2", "--scale=2"], state="readonly")
    append_chooser.current(0)
    append_chooser.grid(row=8, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="Keep XServer Instance:").grid(row=9, column=0, pady=7, sticky="WN")
    kill_chooser = ttk.Combobox(frame_2.frame, values=["True", "False"], state="readonly")
    kill_chooser.current(1)
    kill_chooser.grid(row=9, column=1, padx=10, sticky="WE")

    frame_2.grid(row=4, column=1, padx=10, pady=10, sticky="WE", columnspan=2)

    frame_2.grid_columnconfigure(1, weight=1)

    frame_3 = tk.Frame(boxRoot)  # , padding="0.15i")

    close_b = ttk.Button(frame_3, text="Close", command=quitter)
    close_b.grid(column=0, row=0, sticky="SW", padx=10)

    save_b = ttk.Button(frame_3, text="Add to Start Menu", command=create)
    save_b.grid(column=1, row=0, sticky="SWE", padx=10)

    test_b = ttk.Button(frame_3, text="Test Configuration", command=test)
    test_b.grid(column=2, row=0, sticky="SE", padx=10, ipadx=5)

    frame_3.grid(row=2, column=0, padx=20, pady=20, sticky="SWE", columnspan=2)

    frame_3.grid_columnconfigure(2, weight=1)

    frame_3.grid_columnconfigure(1, weight=1)

    frame_3.grid_columnconfigure(0, weight=1)

    boxRoot.grid_rowconfigure(1, weight=0)
    boxRoot.grid_rowconfigure(2, weight=1)

    boxRoot.grid_rowconfigure(3, weight=0)

    boxRoot.grid_columnconfigure(0, weight=1)
    boxRoot.deiconify()
    boxRoot.wm_attributes("-topmost", 1)

    old = link_label.get()
    new = old
    icon = None
    while True:
        # draw(canvas, mouse=False)
        time.sleep(0.05)
        boxRoot.update()
        if boxRoot.running == False:
            break

        old = new
        new = link_label.get()
        if old != new:
            imager = ui.icon(new.lower(), spec=new.lower())
            image2 = imager.resize([48, 48], resample=PIL.Image.ANTIALIAS)
            img = PIL.ImageTk.PhotoImage(image2)
            labelm.configure(image=img)
            labelm.image = img
        if mach == None:
            if len(machines) > 1:
                machine = machine_chooser.get()
            else:
                machine = machines[0]
        else:
            machine = mach

    # imager.save("test.ico", sizes=[(24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (255, 255)])



def putty():
    global root
    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)  # , fg="red", bg="black")
        boxRoot.withdraw()
    else:
        root = tk.Tk()
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)
        boxRoot.withdraw()

    def quitter():
        boxRoot.quit()
        boxRoot.destroy()
        boxRoot.running = False
        return None

    hwnd2 = boxRoot.winfo_id()


    # win32gui.SetWindowLong(hwnd2, win32con.GWL_EXSTYLE,
    #                       win32gui.GetWindowLong(hwnd2, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    # win32gui.SetLayeredWindowAttributes(hwnd2, win32api.RGB(*(255, 0, 0)), 0, win32con.LWA_COLORKEY)

    # blur.blur(hwnd2)

    boxRoot.title("Graphical SSH Manager")
    boxRoot.iconname("Dialog")
    width, height = ui.inch2pix(5.2), ui.inch2pix(1.7)
    
    boxRoot.minsize(width, height)
    boxRoot.running = True
    boxRoot.protocol("WM_DELETE_WINDOW", quitter)

    boxRoot.iconbitmap(asset_dir + "icon.ico")
    boxRoot.geometry('+%d+%d' % (screensize[0] / 2 - width / 2, screensize[1] / 2 - height / 2 - ui.inch2pix(0.5)))

    lbl = tk.Label(boxRoot, text="Graphical SSH Tools:", justify=CENTER)  # , font=("Helvetica", 16))
    lbl.grid(row=0, padx=10, pady=10, sticky="EW")
    boxRoot.grid_rowconfigure(0, weight=0)

    def test():
        ip_config = ip.get()
        if ip_config != "":
            boxRoot.withdraw()
            creds = get_login(ip_config)
            boxRoot.deiconify()
            if creds == None:
                return False
            sett = iset.read()
            sett["putty"]["ip"] = ip.get()
            iset.set(sett)
            
            password = creds["pass"]

            user = creds["user"]

            key_file = creds["key"]
            
            port_str = "-P"
            por = "22"
            if port.get() != "":
                port_str = f"-P"
                por = str(port.get())

            commander = ["PUTTY/GWSL_putty.exe", "-ssh", f"{user}@{ip.get()}", port_str, por, "-pw", f"{password}", "-X"]

            if key_file != "":
                commander.append("-i")
                commander.append(f'"{key_file}"')
                
            prog = cmd(command=commander,
                       console=True)
            quitter()

    def create():
        sett = iset.read()
        sett["putty"]["ip"] = ip.get()
        iset.set(sett)

        if ip.get() != "":
            porter = port.get()
            if porter == "":
                porter = 22
            command = f'--r --ssh --ip="{ip.get()}:{porter}" --command="open_putty"'
            
            print(command)
            create_shortcut(command, "Graphical SSH on " + ip.get() + " port " + porter, asset_dir + "computer.ico")
            quitter()

    # First frame

    frame_1 = ttk.Frame(boxRoot, padding="0.1i")
    imager = Image.open(asset_dir + "network2.png")
    # imager = imager.resize([48, 48])

    img = PIL.ImageTk.PhotoImage(imager.resize([50, 50]))
    labelm = tk.Label(frame_1, image=img)
    labelm.image = img

    labelm.grid(row=0, padx=10, pady=0, sticky="EW", rowspan=2)

    tk.Label(frame_1, text="Remote IP: ").grid(row=0, column=1, padx=10, rowspan=2, sticky="W")

    ip = ttk.Entry(frame_1)

    port = ConstrainedEntry(frame_1, width=5)
    port.insert(0, 22)
    
    
    sett = iset.read()
    save_ip = sett["putty"]["ip"]
    if save_ip != None:
        ip.insert(0, save_ip)
        if ":" in str(save_ip):
            port_n = save_ip[save_ip.index(":") + 1:]
            port.delete(0,"end")
            port.insert(0, port_n)
            ip.delete(0,"end")
            ip.insert(0, save_ip[:save_ip.index(":")])

    # iset.set(sett)

    ip.grid(row=0, column=2, padx=10, rowspan=2, sticky="WE")
    port.grid(row=0, column=4, padx=10, rowspan=2, columnspan=1, sticky="W")

    ip.focus_force()

    frame_1.grid_columnconfigure(2, weight=1)
    

    frame_1.grid(row=1, column=0, padx=20, pady=0, sticky="NEW")

    frame_3 = tk.Frame(boxRoot)  # , padding="0.15i")

    close_b = ttk.Button(frame_3, text="Close", command=quitter)
    close_b.grid(column=0, row=0, sticky="SW", padx=10)

    save_b = ttk.Button(frame_3, text="Add to Start Menu", command=create)
    save_b.grid(column=1, row=0, sticky="SWE", padx=10, ipadx=5)

    save_b = ttk.Button(frame_3, text="Help", command=help_ssh)
    save_b.grid(column=2, row=0, sticky="WE", padx=10)

    test_b = ttk.Button(frame_3, text="Connect to Machine", command=test)
    test_b.grid(column=3, row=0, sticky="SE", padx=10, ipadx=5)

    frame_3.grid(row=2, column=0, padx=20, pady=20, sticky="SWE", columnspan=2)

    frame_3.grid_columnconfigure(2, weight=1)

    frame_3.grid_columnconfigure(1, weight=1)

    frame_3.grid_columnconfigure(0, weight=1)

    boxRoot.grid_rowconfigure(1, weight=0)
    boxRoot.grid_rowconfigure(2, weight=1)

    boxRoot.grid_rowconfigure(3, weight=0)

    boxRoot.grid_columnconfigure(0, weight=1)

    boxRoot.deiconify()
    boxRoot.wm_attributes("-topmost", 1)

    while True:
        # draw(canvas, mouse=False)
        time.sleep(0.05)
        boxRoot.update()
        if boxRoot.running == False:
            break


def get_running(process):
    proc_list = os.popen('tasklist').readlines()
    for proc in proc_list:
        if process in proc:
            return True
    return False


def update_running():
    global running, service_loaded, white, light, accent
    if get_running("GWSL_service") == False:
        try:
            subprocess.Popen('GWSL_service.exe')
            service_loaded = True
        except Exception as e:
            logger.exception("Cannot start service...")
            if debug == True:
                print("Can't run service...")
            service_loaded = "bad"
    else:
        service_loaded = True

    while True:
        time.sleep(2)
        # if get_running("GWSL_service") == True:
        #    running = True
        # else:
        #    running = False
        get_system_light()

        accent = ui.get_color()
        if light == True:
            for i in range(3):
                if accent[i] > 50:
                    accent[i] -= 50


last = 0
heartbeat = time.perf_counter()

colores = [[255, 0, 0],
        [154, 59, 180],
        [1, 142, 253],
        [249, 179, 26],
        [184, 150, 9],
        [6, 141, 155],
        [255, 0, 0],
        [214, 125, 241],
        [249, 34, 181],
        [227, 188, 12],
        [167, 47, 230],
        [124, 97, 232],
        [71, 21, 248],
        [157, 29, 141],
        [40, 235, 52],
        [253, 57, 204],
        [1, 246, 192],
        [48, 75, 202],
        [149, 243, 64],
        [246, 180, 61],
        [40, 100, 11],
        [83, 219, 37],
        [228, 122, 43],
        [234, 26, 136],
        [10, 213, 2],
        [105, 217, 11],
        [106, 215, 231],
        [233, 116, 30],
        [158, 250, 221],
        [233, 26, 38],
        [210, 21, 229]]

def browse_wsl():
    machine = choose_machine()
    if machine != None:
        v = subprocess.getoutput(rf'wsl -d {machine} echo "hi"')
        subprocess.Popen(rf'explorer.exe "\\wsl$\{machine}"', shell=True)# + str(machine))

def shells():
    machine = choose_machine()
    if machine != None:
        sett = iset.read()
        shell_ui = sett["general"]["shell_gui"]
        if shell_ui == "cmd":
            subprocess.Popen("wsl.exe ~ -d " + str(machine))
        else:
            subprocess.Popen(f'wt -p "{machine}"')

def draw(canvas, mouse=False):
    global mask, light_source, heartbeat, lumen_opac, wait, running, ter, about_open, loading_angle, loader, last, show_ad, pad
    # mask.fill([255, 0, 0])
    canvas.fill([0, 0, 0, 0])
    
    

    # print(time.perf_counter() - heartbeat)
    if time.perf_counter() - heartbeat > 1:
        heartbeat = time.perf_counter()
        animator.animate("donate", random.choice(colores))

    # print(accent)
    launch = animator.get("start")[0] / 100.0
    hover = mouse
    if mouse == False:
        hover = pygame.mouse.get_pos()
    #fade = False
    #pad = 10
    #print(int(HEIGHT * launch))
    if animator.get("start")[0] < 100 and animator.get("start")[0] > 0:
        #print("1")
        #print(screensize[1] - taskbar - (HEIGHT * launch) - pad)
        if acrylic == False:
            canvas.blit(back, [-1 * (screensize[0] - WIDTH), -1 * (screensize[1] - taskbar - int(HEIGHT * launch))])

            
        if pos_config == "bottom":
            win32gui.MoveWindow(HWND, winpos - padx, screensize[1] - taskbar - int(HEIGHT * launch) - pad, WIDTH, HEIGHT, 1)
        elif pos_config == "top":
            win32gui.MoveWindow(HWND, winpos - padx, taskbar - HEIGHT + int(HEIGHT * launch) + pad, WIDTH, HEIGHT, 1)
        elif pos_config == "right":
            win32gui.MoveWindow(HWND, winpos - taskbar + WIDTH - int(WIDTH * launch) - padx, screensize[1] - HEIGHT - pad, WIDTH,
                                HEIGHT, 1)
        elif pos_config == "left":
            win32gui.MoveWindow(HWND, taskbar - WIDTH + int(WIDTH * launch) + padx, screensize[1] - HEIGHT - pad, WIDTH, HEIGHT, 1)
        lumen_opac = 0

        if fade == False:
            animator.pop("start2", [100, 0])
        win32gui.SetLayeredWindowAttributes(HWND, win32api.RGB(*fuchsia), int(launch * 255), win32con.LWA_ALPHA)
        #else:
            #win32gui.SetLayeredWindowAttributes(HWND, win32api.RGB(*fuchsia), int(255), win32con.LWA_ALPHA)
            #animator.pop("start2", [100, 0])

    else:
        if about_open == True:
            about_open = False
            about()
        if show_ad == True:
            show_ad = False
            announce()

        #print(screensize[1] - taskbar - int(HEIGHT) - pad)
        if acrylic == False:
            canvas.blit(back, [-1 * (screensize[0] - WIDTH), -1 * (screensize[1] - taskbar - int(HEIGHT))])
        if pos_config == "bottom":
            win32gui.MoveWindow(HWND, winpos - padx, screensize[1] - taskbar - int(HEIGHT) - pad, WIDTH, HEIGHT, True)
        elif pos_config == "top":
            win32gui.MoveWindow(HWND, winpos - padx, taskbar + pad, WIDTH, HEIGHT, 1)
        elif pos_config == "right":
            win32gui.MoveWindow(HWND, winpos - taskbar - padx, screensize[1] - HEIGHT - pad, WIDTH, HEIGHT, 1)
        elif pos_config == "left":
            win32gui.MoveWindow(HWND, taskbar + pad, screensize[1] - HEIGHT - padx, WIDTH, HEIGHT, 1)
        #if fade == True:
            
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), int(launch * 255), win32con.LWA_ALPHA)
        #else:
        #    win32gui.SetLayeredWindowAttributes(HWND, win32api.RGB(*fuchsia), int(255), win32con.LWA_ALPHA)
        
        #win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*[100, 100, 100]), int(100), win32con.LWA_COLORKEY)#ALPHA)

        #win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, winpos, screensize[1] - taskbar - int(HEIGHT), WIDTH, HEIGHT, win32con.SWP_NOMOVE | win32con.SWP_SHOWWINDOW)

        #win32.

    if animator.get("start")[0] >= 98:
        animator.animate("start2", [100, 0])
        if service_loaded == True:
            animator.animate("loading", [100, 0])
        

        

    if acrylic == False:
        ui.iris2(canvas, [0, 0],
                 [WIDTH, HEIGHT],
                 #False, radius=30, shadow_enabled=False, resolution=50, alpha=int(255))
                 False, radius=20, shadow_enabled=False, resolution=10, alpha=int(255))

    #pygame.draw.circle(canvas, [100, 100, 100], [100, 100], 50)

    
    # print(canvas.get_at([0, 0]))

    launch = animator.get("start2")[0] / 100.0

    

    if animator.get("start2")[0] > 99 and service_loaded == False:
        animator.animate("loading", [0, 0])
        animator.animate("announce", [100, 0])
        #raise_windows()
        
    
    top_height = ui.inch2pix(2)

    l_h = ui.inch2pix(0.9) + int(20 * (1 - launch))
    padd = ui.inch2pix(0.15)

    # pygame.draw.circle(canvas, [255, 0, 0, 255], [100, 100], 50)

    # Draw light/dark accent for readability
    #light = False
    if light == False:
        pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, 100])

        #if fade == True:
        pygame.gfxdraw.line(canvas, padd, l_h, WIDTH - padd, l_h, [180, 180, 180, int(80 * launch)])

    else:
        #pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [255, 255, 255, 200]) pre win11
        pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [255, 255, 255, 180])
        #pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0, 50])

        pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, 80])
        pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, 80])

        #if fade == True:
        pygame.gfxdraw.line(canvas, padd, l_h, WIDTH - padd, l_h, [0, 0, 0, int(80 * launch)])
    
    # canvas.fill(fuchsia)

    icon_font = ui.font(ico_font, int(ui.inch2pix(0.4)))

    sett = icon_font.render(icons["laptop"], True, white)
    sett.set_alpha(int(launch * 255))
    canvas.blit(sett, [ui.inch2pix(0.3), ui.inch2pix(0.28) + (1 - launch) * ui.inch2pix(0.1)])

    icon_font = ui.font(ico_font, int(ui.inch2pix(0.4)))

    title_font = ui.font(default_font, int(ui.inch2pix(0.17)))
    title_font.bold = False
    title_font.italic = False

    if service_loaded != "bad":
        if running == False:
            txt = title_font.render(_("GWSL Dashboard"), True, white)
        else:
            txt = title_font.render(_("X Running On localhost : 0.0"), True, white)
    else:
        txt = title_font.render(_("Error. Please Check Logs"), True, white)

    txt.set_alpha(int(launch * 255))
    canvas.blit(txt, [ui.inch2pix(1), ui.inch2pix(0.35) + (1 - launch) * ui.inch2pix(0.1)])

    # canvas.blit(txt, [ui.inch2pix(0.5), ui.inch2pix(0.35) + (1 - launch) * ui.inch2pix(0.1)])

    title_font = ui.font(default_font, int(ui.inch2pix(0.17)))

    """
    if mouse != False:
        if mouse[1] > ui.inch2pix(0.9) and mouse[1] < ui.inch2pix(0.9) + ui.inch2pix(0.3):
            if mouse[0] > ui.inch2pix(0.83) + display.get_width() and mouse[0] < ui.inch2pix(0.83) + display.get_width() + sett.get_width():
                print("stop/start")
                if running == True:
                    subprocess.getoutput('taskkill /F /IM GWSL_service.exe')
                    subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
                    running = False
                elif running == False:
                    subprocess.Popen(bundle_dir + '\\GWSL_service.exe', shell=True)
                    running = True
            elif running == True and mouse[0] > ui.inch2pix(0.93) + display.get_width() + ui.inch2pix(0.4) and mouse[0] < ui.inch2pix(0.93) + display.get_width() + ui.inch2pix(0.4) + reset.get_width():
                subprocess.getoutput('taskkill /F /IM GWSL_service.exe')
                subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
                time.sleep(1)
                subprocess.Popen(bundle_dir + '\\GWSL_service.exe', shell=True)
    """
    """
    title_font = ui.font(default_font, int(ui.inch2pix(0.21)))
    title_font.bold = False
    txt = title_font.render("Window  Display  Mode:", True, white)
    txt.set_alpha(int(launch * 255))
    canvas.blit(txt, [ui.inch2pix(4) + display.get_width(), ui.inch2pix(0.6)])


    title_font = ui.font(default_font, int(ui.inch2pix(0.2)))
    title_font.italic = True
    title_font.bold = True
    multi = title_font.render("Multi", True, white)
    multi.set_alpha(int(launch * 255))
    canvas.blit(multi, [ui.inch2pix(4) + display.get_width(), ui.inch2pix(0.9)])
    title_font.bold = False
    single = title_font.render("Single", True, white)
    single.set_alpha(int(launch * 255))
    canvas.blit(single, [ui.inch2pix(4) + display.get_width() + multi.get_width() + ui.inch2pix(0.06), ui.inch2pix(0.9)])
    title_font.bold = False
    full = title_font.render("Fullscreen", True, white)
    full.set_alpha(int(launch * 255))
    canvas.blit(full, [ui.inch2pix(4) + display.get_width() + multi.get_width() + single.get_width() + ui.inch2pix(0.12), ui.inch2pix(0.9)])
    """
    # title_font = ui.font(default_font, int(ui.inch2pix(0.21)))
    # title_font.bold = False
    # title_font.italic = False
    # txt = title_font.render("Actions:", True, white)
    # canvas.blit(txt, [ui.inch2pix(0.65), ui.inch2pix(2)])

    title_font = ui.font(default_font, int(ui.inch2pix(0.17)))
    title_font.bold = False
    # title_font.italic = True

    # pygame.gfxdraw.box(canvas, [ui.inch2pix(0.67), ui.inch2pix(2.5), ui.inch2pix(1.2),
    #   ui.inch2pix(1.2)], [0, 0, 0, 100])

    icon_font = ui.font(ico_font, int(ui.inch2pix(0.33)))
    box = ui.inch2pix(0.7)

    start = ui.inch2pix(1.0)
    s = ui.inch2pix(0.25)

    def setter():
        machine = choose_machine()
        if machine != None:
            configure_machine(machine)
            # settings(machine)

    def short():
        shortcut()

    
                

    def apper():
        machine = choose_machine()
        if machine != None:
            app_launcher(machine)

    def donate():
        webbrowser.get('windows-default').open('https://opticos.github.io/gwsl/#donate')
        # https://sites.google.com/bartimee.com/opticos-studios/donate')

    def wsl_installer():
        webbrowser.get('windows-default').open("https://docs.microsoft.com/en-us/windows/wsl/install-win10")

    def wsl_updater():
        webbrowser.get('windows-default').open(
            "https://support.microsoft.com/en-us/help/4028685/windows-10-get-the-update")

    def discorder():
        webbrowser.get('windows-default').open("https://discord.com/invite/VkvNgkH")

    


    heart = icons["heart"]
    if installed == True:
        buttons = [[_("GWSL Distro Tools"), icons["settings"], setter],
                   [_("Shortcut Creator"), icons["link"], short],
                   [_("Linux Apps"), icons["app_list"], apper],
                   [_("Linux Files"), icons["folder"], browse_wsl],
                   [_("Linux Shell"), icons["shell"], shells],
                   [_("Graphical SSH Connection"), icons["network"], putty],
                   #[_("More Apps"), icons["network"], putty],
                   [_("Donate With PayPal etc."), icons["heart"], donate]]
    else:
        buttons = [[_("Graphical SSH Connection"), icons["network"], putty],
                   [_("Install WSL for More Features"), icons["question"], wsl_installer],
                   #[_("Get Help on Discord."), icons["discord"], discorder],
                   [_("Donate With PayPal etc."), icons["heart"], donate]]  # 

    selected = False
    q = 0
    s2 = False

    for i in buttons:
        s2 = False
        pos = [ui.inch2pix(0.4), start + (1 - launch) * s]
        if hover[0] > ui.inch2pix(0.1) and hover[0] < WIDTH - ui.inch2pix(0.1):
            if hover[1] > pos[1] + ui.inch2pix(0.1) and hover[1] < pos[1] + ui.inch2pix(0.3) + ui.inch2pix(0.3):
                if mouse != False:
                    #animator.pop("donate", [255, 0, 0])
                    #animator.pop("select", [0, 0])
                    i[2]()
                selected = True
                s2 = True
                last = q

        # square(canvas, [ui.inch2pix(0.1), pos[1]], [WIDTH - ui.inch2pix(0.1) * 2,
        #                                                             ui.inch2pix(0.3) + ui.inch2pix(0.4)], width=2,
        #                                                             filled = True, color=accent + [int(launch * 100)])

        s3 = animator.get("select")[0] / 100
        # selected
        sett = icon_font.render(i[1], True, white)
        txt = title_font.render(i[0], True, white)

        if i[1] == heart and donate_asker == True:
            colo = animator.get("donate")
            try:
                sett = icon_font.render(i[1], True, colo)
                txt = title_font.render(i[0], True, colo)
            except:
                colo = [255, 0, 0]
                sett = icon_font.render(i[1], True, colo)
                txt = title_font.render(i[0], True, colo)

        if s2 == True or q == last:
            txt.set_alpha(int(launch * 255 * (1 - s3)))
            sett.set_alpha(int(launch * 255 * (1 - s3)))
        else:
            txt.set_alpha(int(launch * 255))
            sett.set_alpha(int(launch * 255))

        modern_offset = 0
        if modern == True:
            modern_offset = -1 * ui.inch2pix(0.01)
            
        canvas.blit(sett, [pos[0], pos[1] + box / 2 - sett.get_height() / 2 + modern_offset])
        canvas.blit(txt, [pos[0] + sett.get_width() + ui.inch2pix(0.2),
                          pos[1] + box / 2 - txt.get_height() / 2 - ui.inch2pix(0.025)])

        # unselected
        if s2 == True or q == last:
            sett = icon_font.render(i[1], True, accent)
            sett.set_alpha(int(launch * 255 * s3))
            canvas.blit(sett, [pos[0], pos[1] + box / 2 - sett.get_height() / 2 + modern_offset])
            txt = title_font.render(i[0], True, accent)
            txt.set_alpha(int(launch * 255 * s3))
            canvas.blit(txt, [pos[0] + sett.get_width() + ui.inch2pix(0.2),
                              pos[1] + box / 2 - txt.get_height() / 2 - ui.inch2pix(0.025)])

        # square(mask, [ui.inch2pix(0.1), pos[1]], [WIDTH - ui.inch2pix(0.1) * 2,
        #                                                            ui.inch2pix(0.3) + ui.inch2pix(0.4)], width=2)


        start += ui.inch2pix(0.22) + ui.inch2pix(0.5) - ui.inch2pix(0.15) #last used to be 0.15
        s += ui.inch2pix(0.17) #used to be 0.17
        q += 1

    # logo.set_alpha(int(launch * 200))
    # canvas.blit(logo, [WIDTH - logo.get_width() - ui.inch2pix(2), HEIGHT - ui.inch2pix(1.15) + (1 - launch) * 20])
    title_font = ui.font(default_font, int(ui.inch2pix(0.17)))
    title_font.bold = False
    title_font.italic = False

    # txt = title_font.render("GWSL Dashboard", True, white)
    # txt.set_alpha(int(launch * 200))
    # canvas.blit(txt, [WIDTH - ui.inch2pix(1.8), HEIGHT - ui.inch2pix(1.15) + (1 - launch) * 40])

    # txt = title_font.render("Version 1.3", True, white)
    # txt.set_alpha(int(launch * 200))
    # canvas.blit(txt, [WIDTH - ui.inch2pix(1.5), HEIGHT - ui.inch2pix(0.85) + (1 - launch) * 50])

    # title_font.italic = True
    s = animator.get("select")[0] / 100

    txt = title_font.render(_("Help"), True, white)
    txt.set_alpha(int(launch * 255))
    canvas.blit(txt, [WIDTH - ui.inch2pix(1.3), HEIGHT - ui.inch2pix(0.5) + (1 - launch) * 60])

    # square(mask, [WIDTH - ui.inch2pix(1.35), HEIGHT - ui.inch2pix(0.55) + (1 - launch) * 60],
    #       [txt.get_width() + ui.inch2pix(0.1), txt.get_height() + ui.inch2pix(0.1)], width=2)

    if hover[0] > WIDTH - ui.inch2pix(1.35) and hover[0] < WIDTH - ui.inch2pix(1.35) + txt.get_width() + ui.inch2pix(
            0.1):
        if hover[1] > HEIGHT - ui.inch2pix(0.55) + (1 - launch) * 60 and hover[1] < HEIGHT - ui.inch2pix(0.55) + (
                1 - launch) * 60 + txt.get_height() + ui.inch2pix(0.1):
            # webbrowser.open("GWSLHELP.com")#, new=0, autoraise=True)
            if mouse != False:
                webbrowser.get('windows-default').open('https://opticos.github.io/gwsl/help.html')
            selected = True
            txt = title_font.render(_("Help"), True, accent)
            txt.set_alpha(int(launch * 255))
            #if s > 0.1:
            #    canvas.fill([0, 0, 0, 0], rect=[WIDTH - ui.inch2pix(1.3), HEIGHT - ui.inch2pix(0.5) + (1 - launch) * 60, txt.get_width(), txt.get_height()])
            txt.set_alpha(int(launch * 255 * s))
            canvas.blit(txt, [WIDTH - ui.inch2pix(1.3), HEIGHT - ui.inch2pix(0.5) + (1 - launch) * 60])
            last = 100

    txt = title_font.render(_("About"), True, white)
    txt.set_alpha(int(launch * 255))
    canvas.blit(txt, [WIDTH - ui.inch2pix(0.7), HEIGHT - ui.inch2pix(0.5) + (1 - launch) * 80])

    # square(mask, [WIDTH - ui.inch2pix(0.8), HEIGHT - ui.inch2pix(0.55) + (1 - launch) * 60],
    #       [txt.get_width() + ui.inch2pix(0.17), txt.get_height() + ui.inch2pix(0.1)], width=2)

    if hover[0] > WIDTH - ui.inch2pix(0.8) and hover[0] < WIDTH - ui.inch2pix(0.8) + txt.get_width() + ui.inch2pix(
            0.17):
        if hover[1] > HEIGHT - ui.inch2pix(0.55) + (1 - launch) * 60 and hover[1] < HEIGHT - ui.inch2pix(0.55) + (
                1 - launch) * 60 + txt.get_height() + ui.inch2pix(0.1):
            if mouse != False:
                about()
            selected = True
            last = 100
            txt = title_font.render(_("About"), True, accent)
            txt.set_alpha(int(launch * 255 * s))

            #txt.set_alpha(int(launch * 255 * s))
            canvas.blit(txt, [WIDTH - ui.inch2pix(0.7), HEIGHT - ui.inch2pix(0.5) + (1 - launch) * 80])

    if selected == True:
        animator.animate("select", [100, 0])
    else:
        animator.animate("select", [0, 0])
        # lumen_opac = 0

    # pay.set_alpha(int(launch * 200))
    # canvas.blit(pay, [ui.inch2pix(0.15), HEIGHT - ui.inch2pix(0.25) - pay.get_height() + (1 - launch) * 20])

    title_font.italic = True
    txt = title_font.render(_("Donate"), True, [240, 240, 240])
    txt.set_alpha(int(launch * 220))
    # canvas.blit(txt, [ui.inch2pix(0.2), HEIGHT - pay.get_height() - txt.get_height() - ui.inch2pix(0.3) + (1 - launch) * 80])

    # pygame.gfxdraw.polygon(mask, [[0, 0],
    #                               [WIDTH - 1, 0],
    #                               [WIDTH - 1, HEIGHT - 1],
    #                               [0, HEIGHT - 1]], [0, 255, 0])
    # draw(canvas)

    # edit mask
    
    # if service_loaded == False:
    #    lumen_opac = 0

    # canvas.blit(lumen, [0, 0])

    title_font.italic = False

    if service_loaded == False:
        txt2 = title_font.render(_("Starting Service"), True, white)
    elif service_loaded == "bad":
        txt2 = title_font.render(_("Error Starting Service"), True, white)
        loading_angle = 0
        icon_font = ui.font(ico_font, int(ui.inch2pix(0.22)))  # 0.19
        loader = icon_font.render(icons["error"], True, white)

    else:
        txt2 = title_font.render(_("Starting Service"), True, white)

    v2 = 1 - (animator.get("loading")[0] / 100)
    v = animator.get("start")[0] / 100

    txt2.set_alpha(int(v * int(v2 * 255)))
    canvas.blit(txt2, [ui.inch2pix(0.55),
                       HEIGHT - txt2.get_height() / 2 - int((v2 - 1) * ui.inch2pix(0.6)) - ui.inch2pix(0.39)])

    if service_loaded != "bad":
        txt2 = pygame.transform.rotozoom(loader, loading_angle, 0.22)
    else:
        txt2 = loader

    txt2.set_alpha(int(v * int(v2 * 255)))
    canvas.blit(txt2, [ui.inch2pix(0.35) - txt2.get_width() / 2,
                       HEIGHT - ui.inch2pix(0.38) - txt2.get_height() / 2 - int((v2 - 1) * ui.inch2pix(0.4))])

    #announce = animator.get("announce")[0] / 100

    #sur = pygame.Surface([WIDTH, HEIGHT], pygame.SRCALPHA)
    #pygame.gfxdraw.filled_circle(sur, int(WIDTH / 2), int(HEIGHT / 2), int(announce * (HEIGHT * 0.5)), [0, 0, 0] + [int(240 * announce)])

    #canvas.blit(sur, [0, 0], special_flags=(pygame.BLEND_ALPHA_SDL2))

    # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0, int(((animator.get("darken")[0] / 100)) * 200)])
    py_root.fill([0, 0, 0, 255])
    py_root.blit(canvas, [0, 0], special_flags=(pygame.BLEND_RGBA_ADD))
    fpsClock.tick(60)
    animator.update()
    


def square(mask, pos, size, width=1, filled=False, color=False):
    if color == False:
        if filled == False:
            pygame.draw.polygon(mask, [0, 255, 0], [pos,
                                                    [pos[0] + size[0], pos[1]],
                                                    [pos[0] + size[0], pos[1] + size[1]],
                                                    [pos[0], pos[1] + size[1]]], width)
        elif filled == True:
            pygame.gfxdraw.filled_polygon(mask, [pos,
                                                 [pos[0] + size[0], pos[1]],
                                                 [pos[0] + size[0], pos[1] + size[1]],
                                                 [pos[0], pos[1] + size[1]]], [0, 255, 0])
    else:
        if filled == False:
            pygame.gfxdraw.polygon(mask, [pos,
                                          [pos[0] + size[0], pos[1]],
                                          [pos[0] + size[0], pos[1] + size[1]],
                                          [pos[0], pos[1] + size[1]]], color)
        elif filled == True:
            pygame.gfxdraw.filled_polygon(mask, [pos,
                                                 [pos[0] + size[0], pos[1]],
                                                 [pos[0] + size[0], pos[1] + size[1]],
                                                 [pos[0], pos[1] + size[1]]], color)


# `print("hmmm", args)


if "--r" not in args:
    class cpane(ttk.Frame):
        def __init__(self, MainWindow, expanded_text, collapsed_text):
            ttk.Frame.__init__(self, MainWindow)
            # The class variable
            self.MainWindow = MainWindow
            self._expanded_text = expanded_text
            self._collapsed_text = collapsed_text
            # Weight=1 to grow it's size as needed
            # self.columnconfigure(0, weight=0)
            self.columnconfigure(1, weight=1)

            self._variable = tk.IntVar()
            # Creating Checkbutton
            self._button = ttk.Checkbutton(self, variable=self._variable,
                                           command=self._activate, style="TButton")
            self._button.grid(row=0, column=0, ipadx=5)
            # Create a Horizontal line
            # self._separator = ttk.Separator(self, orient="horizontal")
            # self._separator.grid(row=0, column=1, sticky="we")
            self.frame = ttk.Frame(self)
            # Activate the class
            self._activate()

        def _activate(self):
            if not self._variable.get():
                # Remove this widget when button pressed.
                self.frame.grid_forget()
                # Show collapsed text
                self._button.configure(text=self._collapsed_text)
            elif self._variable.get():
                # Increase the frame area as needed
                self.frame.grid(row=1, column=0, columnspan=2, sticky="WE")
                self.columnconfigure(1, weight=1)
                self._button.configure(text=self._expanded_text)

        def toggle(self):
            self._variable.set(not self._variable.get())
            self._activate()
            
    class PlaceholderEntry(ttk.Entry):
        def __init__(self, container, placeholder, *args, **kwargs):
            super().__init__(container, *args, style="Placeholder.TEntry", **kwargs)
            self.placeholder = placeholder
            

            self.insert("0", self.placeholder)
            self.bind("<FocusIn>", self._clear_placeholder)
            self.bind("<FocusOut>", self._add_placeholder)

        def _clear_placeholder(self, e):
                if self["style"] == "Placeholder.TEntry":
                    self.delete("0", "end")
                    self["style"] = "TEntry"

        def _add_placeholder(self, e):
                if not self.get():
                    self.insert("0", self.placeholder)
                    self["style"] = "Placeholder.TEntry"
                    
    class ConstrainedEntry(ttk.Entry):
        def __init__(self, *args, **kwargs):
            ttk.Entry.__init__(self, *args, **kwargs)

            vcmd = (self.register(self.on_validate),"%P")
            self.configure(validate="key", validatecommand=vcmd)

        def disallow(self):
            self.bell()

        def on_validate(self, new_value):
            try:
                if new_value.strip() == "": return True
                value = int(new_value)
                if value < 0 or value > 99999:
                    self.disallow()
                    return False
            except ValueError:
                self.disallow()
                return False

            return True

if "--r" not in args: # start normally
    running = True
    service_loaded = False
    updater = threading.Thread(target=update_running)
    updater.daemon = True
    updater.start()
    about_open = False

    read = ""
    from shutil import which

    if which("wsl.exe") != None:
        installed = True
    else:
        installed = False

    # print("Starting GUI")
    if "--about" in args:
        about_open = True
    if True:  # installed == True:
        animator = anima.animator(fpsClock)
        animator.register("start", [1, 0])
        animator.register("start2", [0, 0])
        animator.animate("start", [100, 0])
        animator.register("darken", [0, 0])
        animator.register("choose", [0, 0])
        animator.register("apps", [100, 0])
        animator.register("loading", [100, 0])
        animator.register("select", [0, 0])

        animator.register("announce", [0, 0])

        
        wait = 0
        loading_angle = 0
        icon_font = ui.font(ico_font, int(ui.inch2pix(1)))  # 0.19
        loader = icon_font.render(icons["refresh"], True, white)

        day = time.localtime().tm_wday
        # if day in dd:
        donate_asker = True
        animator.register("donate", [255, 0, 0])
        # else:
        #   donate_asker = False

        if updated == True:
            #os.popen("control /name Microsoft.WindowsFirewall /page pageConfigureApps")
            ch = pymsgbox.confirm(text=_(f'GWSL was just updated to version {version}. \
                            Sometimes after an update, GWSL firewall access is reset,\
                            This is the most likely cause of issues after an update.\
                            If GWSL does not work, re-allow it through the firewall with: \
                            "GWSL Dashboard --> About --> Allow GWSL through the Firewall" \
                            You can also ensure firewall access is enabled from here with "Check Now".'),
                             title=_('GWSL Updated Message'), buttons=["Ok", "Check Now"])
            if ch == "Check Now":
                os.popen("control /name Microsoft.WindowsFirewall /page pageConfigureApps")
                pymsgbox.confirm(text=_('GWSL needs access through the Windows Firewall \
                                to communicate with WSL version 2. Please allow public access to "GWSL_vcxsrv.exe", \
                                "GWSL_vcxsrv_lowdpi.exe", and "pulseaudio.exe" for audio. You will need Admin Priviledges to do this.'),
                                 title=_('Allow GWSL Firewall Access'), buttons=["Ok"])
        while True:
            try:
                loading_angle -= 10
                if win32gui.GetFocus() != HWND:
                    if animator.get("start")[0] == 100:
                        animator.animate("start", [0, 0])
                        animator.animate("start2", [0, 0])
                if animator.get("start")[0] <= 0:
                    pygame.quit()
                    time.sleep(1)
                    sys.exit()
                for event in pygame.event.get():
                    if event.type == QUIT:
                        # subprocess.getoutput('taskkill /F /IM GWSL_service.exe')
                        # subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
                        pygame.quit()
                        sys.exit()
                    elif event.type == MOUSEBUTTONUP:
                        #print(event.button)
                        if event.button == 1:
                            draw(canvas, mouse=event.pos)

                    elif event.type == VIDEORESIZE:
                        WIDTH, HEIGHT = event.size
                        if WIDTH < ui.inch2pix(7.9):
                            WIDTH = ui.inch2pix(7.9)
                        if HEIGHT < ui.inch2pix(5):
                            HEIGHT = ui.inch2pix(5)

                        canvas = pygame.display.set_mode([WIDTH, HEIGHT], RESIZABLE)
                        # ui.set_size([WIDTH, HEIGHT])
                        # mini = pygame.image.load(bak).convert()
                        mini = pygame.transform.smoothscale(mini1,
                                                            [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])

                        back = mini.copy()
                        back = pygame.transform.scale(back, [WIDTH, HEIGHT])
                        ui.iris2(back, [0, 0],
                                 [WIDTH, HEIGHT],
                                 [0, 0, 0], radius=10, shadow_enabled=False, resolution=50)

                        
                        mini = pygame.transform.smoothscale(mini,
                                                            [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                        lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                        # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                        # mask.fill([255, 0, 0])

                draw(canvas)
                pygame.display.update()

            except Exception as e:
                logger.exception("Exception occurred - Error in Mainloop")

    else:
        choice = pymsgbox.confirm(text="WSL is not configured. Please install it and get some distros.",
                                  title="Cannot Find WSL!",
                                  buttons=["Ok", "Online Help"])
        if choice == "Online Help":
            webbrowser.get('windows-default').open(
                "https://docs.microsoft.com/en-us/learn/modules/get-started-with-windows-subsystem-for-linux/2-enable-and-install")

elif args[1] == "--r" and "--startup" in args: # startup
    try:
        print("started")
        if get_running("GWSL_service") != True:
            try:
                subprocess.Popen('GWSL_service.exe')
            except Exception as e:
                logger.exception("Startup Mode. Cannot start service...")
                print("Can't run service...")

    except Exception as e:
        logger.exception("Exception occurred")

elif args[1] == "--r" and "--ssh" not in args: # launch a shortcut
    try:
        print("started")
        themer = "Follow Windows"
        rooter = "False"
        dbuser = "False"
        keeper = "False"
        # python manager.py --r --wsl_machine="Ubuntu-20.04" --wsl_cmd="gedit" --w_mode="multi"
        #   --clip_enabled="true" --gtk_scale=1 --qt_scale=1 --append="--zoom=1"
        for arg in args[2:]:
            if "--wsl_machine" in arg:
                machine = arg[14:]

            elif "--wsl_cmd" in arg:
                command = arg[10:]

            elif "--w_mode" in arg:
                mode = arg[9:]

            elif "--clip_enabled" in arg:
                clipboard = arg[15:]
                if clipboard == "Enabled":
                    clipboard = "Enabled"
                elif clipboard == "Default":
                    pass
                else:
                    clipboard = "Disabled"

            elif "--gtk_scale" in arg:
                gtk = arg[12:]

            elif "--qt_scale" in arg:
                qt = arg[11:]

            elif "--append" in arg:
                append = arg[9:]
            elif "--theme" in arg:
                t = arg[8:]
                if t == "follow":
                    themer = "Follow Windows"
                elif t == "light":
                    themer = "Light Mode"
                elif t == "dark":
                    themer = "Dark Mode"
            elif "--root" in arg:
                t = arg[7:]
                if t == "true":
                    rooter = "True"
                else:
                    rooter = "False"

            elif "--dbus" in arg:
                t = arg[7:]
                if t == "true":
                    dbuser = "True"
                else:
                    dbuser = "False"
            elif "--keep" in arg:
                t = arg[7:]
                if t == "true":
                    keeper = "True"
                else:
                    keeper = "False"

        if get_running("GWSL_service") != True:
            try:
                subprocess.Popen('GWSL_service.exe')
                time.sleep(0.5)
            except Exception as e:
                logger.exception("Exception occurred - Cannot Start Service")
                print("Can't run service...")

        #print("keep", keeper)
        machines = os.popen("wsl.exe -l -q").read()  # lines()
        machines = re.sub(r'[^a-zA-Z0-9./\n-]', r'', machines).splitlines()
        machines[:] = (value for value in machines if value != "")

        if machine not in machines:
            choice = pymsgbox.confirm(
                text='Hmmm... The WSL machine ' + str(machine) + " does not exist. You can delete this shortcut.",
                title='Cannot Find Machine: ' + str(machine),
                buttons=["Ok"])
        else:
            try:
                spawn_n_run(machine, command, mode, clipboard, gtk, qt, append, cmd=True, theme=themer, root=rooter,
                            dbus=dbuser, keep=keeper)
            except Exception as e:
                logger.exception("Exception occurred - bad shortcut")
            """
            except:
                choice = pymsgbox.confirm(
                    text='Hmmm... This shortcut does not seem to work. Try deleting it and making a new one.',
                    title='Bad Shortcut',
                    buttons=["Ok"])
            """
    except Exception as e:
        logger.exception("Exception occurred - bad shortcut 2")


elif args[1] == "--r" and "--ssh" in args:
    try:
        print("started")
        ip = None
        user = None
        command = None
        password = None
        rooter = "false"
        # python manager.py --r --wsl_machine="Ubuntu-20.04" --wsl_cmd="gedit" --w_mode="multi" --clip_enabled="true"
        #   --gtk_scale=1 --qt_scale=1 --append="--zoom=1"
        for arg in args[3:]:
            if "--ip" in arg:
                ip = arg[5:]
            elif "--user" in arg:
                user = arg[7:]
            elif "--pass" in arg:
                password = arg[7:]
            elif "--command" in arg:
                command = arg[10:]
            elif "--root" in arg:
                rooter = arg[7:]

        creds = get_login(ip)

        password = creds["pass"]

        user = creds["user"]

        key_file = creds["key"]

        if get_running("GWSL_service") != True:
            try:
                subprocess.Popen('GWSL_service.exe')
            except Exception as e:
                logger.exception("Exception occurred - Cannot start service")
                print("Can't run service...")

        timer = time.perf_counter()
        if command != "open_putty": #this is obsolete I think...
            
            if ":" in ip:
                port = ip[ip.index(":") + 1:]
                ip = ip[:ip.index(":")]

            port_str = "-P"
            por = "22"
            if port != "":
                port_str = f"-P"
                por = str(port)

            
            commander = ["PUTTY/GWSL_putty.exe", "-ssh", f"{user}@{ip}", port_str, por, "-pw", f"{password}", "-X"]

            if key_file != "":
                commander.append("-i")
                commander.append(f'"{key_file}"')
                
            commander.append("-batch")
            #print(commander)
            
            prog = cmd(command=commander)

            if rooter == "true":
                prog.run(
                    'echo "' + password + '" | sudo -H -S ' + f"xauth add $(xauth -f ~{user}/.Xauthority list | tail -1)")

                prog.run('echo "' + password + '" | sudo -H -S ' + command, wait=True, ident=command)
            else:
                prog.run(command=command, wait=True, ident=command)
            ignore = False
            waiter = 5
            while prog.error == False:  # prog.done == False:
                time.sleep(5)
                """
                if prog.done == True:
                    if time.perf_counter() - timer < waiter:
                        ignore = True
                        print("ignoring early quit")
                if ignore == False and prog.done == True:
                    if time.perf_counter() - timer > waiter:
                        prog.kill()
                        sys.exit()
                else:
                    pass
                """
        else:
            if ":" in ip:
                port = ip[ip.index(":") + 1:]
                ip = ip[:ip.index(":")]

            port_str = "-P"
            por = "22"
            if port != "":
                port_str = f"-P"
                por = str(port)

            
            commander = ["PUTTY/GWSL_putty.exe", "-ssh", f"{user}@{ip}", port_str, por, "-pw", f"{password}", "-X"]

            if key_file != "":
                commander.append("-i")
                commander.append(f'"{key_file}"')
                
            prog = cmd(command=commander,
                       console=True)

    except Exception as e:
        logger.exception("Exception occurred - SSH mode failure")
    except KeyboardInterrupt:
        try:
            prog.kill()
            print("killing service")
        except:
            pass

