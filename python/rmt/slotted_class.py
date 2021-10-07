from pprint import pformat

class SlottedClass:
    __slots__ = []

    def __repr__(self) -> str:
        obj = {attr: getattr(self, attr) for attr in self.__slots__}

        return pformat(obj, indent=4, width=1)