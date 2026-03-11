import tkinter as tk
import ttkbootstrap as tb
from tkinter import ttk

class AutomaticWindow:
    def __init__(self, root, controller):
        self.controller = controller
        self.controller.on_page_access = self.page_access_callback
        self.num_pages = controller.pages
        self.frames = controller.frames
        self.tlb_capacity = controller.tlb_capacity

        self.window = tb.Toplevel(root)
        self.window.title("Automatic Test - Access Pages")

        # Title
        title = tb.Label(self.window, text="Automatic Virtual Memory Simulation", font=("Arial", 14))
        title.pack(pady=10)

        # Main frame
        main_frame = tb.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left frame: pages
        self.pages_frame = tb.Frame(main_frame)
        self.pages_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Calculate grid layout for pages
        self.page_rects = []
        page_frames = []
        if self.num_pages == 8 or self.num_pages == 16:
            cols = 4
        else:
            cols = 8
        page_size = 80
        padding = 10

        for i in range(self.num_pages):
            row = i // cols
            col = i % cols
            page_frames.append(None)
            page_canvas = tk.Canvas(self.pages_frame, width=page_size, height=page_size,
                                    highlightthickness=1, highlightbackground="black")
            page_canvas.grid(row=row, column=col, padx=padding, pady=padding)
            rect = page_canvas.create_rectangle(5, 5, page_size - 5, page_size - 5, fill="grey")
            text = page_canvas.create_text(page_size // 2, page_size // 2, text=f"Page {i}")
            self.page_rects.append((page_canvas, rect, text))

        # Right frame (split into 2 columns)
        right_frame = tb.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Column 0: Page Table
        page_table_frame = tb.Frame(right_frame)
        page_table_frame.grid(row=0, column=0, sticky="n", padx=5, pady=5)

        tb.Label(page_table_frame, text="Page Table", font=("Arial", 12)).pack()
        self.page_table = ttk.Treeview(
            page_table_frame,
            columns=("Frame", "Page"),
            show="headings",
            height=self.frames
        )
        self.page_table.heading("Frame", text="Frame")
        self.page_table.heading("Page", text="Page")
        self.page_table.pack(pady=25)

        # Column 1: TLB + Statistics
        tlb_stats_frame = tb.Frame(right_frame)
        tlb_stats_frame.grid(row=0, column=1, sticky="n", padx=5, pady=5)

        # TLB
        tb.Label(tlb_stats_frame, text="TLB", font=("Arial", 12)).pack()
        self.tlb_table = ttk.Treeview(
            tlb_stats_frame,
            columns=("Page","Frame"),
            show="headings",
            height=self.tlb_capacity
        )
        self.tlb_table.heading("Page", text="Page")
        self.tlb_table.heading("Frame", text="Frame")
        self.tlb_table.pack(pady=25)

        # Statistics
        stats_frame = tb.Frame(tlb_stats_frame)
        stats_frame.pack(pady=10)

        self.time_label = tb.Label(stats_frame, text="Simulation time: 0", font=("Arial", 12), foreground="blue")
        self.time_label.pack(pady=2)

        hits_faults_frame = tb.Frame(stats_frame)
        hits_faults_frame.pack()

        self.hits_label = tb.Label(hits_faults_frame, text="Hits: 0", font=("Arial", 12), foreground="green")
        self.hits_label.pack(side=tk.LEFT, padx=20)

        self.faults_label = tb.Label(hits_faults_frame, text="Faults: 0", font=("Arial", 12), foreground="red")
        self.faults_label.pack(side=tk.RIGHT, padx=20)

        ratio_frame = tb.Frame(stats_frame)
        ratio_frame.pack()

        self.ratio_label = tb.Label(ratio_frame, text="Ratio hits/accesses: 0%", font=("Arial", 11))
        self.ratio_label.pack(side=tk.LEFT, padx=20)

        self.avg_time_label = tb.Label(ratio_frame, text="Average access time: 0", font=("Arial", 11))
        self.avg_time_label.pack(side=tk.LEFT, padx=20)

    def refresh_page_rects(self):
        mmu = self.controller.mmu
        for i, (canvas, rect, text) in enumerate(self.page_rects):
            # Find the frame containing this page
            frame_id = None
            for frame in mmu.frames:
                if frame.page is not None and frame.page.page_id == i:
                    frame_id = frame.frame_id
                    break

            color = "white" if frame_id is not None else "grey"
            canvas.itemconfig(rect, fill=color)
            if frame_id is not None:
                canvas.itemconfig(text, text=f"Page {i}\nFrame: {frame_id}")
            else:
                canvas.itemconfig(text, text=f"Page {i}")

    def update_page_table(self):
        self.page_table.delete(*self.page_table.get_children())
        item_map = {}  # maps page_id to Treeview item
        for frame in self.controller.mmu.frames:
            if frame.page is not None:
                page_id = frame.page.page_id
                item_id = self.page_table.insert("", "end", values=(frame.frame_id, page_id))
                item_map[page_id] = item_id
            else:
                item_id = self.page_table.insert("", "end", values=(frame.frame_id, "-", "No"))
        return item_map

    def update_tlb(self):
        self.tlb_table.delete(*self.tlb_table.get_children())
        item_map = {}
        for (proc_id, page_id), frame_id in self.controller.mmu.tlb.cache.items():
            if proc_id == self.controller.process.pid:
                item_id = self.tlb_table.insert("", "end", values=(page_id, frame_id))
                item_map[page_id] = item_id
        return item_map

    def update_statistics(self):
        self.time_label.config(text=f"Simulation time: {self.controller.mmu.time}")
        self.hits_label.config(text=f"Hits: {self.controller.mmu.page_hits}")
        self.faults_label.config(text=f"Faults: {self.controller.mmu.page_faults}")

        total_accesses = self.controller.mmu.page_hits + self.controller.mmu.page_faults
        ratio = (self.controller.mmu.page_hits / total_accesses * 100) if total_accesses > 0 else 0
        self.ratio_label.config(text=f"Ratio hits/accesses: {ratio:.1f}%")

        avg_time = (self.controller.mmu.time / total_accesses) if total_accesses > 0 else 0
        self.avg_time_label.config(text=f"Average access time: {avg_time:.1f}")

    def highlight_row(self, tree: ttk.Treeview, item_id, color, duration=1000):
        tree.tag_configure("highlight", background=color)
        tree.item(item_id, tags=("highlight",))
        tree.after(duration, lambda: tree.item(item_id, tags=()))

    def page_access_callback(self, page_id, event, frame, replaced_page):
        self.refresh_page_rects()

        # Update tables and get item IDs
        page_table_map = self.update_page_table()
        tlb_map = self.update_tlb()

        self.update_statistics()

        canvas, rect, text = self.page_rects[page_id]

        if event == "tlb_hit":
            color = "green"
            # Highlight TLB row
            if page_id in tlb_map:
                self.highlight_row(self.tlb_table, tlb_map[page_id], "lightgreen")
        elif event == "page_table_hit":
            color = "orange"
            # Highlight Page Table row
            if page_id in page_table_map:
                self.highlight_row(self.page_table, page_table_map[page_id], "orange")
        elif event == "page_fault":
            color = "red"
            # Highlight Page Table row
            if page_id in page_table_map:
                self.highlight_row(self.page_table, page_table_map[page_id], "red")
            # Highlight replaced page in blue
            if replaced_page is not None:
                r_canvas, r_rect, r_text = self.page_rects[replaced_page.page_id]
                r_canvas.itemconfig(r_rect, fill="blue")

        # Update page rectangle color
        canvas.itemconfig(rect, fill=color)
        canvas.itemconfig(text, text=f"Page {page_id}\nFrame: {frame.frame_id}")
