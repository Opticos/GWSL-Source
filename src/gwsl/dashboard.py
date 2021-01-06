"""Dashboard module."""
from __future__ import annotations

import ctypes
import itertools
import os
import threading
from functools import partial
from pathlib import Path
from typing import Tuple, Optional, Callable, List, Type, Any

import pygame
import win32con
import win32gui
from win10toast import ToastNotifier
from wsl_tools import WSLManager, WSLDistro, WSLApp

import gwsl
import pymsgbox
from gwsl import shortcut_creator, ssh_runner, paths, blur, utils, shortcut_runner
from gwsl.settings import Settings
from gwsl.utils import (
    in2pix,
    Coords,
    get_font,
    TaskbarPostion,
    taskbar_info,
    wsl_not_installed_msgbox,
)

# region typing
Box = Tuple[int, int, int, int]
ButtonsDef = List[Tuple[str, Callable, Optional[str]]]
# endregion


def run(about: bool = False) -> None:
    """
    Run GWSL dashboard.

    Args:
        about: if True, directly show the about page
    """
    settings = Settings.load_or_create(paths.settings)
    manager = WSLManager(settings.distro_blacklist)
    if not manager.installed:
        wsl_not_installed_msgbox()
        return
    dash = Dashboard(manager, settings, about)
    dash.mainloop()


