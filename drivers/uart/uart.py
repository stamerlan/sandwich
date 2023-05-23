import fwbuild
import fwbuild.targets
import pathlib

class uart(fwbuild.targets.cxx_module):
    def __init__(self, target: fwbuild.targets.cxx_app):
        super().__init__("uart")
        self.src("src/host.cc")

        this_dir = pathlib.Path(__file__).parent
        if this_dir.is_relative_to(fwbuild.topdir):
            this_dir = pathlib.Path("$topdir", this_dir.relative_to(fwbuild.topdir))
        target.cxxflags += "-I" + (this_dir / "include").as_posix()
