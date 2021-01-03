"""
GWSL CLI.

Uses typer to create subcommands and parse CLI arguments,
then run the corresponding functions.
"""
import sys
from typing import Optional

import typer
import win32gui

from gwsl import dashboard, singleton
from gwsl import service
from gwsl import settings
from gwsl import shortcut_runner
from gwsl import ssh_runner
from gwsl.utils import exception_catcher

app = typer.Typer()


@app.command("run")
def run_shortcut(
    machine: str = typer.Argument(
        ...,
        help="Name of the WSL VM to run the program on.",
        # choices=manager.names  # TODO: manager singleton
    ),
    command: str = typer.Argument(..., help="Command to run."),
    mode: settings.WindowMode = typer.Option(
        default=settings.WindowMode.MULTI,
        help="window mode (single, multi or full).",
    ),
    clipboard: settings.Clipboard = typer.Option(
        default=settings.Clipboard.DEFAULT, help="enables shared clipoard."
    ),
    # TODO: enums con "Default"
    gtk_scale: float = typer.Option(default=1, help="HDPI scaling for GTK apps."),
    qt_scale: float = typer.Option(default=1, help="HDPI scaling for QT apps."),
    append: str = typer.Option(default="", help="arguments to append to the command."),
    theme: settings.Theme = typer.Option(
        default=settings.Theme.FOLLOW_WINDOWS, help="Theme to use."
    ),
    root: bool = typer.Option(default=False, help="Run command with root."),
    dbus: bool = typer.Option(default=False, help="Use DBus."),
    keep: bool = typer.Option(
        default=False, help="Keep the X server running after command terminates."
    ),
):
    """Run a GUI program inside a WSL distro."""
    config = shortcut_runner.ShortcutSettings(
        machine,
        command,
        mode,
        clipboard,
        gtk_scale,
        qt_scale,
        append,
        theme,
        root,
        dbus,
        keep,
    )
    shortcut_runner.run(config)


@app.command("startup")
def start_service():
    """Starts the GWSL service if not already running."""
    service.start_service()


@app.command()
def ssh(
    ip: str = typer.Argument(..., help="ssh machine ip"),
    command: str = typer.Argument(..., help="command to run via ssh"),
    user: str = typer.Option(default="", help="ssh user"),
    password: str = typer.Option(default="", help="ssh password"),
    root: bool = typer.Option(default=False, help="run as root"),
):
    """Start a ssh connection to a remote linux box."""
    config = ssh_runner.SSHConfig(ip, command, user, password, root)
    ssh_runner.run(config)


@app.callback(invoke_without_command=True)
def open_dashboard(
    ctx: typer.Context, about: bool = typer.Option(False, help="show about window.")
):
    """Run GWSL dashboard as the default command."""
    if ctx.invoked_subcommand is not None:
        return

    try:
        _ = singleton.SingleInstance()
    except (singleton.SingleInstanceException, PermissionError):
        win32gui.EnumWindows(bring_to_front, "gwsl dashboard")
        sys.exit(1)

    dashboard.run(about)


def bring_to_front(this_hwnd, window_name: str) -> Optional[bool]:
    """Bring to front the window if its title matches the given name."""
    if window_name in win32gui.GetWindowText(this_hwnd):
        win32gui.ShowWindow(this_hwnd, 5)
        win32gui.SetForegroundWindow(this_hwnd)
        return False


@exception_catcher
def main() -> None:
    """Run the CLI and display a messagebox if an error occurs."""
    app()


if __name__ == "__main__":
    main()
