class LoopList:
    def __init__(self, ilist, start=0):
        self.list = ilist
        self.cur = start
    def next(self):
        self.cur += 1
        if self.cur == len(self.list):
            self.cur = 0
        return self.list[self.cur]
    def prev(self):
        self.cur -= 1
        if self.cur < 0:
            self.cur = len(self.list) - 1
        return self.list[self.cur]
    def __iter__(self):
        return self.list
    def __getitem__(self,key):
        return self.list[key]
    def __delitem__(self,key):
        del self.list[key]
    def __setitem__(self,key,value):
        self[key] = value
    def __str__(self):
        return '<' + ','.join(self.list) + '>'
    
    
