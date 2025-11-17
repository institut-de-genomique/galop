FROM ubuntu:22.04

LABEL maintainer="benjamin.istace@genoscope.cns.fr"
LABEL description="Docker image for the Genoscope long-reads assembly workflow"

WORKDIR /workspace

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update system packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install build dependencies
RUN apt-get update && \
    apt-get install -y \
    git \
    curl \
    build-essential \
    zlib1g-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    python3 \
    python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install fastoche
RUN git clone https://github.com/institut-de-genomique/fastoche /tmp/fastoche && \
    cd /tmp/fastoche && \
    cargo install --path . --root /usr/local && \
    cd / && \
    rm -rf /tmp/fastoche /root/.cargo/registry /root/.cargo/git

# Install get_longest_reads
RUN git clone https://github.com/Genoscope-LBGB/get_longest_reads /tmp/get_longest_reads && \
    cd /tmp/get_longest_reads && \
    make && \
    cp get_longest /usr/local/bin/ && \
    cd / && \
    rm -rf /tmp/get_longest_reads

# Install Filtlong
RUN git clone https://github.com/rrwick/Filtlong.git /tmp/Filtlong && \
    cd /tmp/Filtlong && \
    make -j && \
    cp bin/filtlong /usr/local/bin/ && \
    cd / && \
    rm -rf /tmp/Filtlong

# Install hifiasm
RUN git clone https://github.com/chhylp123/hifiasm /tmp/hifiasm && \
    cd /tmp/hifiasm && \
    make && \
    cp hifiasm /usr/local/bin/ && \
    cd / && \
    rm -rf /tmp/hifiasm

# Install NextDenovo
RUN pip3 install --no-cache-dir paralleltask && \
    git clone https://github.com/Nextomics/NextDenovo.git /opt/NextDenovo && \
    cd /opt/NextDenovo && \
    make && \
    ln -s /usr/bin/python3 /usr/bin/python
COPY run_wrapper.cfg /opt/NextDenovo/doc/
ENV PATH="/opt/NextDenovo:${PATH}"

# Install Flye
RUN git clone https://github.com/mikolmogorov/Flye /tmp/Flye && \
    cd /tmp/Flye && \
    python3 setup.py install && \
    cd / && \
    rm -rf /tmp/Flye
