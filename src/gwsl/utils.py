"""GUI utilities."""

import ctypes
import platform
from enum import Enum
from functools import wraps
from pathlib import Path
from statistics import mean
from typing import Union, Tuple, Any
from winreg import (
    ConnectRegistry,
    HKEY_CURRENT_USER,
    OpenKey,
    QueryValueEx,
    CloseKey,
    CreateKey,
    SetValueEx,
    KEY_WRITE,
    REG_SZ,
)

import PIL
import pygame
import win32gui
from PIL import Image
from fuzzywuzzy.process import extractOne
from wsl_tools import WSLDistro

import pymsgbox
from gwsl import paths


Color = Tuple[int, int, int]
Coords = Tuple[float, float]


# region Dialogs
def msgbox(title: str, text: str, button="OK") -> None:
    """
    Display a message box.

    Args:
        title: message box title
        text: message box text
        button: text of the button
    """
    pymsgbox.alert(title=title, text=text, button=button)


def yesno(text: str, title: str) -> bool:
    """
    Display a Yes/No dialog box and return true if "Yes" is pressed.

    Args:
        text: dialog box text
        title: dialog box title

    Returns:
        True if Yes is pressed.
    """
    choice = pymsgbox.confirm(text=text, title=title, buttons=["Yes", "No"])
    return choice == "Yes"


def ask_password(machine: Union[str, WSLDistro]) -> str:
    """
    Display a masked input dialog for password input.

    Args:
        machine: name of the WSL distribution

    Returns:
        password, None if the dialog is canceled.
    """
    return pymsgbox.password(
        text=f"Enter sudo password for {machine}:", title="Authentication"
    )


def ask_reboot(machine: Union[str, WSLDistro]) -> bool:
    """
    Display a dialog box to ask the user to reboot the WSL distro.

    Args:
        machine: WSL distro name

    Returns:
        True if the user choose to restart the distro
    """
    return yesno(text=f"Restart {machine} To Apply Changes?", title="Restart Machine?")


def exception_dialog(exc: Exception) -> None:
    """
    Display a message box with the exception info.

    Args:
        exc: exception
    """
    # TODO: collapsible panel with stacktrace (pretty-errors or similar)
    pymsgbox.alert(text=f"Error: {exc}", title="GWSL error", button="Ok")


def exception_catcher(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as exc:
            exception_dialog(exc)

    return wrapper


# endregion


# region Windows size and DPI
def set_dpi_awarness() -> None:
    """Set the DPI awarness for the current process."""
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)


set_dpi_awarness()
ppi = ctypes.windll.user32.GetDpiForSystem()


def get_pos(hwnd) -> Coords:
    """Return the position of a window."""
    rect = win32gui.GetWindowRect(hwnd)
    return int(rect[0]), int(rect[1])


def in2pix(inches: float) -> int:
    """Return the size in pixels using the system DPI."""
    return int(ppi * inches)


def _set_reg(key: str, name: str, value: Any):
    """Set the value of a registry key."""
    CreateKey(HKEY_CURRENT_USER, key)
    registry_key = OpenKey(HKEY_CURRENT_USER, key, 0, KEY_WRITE)
    SetValueEx(registry_key, name, 0, REG_SZ, value)
    CloseKey(registry_key)
    return True


class DPIAwarness(str, Enum):
    """DPI awarness options for applications."""

    LINUX = "~ HIGHDPIAWARE"
    WINDOWS = "~ DPIUNAWARE"
    WIN_GDI = "~ GDIDPISCALING DPIUNAWARE"


def set_app_dpi(app: Path, mode: DPIAwarness):
    """Set the DPI awarness of an app in the registry."""
    _set_reg(
        r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers",
        str(app),
        mode.value,
    )


# endregion


# region System colors
def _get_hkcu_key_value(key: str, name: str) -> Any:
    """
    Get the value of a HKCU registry key.

    Args:
        key: registry key
        name: sub-key name

    Returns:
        sub-key value
    """
    registry = ConnectRegistry(None, HKEY_CURRENT_USER)
    hkey = OpenKey(registry, key)
    # TODO: convert types https://docs.python.org/3.7/library/winreg.html#value-types
    value, type_id = QueryValueEx(hkey, name)
    CloseKey(hkey)
    return value


def _get_light(name: str) -> int:
    return int(
        _get_hkcu_key_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", name
        )
    )


def apps_use_light_theme() -> bool:
    """Return true if Windows apps use the light theme."""
    return _get_light("AppsUseLightTheme") == 1


def is_system_light_theme():
    """Return true if the Windows theme is light."""
    return _get_light("SystemUsesLightTheme") == 1


def get_explorer_accent() -> Color:
    """Return the Windows accent color."""
    colormenu = _get_hkcu_key_value(
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent", "AccentColorMenu"
    )
    hex_str = hex(colormenu - 4278190080).split("x")[1]
    return int(hex_str[4:6], 16), int(hex_str[2:4], 16), int(hex_str[0:2], 16)


def get_color() -> Color:
    """Return the Windows 10 user accent color corrected for darker colors."""
    rgb = get_explorer_accent()
    # Make the color lighter if needed
    return [0, 150, 150] if mean(rgb) < 30 else rgb


def get_system_light() -> Tuple[Color, Color, bool]:
    """Return the forground and accent colors based on the system colors."""
    accent = get_color()
    if is_system_light_theme():
        light = True
        fg_color = (0, 0, 0)
        accent = tuple(a - 50 if a > 50 else a for a in accent)
    else:
        light = False
        fg_color = (255, 255, 255)
    return fg_color, accent, light


# endregion


# region Icon manager
class IconManager:
    """Icon manager."""

    def __init__(self, icon_pack_path: Path):
        self._iconpack = None
        self.icons = {}
        self.load_icon_pack(icon_pack_path)

    def load_icon_pack(self, icon_pack_path: Path):
        """Load the icons of the icon pack found at the given path."""
        if self._iconpack != icon_pack_path:
            self._iconpack = icon_pack_path
        self.icons = {i.stem: i.resolve() for i in self._iconpack.glob("**/*.png")}

    def find_icon(self, name: str) -> Path:
        """Find the icon that best matches the given name."""
        best_match = extractOne(name, self.icons.keys(), score_cutoff=80)
        return self.icons[best_match[0] if best_match else "link"]

    def tk_icon(self, name: str) -> PIL.Image.Image:
        """Return the tkinter image that best matches the giben name."""
        filename = self.find_icon(name)
        try:
            return Image.open(filename)
        except (FileNotFoundError, PIL.UnidentifiedImageError):
            content = filename.read_text()
            if ".png" in content:
                return Image.open(filename.parent / content)
            return Image.open(paths.assets / "link.png")

    def pygame_icon(self, name: str) -> pygame.surface.Surface:
        """Return the pygame image that best matches the giben name."""
        filename = self.find_icon(name)
        try:
            return load_image_alpha(filename)
        except:
            content = filename.read_text()
            if ".png" in content:
                return load_image_alpha(filename.parent / content)
            return load_image_alpha(paths.assets / "link.png")


def load_image_alpha(filename: Path) -> pygame.surface.Surface:
    """Return the alpha enable image from the given path."""
    return pygame.image.load(str(filename)).convert_alpha()


# endregion
