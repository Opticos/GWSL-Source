# GWSL-Source
The actual code for GWSL. And some premade binaries.

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
```


# Dependencies (all can be installed with pip)
```
pygame
pywin32
winshell
Pillow
imtools
keyboard
```

The official build currently runs on Python 3.7

# GWSL Website
https://opticos.github.io/gwsl/
