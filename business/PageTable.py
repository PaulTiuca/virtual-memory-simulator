
class PageTable:
    def __init__(self):
        self.entries = {} # [key = (pid,page_id)] -> frame_id

    def map_page(self, process, page_id, frame_id):
        key = (process.pid,page_id)
        self.entries[key] = frame_id

    def get_frame(self, process, page_id):
        return self.entries.get((process.pid, page_id))

    def unmap_page(self, process, page_id):
        key = (process.pid, page_id)
        if key in self.entries:
            del self.entries[key]