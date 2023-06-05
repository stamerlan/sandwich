import fwbuild

fwbuild.deps.add(__file__)

class base(object):
    """ Base class for platform definition """

    def write_buildfiles(self, entry_point_filename: str):
        pass
