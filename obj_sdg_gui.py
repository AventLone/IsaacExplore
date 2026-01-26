from isaacsim.simulation_app import SimulationApp
simu_app = SimulationApp({"renderer": "PathTracing", "headless": True})

from isaacsim.core.utils import stage, prims
# from omni.kit.async_engine import run_coroutine
from sdg import Randomizer, Generator
from pathlib import Path

def find_usds(dir: str) -> list[str]:
    folder = Path(dir)
    usd_files = []
    for usd_file in folder.rglob("*.usd"):
        usd_files.append(str(usd_file))
    return usd_files

import tkinter as tk
from tkinter import ttk, messagebox
import multiprocessing, queue
from dataclasses import dataclass
from typing import Literal
import os

@dataclass
class SDGConfig:
    environments_path: str
    objects_path: str
    save_at: str
    annotation_type: dict
    target_number: int

    def __post_init__(self):
        # path checks
        for name, path in {
            "environments_path": self.environments_path,
            "objects_path": self.objects_path,
            "save_at": self.save_at,
        }.items():
            if not isinstance(path, str) or not path:
                raise ValueError(f"{name} must be a non-empty string")

        if not os.path.isdir(self.environments_path):
            raise ValueError(f"environments_path does not exist: {self.environments_path}")

        if not os.path.isdir(self.objects_path):
            raise ValueError(f"objects_path does not exist: {self.objects_path}")

        # save_at: allow non-existing but parent must exist
        parent = os.path.dirname(self.save_at) or "."
        if not os.path.isdir(parent):
            raise ValueError(f"save_at parent directory does not exist: {parent}")

        # data_type check (Literal is only for type checkers)
        allowed = [{"bounding_box_2d_loose": True},
                   {"semantic_segmentation": True}, 
                   {"instance_segmentaion": True}]
        if self.annotation_type not in allowed:
            raise ValueError(f"data_type must be one of {allowed}")

        # target_number check
        if not isinstance(self.target_number, int) or self.target_number <= 0:
            raise ValueError("target_number must be a positive integer")

progress_queue = multiprocessing.Queue()
configs_queue = multiprocessing.Queue()
shutdown_flag, start_signal = multiprocessing.Event(), multiprocessing.Event()

def main_task():
    while True:
        start_signal.wait()
        if shutdown_flag.is_set():
            break
        
        configs: SDGConfig = configs_queue.get_nowait()

        environments_pool = find_usds(configs.environments_path)
        objs_pool = find_usds(configs.objects_path)
        required_num = configs.target_number

        progress = 0
        progress_all = len(environments_pool) * len(objs_pool)
        OBJ_PRIM_PATH = "/World/Obj"
        for environment in environments_pool:
            stage.create_new_stage()
            prims.create_prim("/World")
            stage.add_reference_to_stage(usd_path=environment,prim_path="/World/Environment")
            
            for obj in objs_pool:
                # Add the obj usd into the stage as a reference
                stage.add_reference_to_stage(usd_path=obj, prim_path=OBJ_PRIM_PATH)

                # Generate the dataset
                randomizer = Randomizer(OBJ_PRIM_PATH, required_num)
                generator = Generator(randomizer, configs.annotation_type, save_path=configs.save_at)
                generator.generate()

                progress += 1
                progress_queue.put(round(progress / progress_all * 100))

                prims.delete_prim(OBJ_PRIM_PATH)   # Remove the obj from the stage

            stage.close_stage()

    simu_app.close()

from gui.window import Window
from tkinter import ttk

class ObjGUI(Window):
    def __init__(self) -> None:
        super().__init__("Obj SDG")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # 1. Chouse the environments directories
        self.env_entry = self.create_dir_browser("Environments Path:", pady=(13, 0))
        self.obj_entry = self.create_dir_browser("Objs Path:")
        self.saveat_entry = self.create_dir_browser("Output Save at: ")

        # 2. A drop-down to choose a generation type
        dropdown_row = ttk.Frame(self, padding=10)
        dropdown_row.pack(fill="x", pady=20, padx=10)

        lbl = ttk.Label(dropdown_row, text="Data Type:")
        lbl.pack(side="left", padx=(0, 3))

        options = ["2D BBox", "Semantic Segmentation", "Instance Segmentation"]   # Define the options list
        self.annotation_types = {"2D BBox": {"bounding_box_2d_loose": True},
                                 "Semantic Segmentation": {"semantic_segmentation": True},
                                 "Instance Segmentation": {"instance_segmentaion": True}}

        self.selected_option = tk.StringVar()    # Create a StringVar to store the selected value
        self.combobox = ttk.Combobox(dropdown_row,       # Create the Combobox
            textvariable=self.selected_option,
            values=options,
            state="readonly",    # 'state="readonly"' prevents users from typing custom values
            font=("Arial", 14),
            cursor="hand2"
        )
        self.combobox.pack(side="left", padx=10)
        self.selected_option.set(options[0])     # Set a default value
        self.combobox.config(state="normal")

        data_num_label = ttk.Label(dropdown_row, text="Data Number:")
        data_num_label.pack(side="left", padx=(150, 0))

        style = ttk.Style()
        style.configure("Red.TButton", foreground="green")
        btn = ttk.Button(dropdown_row, text="Generate", cursor="hand2", style="Red.TButton",command=self.start_task)
        btn.pack(side="right", padx=(20, 0))
        self.button_list.append(btn)

        self.target_num_entry = ttk.Entry(dropdown_row, font=("Arial", 14), width=10)
        self.target_num_entry.pack(side="right")

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

    def _on_close(self):
        shutdown_flag.set()
        start_signal.set()
        self.quit()
        self.destroy()

    def start_task(self):
        # Check all the configurations
        try:
            configs = SDGConfig(self.env_entry.get(), self.obj_entry.get(), self.saveat_entry.get(),
                                self.annotation_types[self.selected_option.get()], int(self.target_num_entry.get()))
            configs_queue.put(configs)
        except Exception:
            messagebox.showerror("Fail", "Recheck your configs!")
            return

        start_signal.set()

        # Disable all control item
        self.combobox.config(state="disabled")
        for btn in self.button_list:
            btn.config(state="disabled")

        start_signal.clear()
        # self.progress_var.set(0) # Ensure it starts at zero
        
        # Start checking the queue for updates
        self.check_queue()

    def check_queue(self):
        """
        Monitors the queue and handles completion logic.
        """
        try:
            while True:
                value = progress_queue.get_nowait()
                self.progress_var.set(value)
                
                # Check if task is finished
                if value >= 100:
                    self._on_task_complete()
                    return
                
        except queue.Empty:
            # Task still running; check again in 100ms
            self.after(100, self.check_queue)

    def _on_task_complete(self):
        start_signal.clear()
        """
        Actions to perform when the task is done.
        """
        messagebox.showinfo("Success", "Generation is complete!")   # Pop out the info window
        self.progress_var.set(0)   # Clear the progress bar
        
        # Re-enable the button
        self.combobox.config(state="normal")
        for btn in self.button_list:
            btn.config(state="normal")


if __name__ == "__main__":
    app = ObjGUI()
    p = multiprocessing.Process(target=app.mainloop)
    p.start()
    main_task()