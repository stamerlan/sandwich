import fwbuild
import fwbuild.platforms
import fwbuild.targets
import fwbuild.utils

fwbuild.deps.add(__file__)

class host(fwbuild.platforms.base):
    name: str = "host"
