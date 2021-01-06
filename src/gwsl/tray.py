"""Tray icon process."""
import subprocess
import time
from functools import partial
from typing import List

import keyboard

from systray import SysTrayIcon
from gwsl.logger import init_logger
from gwsl.service import is_running
from gwsl.settings import Settings, WindowMode
from gwsl import paths, profile, dashboard
from gwsl.utils import yesno, set_app_dpi, DPIAwarness, exception_catcher


@exception_catcher
def main():
    GWSLTray()


class ServerHandler:
    @property
    def is_running(self) -> bool:
        return is_running("GWSL_vcxsrv")

    @exception_catcher
    def start(self, profile_args: List[str]) -> None:
        subprocess.Popen([str(paths.server)] + profile_args)

    def kill(self) -> None:
        subprocess.getoutput("taskkill /F /IM vcxsrv.exe")
        subprocess.getoutput("taskkill /F /IM GWSL_vcxsrv.exe")
        # subprocess.getoutput('taskkill /F /IM GWSL_service.exe')

    def restart(self, profile_args) -> None:
        if self.is_running:
            self.kill()
        self.start(profile_args)


def ask_switch_wmode():
    return yesno(
        "Switch XServer profiles?\n"
        "Be sure to save any work open in GWSL programs.\n"
        "This might force-close some windows.",
        "Switch Profile?",
    )


def ask_clip(action):
    return yesno(
        "Toggle the shared clipboard?\n"
        "Be sure to save any work open in GWSL programs.\n"
        "This might force-close some windows.",
        f"{action} clipboard",
    )


def ask_restart_after_crash():
    return yesno(
        "Hmm... The GWSL service just crashed or was closed.\n"
        "Do you want to restart the service?",
        "Uh Oh!",
    )


def ask_restart():
    return yesno(
        "To apply changes, the GWSL XServer needs to be restarted.\n"
        "Be sure to save any work open in GWSL programs.\n"
        "This will force close windows running in GWSL.\n"
        "Restart now?",
        "Restart XServer to Apply Changes?",
    )


