from typing import Optional
import os
import pathlib

def kconfig(config: Optional[str | pathlib.Path] = None,
            Kconfig: Optional[str | pathlib.Path] = None):
    import fwbuild
    import kconfiglib

    if Kconfig is None:
        Kconfig = fwbuild.topdir / "Kconfig"

    os.environ["srctree"] = str(fwbuild.topdir)
    kconf = kconfiglib.Kconfig(Kconfig)
    if config is None:
        import menuconfig
        menuconfig.menuconfig(kconf)
    else:
        kconf.load_config(config)

    for name, sym in kconf.syms.items():
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

    return fwbuild.conf
