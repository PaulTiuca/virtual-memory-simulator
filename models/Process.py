from models.Page import Page

class Process:
    def __init__(self,pid,num_pages):
        self.pid = pid
        self.pages = [Page(i,self) for i in range(num_pages)]