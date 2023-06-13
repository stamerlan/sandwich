from .file_set import file_set
import kconfiglib
import os
import pathlib

class kconfig(object):
    """ Class to load configuration from Kconfig file """

    def __init__(self, topdir: str | pathlib.Path,
                 kconfig: str | pathlib.Path = "Kconfig"):
        self._topdir = pathlib.Path(topdir)
        self.deps = file_set(topdir)

        kconfig = pathlib.Path(kconfig)
        if kconfig.is_file():
            pass
        elif (self._topdir / kconfig).is_file():
            kconfig = self._topdir / kconfig
        else:
            raise FileNotFoundError(f"Can't find \"{kconfig.as_posix()}\"")

        env_srctree = os.getenv("srctree", None)
        os.environ.pop("srctree", None)
        self._kconf = kconfiglib.Kconfig(kconfig.as_posix(), warn_to_stderr=False)
        if env_srctree is not None:
            os.environ["srctree"] = env_srctree

        for fname in self._kconf.kconfig_filenames:
            self.deps.add(kconfig.parent, fname)

        self._set_symbols()

    def load_config(self, filename: str | pathlib.Path | None) -> str:
        env_kconfig_config = os.getenv("KCONFIG_CONFIG", None)
        os.environ.pop("KCONFIG_CONFIG", None)

        conf_file = None

        if filename is None:
            defaults = [pathlib.Path(".config"), self._topdir / ".config"]
            if self._kconf.defconfig_filename is not None:
                defaults.append(pathlib.Path(self._kconf.defconfig_filename))
                defaults.append(self._topdir / self._kconf.defconfig_filename)

            for fname in defaults:
                if fname.is_file():
                    conf_file = fname
                    break
        else:
            conf_file = pathlib.Path(filename)
            if not conf_file.is_file():
                conf_file = self._topdir / filename
                if not conf_file.is_file():
                    conf_file = None

        if conf_file is None:
            if filename:
                err_msg = f"Can't find configuration file \"{filename}\""
            else:
                err_msg = f"Can't find default configuration file"
            raise FileNotFoundError(err_msg)

        output = self._kconf.load_config(conf_file.as_posix())
        self.deps.add(conf_file)
        self._set_symbols()

        if env_kconfig_config is not None:
            os.environ["KCONFIG_CONFIG"] = env_kconfig_config

        return output

    def _set_symbols(self):
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
