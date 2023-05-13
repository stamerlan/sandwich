import pathlib

class str_list(object):
    def __init__(self, *items):
        self._data = []
        for i in items:
            self += i

    def __iadd__(self, value):
        if isinstance(value, str):
            if value:
                self._data.append(value)
        elif isinstance(value, pathlib.Path):
            self += value.as_posix()
        else:
            for v in value:
                self += v
        return self

    def __add__(self, other):
        new_list = str_list(self._data)
        new_list += other
        return new_list

    def __radd__(self, other):
        new_list = str_list(other)
        new_list += self
        return new_list

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return " ".join(self._data)

    def append(self, item):
        if isinstance(item, (str, pathlib.Path)):
            self += item
        else:
            raise ValueError(f"Can't append item '{item}' ({type(item)})")

    def extend(self, other):
        for i in other:
            self += i
