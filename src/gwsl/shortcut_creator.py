import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from PIL import Image, ImageTk
from wsl_tools import WSLManager
import winshell

from gwsl import settings, shortcut_runner, utils
from gwsl import paths
from gwsl.tk_model import tk_model
from gwsl.utils import exception_dialog


def run(root=None, cmd=None, name=None, machine=None, icon=None):
    defaults = settings.Settings.load_or_create(paths.settings)
    machines = WSLManager(defaults.distro_blacklist).names
    if not machines:
        utils.msgbox(
            "No WSL distros",
            "No WSL distros found.\nPlease install a WSL distro",
        )
        return
    if machine and machine not in machines:
        utils.msgbox(
            "Wrong distro",
            f"Distro {machine} not found.\nPlease specify an existing WSL distro",
        )
        return

    if root:
        root.withdraw()
        box_root = tk.Toplevel(master=root)
    else:
        box_root = tk.Tk()
    model = ShortcutModel()
    model.machine = machine or machines[0]
    if cmd:
        model.command = cmd
    if name:
        model.app_name = name
    if icon:
        model.icon = icon
    window = ShortcutCreator(box_root, machines=machines, model=model)
    window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    return box_root.mainloop()


ShortcutModel = tk_model("ShortcutModel", shortcut_runner.ShortcutSettings)


