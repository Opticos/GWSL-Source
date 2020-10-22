# GWSL Dashboard *lets do this again*

# Copyright Paul-E/Opticos Studios 2020
# https://www.opticos.studio


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


import logging
import os
import random
import subprocess
import threading
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
from winreg import *

import PIL
import PIL.ImageTk
import display as display
import pymsgbox
import win32api
import win32con
import win32gui
import winshell
from PIL import Image
from win32com.client import Dispatch

import iset
from exe_layer import Cmd

BUILD_MODE = "WIN32"  # MSIX or WIN32

version = "1.3.6"

args = sys.argv

frozen = "not"
if getattr(sys, "frozen", False):
    # we are running in a bundle
    frozen = "ever so"
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
print("we are", frozen, "frozen")
print("bundle dir is", bundle_dir)
print("sys.argv[0] is", sys.argv[0])
print("sys.executable is", sys.executable)
print("os.getcwd is", os.getcwd())

asset_dir = bundle_dir + "\\assets\\"

app_path = os.getenv("APPDATA") + "\\GWSL\\"

if os.path.isdir(app_path) == False:
    # os.mkdir(app_path)
    print(subprocess.getoutput('mkdir "' + app_path + '"'))
    print("creating appdata directory")

logger = logging.getLogger(__name__)
# Create handlers
f_handler = logging.FileHandler(app_path + "dashboard.log")
f_handler.setLevel(logging.ERROR)

f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(f_handler)

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
            if sett["conf_ver"] >= 3:
                print("Settings up to date")
            else:
                print("Updating settings")
                iset.create(app_path + "\\settings.json")

    # Get the script ready
    import wsl_tools as tools

    if os.path.exists(app_path + "GWSL_helper.sh") == False:
        # print("Moving helper script")
        print(
            subprocess.getoutput(
                'copy "'
                + bundle_dir
                + r"\\assets\GWSL_helper.sh"
                + '" "'
                + app_path
                + '"'
            )
        )
    else:
        # make sure the script is up to date
        scr = open(app_path + "GWSL_helper.sh", "r")
        lines = scr.read()
        if "v2" in lines:
            print("Script is up to date")
        else:
            print("Updating Script")
            print(
                subprocess.getoutput(
                    'copy "'
                    + bundle_dir
                    + r"\\assets\GWSL_helper.sh"
                    + '" "'
                    + app_path
                    + '"'
                )
            )

    if os.path.exists(app_path + "Licenses.txt") == False:
        # print("Moving Licenses")
        print(
            subprocess.getoutput(
                'copy "'
                + bundle_dir
                + r"\\assets\Licenses.txt"
                + '" "'
                + app_path
                + '"'
            )
        )
except Exception as e:
    logger.exception("Exception occurred")
    sys.exit()

tools.script = app_path + "\\GWSL_helper.sh"

try:
    import ctypes
    import platform

    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
except Exception as e:
    logger.exception("Exception occurred")

root = tk.Tk()
root.withdraw()

if "--r" not in args:
    os.environ["PBR_VERSION"] = "4.0.2"
    from tendo import singleton

    try:
        instance = singleton.SingleInstance()
    except singleton.SingleInstanceException:
        print("quit")
        try:
            import win32gui

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
            logger.exception("Exception occurred")

        sys.exit()
    except PermissionError:
        print("quit")
        try:
            import win32gui

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
            logger.exception("Exception occurred")
            pass

        sys.exit()

    try:

        # DISPLAY ones
        import OpticUI as ui

        import pygame
        import webbrowser

        import animator as anima

        from pygame.locals import *

        t = time.perf_counter()
        import pygame.gfxdraw

        ui.init("dpi", tk, root)
        from ctypes import wintypes, windll

        if int(platform.release()) >= 8:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)

        from win32api import GetMonitorInfo, MonitorFromPoint
        from pathlib import Path

        monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
        monitor_area = monitor_info.get("Monitor")
        work_area = monitor_info.get("Work")
        taskbar = int(monitor_area[3] - work_area[3])

        ui.set_scale(1)
        pygame.init()

        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        WIDTH, HEIGHT = ui.inch2pix(3.8), ui.inch2pix(
            5.7
        )  # ui.inch2pix(7.9), ui.inch2pix(5)

        sett = iset.read()
        side = sett["general"]["position"]
        if side == "left":
            winpos = 0  # screensize[0] - WIDTH
        else:
            winpos = screensize[0] - WIDTH

        os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (
            winpos,
            screensize[1],
        )  # screensize[1] - taskbar)

        py_root = pygame.display.set_mode([WIDTH, HEIGHT], NOFRAME)

        HWND = pygame.display.get_wm_info()["window"]
        # win32gui.MoveWindow(HWND, screensize[0] - WIDTH, screensize[1] - taskbar - HEIGHT, WIDTH, HEIGHT, True)

        canvas = pygame.Surface([WIDTH, HEIGHT])  # , pygame.SRCALPHA)

        ui.set_size([WIDTH, HEIGHT])
        pygame.display.set_caption("GWSL Dashboard")
        ui.start_graphics(pygame, asset_dir)
        ico = pygame.image.load(asset_dir + "icon.png").convert_alpha()
        pygame.display.set_icon(ico)
        fpsClock = pygame.time.Clock()
        default_font = asset_dir + "segoeui.ttf"
        lumen_opac = 6
        # light_source = pygame.image.load(asset_dir + "lumens/7.png").convert_alpha()
        ico_font = asset_dir + "SEGMDL2.TTF"
        # lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
        # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
        # mask.fill([255, 0, 0])
        # pay = pygame.image.load(asset_dir + "paypal.png").convert_alpha()
        # pay = pygame.transform.smoothscale(pay, [ui.inch2pix(1), int((pay.get_height() / pay.get_width()) * ui.inch2pix(1))])
        # try:
        #    mini1 = pygame.image.load(os.getenv('APPDATA') + r"\Microsoft\Windows\Themes\TranscodedWallpaper").convert()
        # except:
        #    bak = asset_dir + random.choice(["1", "2", "3"]) + ".jpg"
        #    mini1 = pygame.image.load(bak).convert()
        back = pygame.Surface([WIDTH, HEIGHT])  # mini1.copy()

        def get_pos():
            rect = win32gui.GetWindowRect(HWND)
            return [int(rect[0]), int(rect[1])]

        poser = get_pos()
        back = pygame.transform.scale(back, screensize)

        accent = ui.get_color()

        registry = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(
            registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        key_value = QueryValueEx(key, "SystemUsesLightTheme")
        k = int(key_value[0])
        light = False
        white = [255, 255, 255]
        if k == 1:
            light = True
            white = [0, 0, 0]
            for i in range(3):
                if accent[i] > 50:
                    accent[i] -= 50

        fuchsia = [12, 222, 123]

        # Set window transparency color
        hwnd = HWND

        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED,
        )

        # win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
        import blur

        blur.blur(HWND)

    except Exception as e:
        logger.exception("Exception occurred")


def get_version(machine):
    try:
        machines = os.popen("wsl.exe -l -v").read()  # lines()
        machines = re.sub(r"[^a-zA-Z0-9./\n-]", r"", machines).splitlines()
        if "VERSION" in machines[0]:
            machines = machines[2:]
            machines[:] = (value for value in machines if value != "")
            for i in machines:
                if machine in i:
                    return int(i[-1])
        else:
            return 1
    except BaseException:
        return 1


def reboot(machine):
    os.popen("wsl.exe -t " + str(machine))
    time.sleep(1)
    os.popen("wsl.exe -d " + str(machine))


def helper(topic):
    if topic == "machine chooser":
        url = "the-gwsl-user-interface"
    elif topic == "configure":
        url = "configuring-a-wsl-distro-for-use-with-gwsl"
    elif topic == "theme":
        url = "configuring-a-wsl-distro-for-use-with-gwsl"
    elif topic == "launcher":
        url = "using-the-integrated-linux-app-launcher"
    webbrowser.get("windows-default").open(
        "https://opticos.github.io/gwsl/tutorials/manual.html#" + str(url)
    )


def help_short():
    webbrowser.get("windows-default").open(
        "https://opticos.github.io/gwsl/tutorials/manual.html#using-the-gwsl-shortcut-creator"
    )


def help_ssh():
    webbrowser.get("windows-default").open(
        "https://opticos.github.io/gwsl/tutorials/manual.html#using-gwsl-with-ssh"
    )


def runs(distro, command):
    subprocess.Popen(
        "wsl.exe ~ -d "
        + str(distro)
        + " . ~/.profile;nohup /bin/sh -c "
        + '"'
        + str(command)
        + '&"',
        shell=True,
    )  # .readlines()
    return None


def run(distro, command):
    out = subprocess.getoutput(
        "wsl.exe ~ -d "
        + str(distro)
        + " . ~/.profile;nohup /bin/sh -c "
        + '"'
        + str(command)
        + ' &"'
    )  # .readlines()
    return out


def runo3(distro, command):
    out = subprocess.getoutput(
        "wsl.exe ~ -d "
        + str(distro)
        + " . ~/.profile;/bin/sh -c "
        + '"'
        + str(command)
        + '"'
    )  # .readlines()
    return out


def runo2(distro, command):
    cmd = "wsl.exe -d " + str(distro) + " " + "/bin/sh -c " + '"' + str(command) + '"'
    out = os.popen(cmd).readlines()
    return out


def runo(distro, command):
    cmd = "wsl.exe -d " + str(distro) + " /bin/sh -c " + '"' + str(command) + '"'
    out = os.popen(cmd).readlines()
    return out


def get_ip(machine):
    return runo3(
        machine,
        """echo $(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit;}')""",
    )  # [0][:-1]


