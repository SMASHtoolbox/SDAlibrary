from traits.api import HasTraits


class Numeric(HasTraits):
    def __init__(self):
        super(Numeric, self).__init__()


class Logical(HasTraits):
    def __init__(self):
        super(Logical, self).__init__()


class Character(HasTraits):
    def __init__(self):
        super(Character, self).__init__()


class Function(HasTraits):
    def __init__(self):
        super(Function, self).__init__()


class Cell(HasTraits):
    def __init__(self):
        super(Cell, self).__init__()


class Structure(HasTraits):
    def __init__(self):
        super(Structure, self).__init__()


class Structures(HasTraits):
    """Maybe unneccessary"""
    def __init__(self):
        super(Structures, self).__init__()


def Object(HasTraits):
    def __init__(self):
        super(Object, self).__init__()


def Objects(HasTraits):
    def __init__(self):
        super(Objects, self).__init__()


def File(HasTraits):
    def __init__(self):
        super(File, self).__init__()


def Split(HasTraits):
    def __init__(self):
        super(Split, self).__init__()
