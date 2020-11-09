import os, subprocess

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

import time
def get_apps(machine):
    #try:
    #    os.remove(script[:-15] + ".scanapps")
    #except:
    #    pass
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" listapps'
    read = os.popen(cmd).read()
    #print("copy")
    #cmd2 = 'wsl.exe -d ' + str(machine) + ' cp ~/.scanapps ' + str(pat_con(script[:-15]))
    #subprocess.getoutput(cmd2)
    #print("read")
    #try:
    #    read = open(script[:-15] + ".scanapps", "r").read()
    #except:
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
                name = name[:name.index("#GenericName=") -  1]
            elif "GenericName=" in name:
                name = name[:name.index("GenericName=") -  1]
            elif "Name=" in name:
                name = name[:name.index("Name=") -  1]

            run = app[ind + 10:]
            
            
            if "Exec=" in run:
                run = run[:run.index("Exec=") -  1]
            if ":ico:" in run:
                run = run[:run.index(":ico:")]
                
            if "%" in run:
                run = run[:run.index("%") - 1]

            if "Icon=" in app:
                icon = app[app.index(":ico:") + 10:]
            else:
                icon=None

            apps.update({name:{"cmd":run, "ico":icon}})
    return apps



def gtk(machine, scale):
    if scale == 1 or scale == 2:
        cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" gtk' + str(scale)
        print(os.popen(cmd).read()[:-1])


def dbus(machine):
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" dbus'
    print(os.popen(cmd).read()[:-1])

        
def qt(machine, scale):
    if scale == 1 or scale == 2:
        cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" qt' + str(scale)
        print(os.popen(cmd).read()[:-1])

def export(machine, version):
    if version == 1 or version == 2:
        cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" export' + str(version)
        print(os.popen(cmd).read()[:-1])

def profile(machine):
    cmd = 'wsl.exe -d ' + str(machine) + ' "' + str(pat_con(script)) + '" profile'
    return os.popen(cmd).read()

