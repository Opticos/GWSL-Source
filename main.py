# GWSL *lets do this*

# Copyright Paul-E/Opticos Studios 2020
# https://www.opticos.studio

import os
import subprocess
import sys
import time
from winreg import *

import key
import pymsgbox
from infi.systray import SysTrayIcon as tray

import iset

cwd = os.getcwd()

frozen = 'not'
if getattr(sys, 'frozen', False):
    # we are running in a bundle
    frozen = 'ever so'
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Nulls
systray = None
exiter = False


def open_about():
    try:
        subprocess.Popen(bundle_dir + "\\GWSL.exe --about")
    except Exception:
        logger.exception("Exception occurred")


def open_dashboard():
    print("dash")
    try:
        subprocess.Popen(bundle_dir + "\\GWSL.exe")
    except Exception:
        logger.exception("Exception occurred")


def quits():
    global exiter
    exiter = True
    # use this to exit
    pass


def toggle_clipboard(systray, force="toggle"):
    global menu, clipboard
    try:
        if force == "toggle":
            do = ask_clip()
        else:
            do = False
            clipboard = force

            if clipboard:
                clip = "Disable"
            else:
                clip = "Enable"

            menu = (("Default Window Mode", None,
                     [("Switch to Multi Window Mode", bundle_dir + "\\assets\\" + "multi.ico", multi_mode),
                      ("Switch to Single Window Mode", bundle_dir + "\\assets\\" + "single.ico", single_mode),
                      ("Switch to Fullscreen Mode", bundle_dir + "\\assets\\" + "full.ico", full_mode)]),
                    (clip + " Shared Clipboard", None, toggle_clipboard),
                    ("GWSL Dashboard", None, open_dashboard),
                    ("About", None, open_about),
                    ("Quit", None, quits))

            systray.shutdown()
            time.sleep(0.2)

            if mode == "multi":
                pass
            if mode == "full":
                message = "GWSL - Fullscreen Mode"
            else:
                message = "GWSL - Single Window Mode"

            systray = tray(
                bundle_dir +
                "\\assets\\" +
                ic,
                message,
                menu,
                default_menu_index=5)
            systray.start()
            restart_server()

        if do:
            if clipboard:
                clipboard = False

            else:
                clipboard = True

            sett = iset.read()
            sett["general"]["clipboard"] = clipboard
            iset.set(sett)

            if clipboard:
                clip = "Disable"
            else:
                clip = "Enable"

            menu = (("Default Window Mode", None,
                     [("Switch to Multi Window Mode", bundle_dir + "\\assets\\" + "multi.ico", multi_mode),
                      ("Switch to Single Window Mode", bundle_dir + "\\assets\\" + "single.ico", single_mode),
                      ("Switch to Fullscreen Mode", bundle_dir + "\\assets\\" + "full.ico", full_mode)]),
                    (clip + " Shared Clipboard", None, toggle_clipboard),
                    ("GWSL Dashboard", None, open_dashboard),
                    ("About", None, open_about),
                    ("Quit", None, quits))

            systray.shutdown()

            if mode == "multi":
                pass
            if mode == "full":
                message = "GWSL - Fullscreen Mode"
            else:
                message = "GWSL - Single Window Mode"

            systray = tray(
                bundle_dir +
                "\\assets\\" +
                ic,
                message,
                menu,
                default_menu_index=5)
            systray.start()
            restart_server()
        else:
            pass
    except Exception:
        logger.exception("Exception occurred")


def ask():
    choice = pymsgbox.confirm(
        text="Do you want to switch default window modes? This might force close some windows.",
        title="Switch Mode?",
        buttons=[
            "Yes",
            "No"])
    if choice == "Yes":
        return True
    else:
        return False


def ask_clip():
    choice = pymsgbox.confirm(
        text="Toggle the shared clipboard? This might force close some windows.",
        title="Toggle Clipboard?",
        buttons=[
            "Yes",
            "No"])
    if choice == "Yes":
        return True
    else:
        return False


def ask_restart():
    answer = pymsgbox.confirm(
        text="Hmm... The GWSL service just crashed or was closed. Do you want to restart the service?",
        title="Uh Oh!",
        buttons=[
            'Yes',
            'No'])
    if answer == "Yes":
        return True
    else:
        return False


def full_mode(systray):
    global mode, timer
    timer = time.perf_counter()
    try:
        if mode == "full":
            return True
        if ask():
            systray.update(hover_text="GWSL - Fullscreen Mode")
            sett = iset.read()
            sett["graphics"]["window_mode"] = "full"
            iset.set(sett)

            mode = "full"
            restart_server()
    except Exception:
        logger.exception("Exception occurred")


def multi_mode(systray):
    global mode, timer
    try:
        if mode == "multi":
            return True
        if ask():
            systray.update(hover_text="GWSL - Multi Window Mode")
            mode = "multi"
            sett = iset.read()
            sett["graphics"]["window_mode"] = "multi"
            iset.set(sett)
            restart_server()
    except Exception:
        logger.exception("Exception occurred")


def single_mode(systray):
    global mode, timer
    timer = time.perf_counter()
    try:
        if mode == "single":
            return True
        if ask():
            systray.update(hover_text="GWSL - Single Window Mode")
            mode = "single"
            sett = iset.read()
            sett["graphics"]["window_mode"] = "single"
            iset.set(sett)
            restart_server()
    except Exception:
        logger.exception("Exception occurred")


