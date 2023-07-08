from pathlib import Path
import contextlib
import fwbuild
import fwbuild.toolchains

@fwbuild.target
class platform_raspi3b(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target, name="platform")

        self.src("startup.S", "vectors.S", "exception.cc")
        self.src("retarget.cc", variables={"cxxflags": "$cxxflags -fno-lto"})

        # Add platform-specific flags to target
        target.binary = True

        target.cxxflags += "-march=armv8-a+crc", "-mcpu=cortex-a53"
        target.cxxflags += "-ffreestanding"

        target.ldflags += "-nostartfiles", "-specs=nosys.specs"
        target.ldflags += "-flto"
        if target.toolchain.tools.ld.version >= (2, 39):
            target.ldflags += "-Wl,--no-warn-rwx-segment"
        target.ldscript = "raspi3b.ld"


class raspi3b(fwbuild.platform_base):
    def __init__(self, conf: fwbuild.kconfig):
        super().__init__(conf)

        self.targets: list[fwbuild.cxx_module] = []

        self.toolchain:      fwbuild.toolchain = None
        self.host_toolchain: fwbuild.toolchain = None

        for cls in fwbuild.target_cls:
            if issubclass(cls, fwbuild.cxx_gtest):
                if self.host_toolchain is None:
                    self.host_toolchain = fwbuild.toolchains.gcc.find()
                self.targets.append(cls(conf, self.host_toolchain))
            else: #issubclass(cls, fwbuild.cxx_app)
                if self.toolchain is None:
                    self.toolchain = fwbuild.toolchains.gcc.find("aarch64-none-elf-")
                app = cls(conf, self.toolchain)
                app.submodule("platform_raspi3b")
                self.targets.append(app)


    def build_cxx_app(self, topout: Path, target: fwbuild.cxx_app,
                      w: fwbuild.ninja_writer) -> fwbuild.cxx_app.artifacts:
        return target.toolchain.build_cxx_app(topout, target, w)

    def vscode_launch(self, topout: Path, target: "fwbuild.cxx_app",
            artifacts: "fwbuild.cxx_app.artifacts") -> \
                dict[str, str] | None:
        gdb = None
        if isinstance(target.toolchain, fwbuild.toolchains.gcc):
            with contextlib.suppress(FileNotFoundError):
                gdb = fwbuild.tool(target.toolchain.tools.cc.path.parent,
                                   target.toolchain.prefix + "gdb")
        if gdb is None:
            return None

        launch_conf = {
            "type": "cppdbg",
            "request": "launch",
            "externalConsole": False,
            "program": topout / artifacts.app,
            "args": [],
            "stopAtEntry": True,
            "cwd": "${workspaceFolder}",
            "MIMode": "gdb",
            "miDebuggerPath": str(gdb),
            "miDebuggerServerAddress": "127.0.0.1:1234",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": True
                }
            ]
        }

        qemu = None
        with contextlib.suppress(FileNotFoundError):
            qemu = fwbuild.tool.find("qemu-system-aarch64")
        if qemu is not None:
            launch_conf["debugServerPath"] = str(qemu)
            launch_conf["debugServerArgs"] = \
                f"-M raspi3b -kernel {(topout / artifacts.app).as_posix()} -serial null -serial stdio -s -S -d cpu_reset"
            launch_conf["filterStderr"] = True

        return launch_conf
