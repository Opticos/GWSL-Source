# GWSL Service

import os
import subprocess
import sys
import time
import keyboard

import GWSL_profiles as profile
# Copyright Paul-E/Opticos Studios 2020
# https://opticos.github.io/gwsl/
import iset
import pymsgbox
from systray import SysTrayIcon as tray

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

# Globals
clipboard = True

display_mode = "m"

hashtag_the_most_default = ["-ac", "-wgl", "-compositewm", "-notrayicon", "-dpi", "auto"]

default_profiles = {"m": hashtag_the_most_default + ["-multiwindow"],
                    "s": hashtag_the_most_default,
                    "f": hashtag_the_most_default + ["-fullscreen"]}

current_custom_profile = None

profile_dict = {}
custom_profiles = []

# DPI Stuff
from winreg import *
modes = ["~ HIGHDPIAWARE", "~ DPIUNAWARE", "~ GDIDPISCALING DPIUNAWARE"]
REG_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"


def set_reg(name, value):
    try:
        CreateKey(HKEY_CURRENT_USER, REG_PATH)
        registry_key = OpenKey(HKEY_CURRENT_USER, REG_PATH, 0, KEY_WRITE)
        SetValueEx(registry_key, name, 0, REG_SZ, value)
        CloseKey(registry_key)
        return True
    except:
        logger.exception("Exception occurred - Cannot Change DPI (set_reg)")
    

def rescan(systray=False):
    global profile_dict, custom_profiles
    try:
        sett = iset.read()
        profile_dict = sett["xserver_profiles"]
        if systray != False:
            menu = build_menu()
            systray.update(menu_options=menu)
        custom_profiles = list(profile_dict)
    except:
        logger.exception("Exception occurred - Cannot scan profiles")
        custom_profiles = []


def get_args(profile_name):
    return profile_dict[profile_name]


def open_about(systray):
    try:
        subprocess.Popen(bundle_dir + "\\GWSL.exe --about")
    except:
        logger.exception("Exception occurred")


def open_dashboard(*args):
    try:
        subprocess.Popen(bundle_dir + "\\GWSL.exe")
    except:
        logger.exception("Exception occurred")


def shutdown(systray):
    global exiter
    exiter = True


def icon(name):
    return f"{bundle_dir}\\assets\\systray\\{name}.ico"


def set_custom_profile(systray, profile):
    global current_custom_profile, display_mode
    try:
        if profile == current_custom_profile:
            return True
        if ask():
            sett = iset.read()
            sett["graphics"]["window_mode"] = profile
            iset.set(sett)
            display_mode = "c"
            current_custom_profile = profile

            menu = build_menu()
            systray.update(hover_text=f"GWSL Running - {profile}", menu_options=menu)
            print("setting", profile)

            restart_server()
    except:
        logger.exception("Exception occurred - Cannot switch to custom profile " + str(profile))


def set_default_profile(systray, mode_type):
    global current_custom_profile, display_mode
    try:
        if mode_type == display_mode:
            return True
        if ask():
            sett = iset.read()
            mode_names = {"m": "multi", "s": "single", "f": "full"}
            sett["graphics"]["window_mode"] = mode_names[mode_type]
            iset.set(sett)
            display_mode = mode_type
            current_custom_profile = ""

            menu = build_menu()
            mode_names = {"m": "Multi Window", "s": "Single Window", "f": "Fullscreen"}
            name = mode_names[display_mode]
            systray.update(hover_text=f"GWSL Running - {name}", menu_options=menu)

            restart_server()
    except:
        logger.exception("Exception occurred - Cannot switch to profile type " + str(mode_type))


def toggle_clipboard(systray, state):
    global clipboard
    try:
        if state == True:
            phrase = "Enable"
        else:
            phrase = "Disable"
        if ask_clip(phrase):
            clipboard = state
            menu = build_menu()
            systray.update(menu_options=menu)
            sett = iset.read()
            sett["general"]["clipboard"] = clipboard
            iset.set(sett)

            restart_server()
    except:
        logger.exception("Exception occurred - Cannot toggle clipboard")


def config():
    try:
        path = os.getenv('APPDATA') + "\\GWSL\\"
        os.popen(f"{path}settings.json")
    except:
        logger.exception("Exception occurred - Cannot open Config File")


def open_logs():
    try:
        path = os.getenv('APPDATA') + "\\GWSL\\"
        subprocess.Popen(f"notepad {path}service.log")
        subprocess.Popen(f"notepad {path}dashboard.log")
    except:
        logger.exception("Exception occurred - Cannot Open Logs")


def open_help(s):
    import webbrowser
    webbrowser.get('windows-default').open('https://opticos.github.io/gwsl/help.html')