class Dashboard:

    """
    Dashboard application.

    Initialize the window on the screen with one of the DashboardPage classes.
    Handles the main loop and events, delegating clicks to the current page.
    """

    def __init__(
        self, manager: WSLManager, settings: Settings, about: bool = False
    ) -> None:
        self.running = True
        self.loading = True
        self.current_page: Optional[DashboardPage] = None
        self.settings = settings
        self.manager = manager
        self.selected_machine = None
        self.window_size = (in2pix(3.8), in2pix(5.7))
        # size = 10
        font_size = 15
        os.environ["PBR_VERSION"] = "4.0.2"
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "4.0.2"
        fgcolor, accent, _ = utils.get_system_light()
        self.fg_color = fgcolor or (180, 180, 180, 80)
        self.accent = accent
        pygame.init()
        self.font = pygame.font.Font(None, font_size)
        self.clock = pygame.time.Clock()
        self._set_window()
        self.change_page(AboutPage if about else MainPage)

    def mainloop(self) -> None:
        """
        Window main loop.

        Exit on ESC keypress and on focus lost.
        Delegate to the current active page the handling of button clicks.
        """
        while self.running:
            for event in pygame.event.get():
                if self._quit_checker(event):
                    self.close()
                    return
                if (
                    event.type == pygame.MOUSEBUTTONUP
                    and event.button == 1
                    and not self.loading
                ):
                    pos = pygame.mouse.get_pos()
                    self.current_page.handle_buttondown(pos)
            self.current_page.update()
            updated_rects = self.current_page.draw(self.screen)
            pygame.display.update(updated_rects)
            self.clock.tick(60)
        print("Not running anymore")

    def close(self):
        """Close the window."""
        # TODO: pull down animation
        pygame.event.clear()
        pygame.display.quit()
        self.running = False

    @staticmethod
    def _quit_checker(event: pygame.event.Event) -> bool:
        """Check if a quit event is triggered."""
        etype = event.type
        return (
            etype == pygame.QUIT
            or (etype == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
            # TODO: focus lost triggers on respawn
            # or (
            #     etype == pygame.WINDOWEVENT
            #     and event.event == pygame.WINDOWEVENT_FOCUS_LOST
            # )
        )

    @property
    def window_center(self) -> Coords:
        """Window center coordinates."""
        width, heigth = self.window_size
        return width // 2, heigth // 2

    def _set_window(self, start_menu_mode: bool = False) -> None:
        """
        Set the window position based on the taskbar position.

        Args:
            start_menu_mode: if True, force the window to the left.
        """
        tbsize, pos = taskbar_info()
        self.taskbar_pos = pos
        u32 = ctypes.windll.user32
        screensize = u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)
        y = tbsize - self.window_size[1] if pos == TaskbarPostion.TOP else screensize[1]
        if pos == TaskbarPostion.LEFT:
            x = tbsize
        elif pos == TaskbarPostion.RIGHT or not start_menu_mode:
            x = screensize[0] - self.window_size[0]
        else:
            x = 0
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x:d},{y:d}"
        self.final_rect = x, y - self.window_size[1], x + self.window_size[0], y
        self.screen = pygame.display.set_mode(self.window_size, pygame.NOFRAME)
        self.handle = pygame.display.get_wm_info()["window"]
        self._set_transparency()
        win32gui.MoveWindow(self.handle, *self.final_rect[:2], *self.window_size, 1)
        pygame.display.set_caption("GWSL Dashboard")
        self.background = pygame.Surface(self.window_size).convert()
        self.background.fill((0, 0, 0, 0))  # TODO: get windows color

    def _set_transparency(self) -> None:
        """Set windows transparency."""
        cur_style = win32gui.GetWindowLong(self.handle, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(
            self.handle, win32con.GWL_EXSTYLE, cur_style | win32con.WS_EX_LAYERED
        )
        blur.blur(self.handle)

    def go_home(self) -> None:
        """Go to main page."""
        self.selected_machine = None
        self.change_page(MainPage)

    def change_page(self, page: Type[DashboardPage], **kwargs: Any) -> None:
        """
        Change the dashboard page.


        Displays a loading page until the target page is ready.

        Args:
            page: target page
            **kwargs: keyword arguments to pass to the target page
        """
        self.loading = True
        self.current_page = LoadingPage(self)
        self.current_page.clear(self.screen, self.background)
        threading.Thread(
            target=self._change_page_thread, args=(page,), kwargs=kwargs, daemon=True
        ).start()

    def _change_page_thread(self, page: Type[DashboardPage], **kwargs: Any) -> None:
        """Thread to load the target page."""
        self.current_page = page(self, **kwargs)
        self.current_page.clear(self.screen, self.background)
        self.loading = False

    def _choose_machine(self, callback: Callable) -> None:
        """Display the choose distro page or dialog."""
        if len(self.manager) == 1:
            self.selected_machine = next(iter(self.manager))
            return callback(self.selected_machine)
        elif len(self.manager) > 7:
            sel_name = pymsgbox.confirm(
                text="Select a WSL Machine",
                title="Choose WSL Machine",
                buttons=self.manager.names,
            )
            self.selected_machine = self.manager[sel_name]
            return callback(self.selected_machine)
        self.change_page(ChooseMachinePage, callback=callback)

    def shells(self) -> None:
        """Choose the distro to open in a shell."""
        self._choose_machine(self.open_shell)

    def open_shell(self, machine: WSLDistro) -> None:
        """Open the selected machine in a shell."""
        self.selected_machine = machine
        machine.open_in_shell(self.settings.general.shell_gui == "wt")
        self.close()

    def setter(self) -> None:
        """Choose the distro to configure."""
        self._choose_machine(self.configure_machine)

    def configure_machine(self, machine: WSLDistro) -> None:
        """Display the configure machine page for the selected distro."""
        self.selected_machine = machine
        self.change_page(ConfigurePage, machine=machine)

    def apper(self) -> None:
        """Choose the distro to list the available applications."""
        self._choose_machine(self.app_launcher)

    def app_launcher(self, machine: WSLDistro) -> None:
        """Display the app launcher page for the selected distro."""
        self.selected_machine = machine
        self.change_page(AppLauncherPage, machine=machine)


# region Widgets
# class Text:
#     def __init__(
#         self,
#         msg,
#         position,
#         color=None,
#         font="Segoe Print",
#         font_size=15,
#         mid=False,
#     ):
#         color = color or [100, 100, 100]
#         self.position = position
#         self.font = pygame.font.SysFont(font, font_size)
#         self.txt_surf = self.font.render(msg, True, color)
#
#         if len(color) == 4:
#             self.txt_surf.set_alpha(color[3])
#
#         if mid:
#             self.position = self.txt_surf.get_rect(center=position)
#
#     def draw(self, screen):
#         screen.blit(self.txt_surf, self.position)


class Spinner(pygame.sprite.DirtySprite):
    """Spinning icon."""

    def __init__(self, position: Coords, fg_color: utils.Color):
        super().__init__()
        icon = get_font(paths.ico_font, 0.3).render("", True, fg_color)
        self.steps = itertools.cycle(
            pygame.transform.rotate(icon, -i) for i in range(0, 360, 10)
        )
        self.center = position

    def update(self, *args, **kwargs) -> None:
        """Spins the icon."""
        self.image = next(self.steps)
        self.rect = self.image.get_rect(center=self.center)
        self.dirty = 1


class Button(pygame.sprite.DirtySprite):
    """Text button with optional icon and mouseover color change."""

    def __init__(
        self,
        position: Coords,
        max_width: float,
        color: Optional[utils.Color] = None,
        cngclr: Optional[utils.Color] = None,
        func: Optional[Callable] = None,
        text: str = "",
        icon: Optional[str] = None,
        txt_font: Path = paths.font,
        font_size: float = 0.17,
        ico_font: Path = paths.ico_font,
        icon_font_size: float = 0.27,
        icon_pad: float = 0.3,
    ) -> None:
        super().__init__()
        self.color = color or [255, 255, 255]
        self.func = func
        self.cngclr = cngclr or color
        self.hover = None
        self.txt_font = get_font(txt_font, font_size)
        self.txt = text
        text_width, btn_height = self.txt_font.size(self.txt)
        self.txt_rect = pygame.Rect(0, 0, text_width, btn_height)

        # TODO: handle png icons (len(icon) > 1?)
        self.icon = icon
        if not icon:
            self.txt_rect.centerx = max_width // 2
        else:
            self.icon_font = get_font(ico_font, icon_font_size)
            icon_width, btn_height = self.icon_font.size(self.icon)
            self.icon_rect = pygame.Rect(0, 0, icon_width, btn_height)
            self.txt_rect.left = icon_width + in2pix(icon_pad)
            self.txt_rect.centery = btn_height // 2

        self.txt_img_normal = self.txt_font.render(self.txt, True, self.color)
        if self.func:
            self.txt_img_hover = self.txt_font.render(self.txt, True, self.cngclr)
        if self.icon:
            self.icon_img_normal = self.icon_font.render(self.icon, True, self.color)
            if self.func:
                self.icon_img_hover = self.icon_font.render(
                    self.icon, True, self.cngclr
                )

        self.image = pygame.Surface((max_width, btn_height))
        self.rect = self.image.get_rect(topleft=position)
        self.change_hover_state(False)

    def update(self) -> None:
        """Handle the mouseover event."""
        if not self.func:
            return
        pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(pos)
        if hover != self.hover:
            self.change_hover_state(hover)

    def change_hover_state(self, hover: bool) -> None:
        """Set the hover state."""
        self.hover = hover
        txt_surf = self.txt_img_hover if hover else self.txt_img_normal
        self.image.blit(txt_surf, self.txt_rect)
        if self.icon:
            icon_surf = self.icon_img_hover if hover else self.icon_img_normal
            self.image.blit(icon_surf, self.icon_rect)
        self.dirty = 1

    def callback(self, *args) -> None:
        """Run the callback function, if set."""
        if self.func:
            return self.func(*args)


class IconButton(pygame.sprite.DirtySprite):
    """Button with icon and mouseover color change."""

    def __init__(
        self,
        position: Coords,
        icon: str,
        color: Optional[utils.Color] = None,
        cngclr: Optional[utils.Color] = None,
        func: Optional[Callable] = None,
        ico_font: Path = paths.ico_font,
        icon_font_size: float = 0.27,
    ) -> None:
        super().__init__()
        self.color = color or [255, 255, 255]
        self.func = func
        self.cngclr = cngclr or color
        self.hover = None

        # TODO: handle png icons (more than 1 char?)
        self.icon = icon
        self.icon_font = get_font(ico_font, icon_font_size)
        self.image_normal = self.icon_font.render(self.icon, True, self.color)
        if func:
            self.image_hover = self.icon_font.render(self.icon, True, self.cngclr)

        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=position)
        self.change_hover_state(False)

    def update(self) -> None:
        """Handle the mouse over event."""
        pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(pos)
        if hover != self.hover:
            self.change_hover_state(hover)

    def change_hover_state(self, hover: bool) -> None:
        """Set the hover state."""
        self.hover = hover
        self.image = self.image_hover if hover else self.image_normal
        self.dirty = 1

    def callback(self, *args) -> None:
        """Run the callback function, if set."""
        if self.func:
            return self.func(*args)


