targets = []

def target(cls):
    """ Decorator for every build target.

        Used to register class during the build, skip target build or rise an
        error if some requirements are not met.
    """
    global targets
    targets.append(cls)
    return cls
