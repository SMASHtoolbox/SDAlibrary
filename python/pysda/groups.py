import h5py


class SDAGroup(h5py.Group):
    """
    This class binds to an hdf5 group, and provides the interaction methods.
    It should do stuff...
    """
    def __init__(self, group_to_bind):
        self = super(SDAGroup, self).__init__(group_to_bind.id)

    def __repr__(self):
        return 'SDA GROUP'
