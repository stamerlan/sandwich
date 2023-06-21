Sandwich
========

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Qemu
----

raspi3b Qemu run::

    qemu-system-aarch64 -M raspi3b -kernel bin/raspi3b/kernel8.elf -serial null -serial stdio

raspi3b Qemu GDB server run (servers starts on TCP port 1234)::

    qemu-system-aarch64 -M raspi3b -kernel bin/raspi3b/kernel8.elf -serial null -serial stdio -s -S

Docker
------

Build Docker image::

    docker build -t stamerlan/sandwich-build .

Run Docker image in interactive mode::

    docker run -it --mount src=.,target=/__w,type=bind stamerlan/sandwich-build

Check Docker images::

    docker images

Push Docker image to Dockerhub::

    docker image push stamerlan/sandwich-build
