# GWSL Service

import os
import subprocess
import sys
import time
import keyboard
import psutil

import GWSL_profiles as profile
# Copyright Paul-E/Opticos Studios 2021
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
server_PID = 0
audio_server_PID = 0

# Globals
clipboard = True

display_mode = "m"

hashtag_the_most_default = ["-ac", "-wgl", "-compositewm", "-notrayicon", "-dpi", "auto"]

default_profiles = {"m": hashtag_the_most_default + ["-multiwindow"],
                    "s": hashtag_the_most_default,
                    "f": hashtag_the_most_default + ["-fullscreen"]}

audio_enabled = True


current_custom_profile = None

profile_dict = {}
custom_profiles = []

# DPI Stuff
hidpi = True
    

def rescan(systray=False):
    """Rescan config"""
    global profile_dict, custom_profiles, hidpi
    try:
        sett = iset.read()
        profile_dict = sett["xserver_profiles"]
        hidpi = sett["graphics"]["hidpi"]
        
        if systray != False:
            menu = build_menu()
            systray.update(menu_options=menu)
        custom_profiles = list(profile_dict)
    except:
        logger.exception("Exception occurred - Cannot scan profiles")
        custom_profiles = []


def get_args(profile_name):
    """Get defaults for launching VCXSRV with a given profile"""
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
    """Returns path of named icon"""
    return f"{bundle_dir}\\assets\\systray\\{name}.ico"


def set_custom_profile(systray, profile):
    """Switch to custom profile"""
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
    """Sets the default XServer display mode (single, multi, fullscreen)"""
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
    """Toggles the clipboard between Windows and WSL graphical apps being on/off. (Only functional in 3 default profiles)"""
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


def config(systray):
    """Open the config file for GWSL (settings.json)"""
    try:
        path = os.getenv('APPDATA') + "\\GWSL\\"
        os.popen(f"{path}settings.json")
    except:
        logger.exception("Exception occurred - Cannot open Config File")


def open_logs(systray):
    """Launches Notepad to view GWSL logs"""
    try:
        path = os.getenv('APPDATA') + "\\GWSL\\"
        subprocess.Popen(f"notepad {path}service.log")
        subprocess.Popen(f"notepad {path}dashboard.log")
    except:
        logger.exception("Exception occurred - Cannot Open Logs")


def open_help(s):
    """Open browser to GWSL help page"""
    import webbrowser
    webbrowser.get('windows-default').open('https://opticos.github.io/gwsl/help.html')

def open_discord(s):
    """Open browser to GWSL Discord invite page"""
    import webbrowser
    webbrowser.get('windows-default').open('https://discord.com/invite/VkvNgkH')

def add_profile(systray):
    """Allows one to add a custom XServer profile (config)"""
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


def dpi_set(systray, hi_dpi):
    """Changes vcxsrv main dpi backend server"""
    global hidpi
    if hi_dpi != hidpi:
        try:
            sett = iset.read()
            sett["graphics"]["hidpi"] = hi_dpi
            iset.set(sett)
            #hidpi = hi_dpi
        except:
            logger.exception("Exception occurred - Cannot Change DPI (dpi_set)")

        if ask_dpi() == True:
            rescan()
            menu = build_menu()
            systray.update(menu_options=menu)
            restart_server()