def choose_machine():
    global selected, canvas, WIDTH, HEIGHT, mini, back, lumen, mask
    machines = os.popen("wsl.exe -l -q").read()  # lines()
    machines = re.sub(r"[^a-zA-Z0-9./\n-]", r"", machines).splitlines()
    machines[:] = (value for value in machines if value != "")

    sett = iset.read()

    avoid = sett["distro_blacklist"]
    docker_blacklist = []
    for i in machines:
        for a in avoid:
            if a.lower() in i.lower():
                docker_blacklist.append(i)

    for i in docker_blacklist:
        machines.remove(i)

    if len(machines) == 1:
        return machines[0]
    elif len(machines) > 7:
        return pymsgbox.confirm(
            text="Select a WSL Machine", title="Choose WSL Machine", buttons=machines
        )

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
                ui.iris2(
                    back,
                    [0, 0],
                    [WIDTH, HEIGHT],
                    [0, 0, 0],
                    radius=10,
                    shadow_enabled=False,
                    resolution=50,
                )
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(
                    mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)]
                )

                b = pygame.Surface([WIDTH, HEIGHT])
                draw(b)
                lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask.fill([255, 0, 0])

        canvas.blit(b, [0, 0])

        v = animator.get("choose")[0] / 100

        # canvas.fill([0, 0, 0, int((1 - v) * 255)])
        ui.iris2(
            canvas,
            [0, 0],
            [WIDTH, HEIGHT],
            False,
            radius=10,
            shadow_enabled=False,
            resolution=30,
            alpha=int(v * 255),
        )

        if not light:
            pygame.gfxdraw.rectangle(
                canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, 100]
            )
        else:
            pygame.gfxdraw.rectangle(
                canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, 80]
            )
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, 80])

        # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0] + [int(v * 180)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))
        if len(machines) != 0:
            txt = title_font.render("Choose A WSL Distro:", True, white)
        else:
            txt = title_font.render("No WSL Distros Installed.", True, white)

        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * v),
            ],
        )

        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        txt = title_font.render("?", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH - txt.get_width() - ui.inch2pix(0.3),
                ui.inch2pix(0.2) - int(ui.inch2pix(0.1) * (1 - v)),
            ],
        )
        hover = pygame.mouse.get_pos()
        if hover[0] > WIDTH - txt.get_width() - ui.inch2pix(0.4) and hover[
            0
        ] < WIDTH - ui.inch2pix(0.1):
            if hover[1] > ui.inch2pix(0.1) and hover[1] < ui.inch2pix(
                0.3
            ) + txt.get_height() - int(ui.inch2pix(0.1) * (1 - v)):
                if mouse:
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

                if hover[0] > (WIDTH / 2) - (txt.get_width() / 2) - ui.inch2pix(
                    0.2
                ) and hover[0] < (WIDTH / 2) - (
                    txt.get_width() / 2
                ) + txt.get_width() + ui.inch2pix(
                    0.2
                ):
                    if hover[1] > h - ui.inch2pix(0.1) - int(v * d) + 1 and hover[
                        1
                    ] < h + txt.get_height() + ui.inch2pix(0.1) - int(v * d):
                        if mouse:
                            machine = i
                            animator.animate("choose", [0, 0])
                        selected = True
                        s2 = True

                s = animator.get("select")[0] / 100

                if not s2:
                    txt.set_alpha(int(v * 255))
                else:
                    txt.set_alpha(int((1 - s) * v * 255))

                canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, h - int(v * d)])
                if s2:
                    txt = title_font.render(ni, True, accent)
                    txt.set_alpha(int(s * v * 255))
                    canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, h - int(v * d)])

                h += ui.inch2pix(0.3) + txt.get_height()
                d += ui.inch2pix(0.1)

        if selected:
            animator.animate("select", [100, 0])
        else:
            animator.animate("select", [0, 0])

        txt = title_font.render("Cancel", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                HEIGHT - ui.inch2pix(0.2) - txt.get_height() - int(v * d),
            ],
        )
        if mouse:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0
            ] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT - ui.inch2pix(
                    0.2
                ) - txt.get_height() - ui.inch2pix(0.1) - int(v * d) and mouse[
                    1
                ] < HEIGHT - ui.inch2pix(
                    0.2
                ) - txt.get_height() + txt.get_height() + ui.inch2pix(
                    0.1
                ) - int(
                    v * d
                ):
                    machine = None
                    animator.animate("choose", [0, 0])

        fpsClock.tick(60)
        animator.update()

        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=pygame.BLEND_RGBA_ADD)

        pygame.display.update()
        if machine and animator.get("choose")[0] <= 1:
            return machine


def about():
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
                ui.iris2(
                    back,
                    [0, 0],
                    [WIDTH, HEIGHT],
                    [0, 0, 0],
                    radius=10,
                    shadow_enabled=False,
                    resolution=50,
                )
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(
                    mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)]
                )

                b = pygame.Surface([WIDTH, HEIGHT])
                draw(b)
                lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask.fill([255, 0, 0])

        canvas.blit(b, [0, 0])

        v = animator.get("choose")[0] / 100

        ui.iris2(
            canvas,
            [0, 0],
            [WIDTH, HEIGHT],
            [0, 0, 0],
            radius=10,
            shadow_enabled=False,
            resolution=30,
            alpha=int(v * 255),
        )

        if not light:
            pygame.gfxdraw.rectangle(
                canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, 100]
            )
        else:
            pygame.gfxdraw.rectangle(
                canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, 80]
            )
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, 80])

        # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0] + [int(v * 180)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))
        txt = title_font.render("About GWSL", True, white)

        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * v),
            ],
        )

        d = ui.inch2pix(0.2)
        h = ui.inch2pix(0.8) + txt.get_height() + ui.inch2pix(0)
        title_font = ui.font(default_font, int(ui.inch2pix(0.17)))
        title_font.italic = False

        machines = [
            "GWSL Version " + str(version),
            "© Copyright Paul-E/Opticos Studios 2020",
            "GWSL Uses:",
            "Python - Pyinstaller - SDL",
            "VCXSRV - Putty - Pillow",
            "Tcl/Tk - Paper Icon Pack",
            "Pymsgbox - OpticUI - Infi.Systray",
            "Visit Opticos Studios Website",
            "View Licenses",
        ]

        if BUILD_MODE == "WIN32":
            machines[0] = "GWSL Version " + str(version) + " (win32)"
        else:
            machines[0] = "GWSL Version " + str(version) + " (store)"

        if len(machines) != 0:
            for i in machines:
                if i == "View Licenses" or i == "Visit Opticos Studios Website":
                    txt = title_font.render(i, True, accent)  # [0, 120, 250])
                else:
                    txt = title_font.render(i, True, white)
                txt.set_alpha(int(v * 255))
                canvas.blit(txt, [WIDTH / 2 - txt.get_width() / 2, h - int(v * d)])
                if mouse:
                    if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(
                        0.2
                    ) and mouse[
                        0
                    ] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(
                        0.2
                    ):
                        if mouse[1] > h - ui.inch2pix(0.1) - int(v * d) and mouse[
                            1
                        ] < h + txt.get_height() + ui.inch2pix(0.1) - int(v * d):
                            if i == "View Licenses":
                                os.popen(app_path + "Licenses.txt")
                            elif i == "Visit Opticos Studios Website":
                                webbrowser.get("windows-default").open(
                                    "http://opticos.studio"
                                )

                h += ui.inch2pix(0.3) + txt.get_height()
                d += ui.inch2pix(0.1)

        txt = title_font.render("Cancel", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                HEIGHT - ui.inch2pix(0.4) - txt.get_height() - int((v - 1) * d),
            ],
        )
        if mouse:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0
            ] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT - ui.inch2pix(0.4) - txt.get_height() - int(
                    (v - 1) * d
                ) and mouse[1] < HEIGHT - ui.inch2pix(0.4) - txt.get_height() - int(
                    (v - 1) * d
                ) + txt.get_height() + ui.inch2pix(
                    0.1
                ):
                    machine = None
                    animator.animate("choose", [0, 0])

        fpsClock.tick(60)
        animator.update()
        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=pygame.BLEND_RGBA_ADD)

        pygame.display.update()
        if machine is None and animator.get("choose")[0] <= 1:
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
    loading = True
    loading_angle = 0
    icon_font = ui.font(ico_font, int(ui.inch2pix(1)))  # 0.19
    loader = icon_font.render("", True, white)
    them = "Default"
    themes = []

    def get():
        nonlocal q_button, g_button, QT, GTK, x_configured, loading, themes, them
        profile = tools.profile(machine)

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

        if "#GWSL_EXPORT_DISPLAY" in profile:
            x_configured = True

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
        except BaseException:
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
                if not loading:
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
                ui.iris2(
                    back,
                    [0, 0],
                    [WIDTH, HEIGHT],
                    [0, 0, 0],
                    radius=10,
                    shadow_enabled=False,
                    resolution=50,
                )
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(
                    mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)]
                )

                b = pygame.Surface([WIDTH, HEIGHT])
                draw(b)
                lumen = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                # mask.fill([255, 0, 0])

        canvas.blit(b, [0, 0])

        v = animator.get("choose")[0] / 100

        ui.iris2(
            canvas,
            [0, 0],
            [WIDTH, HEIGHT],
            [0, 0, 0],
            radius=10,
            shadow_enabled=False,
            resolution=30,
            alpha=int(v * 255),
        )

        if not light:
            pygame.gfxdraw.rectangle(
                canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, 100]
            )
        else:
            pygame.gfxdraw.rectangle(
                canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, 80]
            )
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, 80])

        # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0] + [int(v * 180)])

        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))

        ni = str(machine)[0].upper() + str(machine)[1:]
        ni = ni.replace("-", " ")

        txt = title_font.render("Configure " + str(ni), True, white)

        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * v),
            ],
        )
        # WIDTH / 2 - txt.get_width() / 2 + ui.inch2pix(0.1)
        w = ui.inch2pix(0.5)
        d = ui.inch2pix(0.2)
        h = ui.inch2pix(0.8) + txt.get_height() + ui.inch2pix(0.25)
        icon_font = ui.font(ico_font, int(ui.inch2pix(0.19)))

        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        txt = title_font.render("?", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH - txt.get_width() - ui.inch2pix(0.3),
                ui.inch2pix(0.2) - int(ui.inch2pix(0.1) * (1 - v)),
            ],
        )
        hover = pygame.mouse.get_pos()
        if hover[0] > WIDTH - txt.get_width() - ui.inch2pix(0.4) and hover[
            0
        ] < WIDTH - ui.inch2pix(0.1):
            if hover[1] > ui.inch2pix(0.1) and hover[1] < ui.inch2pix(
                0.3
            ) + txt.get_height() - int(ui.inch2pix(0.1) * (1 - v)):
                if mouse:
                    helper("configure")

        # title_font.bold = True

        def confx():
            nonlocal rebooter, x_configured, machine
            # if x_configured == False:

            # if ver == 1:
            # WSL1
            tools.export(machine)  # , 1)
            # elif ver == 2:
            #    #WSL2
            #    tools.export(machine, 2)

            x_configured = True
            restart = pymsgbox.confirm(
                text="Restart " + machine + " To Apply Changes?",
                title="Restart Machine?",
                buttons=["Yes", "No"],
            )
            if restart == "Yes":
                reboot(machine)
                rebooter = True
                machine = None

        def conf_dbus():
            code = pymsgbox.password(
                text="Enter Sudo Password For " + str(machine.replace("-", " ")) + ":",
                title="Authentication",
                mask="*",
            )
            if code is None:
                return None
            passw = 'echo "' + code + '" | sudo -H -S '
            print("Cheching DBus Install...")
            run(machine, passw + "sudo apt -y install dbus dbus-x11")
            print("Preparing Systemd...")
            run(machine, passw + "sudo systemd-machine-id-setup")
            print("Starting Bus...")
            run(machine, passw + "sudo /etc/init.d/dbus start")
            ##print("Injecting into .profile")
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

            restart = pymsgbox.confirm(
                text="Restart " + machine + " To Apply Changes?",
                title="Restart Machine?",
                buttons=["Yes", "No"],
            )
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

            restart = pymsgbox.confirm(
                text="Restart " + machine + " To Apply Changes?",
                title="Restart Machine?",
                buttons=["Yes", "No"],
            )
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
                s_theme = chooser(
                    canvas, "Choose A GTK Theme:", [" Default Theme"] + themes
                )
                if s_theme is not None:

                    def th():
                        nonlocal them, s_theme
                        if s_theme != " Default Theme":
                            run(machine, """sed -i.bak '/GTK_THEME=/d' ~/.profile """)
                            run(
                                machine,
                                """echo 'export GTK_THEME="""
                                + str(s_theme)
                                + """' >> ~/.profile """,
                            )
                            them = "Default"
                            profile = tools.profile(machine)
                            pl = profile.split("\n")
                            for i in pl:
                                if "GTK_THEME=" in i:
                                    them = i[17:]

                        else:
                            run(machine, """sed -i.bak '/GTK_THEME=/d' ~/.profile """)
                            them = "Default"

                    themer = threading.Thread(target=th)
                    themer.daemon = True
                    themer.start()

        plus = ""
        minus = ""

        buttons = []
        if not x_configured:
            buttons.append(["Auto-Export Display", confx, ""])
        else:
            buttons.append(["Display Is Set To Auto-Export", confx, ""])
        if machine is not None:
            if "deb" in machine.lower() or "ubuntu" in machine.lower():
                buttons.append(["Configure DBus", conf_dbus, ""])

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
            buttons.append(["GTK Theme: " + str(them), theme, ""])
        else:
            buttons.append(["No GTK Themes Installed", theme, ""])

        buttons.append(["Reboot " + ni, reb, ""])
        click = None
        v5 = 1 - animator.get("loading_c")[0] / 100
        hover = pygame.mouse.get_pos()
        selected = False
        for i in buttons:
            s2 = False
            if not loading:
                txt = title_font.render(i[0], True, white)
                if hover[0] > w and hover[
                    0
                ] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(
                    0.2
                ):
                    if hover[1] > h - ui.inch2pix(0.1) - int(v * d) and hover[
                        1
                    ] < h + txt.get_height() + ui.inch2pix(0.1) - int(v * d):
                        if mouse:
                            click = i[1]
                        selected = True
                        s2 = True
                        # animator.animate("choose", [0, 0])

                s = animator.get("select")[0] / 100

                txt2 = icon_font.render(i[2], True, white)

                if not s2:
                    txt2.set_alpha(int(v5 * int(v * 255)))
                    txt.set_alpha(int(v5 * (int(v * 255))))
                else:
                    txt2.set_alpha(int((1 - s) * v5 * int(v * 255)))
                    txt.set_alpha(int((1 - s) * v5 * (int(v * 255))))

                canvas.blit(txt, [w + ui.inch2pix(0.4), h - int(v5 * d)])
                canvas.blit(txt2, [w, h - int(v5 * d) + ui.inch2pix(0.06)])

                if s2:
                    txt = title_font.render(i[0], True, accent)
                    txt.set_alpha(int(v5 * (int(v * 255 * s))))
                    canvas.blit(txt, [w + ui.inch2pix(0.4), h - int(v5 * d)])

                    txt2 = icon_font.render(i[2], True, accent)
                    txt2.set_alpha(int(v5 * int(v * 255 * s)))
                    canvas.blit(txt2, [w, h - int(v5 * d) + ui.inch2pix(0.06)])

            h += ui.inch2pix(0.35) + txt.get_height()
            d += ui.inch2pix(0.1)

        if selected:
            animator.animate("select", [100, 0])
        else:
            animator.animate("select", [0, 0])

        txt = title_font.render("Cancel", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                HEIGHT + ui.inch2pix(0.2) - txt.get_height() - int(v * d),
            ],
        )
        if mouse:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0
            ] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT + ui.inch2pix(0.2) - txt.get_height() - int(
                    v * d
                ) and mouse[1] < HEIGHT + ui.inch2pix(
                    0.2
                ) + txt.get_height() + ui.inch2pix(
                    0.1
                ) - int(
                    v * d
                ):
                    machine = None
                    animator.animate("choose", [0, 0])

        if loading:
            # txt2 = pygame.transform.rotozoom(loader, loading_angle, 0.22)
            # txt2.set_alpha(int(255))
            # canvas.blit(txt2, [WIDTH / 2 - txt2.get_width() / 2, HEIGHT / 2 - txt2.get_height() / 2 + ui.inch2pix(0)])
            pass
        v = animator.get("loading_c")[0] / 100
        txt2 = pygame.transform.rotozoom(loader, loading_angle, 0.22)
        txt2.set_alpha(int(v * 255))
        # canvas.blit(txt2, [ui.inch2pix(0.2) - txt2.get_width() / 2, HEIGHT - ui.inch2pix(0.3) - txt2.get_height() / 2 - int((v - 1) * ui.inch2pix(0.4))])
        canvas.blit(
            txt2,
            [
                WIDTH / 2 - txt2.get_width() / 2,
                HEIGHT / 2
                - ui.inch2pix(0.2)
                - txt2.get_height() / 2
                - int((v - 1) * ui.inch2pix(0.4)),
            ],
        )

        if click is not None:
            click()

        if rebooter:
            animator.animate("choose", [0, 0])

        fpsClock.tick(60)
        animator.update()

        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=pygame.BLEND_RGBA_ADD)

        pygame.display.update()
        if machine is None and animator.get("choose")[0] <= 1:
            return machine


