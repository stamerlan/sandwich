import fwbuild
import fwbuild.utils

class target_base(object):
    """ Base class for target """
    def __init__(self):
        fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        fwbuild.add_conf_file(__file__)

    def __getattribute__(self, name: str):
        attr = object.__getattribute__(self, name)
        if hasattr(attr, "__call__") and not name.startswith("_"):
            fwbuild.add_conf_file(fwbuild.utils.get_caller_filename())
        return attr
