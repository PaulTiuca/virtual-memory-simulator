# business/TLB.py
from collections import OrderedDict

class TLB:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def lookup(self, process, page_id):
        key = (process.pid, page_id)
        frame_id = self.cache.get(key)
        if frame_id is None:
            return None

        try:
            val = self.cache.pop(key)
            self.cache[key] = val
        except KeyError:
            return frame_id

        return frame_id

    def update(self, process, page_id, frame_id):
        key = (process.pid, page_id)
        if key in self.cache:
            self.cache.pop(key, None)
        self.cache[key] = frame_id

        while len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def invalidate(self, process, page_id):
        key = (process.pid, page_id)
        self.cache.pop(key, None)

    def clear(self):
        self.cache.clear()