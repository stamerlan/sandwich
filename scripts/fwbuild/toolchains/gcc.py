from pathlib import Path
import contextlib
import fwbuild

class gcc(fwbuild.toolchain):
    @staticmethod
    def find(prefix: str = "", *search_dirs) -> "gcc":
        for cc in fwbuild.tool.find_all(prefix + "gcc", search_dirs):
            with contextlib.suppress(FileNotFoundError):
                return gcc(prefix, cc.path.parent)
        raise FileNotFoundError(f'Toolchain "{prefix}gcc" not found')

    def __init__(self, prefix: str, dir: Path):
        super().__init__(prefix + "gcc")
        self._prefix = prefix

        self.tools["cc"]      = dir / (prefix + "gcc")
        self.tools["ar"]      = dir / (prefix + "ar")
        self.tools["cxx"]     = dir / (prefix + "g++")
        self.tools["ld"]      = dir / (prefix + "ld")
        self.tools["objcopy"] = dir / (prefix + "objcopy")
        self.tools["objdump"] = dir / (prefix + "objdump")

