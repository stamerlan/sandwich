import fwbuild
import fwbuild.platforms
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils

fwbuild.deps.add(__file__)

class host(fwbuild.platforms.base):
    name: str = "host"
    toolchain: fwbuild.toolchains.gcc | None = None

    def __init__(self):
        if host.toolchain is None:
            host.toolchain = fwbuild.toolchains.gcc.find()

    def cxx_app(self, name: str):
        srcdir = fwbuild.utils.caller().dir
        return super().cxx_app(name, host.toolchain, srcdir)
