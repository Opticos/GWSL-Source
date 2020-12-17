# GWSL Source

## What is GWSL?
GWSL automates the process of running X on top of WSL and over SSH:
*  It lets you easily run graphical Linux apps on Windows 10.
*  It lets you run graphical apps located on remote Linux machines.
*  It provides a simple UI for launching Linux apps, managing them graphicaly, and creating customized Windows shortcuts for them.
*  All this at the click of a button! No memorization of commands necessary. *Easy!*


This is the actual code for GWSL. And some premade binaries.

## Downloading

GWSL can be downloaded from the releases tab or from the Microsoft Store. The Microsoft Store version is recommended.

<a href='//www.microsoft.com/store/apps/9nl6kd1h33v3?cid=storebadge&ocid=badge'><img src='https://developer.microsoft.com/store/badges/images/English_get-it-from-MS.png' alt='English badge' style='width: 50px'/></a>

(I cannot make it smaller for some reason :D)

# More Information

See assets/liceses.txt to see licenses for dependencies (VCXSRV and PUTTY) etc.

Please contact me if anything in the licenses is incorrect or confusing.

# Program Architecture

In case you want to contribute and/or build the program yourself, here is a quick rundown of the code.

```
manager.py # The GWSL Dashboard
main.py # The GWSL Service
animator.py # Handles Smooth Animations
blur.py # Applies Windows Acrylic to GWSL
exe_layer.py # Some Tools for SSH
GWSL_ssh.py # GUI for GWSL SSH Functionality
GWSL_profiles.py # GUI for XServer Profile Creation
iset.py # Handles the GWSL configuration file
OpticUI.py # Custom Graphics Library
singleton.py # From Tendo (https://tendo.readthedocs.io/en/latest/_modules/tendo/singleton.html). Edited to start faster.
wsl_tools.py # Python tools to work with WSL
build.py # Build the packages with PyInstaller
```


# Dependencies (all can be installed with pip)
You can do this in a virtualenv.
```
pygame #Verion 2. The latest.
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

# Donate

If you enjoy GWSL, please consider buying me a cup of coffee. I worked hard to make it free and plan to spend alot of time supporting it. Donations are greaty appreciated.

[Donate with PayPal (any amount helps!)](https://www.paypal.com/donate/?cmd=_donations&business=VV8W4XA2PZ5R8&item_name=GWSL+Donation&currency_code=USD&Z3JncnB0=)

# GWSL Website
https://opticos.github.io/gwsl/
