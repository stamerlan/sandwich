import fwbuild
import fwbuild.platforms
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils

fwbuild.deps.add(__file__)

class HostPlatform(fwbuild.platforms.base):
    name: str = "host"
    toolchain: fwbuild.toolchains.gcc | None = None

    def __init__(self):
        if HostPlatform.toolchain is None:
            HostPlatform.toolchain = fwbuild.toolchains.gcc.find()

    def cxx_target(self, name: str):
        srcdir = fwbuild.utils.get_caller_filename().parent
        return super().cxx_app(name, HostPlatform.toolchain, srcdir)
