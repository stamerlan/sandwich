import fwbuild

@fwbuild.target
class critical_section(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        target.include("include")
