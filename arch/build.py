import fwbuild
import arch.aarch64.build
import arch.host.build

@fwbuild.target
class arch(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        target.include("include")

        if isinstance(target, fwbuild.cxx_gtest):
            # Always use arch_host for unit test
            self.submodule("arch_host")
        elif target.conf.ARCH_AARCH64:
            self.submodule("arch_aarch64")
        else:
            self.submodule("arch_host")