class GWSLTray:
    def __init__(self) -> None:
        self.settings = Settings.load_or_create(paths.settings)
        self.logger = init_logger(paths.log)
        self._server = ServerHandler()
        self.restart_server()
        self._systray = None
        self.start()
        # TODO: customizable hotkey
        keyboard.add_hotkey("alt+ctrl+g", open_dashboard)

    def start(self):
        self._systray = SysTrayIcon(
            paths.get_systray_icon("systray"),
            f"GWSL Running - {self.settings.graphics.profile_name}",
            menu_options=self.menu,
            default_menu_index=open_dashboard,
        )
        self._systray.start()

    def update(self, server=False):
        self._systray.shutdown()
        time.sleep(0.2)
        self.start()
        if server:
            self.restart_server()

    def save_settings(self):
        self.settings.save(paths.settings)

    @property
    def menu(self):
        sett = self.settings.graphics
        icon = paths.get_systray_icon
        profiles = [
            (
                sett.__MODES_DESC__[mode],
                icon(mode.value),
                partial(self.switch_mode, mode),
            )
            for mode in (WindowMode.MULTI, WindowMode.SINGLE, WindowMode.FULLSCREEN)
        ]
        for prof in sett.xserver_profiles:
            profiles.append(
                (
                    f"Custom - {prof} (alpha)",
                    icon("custom"),
                    partial(self.switch_mode, WindowMode.CUSTOM, profile=prof),
                )
            )
        profiles.append(("Add A Profile (alpha)", icon("add"), self.add_profile))
        menu = [
            (
                f"XServer Profiles ({sett.profile_name})",
                icon(sett.window_mode.value),
                profiles,
            )
        ]
        if sett.window_mode != WindowMode.CUSTOM:
            state = "On" if sett.clipboard else "Off"
            icn = icon("check" if sett.clipboard else "quit")
            menu.append((f"Shared Clipboard ({state})", icn, self.toggle_clipboard))

        menu += [
            (
                "DPI Scaling Mode",
                icon("dpi"),
                [
                    (
                        "Linux (GTK and QT)",
                        icon("dpi_lin"),
                        partial(self.set_dpi, DPIAwarness.LINUX),
                    ),
                    (
                        "Windows (Faster but Blurrier)",
                        icon("dpi_win"),
                        partial(self.set_dpi, DPIAwarness.WINDOWS),
                    ),
                    (
                        "Windows GDI Enhanced (Multi-Monitor Aware)",
                        icon("dpi_enhanced"),
                        partial(self.set_dpi, DPIAwarness.WIN_GDI),
                    ),
                ],
            ),
            ("Configure GWSL", icon("config"), open_config),
            ("View Logs", icon("logs"), open_logs),
            ("Dashboard", icon("dashboard"), open_dashboard),
            ("About", icon("info"), open_about),
            ("Help", icon("help"), open_help),
            ("Exit", icon("quit"), self.shutdown),
        ]
        return tuple(menu)

    def toggle_clipboard(self, _systray):
        sett = self.settings.graphics
        action = "Disable" if sett.clipboard else "Enable"
        if not ask_clip(action):
            return
        sett.clipboard = not sett.clipboard
        self.update(server=True)

    def switch_mode(self, new_mode, prof_name=None, ask=True):
        sett = self.settings.graphics
        if sett.window_mode == new_mode and (
            not prof_name or prof_name == sett.custom_profile
        ):
            return
        if ask and not ask_switch_wmode():
            return
        hover_text = sett.profile_name
        self._systray.update(hover_text=hover_text)
        sett.window_mode = new_mode
        if prof_name:
            sett.custom_profile = prof_name
        self.restart_server()

    def monitor(self):
        # start service listener
        timer = time.perf_counter()
        while True:
            try:
                if time.perf_counter() - timer > 4:
                    timer = time.perf_counter()
                    if not self.server_is_running:
                        # In case someone closes a single-window server,
                        # restart as multi window.
                        if self.settings.graphics.window_mode == WindowMode.SINGLE:
                            self._systray.update(hover_text="GWSL - Multi Window Mode")
                            self.settings.graphics.window_mode = WindowMode.MULTI
                            self.restart_server()
                        elif ask_restart_after_crash():
                            self.restart_server()
                        else:
                            self.shutdown()
                    self._systray.update(
                        icon=paths.get_systray_icon("systray")
                    )  # menu_options=self.menu
            except Exception as e:
                self.logger.exception(f"Exception occurred: {e}")
            time.sleep(2)

    def shutdown(self, *_args) -> None:
        self.save_settings()
        self.kill_server()
        subprocess.getoutput("taskkill /F /IM GWSL.exe")
        self._systray.shutdown()

    @property
    def server_is_running(self) -> bool:
        return is_running("GWSL_vcxsrv")

    def start_server(self) -> None:
        self._server.start(self.settings.graphics.profile_args)

    def kill_server(self) -> None:
        self._server.kill()

    def restart_server(self) -> None:
        self.kill_server()
        self.start_server()

    def set_dpi(self, _systray: SysTrayIcon, mode: DPIAwarness):
        set_app_dpi(paths.server, mode)
        set_app_dpi(paths.instance, mode)
        if ask_restart():
            self.restart_server()

    def add_profile(self, _systray: SysTrayIcon):
        profile.run()
        self.update()


def open_dashboard(*_args):
    dashboard.run()


def open_about(*_args):
    dashboard.run(about=True)


def open_help(*_args):
    paths.open_url(f"{paths.site_url}help.html")


def open_logs(*_args):
    paths.open_file(paths.log)
    paths.open_file(paths.service_log)


def open_config(*_args):
    paths.open_file(paths.settings)


if __name__ == "__main__":
    main()
