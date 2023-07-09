Sandwich is a small project to study various tools for embedded C++ development.
The project goal is to make a scalable, configurable cross-platform embedded
application.

Getting started
---------------
Here's a quick overview how to build Sandwich for Raspberry Pi 3 Model B and run
the application using QEMU.

Clone repository
~~~~~~~~~~~~~~~~
First of all::

    git clone https://github.com/stamerlan/sandwich.git

Build docker image
~~~~~~~~~~~~~~~~~~
`Docker <https://www.docker.com/>`_ is an open platform for developing,
shipping, and running applications. Docker provides the ability to package and
run an application in a loosely isolated environment called a container.

Containers are reproducible, isolated environments that yield predictable
results. Building and testing application in a Docker container makes it easier
to prevent unexpected behaviors from occurring. Dockerfile is used to define the
exact requirements for the build environment. However it's possible to setup
development environment on host PC to avoid virtualization overhead.

To build docker image from Dockerfile run `docker build`_::

    docker build -t stamerlan/sandwich-build .

To list build images use `docker images`_::

    docker images

Run docker image
~~~~~~~~~~~~~~~~
To create and run a new container from an image use `docker run`_::

    docker run -it --mount src=.,target=/__w,type=bind stamerlan/sandwich-build

The command starts docker container in interactive mode and mounts current
directory to /__w. It's exactly the same environment as used for continuous
integration.

Configure firmware build
~~~~~~~~~~~~~~~~~~~~~~~~
Since Sandwich is highly configurable project, it is necessary to specify
modules to be built and target platform. Predefined configurations are stored in
``*.config`` files.

A python program ``configure.py`` is used to check build environment, load
configuration and generate build files used for build::

    python configure.py raspi3b.config

After configured once you don't need to invoke configuration script anymore. In
case of changes in configuration program or configuration files it will be
called automatically during the build.

Build firmware
~~~~~~~~~~~~~~
To perform build start ninja in output directory::

    ninja -C bin/raspi3b

Start QEMU
~~~~~~~~~~~
To execute application use the following command::

    qemu-system-aarch64 -M raspi3b -kernel bin/raspi3b/hello/hello.elf

Also it's possible to start QEMU GDB server for debugging. GDB server is run on
TCP port 1234 and virtual machine is stopped at the very first instruction::

    qemu-system-aarch64 -M raspi3b -kernel bin/raspi3b/hello/hello.elf -s -S

.. _docker build: https://docs.docker.com/engine/reference/commandline/build/
.. _docker images: https://docs.docker.com/engine/reference/commandline/images/
.. _docker run: https://docs.docker.com/engine/reference/commandline/run/
