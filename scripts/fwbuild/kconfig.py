from pathlib import Path
import kconfiglib
import os

class kconfig(object):
    """ Class to load configuration from Kconfig file """

    def __init__(self, topdir: str | Path, kconfig: str | Path = "Kconfig"):
        self._topdir = Path(topdir)
        self.deps: set[Path] = set()

        kconfig = Path(kconfig)
        if kconfig.is_file():
            kconfig = kconfig.absolute()
        elif (self._topdir / kconfig).is_file():
            kconfig = self._topdir / kconfig
        else:
            raise FileNotFoundError(f"Can't find \"{kconfig.as_posix()}\"")

        env_srctree = os.environ.pop("srctree", None)
        self._kconf = kconfiglib.Kconfig(kconfig.as_posix(), warn_to_stderr=False)
        if env_srctree is not None:
            os.environ["srctree"] = env_srctree

        for fname in self._kconf.kconfig_filenames:
            self.deps.add(Path(kconfig.parent, fname))

        self._set_symbols()

    def load_config(self, filename: str | Path | None) -> str:
        env_kconfig_config = os.environ.pop("KCONFIG_CONFIG", None)
        conf_file = None

        if filename is None:
            defaults = [Path(".config"), self._topdir / ".config"]
            if self._kconf.defconfig_filename is not None:
                defaults.append(Path(self._kconf.defconfig_filename))
                defaults.append(self._topdir / self._kconf.defconfig_filename)

            for fname in defaults:
                if fname.is_file():
                    conf_file = fname
                    break
        else:
            conf_file = Path(filename)
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
        self.deps.add(conf_file.absolute())
        self._set_symbols()

        if env_kconfig_config is not None:
            os.environ["KCONFIG_CONFIG"] = env_kconfig_config

        return output

    def write_autoconf(self, filename: str | Path, header: str | None = None):
        filename = Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        self._kconf.write_autoconf(filename, header)

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