def reset_config(systray):
    """Resets settings.json to original config, clears GWSL logs"""
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
    """Builds the configuration menu"""
    try:
        menu = []

        modes = {"m": "multi", "s": "single", "f": "full", "c": "custom"}

        mode_names = {"m": "Multi Window", "s": "Single Window", "f": "Fullscreen", "c": current_custom_profile}

        defaults = [["Multi Window Mode", icon("multi"), set_default_profile, "m"],
                    ["Single Window Mode", icon("single"), set_default_profile, "s"],
                    ["Fullscreen Mode", icon("full"), set_default_profile, "f"]]

        l = [" (active)", icon("check")]
        w = ["", icon("dpi_win")]
        dpi_mode = "(Linux)"
        if hidpi == False:
            w = l
            l = ["", icon("dpi_lin")]
            dpi_mode = "(Windows)"
        
        dpi_options = [(f"DPI Scaling Mode {dpi_mode}", icon("dpi"), [("Linux - Sharper but Slower" + l[0], l[1], dpi_set, True),
                                                          ("Windows - Faster but Blurrier" + w[0], w[1], dpi_set, False)])]#,
                                                          #("Windows GDI Enhanced", icon("dpi_enhanced"), dpi_set, 2)])]
        
        options = [("Configure GWSL", icon("config"), config),
                   ("Log and Configuration Cleanup", icon("refresh"), reset_config),
                   ("View Logs", icon("logs"), open_logs),
                   ("Dashboard", icon("dashboard"), open_dashboard),
                   ("About", icon("info"), open_about),
                   ("Help", icon("help"), open_help),
                   #("GWSL Discord Server", icon("discord"), open_discord),
                   ("Exit", icon("quit"), shutdown)]

        current_icon = icon(modes[display_mode])

        profiles = defaults
        
        for profile in custom_profiles:
            text = "Custom - " + str(profile) + ""
            prof = [text, icon("custom"), set_custom_profile, profile]
            profiles.append(prof)
        
        mode_name = mode_names[display_mode]
        
        for p in profiles:
            profile_id = p[3]
            if display_mode == "c":
                if profile_id == mode_name:
                    p[0] = p[0] + " (active)"
                    p[1] = icon("check")

            else:
                if display_mode == profile_id:
                    p[0] = p[0] + " (active)"
                    p[1] = icon("check")

            
            
        profiles = [tuple(l) for l in profiles] #make it a list of tuples
        
        menu.append((f"XServer Profiles ({mode_name})", current_icon,
                     profiles + [("Add A Profile", icon("add"), add_profile)]))
            
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
    """Prompts user to confirm switching XServer profiles"""
    choice = pymsgbox.confirm(text="Switch XServer profiles? Be sure to save any work open in GWSL programs. "
                                   "This might force-close some windows.",
                              title="Switch Profile",
                              buttons=["Yes", "No"])
    if choice == "Yes":
        return True
    else:
        return False


def ask_clip(phrase):
    """Prompts user to confirm enabling/disabling the shared clipboard"""
    choice = pymsgbox.confirm(text="Toggle the shared clipboard? Be sure to save any work open in GWSL programs. "
                                   "This might force-close some windows.",
                              title=f"{phrase} Clipboard",
                              buttons=["Yes", "No"])
    if choice == "Yes":
        return True
    else:
        return False


def ask_dpi():
    """Prompts user to confirm changing DPI"""
    choice = pymsgbox.confirm(text="To apply changes, the GWSL will close. Be sure to save any work open in GWSL "
                                   "programs. This will force close windows running in GWSL. Restart now?",
                              title=f"Restart XServer to Apply Changes?",
                              buttons=["Yes", "No"])
    if choice == "Yes":
        return True
    else:
        return False


def ask_reset():
    """Prompts user to confirm clearing logs and resetting config"""
    choice = pymsgbox.confirm(text="Delete GWSL logs and reset configuration? This will not delete shortcuts. "
                                   "The GWSL XServer will need to be restarted. Be sure to save any work open in GWSL "
                                   "programs. This will force close windows running in GWSL.",
                              title=f"Clear GWSL Data?",
                              buttons=["Yes", "No"])
    if choice == "Yes":
        return True
    else:
        return False


def ask_restart():
    """Prompts user to confirm restarting the GWSL service"""
    answer = pymsgbox.confirm(
        text="Hmm... The main GWSL service just crashed or was closed. Do you want to restart the service? If any GWSL windows are still open, they will be closed. Please save your work in those windows before clicking yes.",
        title="XServer Has Stopped",
        buttons=['Yes', 'No'])
    if answer == "Yes":
        return True
    else:
        return False


def restart_server():
    """Restarts GWSL services"""
    global server_PID
    server_PID = "reloading"
    kill_server()
    start_server()


