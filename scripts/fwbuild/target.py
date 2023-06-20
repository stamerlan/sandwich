import fwbuild

# Classes registered to participiate in the build
target_cls = []

def target(cls):
    """ Decorator for every build target.

        Used to register class during the build, skip target build or rise an
        error if some requirements are not met.
    """
    global target_cls
    target_cls.append(cls)

    fwbuild.deps.add(fwbuild.caller().filename)

    return cls
