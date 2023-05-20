from types import ModuleType
import importlib.util
import pathlib

def include(filename: str | pathlib.Path, mod_name: str | None = None) -> ModuleType:
    """ Load module from file """
    filename = pathlib.Path(filename)
    if not filename.is_absolute():
        import fwbuild.utils
        filename = fwbuild.utils.get_caller_filename().parent / filename

    if mod_name is None:
        mod_name = "fwbuild.include." + filename.stem

    spec = importlib.util.spec_from_file_location(mod_name, filename.as_posix())
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    import fwbuild
    fwbuild.add_conf_file(filename)

    return mod
