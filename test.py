import tkinter as tk
from tkinter import filedialog, ttk, font


class Window(tk.Tk):
    def __init__(self, title: str = "Obj SDG") -> None:
        super().__init__(className="obj_sdg")
        # UI scaling (adjust to taste)
        try:
            self.tk.call("tk", "scaling", 1.8)
        except Exception:
            pass

        # Window setup
        self.title(title)
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = round(screen_w * 0.35), round(screen_h * 0.35)
        self.geometry(f"{w}x{h}")
        self.minsize(600, 320)

        # Fonts and style
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial", size=12)
        self.option_add("*TCombobox*Listbox*Font", "Arial 12")

        style = ttk.Style(self)
        # Use a platform-appropriate theme if available
        for th in ("clam", "default", "alt", "vista", "xpnative"):
            try:
                style.theme_use(th)
                break
            except Exception:
                pass

        style.configure("TButton", padding=(8, 4), font=("Arial", 12))
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12))
        style.configure("TCheckbutton", font=("Arial", 12))
        style.configure("Tall.Horizontal.TProgressbar", thickness=18)

        # Main container with padding
        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        # Top row: headless checkbox + combobox (data type)
        top_row = ttk.Frame(main)
        top_row.pack(fill="x", pady=(0, 8))

        self.headless_var = tk.BooleanVar(value=True)
        headless = ttk.Checkbutton(
            top_row, text="Headless App", variable=self.headless_var
        )
        headless.pack(side="left", anchor="w")

        # spacer
        top_row_spacer = ttk.Frame(top_row)
        top_row_spacer.pack(side="left", expand=True)

        # Combobox
        options = ["2D BBox", "Semantic Segmentation", "Instance Segmentation"]
        self.selected_option = tk.StringVar(value=options[0])
        combo = ttk.Combobox(
            top_row, textvariable=self.selected_option, values=options, state="readonly", width=24
        )
        combo.pack(side="right")

        # Paths area: two labeled rows that expand horizontally
        paths = ttk.Frame(main)
        paths.pack(fill="both", expand=True)

        def make_path_row(parent, label_text):
            row = ttk.Frame(parent)
            row.pack(fill="x", pady=6)

            lbl = ttk.Label(row, text=label_text, width=18)
            lbl.pack(side="left")

            entry = ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True, padx=(8, 8))

            btn = ttk.Button(row, text="Browse", command=lambda e=entry: self._choose_dir(e))
            btn.pack(side="right")

            return entry

        self.env_entry = make_path_row(paths, "Environments Path:")
        self.obj_entry = make_path_row(paths, "Objects Path:")

        # Progress area
        progress_row = ttk.Frame(main)
        progress_row.pack(fill="x", pady=(10, 6))

        progress_label = ttk.Label(progress_row, text="Progress:")
        progress_label.pack(side="left")

        self.pb = ttk.Progressbar(
            progress_row, style="Tall.Horizontal.TProgressbar", orient="horizontal", mode="determinate"
        )
        self.pb.pack(side="left", fill="x", expand=True, padx=(8, 8))
        self.pb['value'] = 50

        # Action buttons
        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(6, 0))

        self.start_btn = ttk.Button(actions, text="Start", command=self._on_start)
        self.start_btn.pack(side="right", padx=(6, 0))

        self.stop_btn = ttk.Button(actions, text="Stop", command=self._on_stop)
        self.stop_btn.pack(side="right")

        # Status bar
        self.status = ttk.Label(self, text="Ready", anchor="w")
        self.status.pack(side="bottom", fill="x")

    def _choose_dir(self, entry_widget: ttk.Entry):
        path = filedialog.askdirectory()
        if path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)

    def _on_start(self):
        self.status.config(text="Running...")
        # place to start a background task (use multiprocessing/threading as needed)

    def _on_stop(self):
        self.status.config(text="Stopped")


if __name__ == "__main__":
    app = Window("Obj SDG")
    app.mainloop()
