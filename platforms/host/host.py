import fwbuild
import fwbuild.platforms
import fwbuild.targets
import fwbuild.utils
import sys

fwbuild.deps.add(__file__)

class host(fwbuild.platforms.base):
    name: str = "host"

    def cxx_app(self, name: str) -> fwbuild.targets.cxx_app:
        app = super().cxx_app(name, srcdir=fwbuild.utils.caller().dir)

        if sys.platform == "win32":
            app.ldscript = fwbuild.this_dir / "host-win32.ld"
        else:
            app.ldscript = fwbuild.this_dir / "host.ld"

        return app
