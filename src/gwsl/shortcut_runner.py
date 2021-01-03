import random
import subprocess
import threading
import time
from dataclasses import dataclass

from wsl_tools import WSLManager

from gwsl import paths
from gwsl.utils import ask_password
from gwsl import service
from gwsl import settings


@dataclass
class ShortcutSettings:
    """WSL app shortcut settings."""

    machine: str
    command: str
    mode: settings.WindowMode = settings.WindowMode.MULTI
    clipboard: settings.Clipboard = settings.Clipboard.DEFAULT
    # TODO: enums con "Default"
    gtk_scale: float = 1
    qt_scale: float = 1
    append: str = ""
    theme: settings.Theme = settings.Theme.FOLLOW_WINDOWS
    root: bool = False
    dbus: bool = False
    keep: bool = False
    icon: str = ""
    app_name: str = ""

    @property
    def default_mode_and_clipboard(self):
        """Use the default window mode and clipboard."""
        return (
            self.mode == settings.WindowMode.DEFAULT
            and self.clipboard == settings.Clipboard.DEFAULT
        )

    @property
    def commandline(self):
        """Arguments to add to the shortcut."""
        return [
            "run",
            self.machine,
            self.command,
            self.mode,
            self.clipboard,
            self.gtk_scale,
            self.qt_scale,
            self.append,
            self.theme,
            self.root,
            self.dbus,
            self.keep
        ]

    @property
    def shortcut_name(self):
        """Name of the shortcut to create."""
        root = " (root)" if self.root else ""
        return f"{self.command} on {self.machine}{root}"


def run(config: ShortcutSettings):
    """Shortcut runner."""
    service.start_service()
    defaults = settings.Settings.load_or_create(paths.settings)
    manager = WSLManager(defaults.distro_blacklist)
    try:
        machine = manager[config.machine]
    except KeyError:
        raise ValueError(f"No distro with name {config.machine} exists.")

    if config.root:
        code = ask_password(config.machine)
        if code is None:
            return
        passw = f"echo '{code}' | sudo -H -S "
    else:
        passw = ""

    # TODO: only if on ubuntu, handle empty password and dbus not running
    if config.dbus:
        machine.start_dbus(passw)

    # TODO: handle light/dark variation
    theme = f"{machine.theme_env}"
    gtk = "" if config.gtk_scale == 1 else f"GDK_SCALE={config.gtk_scale}"
    qt = "" if config.qt_scale == 1 else f"QT_SCALE_FACTOR={config.qt_scale}"
    ip = machine.ip if machine.version == 2 else ""

    if config.default_mode_and_clipboard:
        cli = f"{passw} {theme} DISPLAY={ip}:0 {qt} {gtk} {config.command} {config.append}"
        machine.run_command(cli)
        return

    # In this case, we need to start a new server,
    # run in a new thread that self closes VCXSRV after command
    # if in multi window mode
    port = str(random.randrange(1000, 9999))
    mode = defaults.get_mode_settings(config.mode)
    clipboard = defaults.get_clipboard_settings(config.clipboard)
    pid = service.start_server(port, mode, clipboard)

    cli = f"{passw} {theme} DISPLAY={ip}:{port} {qt} {gtk} {config.command} {config.append}"
    if mode == settings.WindowMode.SINGLE:
        machine.run_command(cli)
        return

    t = threading.Thread(
        target=threaded, args=(machine, cli, config.command, config.keep, pid, port)
    )
    t.daemon = True
    t.start()


def threaded(machine, cli, command, keep, server_pid, server_port):
    """Thread for detached shortcut runner."""
    machine.run_command(cli)
    while True:
        time.sleep(2)
        procs = machine.run_command("ps -ef")
        if command in str(procs):
            time.sleep(1)
        else:
            break
    if not keep:
        print(
            f"All of {command} terminated. "
            f"Killing Server Instance on port {server_port}"
        )
        print(subprocess.getoutput("taskkill /F /PID " + str(server_pid)))
    else:
        print(f"Didn't kill XServer. Keeping X on port {server_port}")
