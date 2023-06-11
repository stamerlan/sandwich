import fwbuild
import fwbuild.platforms
import fwbuild.targets
import fwbuild.utils
import sys

fwbuild.deps.add(__file__)

class host(fwbuild.platforms.base):
    name: str = "host"
