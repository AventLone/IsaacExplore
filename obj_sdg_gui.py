import tkinter as tk
from tkinter import ttk, messagebox
import multiprocessing
import queue
import time

progress_queue = multiprocessing.Queue()
shutdown_flag, start_signal = multiprocessing.Event(), multiprocessing.Event()

def main_task():
    # while not shutdown_flag.is_set():
    while True:
        time.sleep(0.01)
        start_signal.wait()
        if shutdown_flag.is_set():
            break
        total_steps = 100
        for i in range(1, total_steps + 1):
            time.sleep(0.05)  # Simulate actual work
            progress_queue.put(i)      # Send current progress to UI
    
    print("Main task is over.")

from gui.window import Window
import tkinter as tk
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

        btn = ttk.Button(dropdown_row, text="Generate", cursor="hand2", command=self.start_task)
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

    def _on_close(self):
        start_signal.set()
        shutdown_flag.set()
        self.quit()
        self.destroy()

    def start_task(self):
        start_signal.set()
        # self.btn.config(state="disabled")
        self.progress_var.set(0) # Ensure it starts at zero
        
        # Start the background process
        # p = multiprocessing.Process(target=background_worker, args=(self.queue,))
        # p.start()
        
        # Start checking the queue for updates
        self.check_queue()

    def check_queue(self):
        """
        Monitors the queue and handles completion logic.
        """
        try:
            while True:
                # value = self.queue.get_nowait()
                value = progress_queue.get_nowait()
                self.progress_var.set(value)
                
                # Check if task is finished
                if value >= 100:
                    self._on_task_complete()
                    return
                
        # except multiprocessing.queues.Empty:
        except queue.Empty:
            # Task still running; check again in 100ms
            self.after(100, self.check_queue)

    def _on_task_complete(self):
        start_signal.clear()
        """Actions to perform when the task is done."""
        # Pop out the info window
        messagebox.showinfo("Success", "Task completed successfully!")
        
        # Clear the progress bar
        self.progress_var.set(0)
        
        # Re-enable the button
        # self.btn.config(state="normal")


if __name__ == "__main__":
    app = ObjGUI()
    p = multiprocessing.Process(target=app.mainloop)
    p.start()
    main_task()