def app_launcher(machine):
    global selected, canvas, WIDTH, HEIGHT, mini, back, lumen, mask
    animator.animate("choose", [100, 0])
    animator.animate("apps", [0, 0])

    b = pygame.Surface([WIDTH, HEIGHT])
    draw(b)

    apps = {}
    app_list = []
    message = ""
    alpha = {}

    def get():
        nonlocal apps, loading, list_length, app_list, message, alpha
        read = tools.get_apps(machine)
        ui.set_icons(asset_dir + "Paper/")
        apper = {}
        sett = iset.read()

        avoid = sett["app_blacklist"]
        for i in read:

            blocker = False
            name = i[0].lower() + i[1:]
            for a in avoid:
                if a.lower() in name.lower():
                    blocker = True
                    break
            if blocker:
                continue

            cmd = read[i]["cmd"]
            if " " in cmd:
                cmd = cmd.split(" ")[0]

            size = ui.inch2pix(0.4)
            ico_name = read[i]["ico"]
            if ico_name is None or "." in ico_name:
                ico_name = name

            icon = pygame.transform.smoothscale(
                ui.pygame_icon(ico_name, bundle_dir), [size, size]
            )
            apper.update({name: {"icon": icon, "cmd": cmd, "icn": ico_name}})
        apps = apper
        app_list = sorted(apps)

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
            # ui.inch2pix(0.35) + txt.get_height()
            h2 = c * (ui.inch2pix(0.35) + ui.inch2pix(0.28))

        animator.animate("apps", [100, 0])
        list_length = len(apps) * (ui.inch2pix(0.35) + ui.inch2pix(0.23))
        loading = False
        if app_list == []:
            time.sleep(0.5)
            message = "No Graphical Apps Found"
            animator.animate("apps", [0, 0])

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

    loader = icon_font.render("", True, white)
    # print(txt2.get_size())

    end = False

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
                # subprocess.getoutput('taskkill /F /IM GWSL_service.exe')
                # subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                button = event.button
                if button == 1:
                    mouse = event.pos

            elif event.type == MOUSEBUTTONDOWN:
                button = event.button
                if list_length > HEIGHT - bottom_padding - top_padding:
                    if button == 5:  # down
                        if (
                            scroll
                            > -list_length
                            + ui.inch2pix(0.5)
                            - HEIGHT
                            - bottom_padding
                            - top_padding
                        ):
                            scroll2 -= ui.inch2pix(0.5)
                    elif button == 4:  # up
                        if scroll < -ui.inch2pix(0.4):
                            scroll2 += ui.inch2pix(0.5)
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
                ui.iris2(
                    back,
                    [0, 0],
                    [WIDTH, HEIGHT],
                    [0, 0, 0],
                    radius=10,
                    shadow_enabled=False,
                    resolution=50,
                )
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(
                    mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)]
                )

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

        # WIDTH / 2 - txt.get_width() / 2 + ui.inch2pix(0.1)
        w = ui.inch2pix(0.5)
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
        icon_surf.blit(
            b,
            [0, HEIGHT - bottom_padding],
            [0, (HEIGHT - bottom_padding), WIDTH, bottom_padding],
        )

        v3 = animator.get("apps")[0] / 100
        for a in app_list:
            i = apps[a]

            if (
                h - int((v3 - 1) * d) + scroll > -1 * (ui.inch2pix(0.5))
                and h - int((v3 - 1) * d) + scroll < HEIGHT
            ):

                txt = title_font.render(a[0].upper() + a[1:], True, white)
                txt.set_alpha(int(v3 * 255))

                icon = i["icon"]
                icon_surf.blit(
                    icon,
                    [
                        w + ui.inch2pix(0.4) - icon.get_width() - ui.inch2pix(0.1),
                        h
                        + txt.get_height() / 2
                        - icon.get_height() / 2
                        - int((v3 - 1) * d)
                        + scroll
                        + ui.inch2pix(0.03),
                    ],
                    special_flags=pygame.BLEND_RGBA_ADD,
                )

                txt2 = icon_font.render("", True, white)

                txt_width = WIDTH - (
                    w + ui.inch2pix(0.4) + txt2.get_width() + ui.inch2pix(0.6)
                )
                ext = title_font.render("... ", True, white)

                icon_surf.blit(
                    txt,
                    [w + ui.inch2pix(0.4), h - int((v3 - 1) * d) + scroll],
                    [0, 0, txt_width, txt.get_height()],
                    special_flags=pygame.BLEND_RGBA_ADD,
                )
                if txt.get_width() > txt_width:
                    icon_surf.blit(
                        ext,
                        [
                            w + ui.inch2pix(0.4) + txt_width,
                            h - int((v3 - 1) * d) + scroll,
                        ],
                        special_flags=pygame.BLEND_RGBA_ADD,
                    )
                    txt_width += ext.get_width()

                icon_surf.blit(
                    txt2,
                    [
                        WIDTH - txt2.get_width() - ui.inch2pix(0.3),
                        h - int((v3 - 1) * d) + ui.inch2pix(0.06) + scroll,
                    ],
                    special_flags=pygame.BLEND_RGBA_ADD,
                )
                if (
                    mouse
                    and mouse[1] >= top_padding
                    and mouse[1] <= HEIGHT - bottom_padding
                ):
                    if (
                        mouse[1] > h - ui.inch2pix(0.1) - int((v3 - 1) * d) + scroll
                        and mouse[1]
                        < h
                        + txt.get_height()
                        + ui.inch2pix(0.2)
                        - int((v3 - 1) * d)
                        + scroll
                    ):
                        if (
                            mouse[0]
                            > w + ui.inch2pix(0.4) - icon.get_width() - ui.inch2pix(0.1)
                            and mouse[0] < w + ui.inch2pix(0.4) + txt_width
                        ):
                            spawn_n_run(
                                machine,
                                i["cmd"],
                                "Default",
                                "Default",
                                "Default",
                                "Default",
                                "None",
                            )
                            if animator.get("start")[0] == 100:
                                animator.animate("start", [0, 0])
                                animator.animate("start2", [0, 0])
                                end = True

                        elif (
                            mouse[0] > w + ui.inch2pix(0.4) + txt_width
                            and mouse[0] < WIDTH
                        ):
                            shortcut(
                                name=a[0].upper() + a[1:],
                                cmd=i["cmd"],
                                mach=machine,
                                icn=i["icn"],
                            )

            h += ui.inch2pix(0.35) + txt.get_height()
            d += ui.inch2pix(0.1)

        # Draw stuff on canvas
        canvas.blit(b, [0, 0])
        # draw top icons and bottom icons
        icon_surf.set_alpha(int(int(v3 * 255) / 4))
        canvas.blit(icon_surf, [0, 0], [0, 0, WIDTH, top_padding])

        canvas.blit(
            icon_surf,
            [0, HEIGHT - bottom_padding],
            [0, (HEIGHT - bottom_padding), WIDTH, bottom_padding],
        )

        # blur
        ui.iris2(
            canvas,
            [0, 0],
            [WIDTH, HEIGHT],
            [0, 0, 0],
            radius=10,
            shadow_enabled=False,
            resolution=30,
            alpha=int(v * 255),
        )

        # draw central items
        icon_surf.set_alpha(int(v3 * 255))
        canvas.blit(
            icon_surf,
            [0, top_padding],
            [0, top_padding, WIDTH, HEIGHT - bottom_padding - top_padding],
        )

        # Top title above blur
        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))

        txt = title_font.render("Apps on " + str(ni), True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * v),
            ],
        )

        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        txt = title_font.render("?", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH - txt.get_width() - ui.inch2pix(0.3),
                ui.inch2pix(0.2) - int(ui.inch2pix(0.1) * (1 - v)),
            ],
        )
        hover = pygame.mouse.get_pos()
        if hover[0] > WIDTH - txt.get_width() - ui.inch2pix(0.4) and hover[
            0
        ] < WIDTH - ui.inch2pix(0.1):
            if hover[1] > ui.inch2pix(0.1) and hover[1] < ui.inch2pix(
                0.3
            ) + txt.get_height() - int(ui.inch2pix(0.1) * (1 - v)):
                if mouse:
                    helper("launcher")

        # loader
        v2 = 1 - (animator.get("apps")[0] / 100)

        if message == "":
            txt2 = pygame.transform.rotozoom(loader, loading_angle, 0.22)
            txt2.set_alpha(int(v * int(v2 * 255)))

            canvas.blit(
                txt2,
                [
                    WIDTH / 2 - txt2.get_width() / 2,
                    HEIGHT / 2
                    - txt2.get_height() / 2
                    - int((v2 - 1) * ui.inch2pix(0.4))
                    + ui.inch2pix(0),
                ],
            )

        # error Message
        title_font = ui.font(default_font, int(ui.inch2pix(0.17)))
        txt = title_font.render(message, True, white)
        txt.set_alpha(int(v * int(v2 * 255)))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                HEIGHT / 2
                - txt.get_height() / 2
                - int((v2 - 1) * ui.inch2pix(0.4))
                + ui.inch2pix(0),
            ],
        )

        txt = title_font.render("Cancel", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                HEIGHT
                - ui.inch2pix(0.3)
                - txt.get_height()
                - int((v - 1) * ui.inch2pix(0.4)),
            ],
        )
        if mouse:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0
            ] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT - ui.inch2pix(0.3) - txt.get_height() - int(
                    (v - 1) * ui.inch2pix(0.4)
                ) and mouse[1] < HEIGHT - ui.inch2pix(0.3) - txt.get_height() - int(
                    (v - 1) * ui.inch2pix(0.4)
                ) + txt.get_height() + ui.inch2pix(
                    0.1
                ):
                    machine = None
                    animator.animate("choose", [0, 0])
                    animator.animate("apps", [0, 0])

        if not light:
            pygame.gfxdraw.rectangle(
                canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, 100]
            )
        else:
            pygame.gfxdraw.rectangle(
                canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, 80]
            )
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, 80])

        fpsClock.tick(60)
        animator.update()

        if end:
            break

        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=pygame.BLEND_RGBA_ADD)

        pygame.display.update()
        if machine is None and animator.get("choose")[0] <= 1:
            return machine


