import fwbuild

if fwbuild.conf.PLATFORM_HOST:
    fwbuild.platform.load("host")
elif fwbuild.conf.PLATFORM_RASPI3B:
    fwbuild.platform.load("raspi3b")
