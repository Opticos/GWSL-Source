import os
import PyInstaller.__main__
import shutil
from distutils.dir_util import copy_tree

version = "139 MSIX build 2 debug"


print("\nBuilding Dashboard...")
PyInstaller.__main__.run([
    'manager.py',
    '-i=assets/icon.ico',
    #'-w',
    '-y',
    '-n=GWSL',
    '--hidden-import=pkg_resources.py2_warn'
])


print("\nBuilding Service...")
PyInstaller.__main__.run([
    'main.py',
    '-i=assets/icon.ico',
    #'-w',
    '-y',
    '-n=GWSL_service',
    '--hidden-import=pkg_resources',
    '--hidden-import=infi.systray',
    '--hidden-import=pkg_resources.py2_warn'
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


