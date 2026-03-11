from models.Frame import Frame
from business.PageTable import PageTable
from business.TLB import TLB

class MMU:
    def __init__(self, num_frames, replacement_algorithm, tlb_capacity):
        self.frames = [Frame(i) for i in range(num_frames)]
        self.page_table = PageTable()
        self.tlb = TLB(tlb_capacity)
        self.replacement_algorithm = replacement_algorithm
        self.time = 0
        self.page_hits = 0
        self.page_faults = 0

    def access_page(self, process, page_id):

        result = {
            "frame": None,
            "event": None,
            "replaced_page": None
        }

        # 1. Check TLB
        frame_id = self.tlb.lookup(process, page_id)
        if frame_id is not None:
            self.time += 1
            self.page_hits += 1
            print(f"TLB HIT: page {page_id} in frame {frame_id}")
            self.frames[frame_id].page.last_access_time = self.time

            result["frame"] = self.frames[frame_id]
            result["event"] = "tlb_hit"
            return result

        # 2. Check page table
        frame_id = self.page_table.get_frame(process, page_id)
        if frame_id is not None:
            self.time += 10
            self.page_hits += 1
            print(f"Page Table HIT: page {page_id} in physical memory")
            self.tlb.update(process, page_id, frame_id)
            self.frames[frame_id].page.last_access_time = self.time
            result["frame"] = self.frames[frame_id]
            result["event"] = "page_table_hit"
            return result

        # 3. Page fault
        self.time += 100
        self.page_faults += 1
        print(f"PAGE FAULT: Page {page_id}")
        result["event"] = "page_fault"
        frame, replaced_page = self.handle_page_fault(process, page_id)
        result["frame"] = frame
        result["replaced_page"] = replaced_page
        return result

    def handle_page_fault(self, process, page_id):
        page = process.pages[page_id]
        # try to find empty frame
        empty_frame = next((f for f in self.frames if f.page is None), None)
        if empty_frame:
            frame = empty_frame
        else:
            # use replacement policy
            page.last_access_time = self.time
            replaced_page = self.replacement_algorithm.replace_page(self, page)
            frame = self.frames[page.frame_id]
            return frame, replaced_page

        # load page into empty frame
        frame.page = page
        page.frame_id = frame.frame_id
        self.page_table.map_page(process, page_id, frame.frame_id)
        self.tlb.update(process, page_id, frame.frame_id)
        return frame, None