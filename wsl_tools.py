import os
import subprocess
import time

script = None


def pat_con(path):
    if "/" in path:
        pt = path.split("/")
    else:
        pt = path.split("\\")
    lin = "/mnt/" + pt[0][0].lower()
    for f in pt[1:]:
        lin += "/" + str(f.lower())
    return lin


def get_themes(machine):
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" listthemes'
    read = os.popen(cmd).read()
    read = read.split(":theme:")
    read[:] = (value for value in read if value != "\n")
    read[:] = (value for value in read if value != "\n\n")
    themes = []
    for theme in read:
        if theme.startswith("\n"):
            theme = theme[1:]
        if theme == "/usr/share/themes":
            continue
        string = "/usr/share/themes/"
        if string in theme:
            theme = theme[theme.index(string) + len(string):]
        string2 = ".themes/"
        if string2 in theme:
            theme = theme[theme.index(string2) + len(string2):]
        themes.append(theme)

    return themes


from xdg.DesktopEntry import DesktopEntry
class WSLApp: #Credit to @sanzoghenzo on github. I did some adapting
    def from_dotdesktop(app_def):
        """
        Return a WSLApp from a .desktop file.

        Args:
            app_def: .desktop file path
        """
        de = DesktopEntry(app_def)
        name = de.getName()
        generic_name = de.getGenericName()
        cmd = de.getExec()
        gui = not de.getTerminal()
        icon = de.getIcon()
        
        return {"name":name, "generic_name":generic_name, "cmd":cmd, "gui":gui, "icon":icon}

        #raise IOError("Cannot read the .desktop entry")


def get_apps(machine):
    #first make sure the machine is booted. Scanning should do the trick
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" listapps'
    read = os.popen(cmd).read()
    apps = read.splitlines()
    #apps.remove("")
    app_dict = {}
    for app in apps:
        if "screensaver" in app:
            continue
        try:
            path = r"\\wsl$" + "\\" + machine + app
            wsl_app = WSLApp.from_dotdesktop(path)
            if wsl_app["gui"] == True:
                app_dict.update({wsl_app["name"]: {"cmd": wsl_app["cmd"], "ico": wsl_app["icon"]}})
        except:
            pass
        
                
    #print(read)
    return app_dict


def get_apps_old(machine):
    # try:
    #    os.remove(script[:-15] + ".scanapps")
    # except:
    #    pass
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" listappsold'
    read = os.popen(cmd).read()
    # print("copy")
    # cmd2 = 'wsl.exe -d ' + str(machine) + ' cp ~/.scanapps ' + str(pat_con(script[:-15]))
    # subprocess.getoutput(cmd2)
    # print("read")
    # try:
    #    read = open(script[:-15] + ".scanapps", "r").read()
    # except:
    #    return {}

    read = read.split("/:/")
    read[:] = (value for value in read if value != "\n")
    apps = {}
    for app in read:
        if "Name" in app:
            if "screensaver" in app:
                continue
            ind = app.index(":cmd:")
            name = app[5:ind]
            if "#GenericName=" in name:
                name = name[:name.index("#GenericName=") - 1]
            elif "GenericName=" in name:
                name = name[:name.index("GenericName=") - 1]
            elif "Name=" in name:
                name = name[:name.index("Name=") - 1]

            run = app[ind + 10:]

            if "Exec=" in run:
                #print(run)
                run = run[:run.index("Exec=") - 1]
            if ":ico:" in run:
                run = run[:run.index(":ico:")]

            if "%" in run:
                run = run[:run.index("%") - 1]

            if "Icon=" in app:
                icon = app[app.index(":ico:") + 10:]
            else:
                icon = None

            apps.update({name: {"cmd": run, "ico": icon}})
    return apps

def export_v(machine, name, value, shell="bash"):
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + f'" export-v {name} {value} {shell}'
    print(os.popen(cmd).read()[:-1])

def gtk(machine, scale, shell="bash"):
    export_v(machine, "GDK_SCALE", scale, shell=shell)
    """
    if scale == 1 or scale == 2:
        cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" gtk' + str(scale)
        print(os.popen(cmd).read()[:-1])"""
    

def qt(machine, scale, shell="bash"):
    export_v(machine, "QT_SCALE_FACTOR", scale, shell=shell)
    """
    if scale == 1 or scale == 2:
        cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" qt' + str(scale)
        print(os.popen(cmd).read()[:-1])"""
        

def dbus(machine):
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" dbus'
    print(os.popen(cmd).read()[:-1])





def export(machine, version, shell="bash"):
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" export-d ' + str(version) + " " + shell
    print(cmd)
    print(os.popen(cmd).read()[:-1])

def cleanup(machine):
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" cleanup'
    print(cmd)
    print(os.popen(cmd).read()[:-1])
    
    
def profile(machine, shell="bash"):
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" profile ' + shell
    return os.popen(cmd).read()