def add_profile(systray):
    try:
        new_profile = profile.add(bundle_dir)
        if new_profile != None:
            name = new_profile["name"]
            arguments = new_profile["args"].split(" ")
            sett = iset.read()
            sett["xserver_profiles"][name] = arguments
            iset.set(sett)
            rescan()
            menu = build_menu()
            systray.update(menu_options=menu)
    except:
        logger.exception("Exception occurred - Cannot Create Profile")


def dpi_set(mode):
    server_location = f"{bundle_dir}\\VCXSRV\\GWSL_vcxsrv.exe"
    instance_location = f"{bundle_dir}\\VCXSRV\\GWSL_instance.exe"
    print(server_location)
    print(instance_location)
    try:
        set_reg(server_location, modes[int(mode)])
        set_reg(instance_location, modes[int(mode)])
    except:
        logger.exception("Exception occurred - Cannot Change DPI (dpi_set)")

    if ask_dpi() == True:
        restart_server()


def reset_config(systray):
    global exiter
    if ask_reset():
        try:
            systray.shutdown()
            iset.create(sett_path + "\\settings.json")
            print("creating settings")
            print("Stopping Logger...")
            f_handler.close()
            logging.shutdown()
            print("Cleaning Logs...")
            try:
                os.remove(sett_path + '\\dashboard.log')
            except:
                pass
            try:
                os.remove(sett_path + '\\service.log')
            except:
                pass
            try:
                os.remove(sett_path + '\\settings.json')
            except:
                pass
            exiter = True
            kill_server()
            sys.exit()
        except:
            pass


def build_menu():
    try:
        menu = []

        modes = {"m": "multi", "s": "single", "f": "full", "c": "custom"}

        mode_names = {"m": "Multi Window", "s": "Single Window", "f": "Fullscreen", "c": current_custom_profile}

        defaults = [("Multi Window Mode", icon("multi"), set_default_profile, "m"),
                    ("Single Window Mode", icon("single"), set_default_profile, "s"),
                    ("Fullscreen Mode", icon("full"), set_default_profile, "f")]

        dpi_options = [("DPI Scaling Mode", icon("dpi"), [("Linux (GTK and QT)", icon("dpi_lin"), dpi_set, 0),
                                                          ("Windows (Faster but Blurrier)", icon("dpi_win"), dpi_set, 1),
                                                          ("Windows GDI Enhanced", icon("dpi_enhanced"), dpi_set, 2)])]
        
        options = [("Configure GWSL", icon("config"), config),
                   ("Log and Configuration Cleanup", icon("refresh"), reset_config),
                   ("View Logs", icon("logs"), open_logs),
                   ("Dashboard", icon("dashboard"), open_dashboard),
                   ("About", icon("info"), open_about),
                   ("Help", icon("help"), open_help),
                   ("Exit", icon("quit"), shutdown)]

        current_icon = icon(modes[display_mode])

        profiles = []
        
        for profile in custom_profiles:
            text = "Custom - " + str(profile) + ""
            prof = (text, icon("custom"), set_custom_profile, profile)
            profiles.append(prof)
        
        mode_name = mode_names[display_mode]
        menu.append((f"XServer Profiles ({mode_name})", current_icon,
                     defaults + profiles + [("Add A Profile", icon("add"), add_profile)]))
            
        menu.append(("Rescan Profiles", icon("refresh"), rescan))
        
        if display_mode != "c":
            # Clipboard options are only enabled for multi, single, and fullscreen default modes
            if clipboard:
                ico = icon("check")
                command = False
                phrase = "On"
            else:
                ico = icon("quit")
                command = True
                phrase = "Off"
            menu.append((f"Shared Clipboard ({phrase})", ico, toggle_clipboard, command))

        menu += dpi_options
        menu += options
        return menu
    except:
        logger.exception("Exception occurred - Cannot Build Menu")
        return []


def ask():
    choice = pymsgbox.confirm(text="Switch XServer profiles? Be sure to save any work open in GWSL programs. This might force-close some windows.",
                              title="Switch Profile",
                              buttons=["Yes", "No"])
    if choice == "Yes":
        return True
    else:
        return False


def ask_clip(phrase):
    choice = pymsgbox.confirm(text="Toggle the shared clipboard? Be sure to save any work open in GWSL programs. This might force-close some windows.",
                              title=f"{phrase} Clipboard",
                              buttons=["Yes", "No"])
    if choice == "Yes":
        return True
    else:
        return False


def ask_dpi():
    choice = pymsgbox.confirm(text="To apply changes, the GWSL will close. Be sure to save any work open in GWSL programs. This will force close windows running in GWSL. Restart now?",
                              title=f"Restart XServer to Apply Changes?",
                              buttons=["Yes", "No"])
    if choice == "Yes":
        return True
    else:
        return False


