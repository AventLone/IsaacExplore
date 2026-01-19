import tkinter as tk
from tkinter import filedialog, ttk

class Window(tk.Tk):
    def __init__(self, window_titile: str, width: int, height: int, icon_path=None) -> None:
        # super().__init__(baseName="Obj SDG", className="Obj-sdg")
        super().__init__(className="Obj-sdg")
        self.title(window_titile)
        # self.wm_class("obj_sdg", "Obj SDG")
        self.geometry(f"{width}x{height}")
        self.tk.call("tk", "scaling", 2)  # try 1.25 / 1.5 / 2.0
        # Load a PNG image
        # Use PhotoImage for standard formats like .png or .gif
        if icon_path is not None:
            icon = tk.PhotoImage(file=icon_path)

            # Set the window icon
            # The 'True' argument applies this icon to all future top-level windows
            self.wm_iconphoto(True, icon)

# Initialize app
window = Window(window_titile="Obj SDG", width=800, height=600,
                icon_path="/home/avent/Desktop/PythonProjects/IsaacExplore/resources/isaacsim.png")


# Callback for choosing path
def choose_path():
    path = filedialog.askdirectory()  # or askopenfilename()
    
    if path:
        path_label.config(text=f"Selected: {path}")

    show_info()

def show_info():
    info = tk.Toplevel(window)
    info.title("Info")
    info.geometry("300x150")
    info.transient(window)   # stay on top of root
    info.grab_set()        # modal

    tk.Label(info, text="This is an info window").pack(pady=20)
    tk.Button(info, text="OK", command=info.destroy).pack()

# UI elements
tk.Label(window, text="Options:").pack(pady=10)

# Checkbox variables
check_var1 = tk.BooleanVar()
check_var1.set(True)
tk.Checkbutton(window, text="Headless App", 
               font=("Arial", 15, "bold"),
               cursor="hand2",
               variable=check_var1).pack(anchor="w", padx=20)
# tk.Checkbutton(root, text="Enable feature B", variable=check_var2).pack(anchor="w", padx=20)  
# tk.Checkbutton(root, text="Enable feature C", variable=check_var3).pack(anchor="w", padx=20)

tk.Button(window, text="Choose Folder", cursor="hand2", command=choose_path).pack(pady=20)

path_label = tk.Label(window, text="No path selected yet.")
path_label.pack(pady=10)

pb = ttk.Progressbar(window, orient='horizontal', mode='determinate', length=280)
pb.pack(pady=20)

pb['value'] = 50   # Update value manually

# Run app
window.mainloop()