def chooser(backdrop, title, options):
    global selected, canvas, WIDTH, HEIGHT, mini, back, lumen, mask
    animator.register("choose1", [0, 0])
    animator.animate("choose1", [100, 0])

    options.sort()

    b = backdrop.copy()

    size = ui.inch2pix(0.4)
    ui.set_icons(asset_dir + "Paper/")
    iconer = pygame.transform.smoothscale(
        ui.pygame_icon("paint", bundle_dir), [size, size]
    )

    list_length = len(options) * (ui.inch2pix(0.35) + ui.inch2pix(0.25))

    scroll2 = 0
    scroll = 0
    icon_surf = pygame.Surface([WIDTH, HEIGHT], pygame.SRCALPHA)

    choice = False

    alpha = {}
    option_names = {}
    pretty_options = []
    for i in options:
        option_names.update({i[0].upper() + i[1:]: i})

    for i in options:
        pretty_options.append(i[0].upper() + i[1:])
    pretty_options.sort()

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
                # subprocess.getoutput('taskkill /F /IM GWSL_service.exe')
                # subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                button = event.button
                if button == 1:
                    mouse = event.pos

            elif event.type == MOUSEBUTTONDOWN:
                button = event.button
                if list_length > HEIGHT - bottom_padding - top_padding:
                    if button == 5:  # down
                        if scroll > -list_length + ui.inch2pix(
                            0.5
                        ) + HEIGHT - top_padding - bottom_padding - ui.inch2pix(5):
                            scroll2 -= ui.inch2pix(0.5)
                    elif button == 4:  # up
                        if scroll < -ui.inch2pix(0.4):
                            scroll2 += ui.inch2pix(0.5)

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
                ui.iris2(
                    back,
                    [0, 0],
                    [WIDTH, HEIGHT],
                    [0, 0, 0],
                    radius=10,
                    shadow_enabled=False,
                    resolution=50,
                )
                # mini = pygame.transform.smoothscale(mini, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)])
                mini = pygame.transform.smoothscale(
                    mini1, [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)]
                )

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

        # WIDTH / 2 - txt.get_width() / 2 + ui.inch2pix(0.1)
        w = ui.inch2pix(0.5)
        d = ui.inch2pix(0.2)
        h = ui.inch2pix(0.8) + txt.get_height() + ui.inch2pix(0.25)
        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))

        # title_font.bold = True

        if scroll < scroll2 - int((scroll2 - scroll) / 2):
            scroll += int((scroll2 - scroll) / 2)
        if scroll2 < scroll - int((scroll - scroll2) / 2):
            scroll -= int((scroll - scroll2) / 2)

        # draw top and bottom of background
        icon_surf.fill([0, 0, 0, 0])
        icon_surf.blit(b, [0, 0], [0, 0, WIDTH, top_padding])
        icon_surf.blit(
            b,
            [0, HEIGHT - bottom_padding],
            [0, (HEIGHT - bottom_padding), WIDTH, bottom_padding],
        )

        v3 = animator.get("choose1")[0] / 100
        old_key = ""
        alpha = {}
        c = 0
        h2 = 0

        for a in pretty_options:
            if option_names[a][0].lower() != old_key:
                new_key = option_names[a][0].lower()
                old_key = new_key
                alpha.update({new_key: int(h2)})
            c += 1
            # ui.inch2pix(0.35) + txt.get_height()
            h2 = c * (ui.inch2pix(0.35) + ui.inch2pix(0.27))

            if (
                h - int((v3 - 1) * d) + scroll > -1 * (ui.inch2pix(0.5))
                and h - int((v3 - 1) * d) + scroll < HEIGHT
            ):

                txt = title_font.render(a, True, white)
                txt.set_alpha(int(v3 * 255))

                icon_surf.blit(
                    iconer,
                    [
                        w + ui.inch2pix(0.4) - iconer.get_width() - ui.inch2pix(0.1),
                        h
                        + txt.get_height() / 2
                        - iconer.get_height() / 2
                        - int((v3 - 1) * d)
                        + scroll
                        + ui.inch2pix(0.03),
                    ],
                    special_flags=pygame.BLEND_RGBA_ADD,
                )

                txt_width = WIDTH - (
                    w + ui.inch2pix(0.4) + ui.inch2pix(0.2) + ui.inch2pix(0.6)
                )
                ext = title_font.render("... ", True, white)

                icon_surf.blit(
                    txt,
                    [w + ui.inch2pix(0.4), h - int((v3 - 1) * d) + scroll],
                    [0, 0, txt_width, txt.get_height()],
                    special_flags=pygame.BLEND_RGBA_ADD,
                )
                if txt.get_width() > txt_width:
                    icon_surf.blit(
                        ext,
                        [
                            w + ui.inch2pix(0.4) + txt_width,
                            h - int((v3 - 1) * d) + scroll,
                        ],
                        special_flags=pygame.BLEND_RGBA_ADD,
                    )
                    txt_width += ext.get_width()

                if (
                    mouse
                    and mouse[1] >= top_padding
                    and mouse[1] <= HEIGHT - bottom_padding
                ):
                    if (
                        mouse[1] > h - ui.inch2pix(0.1) - int((v3 - 1) * d) + scroll
                        and mouse[1]
                        < h
                        + txt.get_height()
                        + ui.inch2pix(0.2)
                        - int((v3 - 1) * d)
                        + scroll
                    ):
                        if (
                            mouse[0]
                            > w
                            + ui.inch2pix(0.4)
                            - iconer.get_width()
                            - ui.inch2pix(0.1)
                            and mouse[0] < w + ui.inch2pix(0.4) + txt_width
                        ):
                            choice = option_names[a]
                            animator.animate("choose1", [0, 0])

            h += ui.inch2pix(0.35) + txt.get_height()
            d += ui.inch2pix(0.1)
        # Draw stuff on canvas
        canvas.blit(b, [0, 0])
        # draw top icons and bottom icons
        icon_surf.set_alpha(int(int(v3 * 255) / 4))
        canvas.blit(icon_surf, [0, 0], [0, 0, WIDTH, top_padding])

        canvas.blit(
            icon_surf,
            [0, HEIGHT - bottom_padding],
            [0, (HEIGHT - bottom_padding), WIDTH, bottom_padding],
        )

        # blur
        ui.iris2(
            canvas,
            [0, 0],
            [WIDTH, HEIGHT],
            [0, 0, 0],
            radius=10,
            shadow_enabled=False,
            resolution=30,
            alpha=int(v * 255),
        )

        # draw central items
        icon_surf.set_alpha(int(v3 * 255))
        canvas.blit(
            icon_surf,
            [0, top_padding],
            [0, top_padding, WIDTH, HEIGHT - bottom_padding - top_padding],
        )

        # Top title above blur
        title_font = ui.font(default_font, int(ui.inch2pix(0.21)))

        txt = title_font.render(title, True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                ui.inch2pix(0.5) - int(ui.inch2pix(0.1) * v),
            ],
        )

        title_font = ui.font(default_font, int(ui.inch2pix(0.19)))
        txt = title_font.render("?", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH - txt.get_width() - ui.inch2pix(0.3),
                ui.inch2pix(0.2) - int(ui.inch2pix(0.1) * (1 - v)),
            ],
        )
        hover = pygame.mouse.get_pos()
        if hover[0] > WIDTH - txt.get_width() - ui.inch2pix(0.4) and hover[
            0
        ] < WIDTH - ui.inch2pix(0.1):
            if hover[1] > ui.inch2pix(0.1) and hover[1] < ui.inch2pix(
                0.3
            ) + txt.get_height() - int(ui.inch2pix(0.1) * (1 - v)):
                if mouse:
                    helper("theme")

        txt = title_font.render("Cancel", True, white)
        txt.set_alpha(int(v * 255))
        canvas.blit(
            txt,
            [
                WIDTH / 2 - txt.get_width() / 2,
                HEIGHT
                - ui.inch2pix(0.3)
                - txt.get_height()
                - int((v - 1) * ui.inch2pix(0.4)),
            ],
        )
        if mouse:
            if mouse[0] > WIDTH / 2 - txt.get_width() / 2 - ui.inch2pix(0.2) and mouse[
                0
            ] < WIDTH / 2 - txt.get_width() / 2 + txt.get_width() + ui.inch2pix(0.2):
                if mouse[1] > HEIGHT - ui.inch2pix(0.3) - txt.get_height() - int(
                    (v - 1) * ui.inch2pix(0.4)
                ) and mouse[1] < HEIGHT - ui.inch2pix(0.3) - txt.get_height() - int(
                    (v - 1) * ui.inch2pix(0.4)
                ) + txt.get_height() + ui.inch2pix(
                    0.1
                ):
                    choice = None
                    animator.animate("choose1", [0, 0])

        if not light:
            pygame.gfxdraw.rectangle(
                canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, 100]
            )
        else:
            pygame.gfxdraw.rectangle(
                canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, 80]
            )
            pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, 80])

        fpsClock.tick(60)
        animator.update()

        py_root.fill([0, 0, 0, 255])
        py_root.blit(canvas, [0, 0], special_flags=pygame.BLEND_RGBA_ADD)

        pygame.display.update()
        if choice and animator.get("choose1")[0] <= 1:
            return choice


