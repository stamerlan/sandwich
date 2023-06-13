import pathlib

class str_list(object):
    """ List of strings """

    def __init__(self, *items):
        self._items: list[str] = []
        for i in items:
            self += i

    def __iadd__(self, value):
        if isinstance(value, str):
            if value:
                self._items.append(value)
        elif isinstance(value, pathlib.Path):
            self += value.as_posix()
        else:
            for v in value:
                self += v
        return self

    def __add__(self, other):
        new_list = str_list(self._items)
        new_list += other
        return new_list

    def __radd__(self, other):
        new_list = str_list(other)
        new_list += self
        return new_list

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return " ".join(self._items)

    def append(self, item):
        if isinstance(item, (str, pathlib.Path)):
            self += item
        else:
            raise ValueError(f"Can't append item '{item}' ({type(item)})")

    def extend(self, other):
        for i in other:
            self += i
