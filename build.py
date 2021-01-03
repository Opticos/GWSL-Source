import os
import shutil
from distutils.dir_util import copy_tree

from PyInstaller.__main__ import run


version = "137_trad"


print("\nBuilding Dashboard...")
run([
    'src/gwsl/cli.py', '-i=src/gwsl/assets/icon.ico', '-w', '-y', '-n=GWSL'
])


print("\nBuilding Service...")
run([
    'src/gwsl/tray.py',
    '-i=src/gwsl/assets/icon.ico',
    '-w',
    '-y',
    '-n=GWSL_service',
    '--hidden-import=pkg_resources',
    '--hidden-import=infi.systray'
])


print(f"\nCreating dist/GWSL_{version}")
try:
    os.mkdir(f"dist/GWSL_{version}")
except:
    print("Deleting Old Build")
    shutil.rmtree(f"dist/GWSL_{version}")
    os.mkdir(f"dist/GWSL_{version}")

print("Copying Assets...")
folders = ["assets", "locale", "PULSE", "PUTTY", "VCXSRV"]
for folder in folders:
    print("Merging:", folder)
    shutil.copytree(folder, f"dist/GWSL_{version}/" + str(folder))

print("Merging: Dashboard...")
copy_tree("dist/GWSL/", f"dist/GWSL_{version}/")

print("Merging: Service...")
copy_tree("dist/GWSL_service/", f"dist/GWSL_{version}/")


