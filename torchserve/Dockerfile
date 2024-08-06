# syntax = docker/dockerfile:1.2

FROM continuumio/miniconda3:24.1.2-0

# install os dependencies
RUN mkdir -p /usr/share/man/man1
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    ca-certificates \
    curl \
    vim \
    sudo \
    default-jre \
    git \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN conda install python=3.8.13 -y

# install python dependencies
RUN pip install openmim

# Increase timeout and retry pip install torch
RUN pip install torch==2.0.0 --timeout=120 || \
    pip install torch==2.0.0 --timeout=120 || \
    pip install torch==2.0.0 --timeout=120

RUN mim install mmcv-full==1.7.0
RUN pip install mmdet==2.27.0
RUN pip install torchserve

# bugfix for xtcocoapi, an mmpose dependency
RUN git clone https://github.com/jin-s13/xtcocoapi.git
WORKDIR xtcocoapi
RUN pip install -r requirements.txt
RUN python setup.py install
WORKDIR /
RUN pip install mmpose==0.29.0
RUN pip install torchvision==0.15.1  # solve torch version problem
RUN pip install numpy==1.24.4  #solve numpy version problem
RUN pip install glfw

# prep torchserve
RUN mkdir -p /home/torchserve/model-store
RUN wget https://github.com/facebookresearch/AnimatedDrawings/releases/download/v0.0.1/drawn_humanoid_detector.mar -P /home/torchserve/model-store/
RUN wget https://github.com/facebookresearch/AnimatedDrawings/releases/download/v0.0.1/drawn_humanoid_pose_estimator.mar -P /home/torchserve/model-store/
COPY config.properties /home/torchserve/config.properties

# Combine apt-get commands and install additional dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    build-essential \
    cmake \
    git \
    python3-dev \
    python3-numpy \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer1.0-dev \
    libgtk-3-dev \
    libpng-dev \
    libjpeg-dev \
    libopenexr-dev \
    libtiff-dev \
    libwebp-dev \
    libopencv-dev \
    x264 \
    libx264-dev \
    libssl-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install --no-install-recommends -y python3-opencv && rm -rf /var/lib/apt/lists/*

# starting command
CMD /opt/conda/bin/torchserve --start --ts-config /home/torchserve/config.properties --disable-token-auth && sleep infinity