def kill_server(all_servers=False):
    """Stops the GWSL services"""

    """
    #subprocess.getoutput('taskkill /F /IM vcxsrv.exe')
    #subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
    print("startkill")
    #Make sure PID actually points to vcxsrv
    service_name = subprocess.getoutput(f'tasklist /nh /fo csv /FI "PID eq {server_PID}"').split(",")[0]
    if "GWSL_vcxsrv" in service_name:
        print(f'taskkill /F /pid {server_PID}')
        subprocess.getoutput(f'taskkill /F /pid {server_PID}')
    else:
        #resort to older method
        print("killing all vcxsrv")
    """
    subprocess.getoutput('taskkill /F /IM vcxsrv.exe')
    subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv.exe')
    subprocess.getoutput('taskkill /F /IM GWSL_vcxsrv_lowdpi.exe')

    
def kill_audio():
    print(subprocess.getoutput("taskkill /IM pulseaudio.exe /F"))
    try:
        print(subprocess.getoutput(r"del %USERPROFILE%\.pulse\%USERDOMAIN%-runtime\pid /q"))
    except:
        pass
    try:
        print(subprocess.getoutput(r"del %USERPROFILE%\.pulse\%COMPUTERNAME%-runtime\pid /q"))
    except:
        pass
    
def start_audio():
    global audio_server_PID, audio_enabled
    if audio_enabled:
        print("starting audio")
        #proc = subprocess.Popen([f"PULSE/bin/pulseaudio.exe", "--cleanup-shm"], shell=True)
        proc = subprocess.Popen(["PULSE/bin/pulseaudio.exe", "-D"], stdout = subprocess.PIPE,
                               creationflags = subprocess.CREATE_NO_WINDOW)

        #audio_server_PID = proc.pid
    else:
        print("Audio Disabled")

def start_server():
    """Starts the GWSL services"""
    global server_PID
    #start video
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
        hidpi_str = ""
        if hidpi == False:
            hidpi_str = "_lowdpi"
        proc = subprocess.Popen([f"VCXSRV/GWSL_vcxsrv{hidpi_str}.exe"] + default_arguments)
        server_PID = proc.pid
    except:
        logger.exception("Exception occurred - Cannot Start VcXsrv")


def get_running():
    """Checks whether the GWSL service is currently running"""
    """
    service_name = subprocess.getoutput(f'tasklist /nh /fo csv /FI "PID eq {server_PID}"').split(",")[0]
    if server_PID == "reloading":
        return True
    if "GWSL_vcxsrv" in service_name:
        return True
    return False
    """
    #Psutil method
    if server_PID == "reloading":
        return True
    
    for p in psutil.process_iter(attrs=["pid"]):
        try:
            name = int(p.info['pid'])
            if int(server_PID) == name:
                return True
        except:
            continue
    return False


def get_audio_running():
    """Checks whether the GWSL service is currently running"""
    """
    service_name = subprocess.getoutput(f'tasklist /nh /fo csv /FI "IMAGENAME eq pulseaudio.exe"').split(",")[0]
    if "pulseaudio.exe" in service_name:
        return True
    return False
    """
    #Psutil method
    for p in psutil.process_iter(attrs=["name"]):
        try:
            name = p.info['name'].lower()
            if "pulseaudio.exe" in name:
                return True
        except:
            continue
    return False


def main():
    """Main entry point for application"""
    global systray, display_mode, clipboard, exiter, ic, timer, audio_enabled
    # Kill VcXsrv if already running
    #if get_running(): we dont need to check do we...

    kill_server()
    kill_audio()

    # Start VcXsrv
    start_server()
    # Start audio
    try:
        sett = iset.read()
        audio_enabled = sett["general"]["pulseaudio"]
    except:
        pass
    start_audio()

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
                        kill_audio()
                        subprocess.getoutput('taskkill /F /IM GWSL.exe')
                        sys.exit()
                if audio_enabled == True:
                    if not get_audio_running():
                        #if pulseaudio crashes
                        kill_audio()
                        start_audio()
                    
            if exiter:
                kill_server()
                kill_audio()
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
