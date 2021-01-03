"""Paths and urls constants and utilities."""
import os
import sys
import shutil
import webbrowser
from pathlib import Path, PurePosixPath


def wslpath(path: Path) -> PurePosixPath:
    """Return the posix path of a Windows file or folder."""
    return PurePosixPath("/mnt").joinpath(path.drive[0].lower(), *path.parts[1:])


def get_bundle_dir() -> Path:
    """Return the location of the app."""
    if getattr(sys, "frozen", False):
        # we are running in a bundle
        return Path(sys._MEIPASS)
    else:
        # we are running in a normal Python environment
        return Path(__file__).resolve().parent


bundle = get_bundle_dir()
app = bundle / "GWSL.exe"
server = bundle / "VCXSRV" / "GWSL_vcxsrv.exe"
instance = bundle / "VCXSRV" / "GWSL_instance.exe"
assets = bundle / "assets"
asset_license = assets / "Licenses.txt"
font = assets / "segoeui.ttf"
icon_pack = assets / "Paper"
ico_font = assets / "SEGMDL2.ttf"
appdata = Path(os.getenv("APPDATA")) / "GWSL"
log = appdata / "dashboard.log"
service_log = appdata / "service.log"
settings = appdata / "settings.json"
license = appdata / "Licenses.txt"
systray = assets / "systray"
site_url = "https://opticos.github.io/gwsl/"
site_manual_url = f"{site_url}tutorials/manual.html"


def get_systray_icon(name: str) -> str:
    """Return the icon for the systray."""
    return str(systray / f"{name}.ico")


def ensure_paths() -> None:
    """Ensure the appdata directory and the base files in it exist."""
    appdata.mkdir(parents=True, exist_ok=True)
    if not log.exists():
        shutil.copy(asset_license, license)


TUTORIAL_MAP = {
    "machine chooser": "the-gwsl-user-interface",
    "configure": "configuring-a-wsl-distro-for-use-with-gwsl",
    "theme": "configuring-a-wsl-distro-for-use-with-gwsl",
    "launcher": "using-the-integrated-linux-app-launcher",
    "shortcut": "using-the-gwsl-shortcut-creator",
    "ssh": "using-gwsl-with-ssh",
}


def open_tutorial(topic: str) -> None:
    """Open the GWSL manual with the default web browser."""
    bookmark = TUTORIAL_MAP.get(topic, "")
    open_url(f"{site_manual_url}#{bookmark}")


def open_url(url: str) -> None:
    """Open the URL in the default browser."""
    webbrowser.get("windows-default").open(url)


def open_file(path: Path) -> None:
    """Open the file in the default application."""
    os.startfile(path.resolve())
