import fwbuild

# Classes registered to participate in the build
target_cls: list[type[fwbuild.cxx_app]] = []

# Module calsses which can be included by cxx_module.submodule() call
module_cls: list[type[fwbuild.cxx_module]] = []

def target(cls):
    """ Decorator for every build target.

        Used to register class during the build, skip target build or rise an
        error if some requirements are not met.
    """
    global target_cls
    global module_cls

    if issubclass(cls, fwbuild.cxx_app):
        target_cls.append(cls)
    elif issubclass(cls, fwbuild.cxx_module):
        module_cls.append(cls)
    else:
        raise RuntimeError(f"Unexpected target type {cls}")

    fwbuild.deps.add(fwbuild.caller().filename)

    return cls
