import fwbuild
import fwbuild.platforms
import fwbuild.targets
import fwbuild.utils
import sys

class host(fwbuild.platforms.base):
    name: str = "host"