def restart_server():
    kill_server()
    start_server()


def kill_server():
    subprocess.getoutput('taskkill /F /IM vcxsrv.exe')
    subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
    # subprocess.getoutput('taskkill /F /IM GWSL_service.exe')


def start_server():
    global mode, clipboard
    default_arguments = [
        "-ac",
        "-wgl",
        "-compositewm",
        "-notrayicon",
        "-dpi",
        "auto"]
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
    subprocess.Popen(["VCXSRV/GWSL_vcxsrv.exe"] + default_arguments)


def get_running():
    proc_list = os.popen('tasklist').readlines()
    for proc in proc_list:
        if "GWSL_vcxsrv" in proc:
            return True
    return False


timer = time.perf_counter()


def main():
    global systray, mode, clipboard, exiter, ic, timer
    # Kill VcXsrv if already running
    if get_running():
        kill_server()

    # Start VcXsrv
    start_server()

    # Start Tray Icon
    systray = tray(
        bundle_dir +
        "\\assets\\" +
        ic,
        "GWSL - Multi Window Mode",
        menu,
        default_menu_index=5)
    systray.start()

    # start service listener
    timer = time.perf_counter()
    while True:
        try:
            if time.perf_counter() - timer > 4:
                timer = timer = time.perf_counter()
                if get_running() == False:
                    if mode == "single":
                        systray.update(hover_text="GWSL - Multi Window Mode")
                        mode = "multi"
                        sett = iset.read()
                        sett["graphics"]["window_mode"] = "multi"
                        iset.set(sett)
                        restart_server()
                    elif ask_restart():
                        restart_server()

                    else:
                        systray.shutdown()
                        kill_server()
                        subprocess.getoutput('taskkill /F /IM GWSL.exe')
                        sys.exit()
                registry = ConnectRegistry(None, HKEY_CURRENT_USER)
                key = OpenKey(
                    registry,
                    r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
                key_value = QueryValueEx(key, 'SystemUsesLightTheme')
                k = int(key_value[0])

                if k == 0:
                    ic = "logo.ico"
                    systray.update(icon=bundle_dir + "\\assets\\" + "logo.ico")
                else:
                    ic = "logodark.ico"
                    systray.update(
                        icon=bundle_dir +
                             "\\assets\\" +
                             "logodark.ico")

            if exiter:
                kill_server()
                subprocess.getoutput('taskkill /F /IM GWSL.exe')
                systray.shutdown()
                sys.exit()
        # except OSError:
        #    systray.shutdown()
        #    kill_server()
        #    subprocess.getoutput('taskkill /F /IM GWSL.exe')
        #    sys.exit()

        except Exception:
            logger.exception("Exception occurred")
        time.sleep(2)

    kill_server()
    systray.shutdown()
    sys.exit()


if __name__ == "__main__":
    # main_thread
    try:
        sett_path = os.getenv('APPDATA') + "\\GWSL"
        if os.path.isdir(sett_path) == False:
            os.mkdir(sett_path)
            print("creating appdata directory")

        if os.path.exists(sett_path + "\\settings.json") == False:
            iset.create(sett_path + "\\settings.json")
            print("creating settings")

        iset.path = sett_path + "\\settings.json"
        import logging

        logger = logging.getLogger(__name__)
        # Create handlers
        f_handler = logging.FileHandler(sett_path + '\\service.log')
        f_handler.setLevel(logging.ERROR)

        f_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(f_handler)
    except BaseException:
        sett_path = os.getenv('APPDATA') + "\\GWSL\\errorbegin"
        if os.path.isdir(sett_path) == False:
            os.mkdir(sett_path)
        sys.exit()

    try:
        import ctypes
        import platform

        if int(platform.release()) >= 8:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except Exception as e:
        logger.exception("Exception occurred")

    try:
        registry = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(
            registry,
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        key_value = QueryValueEx(key, 'SystemUsesLightTheme')
        k = int(key_value[0])
        if k == 0:
            ic = "logo.ico"
        else:
            ic = "logodark.ico"

        # if len(sys.argv) > 1:
        #    print("using argument")
        #    iset.path = sys.argv[1]
        # else:
        #    print("standalone")

        # defaults
    except Exception as e:
        logger.exception("Exception occurred")
    try:
        mode = iset.read()["graphics"]["window_mode"]
        clipboard = iset.read()["general"]["clipboard"]

        if not clipboard:
            clip = "Enable"
        else:
            clip = "Disable"

        menu = (("Default Window Mode", None,
                 [("Switch to Multi Window Mode", bundle_dir + "\\assets\\" + "multi.ico", multi_mode),
                  ("Switch to Single Window Mode", bundle_dir + "\\assets\\" + "single.ico", single_mode),
                  ("Switch to Fullscreen Mode", bundle_dir + "\\assets\\" + "full.ico", full_mode)]),
                (clip + " Shared Clipboard", None, toggle_clipboard),
                ("GWSL Dashboard", None, open_dashboard),
                ("About", None, open_about),
                ("Quit", None, quits))
        key.add_hotkey('alt+ctrl+g', open_dashboard, args=systray)
        main()
    except Exception as e:
        logger.exception("Exception occurred")
