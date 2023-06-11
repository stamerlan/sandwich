from typing import Optional
import fwbuild
import fwbuild.targets
import fwbuild.toolchains
import fwbuild.utils
import pathlib
import sys

class base(object):
    """ Base class for platform definition """

    host_toolchain: fwbuild.toolchains.gcc | None = None
    targets: dict[str, fwbuild.targets.cxx_app] = {}
    test_targets: dict[str, fwbuild.targets.cxx_app] = {}

    def __init__(self):
        if base.host_toolchain is None:
            base.host_toolchain = fwbuild.toolchains.gcc.find()

    def cxx_app(self, name: str, toolchain = None,
                srcdir: Optional[str | pathlib.Path] = None) -> fwbuild.targets.cxx_app:
        if name in base.targets:
            raise RuntimeError(f'Target {name} already defined')

        if toolchain is None:
            toolchain = base.host_toolchain
        if srcdir is None:
            srcdir = fwbuild.utils.caller().dir

        app = fwbuild.targets.cxx_app(name, toolchain, srcdir)
        base.targets[name] = app
        return app

    def cxx_gtest(self, name: str, toolchain = None,
                  srcdir: Optional[str | pathlib.Path] = None) -> fwbuild.targets.cxx_app:
        if name in base.test_targets:
            raise RuntimeError(f'Test target "{name}" already defined')

        if toolchain is None:
            toolchain = base.host_toolchain
        if srcdir is None:
            srcdir = fwbuild.utils.caller().dir

        test = fwbuild.targets.cxx_app(name, toolchain, srcdir)
        test.default_build = False
        test.ldlibs += "gtest"

        base.test_targets[name] = test
        return test

    def write_buildfiles(self, entry_fname: str):
        config_h   = fwbuild.conf.write_autoconf(fwbuild.topout / "config.h")
        dot_config = fwbuild.conf.write_conf(fwbuild.topout / ".config")

        # If config.h is used, add $topout dir to C preprocessor include search
        # path.
        if config_h is not None:
            for target in base.targets.values():
                target.include(".")

        with fwbuild.utils.ninja_writer(fwbuild.topout / "build.ninja") as w:
            w.comment("DO NOT EDIT THIS FILE")
            w.comment("It is automatically generated by fwbuild using")
            w.comment(entry_fname)
            w.newline()

            w.variable("topdir", fwbuild.topdir.as_posix())
            w.newline()

            if len(base.targets) == 1:
                target = next(iter(base.targets.values()))
                target.write_buildfile(w)
            else:
                for name, target in base.targets.items():
                    buildfile_name = pathlib.Path(name, f"{name}-build.ninja")
                    w.subninja(buildfile_name.as_posix())
                    with fwbuild.utils.ninja_writer(fwbuild.topout / buildfile_name) as sub_w:
                        target.write_buildfile(sub_w, name)
            w.newline()

            if len(base.test_targets):
                w.comment("Tests")
                tests = []
                for name, target in base.test_targets.items():
                    buildfile_name = pathlib.Path("tests", name,
                                                  f"{name}-build.ninja")
                    w.subninja(buildfile_name.as_posix())
                    with fwbuild.utils.ninja_writer(fwbuild.topout / buildfile_name) as sub_w:
                        artifacts = target.write_buildfile(sub_w, buildfile_name.parent)
                        assert(artifacts.exe is not None)
                        tests.append(str(artifacts.exe))
                w.newline()

                w.comment("Run all tests")
                test_cmd = fwbuild.utils.shell_cmd()
                for test in tests:
                    test_cmd.cmd(test)
                w.rule("run_tests", command=test_cmd, description="TEST")
                w.build("test", "run_tests", tests)
                w.newline()


            w.comment("Regenerate build file if build script changed")
            conf_cmd = fwbuild.utils.shell_cmd()
            if dot_config is not None:
                conf_cmd.cmd(sys.executable, [entry_fname, "-c", ".config"])
            else:
                conf_cmd.cd(pathlib.Path.cwd())
                conf_cmd.cmd(sys.executable, sys.argv)

            w.rule("configure", command=conf_cmd, generator=True,
                description="CONFIGURE", depfile="build.ninja.deps")
            w.build("build.ninja", "configure")

        # Writer configuration dependencies
        with open(fwbuild.topout / "build.ninja.deps", "w") as f:
            f.write("build.ninja: \\\n")

            deps = []
            for d in sorted(fwbuild.deps.files | fwbuild.conf.files):
                if d.parts[0] == "$topdir":
                    d = pathlib.Path(fwbuild.topdir, *d.parts[1:])
                elif d.parts[1] == "$topout":
                    d = pathlib.Path(*d.parts[1:])
                deps.append(d.as_posix())

            for fpath in deps:
                f.write(f"  {fpath} \\\n")
            f.write("\n")
            for fpath in deps:
                f.write(f"{fpath}:\n\n")
