from tkinter import ttk
from tkinter import *
import tkinter as tk
import time

root = None

from PIL import Image
import PIL
import PIL.ImageTk

asset_dir = "Assets/"

def get_login(machine):
    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)#, fg="red", bg="black")
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
        nonlocal creds
        passw = link_pass.get()
        user = link_user.get()
        if user != "" and passw != "":
            creds = {"user":user, "pass":passw}
            boxRoot.quit()
            boxRoot.destroy()
            #boxRoot.running = False
        
    
    creds = {}

    boxRoot.title("Login to " + str(machine))
    boxRoot.iconname("Dialog")
    boxRoot.minsize(300, 120)
    boxRoot.running = True
    boxRoot.protocol("WM_DELETE_WINDOW", quitter)


    lbl= tk.Label(boxRoot, text="Login:", justify=LEFT)#, font=("Helvetica", 16))
    #lbl.grid(row=0, padx=10, sticky="W")
    boxRoot.grid_rowconfigure(0, weight=0)


    #First frame

    frame_1 = ttk.Frame(boxRoot, padding="0.15i")
    imager = Image.open(asset_dir + "lock.png")
    img = PIL.ImageTk.PhotoImage(imager.resize([48, 48]))
    labelm = tk.Label(frame_1, image=img)
    labelm.image = img

    
    labelm.grid(row=0, padx=10, pady=10, sticky="EW", rowspan=2)



    tk.Label(frame_1, text="Username: ").grid(row=0, column=1, padx=10, sticky="W")

    link_user = ttk.Entry(frame_1)
    
    link_user.grid(row=0, column=2, padx=10, sticky="WE")

    
    link_user.focus_force()
    
    tk.Label(frame_1, text="Password: ").grid(row=1, column=1, padx=10, sticky="W")

    link_pass = ttk.Entry(frame_1, show="*")
    
    link_pass.grid(row=1, column=2, padx=10, sticky="WE")

    
    machines = []
    
    
    

    frame_1.grid(row=1, column=0, padx=20, sticky="SWE", columnspan=2)
    frame_1.grid_columnconfigure(2, weight=1)
    
    
    frame_3 = tk.Frame(boxRoot)#, padding="0.15i")

    close_b = ttk.Button(frame_3, text="Cancel", command=quitter)
    close_b.grid(column=0, row=0, sticky="SW", padx=10)

    
    test_b = ttk.Button(frame_3, text="Login", command=login)
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
        #draw(canvas, mouse=False)
        time.sleep(0.05)
        boxRoot.update()
        if boxRoot.running == False:
            break
        if creds != {}:
            return creds
        
        

print(get_login("raspberrypi"))