def ask_reset():
    choice = pymsgbox.confirm(text="Delete GWSL logs and reset configuration? This will not delete shortcuts. The GWSL XServer will need to be restarted. Be sure to save any work open in GWSL programs. This will force close windows running in GWSL.",
                              title=f"Clear GWSL Data?",
                              buttons=["Yes", "No"])
    if choice == "Yes":
        return True
    else:
        return False


def ask_restart():
    answer = pymsgbox.confirm(
        text="Hmm... The GWSL service just crashed or was closed. Do you want to restart the service?",
        title="XServer Has Stopped",
        buttons=['Yes', 'No'])
    if answer == "Yes":
        return True
    else:
        return False


def restart_server():
    kill_server()
    start_server()


def kill_server():
    subprocess.getoutput('taskkill /F /IM vcxsrv.exe')
    subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')


def start_server():
    try:
        if display_mode != "c":
            default_arguments = default_profiles[display_mode]
            if clipboard:
                default_arguments.append("-clipboard")
                default_arguments.append("-primary")
            else:
                default_arguments.append("-noclipboard")
                default_arguments.append("-noprimary")
        else:
            default_arguments = ["-ac"] + get_args(current_custom_profile)
        subprocess.Popen(["VCXSRV/GWSL_vcxsrv.exe"] + default_arguments)
    except:
        logger.exception("Exception occurred - Cannot Start VcXsrv")


def get_running():
    proc_list = os.popen('tasklist').readlines()
    for proc in proc_list:
        if "GWSL_vcxsrv" in proc:
            return True
    return False


def main():
    global systray, display_mode, clipboard, exiter, ic, timer
    # Kill VcXsrv if already running
    if get_running():
        kill_server()

    # Start VcXsrv
    start_server()

    # Start Tray Icon
    menu = build_menu()
    if display_mode == "c":
        name = current_custom_profile
    else:
        mode_names = {"m": "Multi Window", "s": "Single Window", "f": "Fullscreen"}
        name = mode_names[display_mode]
    systray = tray(ic, f"GWSL Running - {name}", menu, default_menu_index=open_dashboard)
    systray.start()

    # start service listener
    timer = time.perf_counter()
    while True:
        try:
            if time.perf_counter() - timer > 4:
                timer = timer = time.perf_counter()
                if not get_running():
                    # In case someone closes a single-window server... restart as multi window.
                    if display_mode == "s":
                        display_mode = "m"
                        menu = build_menu()
                        systray.update(hover_text="GWSL Running - Multi Window", menu_options=menu)
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

            if exiter:
                kill_server()
                subprocess.getoutput('taskkill /F /IM GWSL.exe')
                systray.shutdown()
                sys.exit()

        except:
            logger.exception("Exception occurred in main loop")
            kill_server()
            systray.shutdown()
            sys.exit()

        time.sleep(2)

    kill_server()
    systray.shutdown()
    sys.exit()


if __name__ == "__main__":
    # main_thread
    # Create Appdata directory if manager has not done so
    try:
        sett_path = os.getenv('APPDATA') + "\\GWSL"
        if not os.path.isdir(sett_path):
            os.mkdir(sett_path)
            print("creating appdata directory")

        if not os.path.exists(sett_path + "\\settings.json"):
            iset.create(sett_path + "\\settings.json")
            print("creating settings")

        iset.path = sett_path + "\\settings.json"

        # Start Logging
        import logging

        logger = logging.getLogger(__name__)
        # Create handlers
        f_handler = logging.FileHandler(sett_path + '\\service.log')
        f_handler.setLevel(logging.ERROR)

        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(f_handler)
    except:
        sett_path = os.getenv('APPDATA') + "\\GWSL\\errorbegin"
        if not os.path.isdir(sett_path):
            os.mkdir(sett_path)
        sys.exit()

    try:
        import ctypes
        import platform

        if int(platform.release()) >= 8:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except:
        logger.exception("Exception occurred - Cannot Set DPI Aware")

    try:
        mode = iset.read()["graphics"]["window_mode"]
        key = {"multi": "m", "single": "s", "full": "f"}
        try:
            if key[mode] == "m" or key[mode] == "s" or key[mode] == "f":
                print("We have a default!! Hooray!")
                display_mode = key[mode]
                clipboard = iset.read()["general"]["clipboard"]
            else:
                print("We have a custom profile")
                current_custom_profile = mode
        except:
            print("We have a custom profile")
            current_custom_profile = mode
            display_mode = "c"

        rescan()

        menu = build_menu()

        keyboard.add_hotkey('alt+ctrl+g', open_dashboard, args=systray)
        ic = icon("systray")
        main()
    except:
        logger.exception("Exception occurred - Cannot Start Service. Make sure the settings file is not corrupted.")
