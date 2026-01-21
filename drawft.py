import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# container frame (keeps things aligned on the left)
frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="w")

label = ttk.Label(frame, text="Mode:")
combo = ttk.Combobox(frame, values=["A", "B", "C"], width=12)

label.grid(row=0, column=0, sticky="w", padx=(0, 6))
combo.grid(row=0, column=1, sticky="w")

root.mainloop()
