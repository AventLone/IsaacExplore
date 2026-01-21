from gui.window import Window
import tkinter as tk
from tkinter import filedialog, ttk, font
import multiprocessing

class ObjGUI(Window):
    def __init__(self) -> None:
        super().__init__("Obj SDG")

        # 1. Chouse the environments directories
        self.env_entry = self.create_dir_browser("Environments Path:", pady=(13, 0))
        self.obj_entry = self.create_dir_browser("Objs Path:")
        self.saveat_entry = self.create_dir_browser("Output Save at: ")

        # 2. A drop-down to choose a generation type
        dropdown_row = ttk.Frame(self, padding=10)
        dropdown_row.pack(fill="x", pady=20, padx=10)

        lbl = ttk.Label(dropdown_row, text="Data Type:")
        lbl.pack(side="left")

        options = ["2D BBox", "Semantic Segmentation", "Instance Segmentation"]   # Define the options list
        selected_option = tk.StringVar()    # Create a StringVar to store the selected value
        selected_option.set(options[0])     # Set a default value
        combobox = ttk.Combobox(dropdown_row,       # Create the Combobox
            textvariable=selected_option,
            values=options,
            state="readonly",    # 'state="readonly"' prevents users from typing custom values
            font=("Arial", 14),
            cursor="hand2"
        )
        combobox.pack(side="left", padx=10)

        data_num_label = ttk.Label(dropdown_row, text="Data Number:")
        data_num_label.pack(side="left", padx=(150, 0))

        btn = ttk.Button(dropdown_row, text="Generate", cursor="hand2", command=self.notify)
        btn.pack(side="right", padx=(20, 0))

        entry = ttk.Entry(dropdown_row, font=("Arial", 14), width=10)
        entry.pack(side="right")

        

        # 3. Progress Bar Setup
        progress_row = ttk.Frame(self, padding=10)
        progress_row.pack(fill="x", pady=20, padx=10)

        progress_label = ttk.Label(progress_row, text="Generation Progress: ")
        progress_label.pack(side="left")

        self.progress_var = tk.DoubleVar()
        pb_style = ttk.Style()
        pb_style.configure("Tall.Horizontal.TProgressbar", thickness=30)  # height in pixels
        pb = ttk.Progressbar(progress_row, variable=self.progress_var, style="Tall.Horizontal.TProgressbar", 
                             orient='horizontal', mode='determinate')
        pb.pack(fill="x", padx=(10, 30))

        self.generate_signal = multiprocessing.Event()

    def notify(self):
        self.generate_signal.set()


        
    
obj_gui = ObjGUI()
obj_gui.mainloop()
    