# def about():
#    choice = pymsgbox.confirm(text="This is the GWSL2 dashboard. GWSL2 is copyright Paul-E/Opticos Studios 2020. The X-Window backend is VCXSRV.", title="GWSL",
#                                  buttons=["Sounds Good!"])


def create_shortcut(command, name, icon):
    try:
        args = str(command)
        # winshell.start_menu()
        shortcut_path = os.path.join(app_path, str(str(name) + ".lnk"))
        home = str(Path.home())
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)

        print("attempt create shortcut")
        print("args:", args)
        print("cwd:", home)
        print("in:", shortcut_path)

        if BUILD_MODE == "MSIX":
            CSIDL_COMMON_APPDATA = 28

            _SHGetFolderPath = windll.shell32.SHGetFolderPathW
            _SHGetFolderPath.argtypes = [
                wintypes.HWND,
                ctypes.c_int,
                wintypes.HANDLE,
                wintypes.DWORD,
                wintypes.LPCWSTR,
            ]

            path_buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
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
        if os.path.exists(shortcut_path):
            print("Shortcut Successfully Created")
        print(
            subprocess.getoutput(
                'copy "' + shortcut_path + '" "' + winshell.start_menu() + '"'
            )
        )

    except Exception:
        logger.exception("Exception occurred")


def start_server(port, mode, clipboard):
    default_arguments = ["-ac", "-wgl", "-compositewm", "-notrayicon", "-dpi", "auto"]
    if mode == "multi":
        default_arguments.append("-multiwindow")
    elif mode == "full":
        default_arguments.append("-fullscreen")
    if clipboard:
        default_arguments.append("-clipboard")
        default_arguments.append("-primary")
    else:
        default_arguments.append("-noclipboard")
        default_arguments.append("-noprimary")

    proc = subprocess.Popen(
        ["VCXSRV/GWSL_instance.exe", ":" + str(port)] + default_arguments
    )
    return proc.pid


def get_light():
    registry = ConnectRegistry(None, HKEY_CURRENT_USER)
    key = OpenKey(
        registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    )
    key_value = QueryValueEx(key, "AppsUseLightTheme")
    k = int(key_value[0])
    return k


def spawn_n_run(
    machine,
    command,
    w_mode,
    w_clipboard,
    GTK,
    QT,
    appends,
    cmd=False,
    theme="Follow Windows",
    root="False",
    dbus="False",
    keep="False",
):
    ver = get_version(machine)
    if root == "True":
        code = pymsgbox.password(
            text="Enter Sudo Password For " + str(machine.replace("-", " ")) + ":",
            title="Authentication",
            mask="*",
        )
        if code is None:
            return None
        passw = "echo '" + code + "' | sudo -H -S "

    else:
        passw = ""

    v = run(machine, "/etc/init.d/dbus start")
    if dbus == "True" and "system message bus already started" not in v:
        if passw == "":
            code = pymsgbox.password(
                text="Enter Sudo Password To Start DBus:",
                title="DBus Not Started.",
                mask="*",
            )

            runo3(
                machine, "echo '" + code + "' | sudo -H -S " + "/etc/init.d/dbus start"
            )
        else:
            runo3(machine, passw + "/etc/init.d/dbus start")

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
                runs(
                    machine,
                    passw + l_mode + "DISPLAY=:0 " + qt + gtk + command + append,
                )
            else:
                ip = get_ip(machine)
                runs(
                    machine,
                    passw
                    + l_mode
                    + "DISPLAY="
                    + str(ip)
                    + ":0 "
                    + qt
                    + gtk
                    + command
                    + append,
                )

        else:
            # In this case, we need to start a new server, run in a new thread
            # that self closes VCXSRV after command if in multi window mode
            port = str(random.randrange(1000, 9999))

            if w_mode == "Multi Window":
                mode = "multi"
            elif w_mode == "Single Window":
                mode = "single"
            elif w_mode == "Fullscreen":
                mode = "full"
            elif w_mode == "Default":
                sett = iset.read()
                mode = sett["graphics"]["window_mode"]
            else:
                mode = w_mode

            if w_clipboard == "Default":
                sett = iset.read()
                clipboard = sett["general"]["clipboard"]
            elif w_clipboard == "Enabled" or w_clipboard:
                clipboard = True
            elif w_clipboard == "Disabled" or w_clipboard == False:
                clipboard = False

            PID = start_server(port, mode, clipboard)
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
                    print(
                        runs(
                            machine,
                            passw
                            + l_mode
                            + "DISPLAY=:"
                            + port
                            + " "
                            + qt
                            + gtk
                            + command
                            + append,
                        )
                    )

                elif ver == 2:
                    ip = get_ip(machine)
                    print(
                        runs(
                            machine,
                            passw
                            + l_mode
                            + "DISPLAY="
                            + str(ip)
                            + ":"
                            + port
                            + " "
                            + qt
                            + gtk
                            + command
                            + append,
                        )
                    )

                while True:
                    time.sleep(2)
                    procs = runo2(machine, "ps -ef")
                    if command in str(procs):
                        time.sleep(1)
                    else:
                        break
                if keep == "False":
                    print(
                        f"All of {command} terminated. Killing Server Instance on port {port}"
                    )
                    print(subprocess.getoutput("taskkill /F /PID " + str(PID)))
                else:
                    print(f"XServer do not kill. Keeping X on port {port}")

            if mode == "single":
                if ver == 1:
                    runs(
                        machine,
                        passw
                        + l_mode
                        + "DISPLAY=:"
                        + port
                        + " "
                        + qt
                        + gtk
                        + command
                        + append,
                    )

                elif ver == 2:
                    ip = get_ip(machine)
                    runs(
                        machine,
                        passw
                        + l_mode
                        + "DISPLAY="
                        + str(ip)
                        + ":"
                        + port
                        + " "
                        + qt
                        + gtk
                        + command
                        + append,
                    )

            else:
                if not cmd:
                    t = threading.Thread(target=threaded)
                    t.daemon = True
                    t.start()
                else:
                    threaded()
    except Exception:
        logger.exception("Exception occurred")


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

    # noinspection PyUnusedLocal
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

    # , font=("Helvetica", 16))
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
        if not boxRoot.running:
            break
        if creds != {}:
            return creds


