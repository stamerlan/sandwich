import fwbuild

# Classes registered to participiate in the build
build_cls = []

def build(cls):
    """ Decorator for every build target.

        Used to register class during the build, skip target build or rise an
        error if some requirements are not met.
    """
    global build_cls
    build_cls.append(cls)

    fwbuild.deps.add(fwbuild.caller().filename)

    return cls
