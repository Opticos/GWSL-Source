from tkinter import ttk
from tkinter import *
import tkinter as tk
import time

root = None

from PIL import Image
import PIL
import PIL.ImageTk


def add(asset_dir):
    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)  # , fg="red", bg="black")
        boxRoot.withdraw()
    else:
        boxRoot = tk.Tk()
        boxRoot.withdraw()

    def quitter():
        boxRoot.quit()
        boxRoot.destroy()
        boxRoot.running = False
        return None

    def login(*args):
        nonlocal options
        passw = link_pass.get()
        user = link_user.get()
        if var.get() == 1:
            passw += (" -notrayicon")
        if user != "" and passw != "":
            options = {"name": user, "args": passw}
            boxRoot.quit()
            boxRoot.destroy()
            # boxRoot.running = False

    boxRoot.title("XServer Profile Creator")
    boxRoot.iconname("Dialog")
    boxRoot.minsize(700, 120)
    boxRoot.running = True
    boxRoot.protocol("WM_DELETE_WINDOW", quitter)
    options = {}
    lbl = tk.Label(boxRoot, text="Add", justify=LEFT)  # , font=("Helvetica", 16))
    # lbl.grid(row=0, padx=10, sticky="W")
    boxRoot.grid_rowconfigure(0, weight=0)

    # First frame

    frame_1 = ttk.Frame(boxRoot, padding="0.15i")
    imager = Image.open(asset_dir + "\\assets\\icon.png")
    img = PIL.ImageTk.PhotoImage(imager.resize([48, 48]))
    labelm = tk.Label(frame_1, image=img)
    labelm.image = img

    labelm.grid(row=0, padx=10, pady=10, sticky="EW", rowspan=2)

    tk.Label(frame_1, text="Profile Name: ").grid(row=0, column=1, padx=10, sticky="W")

    link_user = ttk.Entry(frame_1)

    link_user.grid(row=0, column=2, columnspan=4, padx=10, sticky="WE")

    link_user.focus_force()

    tk.Label(frame_1, text="VcXsrv Flags: ").grid(row=1, column=1, padx=10, sticky="W")

    link_pass = ttk.Entry(frame_1)

    link_pass.grid(row=1, column=2, padx=10, sticky="WE")

    tk.Label(frame_1, text="Hide VcXsrv Systray Icon: ").grid(row=2, column=1, padx=10, sticky="W")

    var = tk.IntVar(root)
    hide_systray = ttk.Checkbutton(frame_1, variable=var)

    var.set(1)

    #hide_systray.configure(state='enabled')

    hide_systray.grid(row=2, column=2, columnspan=4, padx=10, sticky="WE")
    
    tk.Label(frame_1, text='(Please leave the display port number untouched and do not use -ac or -[no]trayicon)').grid(row=3, column=1,
                                                                                                       columnspan=4,
                                                                                                 padx=10,
                                                                                                       sticky="W")

    machines = []

    frame_1.grid(row=1, column=0, padx=20, sticky="SWE", columnspan=2)
    frame_1.grid_columnconfigure(2, weight=1)

    frame_3 = tk.Frame(boxRoot)  # , padding="0.15i")

    close_b = ttk.Button(frame_3, text="Cancel", command=quitter)
    close_b.grid(column=0, row=0, sticky="SW", padx=10)

    test_b = ttk.Button(frame_3, text="Add", command=login)
    test_b.grid(column=2, row=0, sticky="SE", padx=10)

    frame_3.grid(row=2, column=0, padx=20, pady=20, sticky="SWE", columnspan=2)

    frame_3.grid_columnconfigure(2, weight=1)

    frame_3.grid_columnconfigure(1, weight=1)

    frame_3.grid_columnconfigure(0, weight=1)

    boxRoot.grid_rowconfigure(1, weight=0)
    boxRoot.grid_rowconfigure(2, weight=1)

    boxRoot.grid_rowconfigure(3, weight=0)

    boxRoot.bind("<Return>", login)
    boxRoot.grid_columnconfigure(0, weight=1)
    boxRoot.deiconify()
    boxRoot.wm_attributes("-topmost", 1)

    while True:
        # draw(canvas, mouse=False)
        time.sleep(0.05)
        boxRoot.update()
        if boxRoot.running == False:
            break
        if options != {}:
            return options

# print(get_login("raspberrypi"))
