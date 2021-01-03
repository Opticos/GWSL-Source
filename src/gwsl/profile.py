import tkinter as tk
from tkinter import ttk
from typing import Any

import PIL
from PIL import Image, ImageTk

from gwsl import paths
from gwsl.settings import Settings, XProfile


def run(root=None):
    if root:
        root.withdraw()
        box_root = tk.Toplevel(master=root)
    else:
        box_root = tk.Tk()
    window = ProfileCreator(box_root)
    window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    return box_root.mainloop()


class ProfileModel:
    def __init__(self):
        self.name = tk.StringVar()
        self.arguments = tk.StringVar()
        self.hide_systray = tk.BooleanVar(value=True)

    def to_settings(self) -> XProfile:
        name = self.name.get()
        arguments = self.arguments.get().split(" ")
        if name and arguments:
            if self.hide_systray.get():
                arguments.append("-notrayicon")
            return XProfile(name=name, arguments=arguments)
        raise ValueError("Profile name or flags not set.")


class ProfileCreator(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.model = ProfileModel()
        self.parent.title("XServer Profile Creator")
        self.parent.iconname("Dialog")
        self.parent.minsize(700, 120)
        self.parent.running = True
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        tk.Label(self, text="Add", justify=tk.LEFT)  # .grid(row=0, padx=10, sticky="W")

        MainFrame(self, model=self.model, padding="0.15i")
        ButtonsFrame(self)  # , padding="0.15i")

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

    def add(self):
        try:
            prof = self.model.to_settings()
        except ValueError:
            pass
        else:
            sett = Settings.load_or_create(paths.settings)
            sett.graphics.xserver_profiles.append(prof)
            sett.save(paths.settings)
            self.quit()


class MainFrame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, model: ProfileModel = None, **kwargs: Any):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.model = model

        image = Image.open(paths.assets / "icon.png").resize([48, 48])
        img = PIL.ImageTk.PhotoImage(image)
        img_label = tk.Label(self, image=img)
        img_label.image = img
        img_label.grid(row=0, padx=10, pady=10, sticky="EW", rowspan=2)

        tk.Label(self, text="Profile Name:").grid(row=0, column=1, padx=10, sticky="W")
        profile_entry = ttk.Entry(self, textvariable=self.model.name)
        profile_entry.grid(row=0, column=2, columnspan=4, padx=10, sticky="WE")
        profile_entry.focus_force()
        tk.Label(self, text="VcXsrv Flags:").grid(row=1, column=1, padx=10, sticky="W")
        args_entry = ttk.Entry(self, textvariable=self.model.arguments)
        args_entry.grid(row=1, column=2, padx=10, sticky="WE")
        tk.Label(self, text="Hide VcXsrv Systray Icon:").grid(
            row=2, column=1, padx=10, sticky="W"
        )
        var = tk.IntVar(value=1)
        hide_systray = ttk.Checkbutton(self, variable=self.model.hide_systray)
        hide_systray.grid(row=2, column=2, columnspan=4, padx=10, sticky="WE")

        tk.Label(
            self,
            text="(Please leave the display port number untouched "
            "and do not use -ac or -[no]trayicon)",
        ).grid(row=3, column=1, columnspan=4, padx=10, sticky="W")
        self.grid(row=1, column=0, padx=20, sticky="SWE", columnspan=2)
        self.grid_columnconfigure(2, weight=1)


class ButtonsFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        close_b = ttk.Button(self, text="Cancel", command=self.parent.quit)
        close_b.grid(column=0, row=0, sticky="SW", padx=10)
        test_b = ttk.Button(self, text="Add", command=self.parent.add)
        test_b.grid(column=2, row=0, sticky="SE", padx=10)
        self.grid(row=2, column=0, padx=20, pady=20, sticky="SWE", columnspan=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
