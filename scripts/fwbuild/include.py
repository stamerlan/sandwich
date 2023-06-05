from types import ModuleType
import importlib.util
import pathlib

def include(filename: str | pathlib.Path, mod_name: str | None = None) -> ModuleType:
    """ Load module from file """
    import fwbuild
    import fwbuild.utils

    filename = pathlib.Path(filename)

    if mod_name is None:
        mod_name = "fwbuild.include." + filename.stem

    if filename.is_absolute():
        filenames = [
            filename,
            filename / "__init__.py",
            filename / filename.with_suffix(".py").name
        ]
    else:
        filenames = [
            fwbuild.utils.caller().dir / filename,
            fwbuild.utils.caller().dir / filename / "__init__.py",
            fwbuild.utils.caller().dir / filename / filename.with_suffix(".py").name,
            fwbuild.topdir / filename,
            fwbuild.topdir / filename / "__init__.py",
            fwbuild.topdir / filename / filename.with_suffix(".py").name,
            fwbuild.root / filename,
            fwbuild.root / filename.with_suffix(".py").name,
            fwbuild.root / filename / filename.with_suffix(".py")
        ]

    spec = None
    for fname in filenames:
        if not fname.is_file():
            continue
        spec = importlib.util.spec_from_file_location(mod_name, fname)
        if spec is not None:
            break

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fwbuild.deps.add(mod.__file__)

    return mod
