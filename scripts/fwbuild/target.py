def target(cls):
    """ Decorator for every build target.

        Used to register class during the build, skip target build or rise an
        error if some requirements are not met.
    """
    return cls
