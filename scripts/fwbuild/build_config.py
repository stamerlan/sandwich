from typing import Optional
import fwbuild
import fwbuild.config_deps
import kconfiglib
import os
import pathlib

class BuildConfig(object):
    def __init__(self, topdir: str | pathlib.Path):
        self._deps = fwbuild.config_deps.ConfigDeps(topdir)
        self._kconf: Optional[kconfiglib.Kconfig] = None

    @property
    def files(self) -> set[pathlib.Path]:
        return self._deps.files

    def load_kconfig(self, config_file: Optional[str | pathlib.Path] = None,
                    kconfig_file: Optional[str | pathlib.Path] = None) -> str:
        if kconfig_file is None:
            kconfig_file = fwbuild.topdir / "Kconfig"
        else:
            kconfig_file = pathlib.Path(kconfig_file)

        srctree = os.getenv("srctree", None)
        self._kconf = kconfiglib.Kconfig(kconfig_file, warn_to_stderr=False)
        if srctree is None:
            os.environ.pop("srctree", None)
        else:
            os.environ["srctree"] = srctree

        output = self._kconf.load_config(config_file)

        for name, sym in self._kconf.syms.items():
            if name == "MODULES":
                continue

            if sym.type is kconfiglib.BOOL or sym.type is kconfiglib.TRISTATE:
                setattr(self, name, bool(sym.tri_value))
            elif sym.type is kconfiglib.STRING:
                setattr(self, name, sym.str_value)
            elif sym.type is kconfiglib.INT:
                setattr(self, name, int(sym.str_value))
            elif sym.type is kconfiglib.HEX:
                setattr(self, name, int(sym.str_value, 16))
            else:
                type_str = kconfiglib.TYPE_TO_STR.get(sym.type, None)
                if type_str is None:
                    type_str = sym.type
                else:
                    type_str = f'"{type_str}"({sym.type})'
                raise RuntimeError(
                    f'Kconfig symbol "{name}" has unexpected type {type_str}')

        for kconf_fname in self._kconf.kconfig_filenames:
            kconf_fname = pathlib.Path(kconf_fname)
            if not kconf_fname.is_absolute():
                kconf_fname = kconfig_file.parent / kconf_fname
            self._deps.add(kconf_fname)

        # TODO: Add config_file to self._deps

        return output

    def write_autoconf(self, filename: str | pathlib.Path, header = None) -> \
                                                        Optional[pathlib.Path]:
        if self._kconf is None:
            return None

        filename = pathlib.Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        self._kconf.write_autoconf(filename, header)

        return filename

    def write_conf(self, filename: str | pathlib.Path, header = None) -> \
                                                        Optional[pathlib.Path]:
        if self._kconf is None:
            return None

        filename = pathlib.Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        self._kconf.write_config(filename, header, save_old=False)
        return filename
