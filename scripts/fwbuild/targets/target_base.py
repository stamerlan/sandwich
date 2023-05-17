import fwbuild
import fwbuild.utils

class target_base(object):
    """ Base class for target """

    def __getattribute__(self, name: str):
        attr = object.__getattribute__(self, name)
        if hasattr(attr, "__call__") and not name.startswith("_"):
            fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return attr