# endregion


# region Pages
class DashboardPage(pygame.sprite.LayeredDirty):
    """
    Base dashboard page.

    Builds the buttons using the tuple (text, callback, icon) in `buttons_def`.
    If `icon` is none, skips the icon rendering.
    """

    def __init__(self, parent: Dashboard, machine: Optional[WSLDistro] = None) -> None:
        super().__init__()
        self.parent = parent
        self.machine = machine
        self.buttons_def = []
        self.btn_spacing = in2pix(0.65)
        self._init_buttons_def()
        self._update_buttons()

    def _init_buttons_def(self) -> None:
        """Protected method to override to init buttons definition."""
        raise NotImplementedError

    def _update_buttons(self, width: Optional[float] = None):
        """Update the buttons from the definition."""
        y_pad = in2pix(1)
        btn_x = in2pix(0.4)
        btn_width = width or (self.parent.window_size[0] - (2 * btn_x))
        for i, (text, func, icon) in enumerate(self.buttons_def):
            btn = Button(
                (btn_x, i * self.btn_spacing + y_pad),
                btn_width,
                self.parent.fg_color,
                cngclr=self.parent.accent,
                func=func,
                text=text,
                icon=icon,
            )
            self.add(btn)

    def handle_buttondown(self, pos: Coords) -> None:
        """Run the callback of the clicked button."""
        for b in self.sprites():
            if b.rect.collidepoint(pos):
                b.callback()