def create_icon(icon, app_name):
    path = paths.appdata / f"{app_name}.ico"
    Image.open(icon).save(
        path, sizes=[(24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (255, 255)]
    )
    return path


class ShortcutCreator(ttk.Frame):
    def __init__(self, parent, machines=None, model=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.model = model
        self.icon_manager = utils.IconManager(paths.icon_pack)
        self.parent.title("Shortcut Creator")
        self.parent.iconname("Dialog")
        self.parent.minsize(420, 280)
        self.parent.running = True
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)

        lbl = tk.Label(self, text="Create a Start Menu Shortcut:", justify=tk.CENTER)
        lbl.grid(row=0, padx=10, pady=10, sticky="EW")

        ShortcutBaseFrame(self, machines=machines, model=self.model, padding="0.15i")
        ButtonsFrame(self)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.parent.deiconify()
        self.parent.wm_attributes("-topmost", 1)

    def quit(self):
        self.parent.quit()
        self.parent.destroy()
        return None

    def test(self):
        shortcut_data = self.model._to_dataclass()
        try:
            shortcut_runner.run(shortcut_data)
        except Exception as exc:
            exception_dialog(exc)

    def create(self):
        shortcut_data: shortcut_runner.ShortcutSettings = self.model.to_dataclass()
        icon = create_icon(shortcut_data.icon, shortcut_data.app_name)
        create_shortcut(shortcut_data.commandline, shortcut_data.shortcut_name, icon)
        self.quit()


class ShortcutBaseFrame(ttk.Frame):
    def __init__(self, parent, machines=None, model=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.model = model

        self.img_label = tk.Label(self)
        self.img_label.grid(row=0, padx=10, pady=10, sticky="EW", rowspan=2)
        self.set_icon()

        tk.Label(self, text="Shortcut Label:").grid(
            row=0, column=1, padx=10, sticky="E"
        )

        self.link_label = ttk.Entry(
            self,
            textvariable=self.model._app_name,
            validate="focusout",
            validatecommand=self.set_icon,
        )
        self.link_label.grid(row=0, column=2, padx=10, sticky="WE")
        self.link_label.focus_force()

        tk.Label(self, text="Shortcut Command:").grid(
            row=1, column=1, padx=10, sticky="E"
        )

        link_command = ttk.Entry(self, textvariable=self.model._command)
        link_command.grid(row=1, column=2, padx=10, sticky="WE")

        tk.Label(self, text="Run In:").grid(
            row=2, column=1, padx=10, pady=7, sticky="E"
        )

        self.machine_chooser = ttk.Combobox(
            self, values=machines, textvariable=self.model._machine, state="readonly"
        )
        self.machine_chooser.grid(row=2, column=2, padx=10, sticky="WE")

        reset_b = ttk.Button(self, text="Reset Icon", command=self.reset_icon)
        reset_b.grid(row=3, column=0, padx=10, pady=0, sticky="EW", rowspan=1)

        help_b = ttk.Button(self, text="Help", command=self.help)
        help_b.grid(row=3, column=1, padx=10, pady=0, sticky="EW", rowspan=1)

        self._expanded = tk.BooleanVar(value=False)
        self._expanded_frame = ShortcutAdvancedFrame(self)
        self.collapse_button = ttk.Checkbutton(
            self,
            text="Advanced >>",
            variable=self._expanded,
            command=self._toggle_expand,
            style="TButton",
        )
        self.collapse_button.grid(
            row=3, column=2, padx=10, pady=0, sticky="EW", rowspan=1
        )

        self.grid_columnconfigure(2, weight=1)
        self.grid(row=1, column=0, padx=10, pady=0, sticky="NEW")
        self._toggle_expand()

    def set_icon(self):
        icon = self.parent.icon_manager.tk_icon(self.model.app_name)
        return self._set_icon(icon)

    def reset_icon(self):
        self._set_icon(paths.assets / "link.png")

    def _set_icon(self, icon):
        self.model.icon = icon
        image = Image.open(icon).resize([48, 48], resample=Image.ANTIALIAS)
        img = ImageTk.PhotoImage(image)
        self.img_label.configure(image=img)
        self.img_label.image = img
        return True  # needed to pass validation on lose focus

    def _toggle_expand(self):
        if not self._expanded.get():
            # Remove this widget when button pressed.
            self._expanded_frame.grid_forget()
            # Show collapsed text
            self.collapse_button.configure(text="Advanced >>")
        else:
            # Increase the frame area as needed
            self._expanded_frame.grid(
                row=4, column=1, padx=10, pady=10, sticky="WE", columnspan=2
            )
            self._expanded_frame.grid_columnconfigure(1, weight=1)
            self.collapse_button.configure(text="<< Base")

    @staticmethod
    def help():
        paths.open_tutorial("shortcut")


class ShortcutAdvancedFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        tk.Label(self, text="Display Mode: ").grid(row=0, column=0, pady=7, sticky="WN")

        mode_chooser = ttk.Combobox(
            self,
            values=["Default", "Multi Window", "Single Window", "Fullscreen"],
            state="readonly",
        )
        mode_chooser.current(0)
        mode_chooser.grid(row=0, column=1, padx=10, sticky="WE")

        tk.Label(self, text="GTK Scale Mode: ").grid(
            row=1, column=0, pady=7, sticky="WN"
        )
        GTK_chooser = ttk.Combobox(
            self, values=["Default", "1", "2", "3"], state="readonly"
        )
        GTK_chooser.current(0)
        GTK_chooser.grid(row=1, column=1, padx=10, sticky="WE")

        tk.Label(self, text="QT Scale Mode: ").grid(
            row=2, column=0, pady=7, sticky="WN"
        )
        QT_chooser = ttk.Combobox(
            self, values=["Default", "1", "2", "3"], state="readonly"
        )
        QT_chooser.current(0)
        QT_chooser.grid(row=2, column=1, padx=10, sticky="WE")

        tk.Label(self, text="Shared Clipboard: ").grid(
            row=3, column=0, pady=7, sticky="WN"
        )
        clip_chooser = ttk.Combobox(
            self, values=["Default", "Enabled", "Disabled"], state="readonly"
        )
        clip_chooser.current(0)
        clip_chooser.grid(row=3, column=1, padx=10, sticky="WE")

        tk.Label(self, text="Color Mode: ").grid(row=4, column=0, pady=7, sticky="WN")
        color_chooser = ttk.Combobox(
            self,
            values=["Follow Windows", "Light Mode", "Dark Mode"],
            state="readonly",
        )
        color_chooser.current(0)
        color_chooser.grid(row=4, column=1, padx=10, sticky="WE")

        tk.Label(self, text="Run As Root:").grid(row=5, column=0, pady=7, sticky="WN")
        root_chooser = ttk.Combobox(self, values=["True", "False"], state="readonly")
        root_chooser.current(1)
        root_chooser.grid(row=5, column=1, padx=10, sticky="WE")

        tk.Label(self, text="Experimental Features:").grid(
            row=6, column=0, pady=7, sticky="WN"
        )

        tk.Label(self, text="Use DBus (Sudo Required):").grid(
            row=7, column=0, pady=7, sticky="WN"
        )
        dbus_chooser = ttk.Combobox(self, values=["True", "False"], state="readonly")
        dbus_chooser.current(1)
        dbus_chooser.grid(row=7, column=1, padx=10, sticky="WE")

        tk.Label(self, text="Experimental Flags:").grid(
            row=8, column=0, pady=7, sticky="WN"
        )
        append_chooser = ttk.Combobox(
            self,
            values=["None", "--zoom=2", "--scale=2"],
            state="readonly",
            textvariable=self.parent.model._append,
        )
        append_chooser.current(0)
        append_chooser.grid(row=8, column=1, padx=10, sticky="WE")

        tk.Label(self, text="Keep XServer Instance:").grid(
            row=9, column=0, pady=7, sticky="WN"
        )
        kill_chooser = ttk.Combobox(self, values=["True", "False"], state="readonly")
        kill_chooser.current(1)
        kill_chooser.grid(row=9, column=1, padx=10, sticky="WE")


class ButtonsFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        close_b = ttk.Button(self, text="Close", command=self.parent.quit)
        close_b.grid(column=0, row=0, sticky="SW", padx=10)

        save_b = ttk.Button(self, text="Add to Start Menu", command=self.parent.create)
        save_b.grid(column=1, row=0, sticky="SWE", padx=10)

        test_b = ttk.Button(self, text="Test Configuration", command=self.parent.test)
        test_b.grid(column=2, row=0, sticky="SE", padx=10)

        self.grid(row=2, column=0, padx=20, pady=20, sticky="SWE", columnspan=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)


def create_shortcut(command, name, icon, msix: bool = False):
    args = str(command)
    shortcut_path = paths.appdata / f"{name}.lnk"
    home = Path.home()

    if msix:
        target_loc = str(
            Path(winshell.folder("CSIDL_COMMON_APPDATA"))
            .joinpath("Microsoft", "WindowsApps", "gwsl.exe")
            .resolve()
        )
    else:
        target_loc = sys.executable

    with winshell.shortcut(str(shortcut_path.resolve())) as link:
        link.path = target_loc
        link.description = ""
        link.arguments = args
        link.icon_location = icon
        link.working_directory = home

    shutil.copy(shortcut_path, Path(winshell.start_menu()) / f"{name}.lnk")


if __name__ == "__main__":
    run()
