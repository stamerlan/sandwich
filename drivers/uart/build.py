import fwbuild

@fwbuild.target
class uart(fwbuild.cxx_module):
    def __init__(self, target: fwbuild.cxx_app):
        super().__init__(target)
        if target.conf.HOST_UART:
            self.src("src/host.cc")
        elif target.conf.BCM2837_UART1:
            self.src("src/bcm2837_aux_uart.cc")

        target.include("include")
