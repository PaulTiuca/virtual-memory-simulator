from business.MMU import MMU
from business.Algorithms import *
from models.Process import Process

class Controller:
    def __init__(self, pages, frames, tlb_capacity, repl_algorithm):
        self.algorithm = LRU() if repl_algorithm == "LRU" else FIFO()
        self.pages = pages
        self.frames = frames
        self.tlb_capacity = tlb_capacity
        self.mmu = MMU(frames,self.algorithm,tlb_capacity)
        self.process = Process(1,pages)
        self.on_page_access = None

    def start_simulation(self, root, speed):
        speed_map = {"Slow": 5000, "Moderate": 3000, "Fast": 1000}  # milliseconds
        delay = speed_map.get(speed, 3000)

        def step():
            import random
            page_id = random.randint(0, self.pages - 1)
            result = self.mmu.access_page(self.process, page_id)

            # call callback to update GUI
            if self.on_page_access:
                self.on_page_access(
                    page_id,
                    result["event"],
                    result["frame"],
                    result.get("replaced_page")
                )

            # schedule next step
            root.after(delay, step)

        root.after(delay, step)

    def access_page(self, page_id):
        result = self.mmu.access_page(self.process, page_id)
        if hasattr(self, "on_page_access"):
            self.on_page_access(page_id, result["event"], result["frame"], result.get("replaced_page"))