class LoadingPage(DashboardPage):
    """
    Loading page with a spinner at the center of the page.

    Called by Dashboard.change_page.
    """

    def _init_buttons_def(self) -> None:
        """Don't care about buttons, just add a Spinner."""
        self.empty()
        self.add(Spinner(self.parent.window_center, self.parent.fg_color))


class MainPage(DashboardPage):
    """Main page."""

    def _init_buttons_def(self) -> None:
        self.buttons_def = [
            ("GWSL Distro Tools", self.parent.setter, ""),
            ("Shortcut Creator", shortcut_creator.run, ""),
            ("Linux Apps", self.parent.apper, ""),
            ("Linux Shell", self.parent.shells, ""),
            ("Graphical SSH Connection", ssh_runner.putty, ""),
            ("Donate With PayPal", self.donate, ""),
        ]

    @staticmethod
    def donate() -> None:
        """Open the donation page."""
        paths.open_url(f"{paths.site_url}#donate")


class AboutPage(DashboardPage):
    """About page."""

    def _init_buttons_def(self) -> None:
        self.btn_spacing = in2pix(0.3)
        self.buttons_def = [
            (f"GWSL Version {gwsl.__version__}", None, None),
            ("© Copyright Paul-E/Opticos Studios 2020", None, None),
            ("GWSL Uses:", None, None),
            ("Python - Pyinstaller - SDL", None, None),
            ("VCXSRV - Putty - Pillow", None, None),
            ("Tcl/Tk - Paper Icon Pack", None, None),
            ("Pymsgbox - OpticUI - Infi.Systray", None, None),
            ("Visit Opticos Studios Website", self.visit_site, None),
            ("View Licenses", self.view_license, None),
            ("Edit Configuration", self.edit_settings, None),
            ("View Logs", self.view_logs, None),
            ("Cancel", self.parent.go_home, None),
        ]

    @staticmethod
    def visit_site() -> None:
        """Open the website."""
        paths.open_url("http://opticos.studio")

    @staticmethod
    def view_license() -> None:
        """View the license file."""
        paths.open_file(paths.license)

    @staticmethod
    def view_logs() -> None:
        """Open the logs."""
        paths.open_file(paths.log)

    @staticmethod
    def edit_settings() -> None:
        """Open the settings."""
        paths.open_file(paths.settings)


class ChooseMachinePage(DashboardPage):

    """
    Choose machine page.

    List the available distros as buttons with the provided callback.
    """

    def __init__(self, parent, callback: Optional[Callable] = None) -> None:
        self.callback = callback
        super().__init__(parent)

    def _init_buttons_def(self) -> None:
        manager = self.parent.manager
        bd = [(name, partial(self.callback, manager[name]), None) for name in manager]
        bd.append(("Cancel", self.parent.go_home, None))
        self.buttons_def = bd