def shortcut(name=None, cmd=None, mach=None, icn=None):
    ui.set_icons(asset_dir + "Paper/")

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
        # pygame.quit()
        # sys.exit()
        return None

    boxRoot.title("Shortcut Creator")
    boxRoot.iconname("Dialog")
    boxRoot.minsize(420, 480)
    boxRoot.running = True
    boxRoot.protocol("WM_DELETE_WINDOW", quitter)

    lbl = tk.Label(
        boxRoot, text="Create a Start Menu Shortcut:", justify=CENTER
    )  # , font=("Helvetica", 16))
    lbl.grid(row=0, padx=10, pady=10, sticky="EW")
    boxRoot.grid_rowconfigure(0, weight=0)

    def test():
        nonlocal machine
        try:
            machine = machine_chooser.get()
        except BaseException:
            pass

        command = link_command.get()
        if link_label.get() != "" and command != "":
            spawn_n_run(
                machine,
                command,
                mode_chooser.get(),
                clip_chooser.get(),
                GTK_chooser.get(),
                QT_chooser.get(),
                append_chooser.get(),
                theme=color_chooser.get(),
                root=root_chooser.get(),
                dbus=dbus_chooser.get(),
                keep=kill_chooser.get(),
            )

    def create():
        nonlocal machine
        try:
            machine = machine_chooser.get()
        except BaseException:
            pass

        command = link_command.get()
        if link_label.get() != "" and command != "":
            # --r --wsl_machine="Ubuntu-20.04" --wsl_cmd="gedit" --w_mode="Default" --clip_enabled="Default" --gtk_scale=1 --qt_scale=1 --append=""
            if append_chooser.get() == "None":
                append = ""
            else:
                append = append_chooser.get()
            command = (
                '--r --wsl_machine="'
                + str(machine)
                + '" --wsl_cmd="'
                + command
                + '" --w_mode="'
                + str(mode_chooser.get())
                + '" --clip_enabled="'
                + str(clip_chooser.get())
            )
            command += (
                '" --gtk_scale="'
                + str(GTK_chooser.get())
                + '" --qt_scale="'
                + str(QT_chooser.get())
                + '" --append="'
                + str(append)
                + '"'
            )
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

            imager.save(
                app_path + "\\" + str(link_label.get()) + ".ico",
                sizes=[(24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (255, 255)],
            )
            if root_chooser.get() == "False":
                create_shortcut(
                    command,
                    link_label.get() + " on " + str(machine.replace("-", " ")),
                    app_path + "\\" + str(link_label.get()) + ".ico",
                )
            else:
                create_shortcut(
                    command,
                    "(root) "
                    + link_label.get()
                    + " on "
                    + str(machine.replace("-", " ")),
                    app_path + "\\" + str(link_label.get()) + ".ico",
                )
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
    imager = Image.open(asset_dir + "link.png")
    # imager = imager.resize([48, 48])

    img = PIL.ImageTk.PhotoImage(imager.resize([48, 48]))
    labelm = tk.Label(frame_1, image=img)
    labelm.image = img

    if icn is not None:
        imager = ui.icon(icn.lower())
        image2 = imager.resize([48, 48], resample=PIL.Image.ANTIALIAS)
        img = PIL.ImageTk.PhotoImage(image2)
        labelm.configure(image=img)
        labelm.image = img
    labelm.grid(row=0, padx=10, pady=10, sticky="EW", rowspan=2)

    tk.Label(frame_1, text="Shortcut Label: ").grid(
        row=0, column=1, padx=10, sticky="W"
    )

    link_label = ttk.Entry(frame_1)
    if name is not None:
        link_label.insert(0, name)
    link_label.grid(row=0, column=2, padx=10, sticky="WE")

    link_label.focus_force()

    tk.Label(frame_1, text="Shortcut Command: ").grid(
        row=1, column=1, padx=10, sticky="W"
    )

    link_command = ttk.Entry(frame_1)
    if name is not None:
        link_command.insert(0, cmd)
    link_command.grid(row=1, column=2, padx=10, sticky="WE")

    tk.Label(frame_1, text="Run In: ").grid(
        row=2, column=1, padx=10, pady=7, sticky="W"
    )

    machines = os.popen("wsl.exe -l -q").read()
    machines = re.sub(r"[^a-zA-Z0-9./\n-]", r"", machines).splitlines()
    machines[:] = (value for value in machines if value != "")

    sett = iset.read()

    avoid = sett["distro_blacklist"]
    docker_blacklist = []
    for i in machines:
        for a in avoid:
            if a.lower() in i.lower():
                docker_blacklist.append(i)

    for i in docker_blacklist:
        machines.remove(i)

    if mach is None:
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
            pymsgbox.alert(
                text="No WSL Distros Found",
                title="Please Install a WSL Distro",
                button="OK",
            )
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

    tk.Label(frame_2.frame, text="Display Mode: ").grid(
        row=0, column=0, pady=7, sticky="WN"
    )

    mode_chooser = ttk.Combobox(
        frame_2.frame,
        values=["Default", "Multi Window", "Single Window", "Fullscreen"],
        state="readonly",
    )
    mode_chooser.current(0)
    mode_chooser.grid(row=0, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="GTK Scale Mode: ").grid(
        row=1, column=0, pady=7, sticky="WN"
    )
    GTK_chooser = ttk.Combobox(
        frame_2.frame, values=["Default", "1", "2", "3"], state="readonly"
    )
    GTK_chooser.current(0)
    GTK_chooser.grid(row=1, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="QT Scale Mode: ").grid(
        row=2, column=0, pady=7, sticky="WN"
    )
    QT_chooser = ttk.Combobox(
        frame_2.frame, values=["Default", "1", "2", "3"], state="readonly"
    )
    QT_chooser.current(0)
    QT_chooser.grid(row=2, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="Shared Clipboard: ").grid(
        row=3, column=0, pady=7, sticky="WN"
    )
    clip_chooser = ttk.Combobox(
        frame_2.frame, values=["Default", "Enabled", "Disabled"], state="readonly"
    )
    clip_chooser.current(0)
    clip_chooser.grid(row=3, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="Color Mode: ").grid(
        row=4, column=0, pady=7, sticky="WN"
    )
    color_chooser = ttk.Combobox(
        frame_2.frame,
        values=["Follow Windows", "Light Mode", "Dark Mode"],
        state="readonly",
    )
    color_chooser.current(0)
    color_chooser.grid(row=4, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="Run As Root:").grid(
        row=5, column=0, pady=7, sticky="WN"
    )
    root_chooser = ttk.Combobox(
        frame_2.frame, values=["True", "False"], state="readonly"
    )
    root_chooser.current(1)
    root_chooser.grid(row=5, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="Experimental Features:").grid(
        row=6, column=0, pady=7, sticky="WN"
    )

    tk.Label(frame_2.frame, text="Use DBus (Sudo Required):").grid(
        row=7, column=0, pady=7, sticky="WN"
    )
    dbus_chooser = ttk.Combobox(
        frame_2.frame, values=["True", "False"], state="readonly"
    )
    dbus_chooser.current(1)
    dbus_chooser.grid(row=7, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="Experimental Flags:").grid(
        row=8, column=0, pady=7, sticky="WN"
    )
    append_chooser = ttk.Combobox(
        frame_2.frame, values=["None", "--zoom=2", "--scale=2"], state="readonly"
    )
    append_chooser.current(0)
    append_chooser.grid(row=8, column=1, padx=10, sticky="WE")

    tk.Label(frame_2.frame, text="Keep XServer Instance:").grid(
        row=9, column=0, pady=7, sticky="WN"
    )
    kill_chooser = ttk.Combobox(
        frame_2.frame, values=["True", "False"], state="readonly"
    )
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
    test_b.grid(column=2, row=0, sticky="SE", padx=10)

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
    while True:
        # draw(canvas, mouse=False)
        time.sleep(0.05)
        boxRoot.update()
        if not boxRoot.running:
            break

        old = new
        new = link_label.get()
        if old != new:
            imager = ui.icon(new.lower(), spec=new.lower())
            image2 = imager.resize([48, 48], resample=PIL.Image.ANTIALIAS)
            img = PIL.ImageTk.PhotoImage(image2)
            labelm.configure(image=img)
            labelm.image = img
        if mach is None:
            if len(machines) > 1:
                machine = machine_chooser.get()
            else:
                machine = machines[0]
        else:
            machine = mach

    # imager.save("test.ico", sizes=[(24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (255, 255)])


def putty():
    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)  # , fg="red", bg="black")
        # boxRoot.attributes("-transparentcolor", "red")
        # boxRoot.attributes("-alpha", 0.5)
        boxRoot.withdraw()
    else:
        boxRoot = tk.Tk()
        boxRoot.withdraw()

    def quitter():
        boxRoot.quit()
        boxRoot.destroy()
        boxRoot.running = False
        return None

    # win32gui.SetWindowLong(hwnd2, win32con.GWL_EXSTYLE,
    #                       win32gui.GetWindowLong(hwnd2, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    # win32gui.SetLayeredWindowAttributes(hwnd2, win32api.RGB(*(255, 0, 0)), 0, win32con.LWA_COLORKEY)

    # blur.blur(hwnd2)

    boxRoot.title("Graphical SSH Manager")
    boxRoot.iconname("Dialog")
    boxRoot.minsize(420, 200)
    boxRoot.running = True
    boxRoot.protocol("WM_DELETE_WINDOW", quitter)

    lbl = tk.Label(
        boxRoot, text="Graphical SSH Tools:", justify=CENTER
    )  # , font=("Helvetica", 16))
    lbl.grid(row=0, padx=10, pady=10, sticky="EW")
    boxRoot.grid_rowconfigure(0, weight=0)

    def test():
        ip_config = ip.get()
        if ip_config != "":
            creds = get_login(ip_config)
            sett = iset.read()
            sett["putty"]["ip"] = ip.get()
            iset.set(sett)

            password = creds["pass"]

            user = creds["user"]
            quitter()

    def create():
        sett = iset.read()
        sett["putty"]["ip"] = ip.get()
        iset.set(sett)

        if ip.get() != "":
            command = f'--r --ssh --ip="{ip.get()}" --command="open_putty"'

            print(command)
            create_shortcut(
                command, "Graphical SSH on " + ip.get(), asset_dir + "computer.ico"
            )
            quitter()

    # First frame

    frame_1 = ttk.Frame(boxRoot, padding="0.1i")
    imager = Image.open(asset_dir + "network.png")
    # imager = imager.resize([48, 48])

    img = PIL.ImageTk.PhotoImage(imager.resize([48, 48]))
    labelm = tk.Label(frame_1, image=img)
    labelm.image = img

    labelm.grid(row=0, padx=10, pady=0, sticky="EW", rowspan=2)

    tk.Label(frame_1, text="Remote IP: ").grid(
        row=0, column=1, padx=10, rowspan=2, sticky="W"
    )

    ip = ttk.Entry(frame_1)

    sett = iset.read()
    save_ip = sett["putty"]["ip"]
    if save_ip is not None:
        ip.insert(0, save_ip)
    # iset.set(sett)

    ip.grid(row=0, column=2, padx=10, rowspan=2, sticky="WE")

    ip.focus_force()

    frame_1.grid_columnconfigure(2, weight=1)

    frame_1.grid(row=1, column=0, padx=20, pady=0, sticky="NEW")

    frame_3 = tk.Frame(boxRoot)  # , padding="0.15i")

    close_b = ttk.Button(frame_3, text="Close", command=quitter)
    close_b.grid(column=0, row=0, sticky="SW", padx=10)

    save_b = ttk.Button(frame_3, text="Add to Start Menu", command=create)
    save_b.grid(column=1, row=0, sticky="SWE", padx=10)

    save_b = ttk.Button(frame_3, text="Help", command=help_ssh)
    save_b.grid(column=2, row=0, sticky="WE", padx=10)

    test_b = ttk.Button(frame_3, text="Connect to Machine", command=test)
    test_b.grid(column=3, row=0, sticky="SE", padx=10)

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
        if not boxRoot.running:
            break


def get_running(process):
    proc_list = os.popen("tasklist").readlines()
    for proc in proc_list:
        if process in proc:
            return True
    return False


