import tkinter as tk
from tkinter import ttk, messagebox
import multiprocessing
from multiprocessing.synchronize import Event
import queue
import time, ctypes

def background_worker(status: Event, queue:multiprocessing.Queue):
    """Simulates a heavy task in a separate process."""
    total_steps = 100
    for i in range(1, total_steps + 1):
        time.sleep(0.05)  # Simulate actual work
        queue.put(i)      # Send current progress to UI

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

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager 2026")
        self.geometry("350x150")

        ttk.Label(self, text="Generating Progress:").pack(pady=(15, 5))

        # 1. Progress Bar Setup
        self.progress_var = tk.DoubleVar()
        self.pb = ttk.Progressbar(self, variable=self.progress_var, maximum=100, length=250)
        self.pb.pack(pady=(0, 15))
        
        # 2. Control Button
        self.btn = ttk.Button(self, text="Start Heavy Task", cursor="hand2", command=self.start_task)
        self.btn.pack()

        # 3. Inter-process Communication
        # self.queue = multiprocessing.Queue()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def start_task(self):
        start_signal.set()
        self.btn.config(state="disabled")
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
        self.btn.config(state="normal")

    def _on_close(self):
        start_signal.set()
        shutdown_flag.set()
        self.quit()
        self.destroy()

if __name__ == "__main__":
    # Required for Windows & macOS multiprocessing stability
    app = App()
    p = multiprocessing.Process(target=app.mainloop)
    p.start()
    main_task()
