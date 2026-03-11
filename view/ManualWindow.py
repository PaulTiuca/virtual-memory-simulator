import tkinter as tk
import ttkbootstrap as tb
from tkinter import ttk

class ManualWindow:
    def __init__(self, root, controller):
        self.controller = controller
        self.controller.on_page_access = self.page_access_callback

        self.window = tb.Toplevel(root)
        self.window.title("Manual Virtual Memory Simulation")

        # Title
        tb.Label(self.window, text="Manual Virtual Memory Simulation", font=("Arial", 14)).pack(pady=10)

        # Simulation time
        time_frame = tb.Frame(self.window)
        time_frame.pack(pady=5)
        self.time_label = tb.Label(time_frame, text="Simulation Time: 0", font=("Arial", 12), foreground="blue")
        self.time_label.pack(side=tk.LEFT, padx=10)

        # Page ID entry + Access button
        entry_frame = tb.Frame(self.window)
        entry_frame.pack(pady=5)
        tb.Label(entry_frame, text="Page ID:").pack(side=tk.LEFT)
        self.entry = tb.Entry(entry_frame, width=10)
        self.entry.pack(side=tk.LEFT, padx=5)
        tb.Button(entry_frame, text="Access", bootstyle="info", command=self.on_access).pack(side=tk.LEFT, padx=5)

        # Tables frame
        tables_frame = tb.Frame(self.window)
        tables_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        # Page Table
        page_table_frame = tb.Frame(tables_frame)
        page_table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tb.Label(page_table_frame, text="Page Table", font=("Arial", 12)).pack()
        self.page_table = ttk.Treeview(page_table_frame, columns=("Frame", "Page"), show="headings", height=10)
        self.page_table.heading("Frame", text="Frame")
        self.page_table.heading("Page", text="Page")
        self.page_table.pack(fill=tk.BOTH, expand=True, pady=5)

        # TLB Table
        tlb_frame = tb.Frame(tables_frame)
        tlb_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        tb.Label(tlb_frame, text="TLB", font=("Arial", 12)).pack()
        self.tlb_table = ttk.Treeview(tlb_frame, columns=("Page", "Frame"), show="headings", height=10)
        self.tlb_table.heading("Page", text="Page")
        self.tlb_table.heading("Frame", text="Frame")
        self.tlb_table.pack(fill=tk.BOTH, expand=True, pady=5)

        # Row 1: Hits and Faults
        stats_frame1 = tb.Frame(self.window)
        stats_frame1.pack(pady=5)
        self.hits_label = tb.Label(stats_frame1, text="Hits: 0", font=("Arial", 12), foreground="green")
        self.hits_label.pack(side=tk.LEFT, padx=40)
        self.faults_label = tb.Label(stats_frame1, text="Faults: 0", font=("Arial", 12), foreground="red")
        self.faults_label.pack(side=tk.RIGHT, padx=40)

        # Row 2: Ratio and Average Access Time
        stats_frame2 = tb.Frame(self.window)
        stats_frame2.pack(pady=5)
        self.ratio_label = tb.Label(stats_frame2, text="Ratio hits/accesses: 0%", font=("Arial", 11))
        self.ratio_label.pack(side=tk.LEFT, padx=20)
        self.avg_time_label = tb.Label(stats_frame2, text="Average access time: 0", font=("Arial", 11))
        self.avg_time_label.pack(side=tk.LEFT, padx=20)

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

    def page_access_callback(self, page_id, event, frame, replaced_page):
        # Get current items before updating
        page_table_map = self.update_page_table()  # returns current item IDs
        tlb_map = self.update_tlb()

        # Highlight first
        if event == "tlb_hit" and page_id in tlb_map:
            self.highlight_row(self.tlb_table, tlb_map[page_id], "lightgreen")
        elif event == "page_table_hit" and page_id in page_table_map:
            self.highlight_row(self.page_table, page_table_map[page_id], "orange")
        elif event == "page_fault":
            if page_id in page_table_map:
                self.highlight_row(self.page_table, page_table_map[page_id], "red")
            if replaced_page and replaced_page.page_id in page_table_map:
                self.highlight_row(self.page_table, page_table_map[replaced_page.page_id], "blue")

        # Now update statistics
        mmu = self.controller.mmu
        self.time_label.config(text=f"Simulation Time: {mmu.time}")
        self.hits_label.config(text=f"Hits: {mmu.page_hits}")
        self.faults_label.config(text=f"Faults: {mmu.page_faults}")
        total_accesses = mmu.page_hits + mmu.page_faults
        ratio = (mmu.page_hits / total_accesses * 100) if total_accesses > 0 else 0
        avg_time = (mmu.time / total_accesses) if total_accesses > 0 else 0
        self.ratio_label.config(text=f"Ratio hits/accesses: {ratio:.1f}%")
        self.avg_time_label.config(text=f"Average access time: {avg_time:.1f}")

    def on_access(self):
        try:
            page_id = int(self.entry.get())
            self.controller.access_page(page_id)
        except ValueError:
            return

    def highlight_row(self, tree: ttk.Treeview, item_id, color, duration=500):
        tree.tag_configure("highlight", background=color)
        tree.item(item_id, tags=("highlight",))
        tree.after(duration, lambda: tree.item(item_id, tags=()))