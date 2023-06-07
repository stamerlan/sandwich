# syntax=docker/dockerfile:1
FROM ubuntu:latest
RUN apt-get update

# Install build tools
RUN apt-get install -y python3 python3-pip ninja-build g++ wget xz-utils
RUN python3 -m pip install kconfiglib

# Setup aarch64-none-elf 12.2 toolchain
RUN wget -O /opt/arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf.tar.xz 'https://developer.arm.com/-/media/Files/downloads/gnu/12.2.rel1/binrel/arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf.tar.xz?rev=28d5199f6db34e5980aae1062e5a6703&hash=F6F5604BC1A2BBAAEAC4F6E98D8DC35B'
RUN echo "62d66e0ad7bd7f2a183d236ee301a5c73c737c886c7944aa4f39415aab528daf  /opt/arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf.tar.xz" > /opt/arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf.tar.xz.sha256asc
RUN sha256sum --check /opt/arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf.tar.xz.sha256asc
RUN mkdir -p /opt/arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf
RUN tar -xvf /opt/arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf.tar.xz -C /opt
ENV PATH="${PATH}:/opt/arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf/bin"
