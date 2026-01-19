import tkinter as tk
from tkinter import ttk, messagebox
import multiprocessing
import time

def background_worker(queue):
    """Simulates a heavy task in a separate process."""
    total_steps = 100
    for i in range(1, total_steps + 1):
        time.sleep(0.05)  # Simulate actual work
        queue.put(i)      # Send current progress to UI

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager 2026")
        self.geometry("350x150")
        
        # 1. Progress Bar Setup
        self.progress_var = tk.DoubleVar()
        self.pb = ttk.Progressbar(self, variable=self.progress_var, maximum=100, length=250)
        self.pb.pack(pady=20)
        
        # 2. Control Button
        self.btn = ttk.Button(self, text="Start Heavy Task", cursor="hand2", command=self.start_task)
        self.btn.pack()

        # 3. Inter-process Communication
        self.queue = multiprocessing.Queue()

    def start_task(self):
        self.btn.config(state="disabled")
        self.progress_var.set(0) # Ensure it starts at zero
        
        # Start the background process
        p = multiprocessing.Process(target=background_worker, args=(self.queue,))
        p.start()
        
        # Start checking the queue for updates
        self.check_queue()

    def check_queue(self):
        """Monitors the queue and handles completion logic."""
        try:
            while True:
                value = self.queue.get_nowait()
                self.progress_var.set(value)
                
                # Check if task is finished
                if value >= 100:
                    self.on_task_complete()
                    return
        except multiprocessing.queues.Empty:
            # Task still running; check again in 100ms
            self.after(100, self.check_queue)

    def on_task_complete(self):
        """Actions to perform when the task is done."""
        # Pop out the info window
        messagebox.showinfo("Success", "Task completed successfully!")
        
        # Clear the progress bar
        self.progress_var.set(0)
        
        # Re-enable the button
        self.btn.config(state="normal")

if __name__ == "__main__":
    # Required for Windows & macOS multiprocessing stability
    app = App()
    app.mainloop()
