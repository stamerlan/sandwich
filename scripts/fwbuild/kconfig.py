from typing import Optional
import kconfiglib
import os
import pathlib

_kconf: Optional[kconfiglib.Kconfig] = None

def kconfig(config: Optional[str | pathlib.Path] = None,
            Kconfig: Optional[str | pathlib.Path] = None):
    import fwbuild
    global _kconf

    if Kconfig is None:
        Kconfig = fwbuild.topdir / "Kconfig"
    else:
        Kconfig = pathlib.Path(Kconfig)

    os.environ["srctree"] = str(fwbuild.topdir)
    _kconf = kconfiglib.Kconfig(Kconfig)
    if config is None:
        import menuconfig
        menuconfig.menuconfig(_kconf)
    else:
        _kconf.load_config(config)

    for name, sym in _kconf.syms.items():
        if name == "MODULES":
            continue

        if sym.type is kconfiglib.BOOL or sym.type is kconfiglib.TRISTATE:
            setattr(fwbuild.conf, name, bool(sym.tri_value))
        elif sym.type is kconfiglib.STRING:
            setattr(fwbuild.conf, name, sym.str_value)
        elif sym.type is kconfiglib.INT:
            setattr(fwbuild.conf, name, int(sym.str_value))
        elif sym.type is kconfiglib.HEX:
            setattr(fwbuild.conf, name, int(sym.str_value, 16))
        else:
            type_str = kconfiglib.TYPE_TO_STR.get(sym.type, None)
            if type_str is None:
                type_str = sym.type
            else:
                type_str = f'"{type_str}"({sym.type})'

            raise RuntimeError(
                f'Kconfig symbol "{name}" has unexpected type {type_str}')

    for kconf_fname in _kconf.kconfig_filenames:
        kconf_fname = pathlib.Path(kconf_fname)
        if not kconf_fname.is_absolute():
            kconf_fname = Kconfig.parent / kconf_fname
        fwbuild.add_conf_file(kconf_fname)

    return fwbuild.conf
