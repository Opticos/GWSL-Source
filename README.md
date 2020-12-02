# GWSL Source

## What is GWSL?
GWSL automates the process of running X on top of WSL and over SSH:
*  It lets you easily run graphical Linux apps on Windows 10.
*  It lets you run graphical apps located on remote Linux machines.
*  It provides a simple UI for launching Linux apps, managing them graphicaly, and creating customized Windows shortcuts for them.
*  All this at the click of a button! No memorization of commands necessary. *Easy!*


This is the actual code for GWSL. And some premade binaries.

See assets/liceses.txt to see licenses for dependencies (VCXSRV and PUTTY) etc.

Please contact me if anything in the licenses is incorrect or confusing.

# Program Architecture
```
manager.py # The GWSL Dashboard
main.py # The GWSL Service
animator.py # Handles Smooth Animations
blur.py # Applies Windows Acrylic to GWSL
exe_layer.py # Some Tools for SSH
GWSL_ssh.py # GUI for GWSL SSH Functionality
iset.py # Handles the GWSL configuration file
OpticUI.py # Custom Graphics Library
singleton.py # From Tendo (https://tendo.readthedocs.io/en/latest/_modules/tendo/singleton.html). Edited to start faster.
wsl_tools.py # Python tools to work with WSL
build.py # Build the packages with PyInstaller
```


# Dependencies (all can be installed with pip)
```
pygame
pywin32
winshell
Pillow
imtools
keyboard
pyinstaller==3.5
```

# Building GWSL
Clone the source from here, install the dependencies with pip, and run ```build.py```.

It will build to ```dist/GWSL_'version'/```.


The official build currently runs on Python 3.7

# GWSL Website
https://opticos.github.io/gwsl/
