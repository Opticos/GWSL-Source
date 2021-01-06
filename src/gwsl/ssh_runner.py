import time
from dataclasses import dataclass

import PIL
import tkinter as tk
from tkinter import ttk

from PIL import Image

from gwsl.exe_layer import Cmd
from gwsl.service import start_service
from gwsl import paths
from gwsl.tk_model import tk_model


@dataclass
class SSHConfig:
    """SSH connection config."""
    ip: str
    command: str
    user: str = ""
    password: str = ""
    root: bool = False


SSHModel = tk_model("SSHModel", SSHConfig)


class LoginTextboxes(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        imager = PIL.Image.open(paths.assets / "lock.png")
        img = PIL.ImageTk.PhotoImage(imager.resize([48, 48]))
        img_label = tk.Label(self, image=img)
        img_label.image = img
        img_label.grid(row=0, padx=10, pady=10, sticky="EW", rowspan=2)

        tk.Label(self, text="Username: ").grid(row=0, column=1, padx=10, sticky="W")

        self.user = ttk.Entry(self)
        self.user.grid(row=0, column=2, padx=10, sticky="WE")
        self.user.focus_force()

        tk.Label(self, text="Password: ").grid(row=1, column=1, padx=10, sticky="W")

        self.password = ttk.Entry(self, show="*")
        self.password.grid(row=1, column=2, padx=10, sticky="WE")

        self.grid(row=1, column=0, padx=20, sticky="SWE", columnspan=2)
        self.grid_columnconfigure(2, weight=1)


class LoginButtons(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        close_b = ttk.Button(self, text="Cancel", command=self.parent.quit)
        close_b.grid(column=0, row=0, sticky="SW", padx=10)

        test_b = ttk.Button(self, text="Login", command=self.parent.login)
        test_b.grid(column=2, row=0, sticky="SE", padx=10)

        self.grid(row=2, column=0, padx=20, pady=20, sticky="SWE", columnspan=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)


class SSHLoginWindow(ttk.Frame):
    def __init__(self, parent, machine, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.parent.title(f"Login to {machine}")
        self.parent.iconname("Dialog")
        self.parent.minsize(300, 120)
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        self.running = True

        tk.Label(self, text="Login:", justify=tk.LEFT)
        self.grid_rowconfigure(0, weight=0)

        self.frame_1 = LoginTextboxes(self, padding="0.15i")
        self.frame_3 = LoginButtons(self)

        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.bind("<Return>", self.login)
        self.grid_columnconfigure(0, weight=1)
        self.parent.deiconify()
        self.parent.wm_attributes("-topmost", 1)

    def quit(self):
        self.quit()

    def login(self, *_args):
        passw = self.frame_1.password.get()
        user = self.frame_1.user.get()
        if user != "" and passw != "":
            self.quit()


def get_login(machine, root=None):
    if root:
        root.withdraw()
        self = tk.Toplevel(master=root)
    else:
        self = tk.Tk()
    SSHLoginWindow(self, machine).pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    return self.mainloop()


def run(config: SSHConfig):
    user = config.user
    password = config.password
    if not user or not password:
        user, password = get_login(config.ip)

    start_service()

    command = config.command
    if command == "open_putty":
        Cmd(
            command=[
                "PUTTY/GWSL_putty.exe",
                "-ssh",
                f"{user}@{config.ip}",
                "-pw",
                f"{password}",
                "-X",
            ],
            console=True,
        )
        return

    prog = Cmd(
        command=[
            "PUTTY/GWSL_plink.exe",
            "-ssh",
            f"{user}@{config.ip}",
            "-pw",
            f"{password}",
            "-X",
            "-batch",
        ]
    )

    if config.root:
        prog.run(
            f'echo "{password}" | sudo -H -S xauth add $(xauth -f ~{user}/.Xauthority list | tail -1)'
        )

        prog.run(
            f'echo "{password}" | sudo -H -S {command}',
            wait=True,
            ident=command,
        )
    else:
        prog.run(command=command, wait=True, ident=command)
    while not prog.error:
        time.sleep(5)


def putty(root = None):
    if not root:
        root = tk.Tk()
    root.withdraw()
    boxRoot = tk.Toplevel(master=root)
    boxRoot.withdraw()

    def quitter():
        boxRoot.quit()

    boxRoot.title("Graphical SSH Manager")
    boxRoot.iconname("Dialog")
    boxRoot.minsize(420, 200)
    boxRoot.running = True
    boxRoot.protocol("WM_DELETE_WINDOW", quitter)

    lbl = tk.Label(boxRoot, text="Graphical SSH Tools:", justify=tk.CENTER)
    lbl.grid(row=0, padx=10, pady=10, sticky="EW")
    boxRoot.grid_rowconfigure(0, weight=0)

    def test():
        ip_config = ip.get()
        if ip_config != "":
            creds = get_login(ip_config)
            settings.ssh.ip = ip.get()
            password = creds["pass"]
            user = creds["user"]
            prog = Cmd(
                command=[
                    "PUTTY/GWSL_putty.exe",
                    "-ssh",
                    f"{user}@{ip.get()}",
                    "-pw",
                    f"{password}",
                    "-X",
                ],
                console=True,
            )
            quitter()

    def create():
        sett = iset.read()
        sett["putty"]["ip"] = ip.get()
        iset.set(sett)

        if ip.get() != "":
            command = f'--r --ssh --ip="{ip.get()}" --command="open_putty"'

            print(command)
            gwsl.shortuct_creator.create_shortcut(
                command,
                "Graphical SSH on " + ip.get(),
                asset_dir + "computer.ico",
                msix=BUILD_MODE=="MSIX",
            )
            quitter()

    # First frame

    frame_1 = ttk.Frame(boxRoot, padding="0.1i")
    imager = Image.open(asset_dir / "network.png")

    img = PIL.ImageTk.PhotoImage(imager.resize([48, 48]))
    labelm = tk.Label(frame_1, image=img)
    labelm.image = img

    labelm.grid(row=0, padx=10, pady=0, sticky="EW", rowspan=2)

    tk.Label(frame_1, text="Remote IP: ").grid(
        row=0, column=1, padx=10, rowspan=2, sticky="W"
    )

    ip = ttk.Entry(frame_1)

    sett = iset.read()
    save_ip = sett["putty"]["ip"]
    if save_ip is not None:
        ip.insert(0, save_ip)
    # iset.set(sett)

    ip.grid(row=0, column=2, padx=10, rowspan=2, sticky="WE")

    ip.focus_force()

    frame_1.grid_columnconfigure(2, weight=1)

    frame_1.grid(row=1, column=0, padx=20, pady=0, sticky="NEW")

    frame_3 = tk.Frame(boxRoot)  # , padding="0.15i")

    close_b = ttk.Button(frame_3, text="Close", command=quitter)
    close_b.grid(column=0, row=0, sticky="SW", padx=10)

    save_b = ttk.Button(frame_3, text="Add to Start Menu", command=create)
    save_b.grid(column=1, row=0, sticky="SWE", padx=10)

    save_b = ttk.Button(frame_3, text="Help", command=partial(paths.open_tutorial("ssh")))
    save_b.grid(column=2, row=0, sticky="WE", padx=10)

    test_b = ttk.Button(frame_3, text="Connect to Machine", command=test)
    test_b.grid(column=3, row=0, sticky="SE", padx=10)

    frame_3.grid(row=2, column=0, padx=20, pady=20, sticky="SWE", columnspan=2)

    frame_3.grid_columnconfigure(2, weight=1)

    frame_3.grid_columnconfigure(1, weight=1)

    frame_3.grid_columnconfigure(0, weight=1)

    boxRoot.grid_rowconfigure(1, weight=0)
    boxRoot.grid_rowconfigure(2, weight=1)

    boxRoot.grid_rowconfigure(3, weight=0)

    boxRoot.grid_columnconfigure(0, weight=1)

    boxRoot.deiconify()
    boxRoot.wm_attributes("-topmost", 1)

    boxRoot.mainloop()