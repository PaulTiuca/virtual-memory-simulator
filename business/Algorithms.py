class ReplacementPolicy:
    def replace_page(self, mmu, new_page):
        raise NotImplementedError

class LRU(ReplacementPolicy):
    def replace_page(self, mmu, new_page):
        # find page with smallest last_access_time
        victim_frame = min(
            (f for f in mmu.frames if f.page is not None),
            key=lambda fr: fr.page.last_access_time
        )
        old_page = victim_frame.page

        # unmap old
        mmu.page_table.unmap_page(old_page.process, old_page.page_id)
        mmu.tlb.invalidate(old_page.process, old_page.page_id)

        # place new_page into victim frame
        victim_frame.page = new_page
        new_page.frame_id = victim_frame.frame_id

        mmu.page_table.map_page(new_page.process, new_page.page_id, victim_frame.frame_id)
        mmu.tlb.update(new_page.process, new_page.page_id, victim_frame.frame_id)

        return old_page

class FIFO(ReplacementPolicy):
    def replace_page(self, mmu, new_page):
        # find page with smallest load_time
        victim_frame = min(
            (f for f in mmu.frames if f.page is not None),
            key=lambda fr: fr.page.load_time
        )
        old_page = victim_frame.page

        # unmap old
        mmu.page_table.unmap_page(old_page.process, old_page.page_id)
        mmu.tlb.invalidate(old_page.process, old_page.page_id)

        # place new_page into victim frame
        victim_frame.page = new_page
        new_page.frame_id = victim_frame.frame_id
        new_page.load_time = mmu.time

        mmu.page_table.map_page(new_page.process, new_page.page_id, victim_frame.frame_id)
        mmu.tlb.update(new_page.process, new_page.page_id, victim_frame.frame_id)

        return old_page