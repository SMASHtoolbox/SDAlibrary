""" Base class for records. """

from abc import ABCMeta, abstractmethod

from .utils import set_encoded


class InserterRegistry(object):
    """ Registry of inserters. """

    def __init__(self):
        self._inserters = []
        self._register_inserters()

    def _register_inserters(self):
        """ Register all inserters. """
        from itertools import chain

        import sdafile.numeric_inserter as numeric
        import sdafile.logical_inserter as logical
        import sdafile.character_inserter as character
        import sdafile.cell_inserter as cell
        import sdafile.structure_inserter as structure
        import sdafile.file_inserter as file_

        objs = chain(
            numeric.__dict__.values(),
            logical.__dict__.values(),
            character.__dict__.values(),
            cell.__dict__.values(),
            structure.__dict__.values(),
            file_.__dict__.values(),
        )

        inserters = []
        for obj in objs:
            if getattr(obj, '__inserter__', False):
                inserters.append(obj)
        self._inserters = inserters

    def get_inserter(self, data):
        """" Get the inserter appropriate for the passed data.

        This loops through available inserters and uses the first one it
        encounters that can insert the data.

        Parameters
        ----------
        data :
            Data to be inserted into an archive

        Returns
        -------
        inserter : RecordInserter or None
            The RecordInserter *class* that can insert the data into an
            archive, or None if no such inserter can be found.

        """
        for cls in self._inserters:
            if cls.can_insert(data):
                return cls
        return None


def inserter(cls):
    """ Mark a class as an inserter. """
    cls.__inserter__ = True
    return cls


class RecordInserter(object):
    """ Stores a record for insertion. """

    __metaclass__ = ABCMeta

    # The record type supported by the inserter
    record_type = None

    def __init__(self, label, data, deflate, registry=None):
        self.label = label
        self.deflate = int(deflate)
        self.data = self.original_data = data
        self.empty = 'no'
        self._registry = registry

    @property
    def registry(self):
        if self._registry is None:
            self._registry = InserterRegistry()
        return self._registry

    @staticmethod
    @abstractmethod
    def can_insert(data):
        """ Indicates if the Record can insert the passed data.

        This is to be overloaded by derived classes

        """
        return False

    @abstractmethod
    def prepare_data(data):
        """ Prepare data for writing and record metadata.

        This is to be overloaded by derived classes. This is reponsible for
        recording metadata to be written by ``record_group_attributes`` and
        ``record_dataset_attributes``.

        """
        return

    def record_group_attributes(self, dict_like):
        """ Record group attributes specific to the data.

        This includes all group-level data except 'Description'.

        """
        set_encoded(
            dict_like,
            RecordType=self.record_type,
            Empty=self.empty,
            Deflate=self.deflate,
        )

    @abstractmethod
    def insert(self, h5file, description):
        """ Insert the data into an h5py File. """
        return

    @abstractmethod
    def insert_into_group(self, group):
        """ Insert data at the group level """
        return


class SimpleRecordInserter(RecordInserter):
    """ RecordInserter for simple objects.

    Subclasses must convert ``data`` to an ndarray.

    """

    def insert(self, h5file, description):
        """ Insert the data into an h5py File. """
        group = h5file.create_group(self.label)
        set_encoded(
            group.attrs,
            Description=description,
        )
        self.insert_into_group(group)

    def insert_into_group(self, group):
        """ Insert at the group level """
        self.prepare_data()
        self.record_group_attributes(group.attrs)
        self.insert_below_group(group)

    def insert_below_group(self, group):
        """ Insert below a group, creating the necessary dataset entry. """
        maxshape = (None,) * self.data.ndim
        ds = group.create_dataset(
            self.label,
            maxshape=maxshape,
            data=self.data,
            compression=self.deflate,
        )
        self.record_dataset_attributes(ds.attrs)

    def record_dataset_attributes(self, dict_like):
        """ Record the dataset attributes specific to the data. """
        set_encoded(
            dict_like,
            RecordType=self.record_type,
            Empty=self.empty,
        )


class CompositeRecordInserter(RecordInserter):
    """ RecordInserter for composite objects. """

    @abstractmethod
    def __iter__(self):
        """ Yield RecordInserter instances for subitems. """
        return

    def record_dataset_attributes(self, dataset_attrs):
        """ CompositeRecordInserters do not record to datasets. """
        return

    def insert(self, h5file, description):
        """ Insert the data into an h5py File. """
        group = h5file.create_group(self.label)
        set_encoded(
            group.attrs,
            Description=description,
        )
        self.insert_into_group(group)

    def insert_into_group(self, group):
        """ Insert at the group level """
        self.prepare_data()
        self.record_group_attributes(group.attrs)
        for inserter in self:
            if isinstance(inserter, CompositeRecordInserter):
                # Sub-composites get their own new groups
                sub_group = group.create_group(inserter.label)
                inserter.insert_into_group(sub_group)
            else:
                # Simple data inserts below the composite group
                inserter.prepare_data()
                inserter.insert_below_group(group)
