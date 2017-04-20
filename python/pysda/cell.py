import h5py


class Cell(h5py.Group):
    # probably want to have a resize.
    # to be honest though, it doesnt matter
    # the only thing that matters is that the index
    # increments over with precedent on the leftmost
    # index. It's just a set of stuff
    def __init__(self):
        h5py.Group.__init__(self)
        self._items = 0
        self._record_size = 0
    
    def add_record(self, record_name, record_type, index_location):
        record_group = self.create_group(record_name)
        self._items += 1

