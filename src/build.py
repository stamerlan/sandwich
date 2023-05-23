import fwbuild

app = fwbuild.platform.cxx_target("hello")
app.gen_dasm = True
app.gen_map = True

app.cxxflags += "-std=c++23", "-g", "-O3"
app.cxxflags += "-fcheck-new", "-flto", "-fno-rtti", "-fno-exceptions"
app.cxxflags += "-fno-threadsafe-statics"
app.cxxflags += "-Wall", "-Wextra", "-Werror", "-Weffc++"
app.cxxflags += "-Wmultiple-inheritance", "-Wvirtual-inheritance"
app.cxxflags += "-ffile-prefix-map=$srcdir/="

app.ldflags += "-flto"

uart_drv = "host" if fwbuild.platform.__name__ == "fwbuild.platform.host" else "bcm2837_aux_uart"
drivers = fwbuild.include(fwbuild.topdir / "drivers").drivers
app.submodule(drivers(app, uart_drv=uart_drv))

app.src("main.cc")
