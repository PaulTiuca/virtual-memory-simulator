
class Page:
    def __init__(self, page_id, process):
        self.page_id = page_id
        self.process = process
        self.frame_id = None
        self.last_access_time = 0
        self.load_time = 0