class ConfigurePage(DashboardPage):

    """Configure machine page."""

    def _init_buttons_def(self) -> None:
        # TODO: split buttons in methods used on update
        profile = self.machine.profile
        if "export DISPLAY=" in profile:
            btns = [("Display Is Set To Auto-Export", None, "")]
        else:
            btns = [("Auto-Export Display", self.configure_x, "")]
        if "deb" in self.machine.name.lower() or "ubuntu" in self.machine.name.lower():
            btns.append(("Configure DBus", self.conf_dbus, ""))

        plus = ""
        minus = ""
        if self.machine.qt_scale == 1:
            btns.append(("Set GTK To: HI-DPI", partial(self.set_gtk_scale, 2), plus))
        else:
            btns.append(("Set GTK To: LOW-DPI", partial(self.set_gtk_scale, 1), minus))
        if self.machine.gtk_scale == 1:
            btns.append(("Set QT To: HI-DPI", partial(self.set_qt_scale, 2), plus))
        else:
            btns.append(("Set QT To: LOW-DPI", partial(self.set_qt_scale, 1), minus))
        if self.machine.themes:
            btns.append((f"GTK Theme: {self.machine.theme}", self.choose_theme, ""))
        else:
            btns.append(("No GTK Themes Installed", None, ""))
        btns.append((f"Reboot {self.machine.name}", self.reboot_machine, ""))
        self.buttons_def = btns

    def configure_x(self):
        """Configure the Xorg display env var of the distro."""
        machine = self.machine
        machine.set_display()
        ToastNotifier().show_toast(
            "Display Exported",
            f"{machine} is set to forward X through port 0.",
            icon_path=paths.assets / "icon.ico",
            duration=7,
            threaded=True,
        )
        if utils.ask_reboot(machine):
            machine.reboot()

    def conf_dbus(self):
        """Install DBUS on the distro."""
        machine = self.machine
        passwd = utils.ask_password(machine)
        if passwd:
            machine.install_dbus(passwd)
            print("Complete")

    def set_gtk_scale(self, value: int) -> None:
        """Set the GTK scaling."""
        machine = self.machine
        machine.gtk_scale = value
        # TODO: change button and callback
        if utils.ask_reboot(machine):
            machine.reboot()

    def set_qt_scale(self, value: int) -> None:
        """Set the QT scaling."""
        machine = self.machine
        machine.qt_scale = value
        # TODO: change button and callback
        if utils.ask_reboot(machine):
            machine.reboot()

    def reboot_machine(self):
        """Reboot the distribution."""
        self.machine.reboot()

    def choose_theme(self):
        """Choose the theme."""
        self.parent.change_page(ThemeChooserPage, machine=self.machine)


class AppLauncherPage(DashboardPage):

    """
    App launcher page.

    Add the "create shortcut" icon button to the right of the app launcher button.
    """

    def _init_buttons_def(self) -> None:
        apps = self.machine.gui_apps
        self.buttons_def = [
            (app_name, partial(self.launch_app, app), app.ico)
            for app_name, app in apps.items()
        ]
        self.shortcut_btns_def = [
            ("", partial(self.create_shortcut, app)) for app_name, app in apps.items()
        ]

    def _update_buttons(self, **kwargs):
        super()._update_buttons(width=self.parent.window_size[0] - in2pix(1.2))
        btn_x = self.parent.window_size[0] - in2pix(0.8)
        y_pad = in2pix(1)
        btn_spacing = in2pix(0.65)
        for i, (icon, func) in enumerate(self.shortcut_btns_def):
            btn = IconButton(
                (btn_x, i * btn_spacing + y_pad),
                icon,
                self.parent.fg_color,
                cngclr=self.parent.accent,
                func=func,
            )
            self.add(btn)

    def launch_app(self, app: WSLApp):
        """Launch the selected application."""
        shortcut = shortcut_runner.ShortcutSettings(str(self.machine), app.cmd)
        self.parent.close()
        shortcut_runner.run(shortcut)

    def create_shortcut(self, app: WSLApp):
        """Open the shortcut creator for the selected application."""
        self.parent.close()
        shortcut_creator.run(
            cmd=app.cmd, name=app.name, machine=self.machine.name, icon=app.ico
        )


class ThemeChooserPage(DashboardPage):

    """Theme chooser page."""

    def _init_buttons_def(self) -> None:
        btns = [
            (theme.capitalize(), partial(self.set_theme, theme), "paint")
            for theme in self.machine.themes
        ]
        self.buttons_def = btns

    def set_theme(self, theme: str) -> None:
        """Set the selected theme."""
        self.machine.theme = theme


# endregion


if __name__ == "__main__":
    run()
