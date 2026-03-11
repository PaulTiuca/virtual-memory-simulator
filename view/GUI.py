import tkinter as tk
import ttkbootstrap as tb
from Controller import Controller

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Memory Simulator")
        self.root.geometry("640x500")

        style = tb.Style(theme="flatly")

        # Padding at the top
        spacer = tb.Frame(root, height=30)
        spacer.pack()

        # Title
        title = tb.Label(root, text="Setup Virtual Memory Simulator", font=("Arial", 20, "bold"))
        title.pack(pady=15)

        # Frame for dropdowns
        frame = tb.Frame(root, padding=10)
        frame.pack(pady=5)

        # Number of accessible pages in the process
        tb.Label(frame, text="Number of pages:").grid(row=0, column=0, sticky="w", pady = 5)
        self.pages_var = tk.IntVar(value=16)
        pages_options = [8, 16, 32, 64]
        self.frames_menu = tb.Combobox(frame, textvariable=self.pages_var, values=pages_options, state="readonly", width=12)
        self.frames_menu.grid(row=0, column=1, padx=10, pady = 5)

        # Number of frames in page table
        tb.Label(frame, text="Number of frames:").grid(row=1, column=0, sticky="w", pady=5)
        self.frames_var = tk.IntVar(value=8)
        frames_options = [2, 4, 8, 16, 32]
        self.frames_menu = tb.Combobox(frame, textvariable=self.frames_var, values=frames_options, state="readonly", width=12)
        self.frames_menu.grid(row=1, column=1, padx=10, pady=5)

        # TLB capacity
        tb.Label(frame, text="TLB capacity:").grid(row=2, column=0, sticky="w", pady=5)
        self.tlb_var = tk.IntVar(value=2)
        tlb_options = [2, 4, 8]
        self.tlb_menu = tb.Combobox(frame, textvariable=self.tlb_var, values=tlb_options, state="readonly", width=12)
        self.tlb_menu.grid(row=2, column=1, padx=10, pady=5)

        # Replacement algorithm
        tb.Label(frame, text="Replacement algorithm:").grid(row=3, column=0, sticky="w", pady=5)
        self.alg_var = tk.StringVar(value="LRU")
        alg_options = ["LRU", "FIFO"]
        self.alg_menu = tb.Combobox(frame, textvariable=self.alg_var, values=alg_options, state="readonly", width=12)
        self.alg_menu.grid(row=3, column=1, padx=10, pady=5)

        # Automatic Simulation speed
        tb.Label(frame, text="Simulation Speed:").grid(row=4, column=0, sticky="w", pady=5)
        self.speed_var = tk.StringVar(value="Moderate")
        speed_options = ["Slow", "Moderate", "Fast"]
        self.speed_menu = tb.Combobox(frame, textvariable=self.speed_var, values=speed_options, state="readonly", width=12)
        self.speed_menu.grid(row=4, column=1, padx=10, pady=5)

        # Buttons frame
        btn_frame = tb.Frame(root, padding=10)
        btn_frame.pack(pady=20)

        self.manual_btn = tb.Button(btn_frame, text="Manual Test", bootstyle="success", width=20, command=self.open_manual)
        self.manual_btn.grid(row=0, column=0, padx=10, pady=5)

        self.auto_btn = tb.Button(btn_frame, text="Automatic Test", bootstyle="info", width=20, command=self.open_automatic)
        self.auto_btn.grid(row=0, column=1, padx=10, pady=5)

        # Controller instance
        self.controller = None

    def setup_controller(self):
        # Initialize controller with the chosen parameters
        num_pages = self.pages_var.get()
        num_frames = self.frames_var.get()
        tlb_capacity = self.tlb_var.get()
        algorithm = self.alg_var.get()
        self.controller = Controller(num_pages, num_frames, tlb_capacity, algorithm)

    def open_manual(self):
        self.setup_controller()
        from ManualWindow import ManualWindow
        ManualWindow(self.root, self.controller)

    def open_automatic(self):
        self.setup_controller()
        from AutomaticWindow import AutomaticWindow
        AutomaticWindow(self.root, self.controller)

        # start the simulation automatically
        speed = self.speed_var.get()
        self.controller.start_simulation(self.root, speed)  # or get speed from dropdown


if __name__ == "__main__":
    root = tb.Window(themename="flatly")  # ttkbootstrap main window
    app = MainMenu(root)
    root.mainloop()