def update_running():
    global running, service_loaded, white, light, accent
    if get_running("GWSL_service") == False:
        try:
            subprocess.Popen("GWSL_service.exe")
            service_loaded = True
        except Exception:
            logger.exception("Exception occurred")
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
        registry = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(
            registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        key_value = QueryValueEx(key, "SystemUsesLightTheme")
        k = int(key_value[0])
        light = False
        white = [255, 255, 255]
        if k == 1:
            light = True
            white = [0, 0, 0]

        accent = ui.get_color()
        if light:
            for i in range(3):
                if accent[i] > 50:
                    accent[i] -= 50


last = 0


def draw(canvas, mouse=False):
    global mask, light_source, lumen_opac, wait, running, ter, about_open, loading_angle, loader, last
    # mask.fill([255, 0, 0])
    canvas.fill([0, 0, 0, 0])

    launch = animator.get("start")[0] / 100.0
    hover = mouse
    if not mouse:
        hover = pygame.mouse.get_pos()
    if animator.get("start")[0] < 100 and animator.get("start")[0] > 0:
        # canvas.blit(back, [-1 * (screensize[0] - WIDTH), -1 * (screensize[1] - taskbar - int(HEIGHT * launch))])
        win32gui.MoveWindow(
            HWND,
            winpos,
            screensize[1] - taskbar - int(HEIGHT * launch),
            WIDTH,
            HEIGHT,
            1,
        )
        lumen_opac = 0
        win32gui.SetLayeredWindowAttributes(
            hwnd, win32api.RGB(*fuchsia), int(launch * 255), win32con.LWA_ALPHA
        )

    else:
        if about_open:
            about_open = False
            about()
        # canvas.blit(back, [-1 * (screensize[0] - WIDTH), -1 * (screensize[1] - taskbar - int(HEIGHT))])
        win32gui.MoveWindow(
            HWND, winpos, screensize[1] - taskbar - int(HEIGHT), WIDTH, HEIGHT, True
        )
        win32gui.SetLayeredWindowAttributes(
            hwnd, win32api.RGB(*fuchsia), int(launch * 255), win32con.LWA_ALPHA
        )
        animator.animate("start2", [100, 0])
        if service_loaded:
            animator.animate("loading", [100, 0])

    # print(canvas.get_at([0, 0]))

    launch = animator.get("start2")[0] / 100.0

    if animator.get("start2")[0] > 99 and service_loaded == False:
        animator.animate("loading", [0, 0])

    l_h = ui.inch2pix(0.9) + int(20 * (1 - launch))
    padd = ui.inch2pix(0.15)

    # pygame.draw.circle(canvas, [255, 0, 0, 255], [100, 100], 50)

    if not light:
        pygame.gfxdraw.rectangle(
            canvas, [0, 0, WIDTH, HEIGHT + 1], [100, 100, 100, 100]
        )

        pygame.gfxdraw.line(
            canvas, padd, l_h, WIDTH - padd, l_h, [180, 180, 180, int(80 * launch)]
        )

    else:
        pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [255, 255, 255, 200])
        pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0, 50])

        pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [255, 255, 255, 80])
        pygame.gfxdraw.rectangle(canvas, [0, 0, WIDTH, HEIGHT + 1], [0, 0, 0, 80])

        pygame.gfxdraw.line(
            canvas, padd, l_h, WIDTH - padd, l_h, [0, 0, 0, int(80 * launch)]
        )

    # canvas.fill(fuchsia)

    icon_font = ui.font(ico_font, int(ui.inch2pix(0.4)))

    sett = icon_font.render("", True, white)
    sett.set_alpha(int(launch * 255))
    canvas.blit(
        sett, [ui.inch2pix(0.3), ui.inch2pix(0.28) + (1 - launch) * ui.inch2pix(0.1)]
    )

    title_font = ui.font(default_font, int(ui.inch2pix(0.17)))
    title_font.bold = False
    title_font.italic = False

    if service_loaded != "bad":
        if not running:
            txt = title_font.render("GWSL Dashboard", True, white)
        else:
            txt = title_font.render("X Running On locahost : 0.0", True, white)
    else:
        txt = title_font.render("Error. Please Check Logs", True, white)

    txt.set_alpha(int(launch * 255))
    canvas.blit(
        txt, [ui.inch2pix(1), ui.inch2pix(0.35) + (1 - launch) * ui.inch2pix(0.1)]
    )

    # canvas.blit(txt, [ui.inch2pix(0.5), ui.inch2pix(0.35) + (1 - launch) * ui.inch2pix(0.1)])

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

    # pygame.gfxdraw.box(canvas, [ui.inch2pix(0.67), ui.inch2pix(2.5), ui.inch2pix(1.2), ui.inch2pix(1.2)], [0, 0, 0, 100])

    icon_font = ui.font(ico_font, int(ui.inch2pix(0.33)))
    box = ui.inch2pix(0.7)

    start = ui.inch2pix(1.1)
    s = ui.inch2pix(0.25)

    def setter():
        machine = choose_machine()
        if machine is not None:
            configure_machine(machine)
            # settings(machine)

    def short():
        shortcut()

    def shells():
        machine = choose_machine()
        if machine is not None:
            # + ". ~/.profile;bash")
            subprocess.Popen("wsl.exe ~ -d " + str(machine))

    def apper():
        machine = choose_machine()
        if machine is not None:
            app_launcher(machine)

    def donate():
        webbrowser.get("windows-default").open(
            "https://sites.google.com/bartimee.com/opticos-studios/donate"
        )

    def wsl_installer():
        webbrowser.get("windows-default").open(
            "https://docs.microsoft.com/en-us/windows/wsl/install-win10"
        )

    if installed:
        buttons = [
            ["GWSL Distro Tools", "", setter],
            ["Shortcut Creator", "", short],
            ["Linux Apps", "", apper],
            ["Linux Shell", "", shells],
            ["Graphical SSH Connection", "", putty],
            ["Donate With PayPal", "", donate],
        ]
    else:
        buttons = [
            ["Graphical SSH Connection", "", putty],
            ["Install WSL for More Features", "", wsl_installer],
            ["Donate With PayPal", "", donate],
        ]  # 

    selected = False
    q = 0
    for i in buttons:
        s2 = False
        pos = [ui.inch2pix(0.4), start + (1 - launch) * s]
        if hover[0] > ui.inch2pix(0.1) and hover[0] < WIDTH - ui.inch2pix(0.1):
            if hover[1] > pos[1] + ui.inch2pix(0.1) and hover[1] < pos[1] + ui.inch2pix(
                0.3
            ) + ui.inch2pix(0.3):
                if mouse:
                    i[2]()
                selected = True
                s2 = True
                last = q

        # square(canvas, [ui.inch2pix(0.1), pos[1]], [WIDTH - ui.inch2pix(0.1) * 2,
        # ui.inch2pix(0.3) + ui.inch2pix(0.4)], width=2, filled = True,
        # color=accent + [int(launch * 100)])

        s3 = animator.get("select")[0] / 100
        # selected
        sett = icon_font.render(i[1], True, white)
        txt = title_font.render(i[0], True, white)
        if s2 or q == last:
            txt.set_alpha(int(launch * 255 * (1 - s3)))
            sett.set_alpha(int(launch * 255 * (1 - s3)))
        else:
            txt.set_alpha(int(launch * 255))
            sett.set_alpha(int(launch * 255))

        canvas.blit(sett, [pos[0], pos[1] + box / 2 - sett.get_height() / 2])
        canvas.blit(
            txt,
            [
                pos[0] + sett.get_width() + ui.inch2pix(0.2),
                pos[1] + box / 2 - txt.get_height() / 2 - ui.inch2pix(0.025),
            ],
        )

        # unselected
        if s2 or q == last:
            sett = icon_font.render(i[1], True, accent)
            sett.set_alpha(int(launch * 255 * s3))
            canvas.blit(sett, [pos[0], pos[1] + box / 2 - sett.get_height() / 2])
            txt = title_font.render(i[0], True, accent)
            txt.set_alpha(int(launch * 255 * s3))
            canvas.blit(
                txt,
                [
                    pos[0] + sett.get_width() + ui.inch2pix(0.2),
                    pos[1] + box / 2 - txt.get_height() / 2 - ui.inch2pix(0.025),
                ],
            )

        # square(mask, [ui.inch2pix(0.1), pos[1]], [WIDTH - ui.inch2pix(0.1) * 2,
        # ui.inch2pix(0.3) + ui.inch2pix(0.4)], width=2)
        start += ui.inch2pix(0.3) + ui.inch2pix(0.5) - ui.inch2pix(0.15)
        s += ui.inch2pix(0.17)
        q += 1

    # logo.set_alpha(int(launch * 200))
    # canvas.blit(logo, [WIDTH - logo.get_width() - ui.inch2pix(2), HEIGHT - ui.inch2pix(1.15) + (1 - launch) * 20])
    title_font = ui.font(default_font, int(ui.inch2pix(0.17)))
    title_font.bold = False
    title_font.italic = False

    txt = title_font.render("GWSL Dashboard", True, white)
    txt.set_alpha(int(launch * 200))
    # canvas.blit(txt, [WIDTH - ui.inch2pix(1.8), HEIGHT - ui.inch2pix(1.15) + (1 - launch) * 40])

    txt = title_font.render("Version 1.3", True, white)
    txt.set_alpha(int(launch * 200))
    # canvas.blit(txt, [WIDTH - ui.inch2pix(1.5), HEIGHT - ui.inch2pix(0.85) + (1 - launch) * 50])

    # title_font.italic = True
    s = animator.get("select")[0] / 100

    txt = title_font.render("Help", True, white)
    txt.set_alpha(int(launch * 255))
    canvas.blit(
        txt, [WIDTH - ui.inch2pix(1.3), HEIGHT - ui.inch2pix(0.5) + (1 - launch) * 60]
    )

    # square(mask, [WIDTH - ui.inch2pix(1.35), HEIGHT - ui.inch2pix(0.55) + (1 - launch) * 60],
    #       [txt.get_width() + ui.inch2pix(0.1), txt.get_height() + ui.inch2pix(0.1)], width=2)

    if hover[0] > WIDTH - ui.inch2pix(1.35) and hover[0] < WIDTH - ui.inch2pix(
        1.35
    ) + txt.get_width() + ui.inch2pix(0.1):
        if hover[1] > HEIGHT - ui.inch2pix(0.55) + (1 - launch) * 60 and hover[
            1
        ] < HEIGHT - ui.inch2pix(0.55) + (
            1 - launch
        ) * 60 + txt.get_height() + ui.inch2pix(
            0.1
        ):
            # webbrowser.open("GWSLHELP.com")#, new=0, autoraise=True)
            if mouse:
                webbrowser.get("windows-default").open(
                    "https://opticos.github.io/gwsl/help.html"
                )
            selected = True
            txt = title_font.render("Help", True, accent)
            txt.set_alpha(int(launch * 255 * s))
            canvas.blit(
                txt,
                [
                    WIDTH - ui.inch2pix(1.3),
                    HEIGHT - ui.inch2pix(0.5) + (1 - launch) * 60,
                ],
            )
            last = 100

    txt = title_font.render("About", True, white)
    txt.set_alpha(int(launch * 255))
    canvas.blit(
        txt, [WIDTH - ui.inch2pix(0.7), HEIGHT - ui.inch2pix(0.5) + (1 - launch) * 80]
    )

    # square(mask, [WIDTH - ui.inch2pix(0.8), HEIGHT - ui.inch2pix(0.55) + (1 - launch) * 60],
    #       [txt.get_width() + ui.inch2pix(0.17), txt.get_height() + ui.inch2pix(0.1)], width=2)

    if hover[0] > WIDTH - ui.inch2pix(0.8) and hover[0] < WIDTH - ui.inch2pix(
        0.8
    ) + txt.get_width() + ui.inch2pix(0.17):
        if hover[1] > HEIGHT - ui.inch2pix(0.55) + (1 - launch) * 60 and hover[
            1
        ] < HEIGHT - ui.inch2pix(0.55) + (
            1 - launch
        ) * 60 + txt.get_height() + ui.inch2pix(
            0.1
        ):
            if mouse:
                about()
            selected = True
            last = 100
            txt = title_font.render("About", True, accent)
            txt.set_alpha(int(launch * 255 * s))
            canvas.blit(
                txt,
                [
                    WIDTH - ui.inch2pix(0.7),
                    HEIGHT - ui.inch2pix(0.5) + (1 - launch) * 80,
                ],
            )

    if selected:
        animator.animate("select", [100, 0])
    else:
        animator.animate("select", [0, 0])
        # lumen_opac = 0

    # pay.set_alpha(int(launch * 200))
    # canvas.blit(pay, [ui.inch2pix(0.15), HEIGHT - ui.inch2pix(0.25) - pay.get_height() + (1 - launch) * 20])

    title_font.italic = True
    txt = title_font.render("Donate", True, [240, 240, 240])
    txt.set_alpha(int(launch * 220))
    # canvas.blit(txt, [ui.inch2pix(0.2), HEIGHT - pay.get_height() - txt.get_height() - ui.inch2pix(0.3) + (1 - launch) * 80])

    # pygame.gfxdraw.polygon(mask, [[0, 0],
    #                               [WIDTH - 1, 0],
    #                               [WIDTH - 1, HEIGHT - 1],
    #                               [0, HEIGHT - 1]], [0, 255, 0])
    # draw(canvas)

    # edit mask
    """
    arr = pygame.PixelArray(mask)
    arr.replace((0, 255, 0), (0, 0, 0, 0))
    arr.close()




    lumen.fill([0, 0, 0, 0])
    if lumen_opac > 0:
        mouse1 = pygame.mouse.get_pos()
        lumen.blit(light_source, [mouse1[0] - light_source.get_width() / 2,
                              mouse1[1] - light_source.get_height() / 2], special_flags=(pygame.BLEND_RGBA_ADD))

    lumen.blit(mask, [0, 0])
    arr = pygame.PixelArray(lumen)
    arr.replace((255, 0, 0), (0, 0, 0, 0))
    arr.close()

    """
    """
    mouse = pygame.mouse.get_pos()

    if pygame.mouse.get_pressed()[0] == 1:
        lumen_opac = 0
        light_source = pygame.image.load(asset_dir + "lumens/" + str(lumen_opac + 1) + ".png").convert_alpha()


    if pygame.mouse.get_pressed()[0] != 1 and pygame.mouse.get_focused() == 1:
        if lumen_opac < 6:
            wait += 1
            if wait >= 1:
                lumen_opac += 1
                wait = 0
                light_source = pygame.image.load(asset_dir + "lumens/" + str(lumen_opac + 1) + ".png").convert_alpha()


    if pygame.mouse.get_focused() == 0:
        if lumen_opac > 0:
            wait += 1
            if wait >= 1:
                lumen_opac -= 1
                wait = 0
                light_source = pygame.image.load(asset_dir + "lumens/" + str(lumen_opac + 1) + ".png").convert_alpha()


    """
    # if service_loaded == False:
    #    lumen_opac = 0

    # canvas.blit(lumen, [0, 0])

    title_font.italic = False

    if not service_loaded:
        txt2 = title_font.render("Starting Service", True, white)
    elif service_loaded == "bad":
        txt2 = title_font.render("Error Starting Service", True, white)
        loading_angle = 0
        icon_font = ui.font(ico_font, int(ui.inch2pix(0.22)))  # 0.19
        loader = icon_font.render("", True, white)

    else:
        txt2 = title_font.render("Starting Service", True, white)

    v2 = 1 - (animator.get("loading")[0] / 100)
    v = animator.get("start")[0] / 100

    txt2.set_alpha(int(v * int(v2 * 255)))
    canvas.blit(
        txt2,
        [
            ui.inch2pix(0.55),
            HEIGHT
            - txt2.get_height() / 2
            - int((v2 - 1) * ui.inch2pix(0.6))
            - ui.inch2pix(0.39),
        ],
    )

    if service_loaded != "bad":
        txt2 = pygame.transform.rotozoom(loader, loading_angle, 0.22)
    else:
        txt2 = loader

    txt2.set_alpha(int(v * int(v2 * 255)))
    canvas.blit(
        txt2,
        [
            ui.inch2pix(0.35) - txt2.get_width() / 2,
            HEIGHT
            - ui.inch2pix(0.38)
            - txt2.get_height() / 2
            - int((v2 - 1) * ui.inch2pix(0.4)),
        ],
    )

    #
    # pygame.gfxdraw.box(canvas, [0, 0, WIDTH, HEIGHT], [0, 0, 0, int(((animator.get("darken")[0] / 100)) * 200)])
    py_root.fill([0, 0, 0, 255])
    py_root.blit(canvas, [0, 0], special_flags=pygame.BLEND_RGBA_ADD)
    fpsClock.tick(60)
    animator.update()


