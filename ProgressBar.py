import math

class ProgressBar:

    def __init__(self, length):
        self.length = length

    def start(self):
        print('|'+'-'*(self.length)+'|')
        print('|',end='', flush=True)
        self.displayed_chunks=0
        self.ended = False

    def update_progress(self, current_item, total_items):
        progress = current_item/total_items
        new_displayed_chunks = math.ceil(progress*self.length)
        if self.displayed_chunks != new_displayed_chunks:
            print('#'*(new_displayed_chunks-self.displayed_chunks), end='', flush=True)
        self.displayed_chunks = new_displayed_chunks
        if (self.displayed_chunks == self.length):
            self.end()

    def end(self):
        if not self.ended:
            print('|')
            self.ended = True
