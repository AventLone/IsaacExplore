import tkinter as tk
from tkinter import filedialog, ttk, font

class Window(tk.Tk):
    def __init__(self, window_titile: str) -> None:
        super().__init__(className="Obj-sdg")
        self.tk.call("tk", "scaling", 2.0)  # try 1.5 ~ 2.5
        # self.withdraw()
        self.monitor_size = (self.winfo_screenwidth(), self.winfo_screenheight())
        self.title(window_titile)
        width, height = round(self.monitor_size[0] * 0.28), round(self.monitor_size[1] * 0.15)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        # self.tk.call("tk", "scaling", 2)  # try 1.25 / 1.5 / 2.0

        # Font and style
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial", size=14)
        self.option_add("*TCombobox*Listbox*Font", "Arial 14")

        # Set msgbox's size
        self.option_add('*Dialog.msg.font', 'Helvetica 15')
        self.option_add('*Dialog.msg.width', 25)  # Character width
        self.option_add('*Dialog.msg.wrapLength', '4i')  # Wrap after 4 inches

        self.button_list: list[ttk.Button] = []

    def create_dir_browser(self, label_text, pady=6):
        def choose_dir(entry_widget: ttk.Entry):
            path = filedialog.askdirectory()
            if path:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, path)

        row = ttk.Frame(self)
        row.pack(fill="x", pady=pady)

        lbl = ttk.Label(row, text=label_text, width=18)
        lbl.pack(side="left", padx=20)

        entry = ttk.Entry(row, font=("Arial", 14))
        entry.pack(side="left", fill="x", expand=True, padx=(8, 8))

        btn = ttk.Button(row, text="Browse", cursor="hand2", command=lambda e=entry: choose_dir(e))
        btn.pack(side="right", padx=(10, 20))
        self.button_list.append(btn)

        return entry

if __name__ == "__main__":
    # Initialize app
    window = Window("Obj SDG")

    # Checkbox variables
    check_var1 = tk.BooleanVar()
    check_var1.set(True)
    tk.Checkbutton(window, text="Headless App", 
                font=("Arial", 15),
                cursor="hand2",
                variable=check_var1).pack(anchor="w", padx=20)

    # Choose a generating data type
    # 1. Define the options list
    options = ["2D BBox", "Semantic Segmentation", "Instance Segmentation"]

    # 2. Create a StringVar to store the selected value
    selected_option = tk.StringVar()
    selected_option.set(options[0]) # Set a default value

    # 3. Create the Combobox
    # 'state="readonly"' prevents users from typing custom values
    combobox = ttk.Combobox(
        window,
        textvariable=selected_option,
        values=options,
        state="readonly",
        font=("Arial", 14),
        cursor="hand2"
    )
    combobox.pack(pady=20)

    def choose_dir():
        path = filedialog.askdirectory()
        if path:
            entry1.delete(0, tk.END)
            entry1.insert(0, path)

    def choose_dir2():
        path = filedialog.askdirectory()
        if path:
            entry2.delete(0, tk.END)
            entry2.insert(0, path)

    row1 = tk.Frame(window)
    row1.pack(padx=10, pady=10, fill="x")

    entry1 = tk.Entry(row1, font=font.Font(size=14), width=40)
    entry1.pack(side="left", fill="x", expand=True)

    btn1 = tk.Button(row1, text="Choose Environments Path", cursor="hand2", command=choose_dir)
    btn1.pack(side="right", padx=(5, 0))

    row2 = tk.Frame(window)
    row2.pack(padx=10, pady=10, fill="x")

    entry2 = tk.Entry(row2, font=font.Font(size=14), width=40)
    entry2.pack(side="left", fill="x", expand=True)

    btn2 = tk.Button(row2, text="Choose Objs Path", cursor="hand2", command=choose_dir2)
    btn2.pack(side="right", padx=(5, 0))

    row2 = tk.Frame(window)
    row2.pack(padx=10, pady=10, fill="x")

    label = tk.Label(row2, text="Progress:")
    label.pack(side="left")

    style = ttk.Style()
    style.configure("Tall.Horizontal.TProgressbar", thickness=30)  # height in pixels
    pb = ttk.Progressbar(row2, style="Tall.Horizontal.TProgressbar", orient='horizontal', mode='determinate', length=580)
    pb.pack(pady=20)

    pb['value'] = 50   # Update value manually

    # Run app
    window.mainloop()