def square(mask, pos, size, width=1, filled=False, color=False):
    if not color:
        if not filled:
            pygame.draw.polygon(
                mask,
                [0, 255, 0],
                [
                    pos,
                    [pos[0] + size[0], pos[1]],
                    [pos[0] + size[0], pos[1] + size[1]],
                    [pos[0], pos[1] + size[1]],
                ],
                width,
            )
        elif filled:
            pygame.gfxdraw.filled_polygon(
                mask,
                [
                    pos,
                    [pos[0] + size[0], pos[1]],
                    [pos[0] + size[0], pos[1] + size[1]],
                    [pos[0], pos[1] + size[1]],
                ],
                [0, 255, 0],
            )
    else:
        if not filled:
            pygame.gfxdraw.polygon(
                mask,
                [
                    pos,
                    [pos[0] + size[0], pos[1]],
                    [pos[0] + size[0], pos[1] + size[1]],
                    [pos[0], pos[1] + size[1]],
                ],
                color,
            )
        elif filled:
            pygame.gfxdraw.filled_polygon(
                mask,
                [
                    pos,
                    [pos[0] + size[0], pos[1]],
                    [pos[0] + size[0], pos[1] + size[1]],
                    [pos[0], pos[1] + size[1]],
                ],
                color,
            )


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
            self._button = ttk.Checkbutton(
                self, variable=self._variable, command=self._activate, style="TButton"
            )
            self._button.grid(row=0, column=0)
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


if "--r" not in args:
    running = True
    service_loaded = False
    updater = threading.Thread(target=update_running)
    updater.daemon = True
    updater.start()
    about_open = False

    read = ""
    from shutil import which

    if which("wsl.exe") is not None:
        installed = True
    else:
        installed = False

    # print("Starting GUI")
    if "--about" in args:
        about_open = True
    if True:  # installed == True:
        animator = anima.Animator(fpsClock)
        animator.register("start", [1, 0])
        animator.register("start2", [0, 0])
        animator.animate("start", [100, 0])
        animator.register("darken", [0, 0])
        animator.register("choose", [0, 0])
        animator.register("apps", [100, 0])
        animator.register("loading", [100, 0])
        animator.register("select", [0, 0])
        wait = 0
        loading_angle = 0
        icon_font = ui.font(ico_font, int(ui.inch2pix(1)))  # 0.19
        loader = icon_font.render("", True, white)

        while True:
            try:
                loading_angle -= 10
                if win32gui.GetFocus() != HWND:
                    if animator.get("start")[0] == 100:
                        animator.animate("start", [0, 0])
                        animator.animate("start2", [0, 0])
                if animator.get("start")[0] <= 0:
                    pygame.quit()
                    sys.exit()
                for event in pygame.event.get():
                    if event.type == QUIT:
                        # subprocess.getoutput('taskkill /F /IM GWSL_service.exe')
                        # subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
                        pygame.quit()
                        sys.exit()
                    elif event.type == MOUSEBUTTONUP:
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
                        mini = pygame.transform.smoothscale(
                            mini1,
                            [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)],
                        )

                        back = mini.copy()
                        back = pygame.transform.scale(back, [WIDTH, HEIGHT])
                        ui.iris2(
                            back,
                            [0, 0],
                            [WIDTH, HEIGHT],
                            [0, 0, 0],
                            radius=10,
                            shadow_enabled=False,
                            resolution=50,
                        )
                        mini = pygame.transform.smoothscale(
                            mini,
                            [display.get_width() - ui.inch2pix(0.1), ui.inch2pix(0.55)],
                        )
                        lumen = pygame.Surface(
                            [WIDTH, HEIGHT], SRCALPHA
                        ).convert_alpha()
                        # mask = pygame.Surface([WIDTH, HEIGHT], SRCALPHA).convert_alpha()
                        # mask.fill([255, 0, 0])

                draw(canvas)
                pygame.display.update()
            except Exception as e:
                logger.exception("Exception occurred")

    else:
        choice = pymsgbox.confirm(
            text="WSL is not configured. Please install it and get some distros.",
            title="Cannot Find WSL!",
            buttons=["Ok", "Online Help"],
        )
        if choice == "Online Help":
            webbrowser.get("windows-default").open(
                "https://docs.microsoft.com/en-us/learn/modules/get-started-with-windows-subsystem-for-linux/2-enable-and-install"
            )


elif args[1] == "--r" and "--ssh" not in args:
    try:
        print("started")
        themer = "Follow Windows"
        rooter = "False"
        dbuser = "False"
        keeper = "False"
        # python manager.py --r --wsl_machine="Ubuntu-20.04" --wsl_cmd="gedit"
        # --w_mode="multi" --clip_enabled="true" --gtk_scale=1 --qt_scale=1
        # --append="--zoom=1"
        for arg in args[2:]:
            if "--wsl_machine" in arg:
                machine = arg[14:]

            elif "--wsl_cmd" in arg:
                command = arg[10:]

            elif "--w_mode" in arg:
                mode = arg[9:]

            elif "--clip_enabled" in arg:
                clipboard = arg[15:]
                if clipboard == "true":
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
                subprocess.Popen("GWSL_service.exe")
            except Exception as e:
                logger.exception("Exception occurred")
                print("Can't run service...")

        print("keep", keeper)
        machines = os.popen("wsl.exe -l -q").read()  # lines()
        machines = re.sub(r"[^a-zA-Z0-9./\n-]", r"", machines).splitlines()
        machines[:] = (value for value in machines if value != "")

        if machine not in machines:
            choice = pymsgbox.confirm(
                text="Hmmm... The WSL machine "
                + str(machine)
                + " does not exist. You can delete this shortcut.",
                title="Cannot Find Machine: " + str(machine),
                buttons=["Ok"],
            )
        else:
            if True:
                spawn_n_run(
                    machine,
                    command,
                    mode,
                    clipboard,
                    gtk,
                    qt,
                    append,
                    cmd=True,
                    theme=themer,
                    root=rooter,
                    dbus=dbuser,
                    keep=keeper,
                )
            else:
                choice = pymsgbox.confirm(
                    text="Hmmm... This shortcut does not seem to work. Try deleting it and making a new one.",
                    title="Bad Shortcut",
                    buttons=["Ok"],
                )
    except Exception as e:
        logger.exception("Exception occurred")


elif args[1] == "--r" and "--ssh" in args:
    try:
        print("started")
        ip = None
        user = None
        command = None
        password = None
        rooter = "false"
        # python manager.py --r --wsl_machine="Ubuntu-20.04" --wsl_cmd="gedit"
        # --w_mode="multi" --clip_enabled="true" --gtk_scale=1 --qt_scale=1
        # --append="--zoom=1"
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

        if get_running("GWSL_service") != True:
            try:
                subprocess.Popen("GWSL_service.exe")
            except Exception as e:
                logger.exception("Exception occurred")
                print("Can't run service...")

        timer = time.perf_counter()
        if command != "open_putty":
            prog = Cmd(
                command=[
                    "PUTTY/GWSL_plink.exe",
                    "-ssh",
                    f"{user}@{ip}",
                    "-pw",
                    f"{password}",
                    "-X",
                    "-batch",
                ]
            )

            if rooter == "true":
                prog.run(
                    'echo "'
                    + password
                    + '" | sudo -H -S '
                    + f"xauth add $(xauth -f ~{user}/.Xauthority list | tail -1)"
                )

                prog.run(
                    'echo "' + password + '" | sudo -H -S ' + command,
                    wait=True,
                    ident=command,
                )
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
            prog = Cmd(
                command=[
                    "PUTTY/GWSL_putty.exe",
                    "-ssh",
                    f"{user}@{ip}",
                    "-pw",
                    f"{password}",
                    "-X",
                ],
                console=True,
            )

    except Exception as e:
        logger.exception("Exception occurred")
    except KeyboardInterrupt:
        try:
            prog.kill()
            print("killing service")
        except BaseException:
            pass
