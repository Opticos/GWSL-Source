"""Json Settings manager."""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, ValidationError

from gwsl.utils import apps_use_light_theme

CURRENT_SETTINGS_VERSION = 4


class WindowMode(str, Enum):
    """X server window mode."""

    DEFAULT = "Default"
    FULLSCREEN = "full"
    SINGLE = "single"
    MULTI = "multi"
    CUSTOM = "custom"

    def __str__(self):
        return self.value


class Theme(str, Enum):
    """Linux app theme setting."""

    FOLLOW_WINDOWS = "follow"
    LIGHT_MODE = "light"
    DARK_MODE = "dark"

    def __str__(self):
        return self.value


class Clipboard(str, Enum):
    """X server clipboard settings."""

    DEFAULT = "Default"
    DIISABLED = "Disabled"
    ENABLED = "Enabled"

    def __str__(self):
        return self.value


class GeneralSettings(BaseModel):
    """General settings."""
    position: str = "right"  # TODO: enum
    start_menu_mode: bool = False
    shell_gui: str = "cmd"


class XProfile(BaseModel):
    """X server profile settings."""
    name: str
    arguments: List[str] = Field(default_factory=list)


class GraphicsSettings(BaseModel):
    """X server related settings."""
    window_mode: WindowMode = WindowMode.MULTI
    xserver_profiles: List[XProfile] = Field(default_factory=list)
    custom_profile: str = None
    clipboard: bool = True

    __MODES_DESC__ = {
        WindowMode.FULLSCREEN: "Fullscreen Mode",
        WindowMode.MULTI: "Multi Window Mode",
        WindowMode.SINGLE: "Single Window Mode",
    }

    @property
    def profile_args(self) -> List[str]:
        """Profile arguments for X server."""
        if self.window_mode == WindowMode.CUSTOM:
            return ["-ac"] + next(
                p.arguments
                for p in self.xserver_profiles
                if p.name == self.custom_profile
            )
        args = ["-ac", "-wgl", "-compositewm", "-notrayicon", "-dpi", "auto"]
        if self.window_mode == WindowMode.MULTI:
            args.append("-multiwindow")
        elif self.window_mode == WindowMode.FULLSCREEN:
            args.append("-fullscreen")
        prefix = "" if self.clipboard else "no"
        args.append(f"-{prefix}clipboard")
        args.append(f"-{prefix}primary")
        return args

    @property
    def profile_name(self):
        """Name of the current X server profile or window mode."""
        if self.window_mode == WindowMode.CUSTOM:
            return self.custom_profile
        return self.__MODES_DESC__[self.window_mode]


class PuttySettings(BaseModel):
    """SSH settings."""
    ip: str = None


def default_distro_blacklist():
    """Default distribution blacklist."""
    return ["docker"]


class Settings(BaseModel):
    """Main GWSL settings."""
    conf_ver: int = CURRENT_SETTINGS_VERSION
    general: GeneralSettings = GeneralSettings()
    graphics: GraphicsSettings = GraphicsSettings()
    putty: PuttySettings = PuttySettings()
    distro_blacklist: List[str] = Field(default_factory=default_distro_blacklist)
    app_blacklist: List[str] = Field(default_factory=list)

    @classmethod
    def from_json(cls, path: Path) -> Settings:
        """Load the settings from a json file."""
        with open(path, "r") as json_file:
            return cls.parse_raw(json_file.read())

    def save(self, path: Path) -> None:
        """Save the settings to a json file."""
        with open(path, "w") as json_file:
            json_file.write(self.json(indent=True))

    @classmethod
    def create(cls, path: Path) -> Settings:
        """Create a new settings file with defaults."""
        instance = cls()
        instance.save(path)
        return instance

    @classmethod
    def load_or_create(cls, path: Path) -> Settings:
        """Load the settings from a json file or create one if it doesn't exist."""
        if path.exists():
            try:
                return cls.from_json(path)
            except ValidationError:
                # TODO: alert/log
                return cls.create(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return cls.create(path)

    def get_clipboard_settings(self, from_cli):
        """Return the clipboard settings."""
        return self.graphics.clipboard if from_cli == Clipboard.DEFAULT else from_cli

    def get_mode_settings(self, from_cli):
        """Return the window mode settings."""
        return self.graphics.window_mode if from_cli == WindowMode.DEFAULT else from_cli


def get_accent(theme: Theme) -> str:
    """Return the accent description."""
    if theme == Theme.DARK_MODE:
        return "dark"
    if theme == Theme.LIGHT_MODE:
        return "light"
    return "light" if apps_use_light_theme() else "dark"
