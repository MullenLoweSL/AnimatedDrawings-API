# syntax = docker/dockerfile:1.2

FROM continuumio/miniconda3:24.1.2-0

# Install OS dependencies
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
    cmake \
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
    python3-opencv \
    xvfb \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN conda install python=3.8.13 -y && \
    pip install openmim torch==2.0.0 mmdet==2.27.0 torchserve torchvision==0.15.1 numpy==1.24.4 && \
    mim install mmcv-full==1.7.0

# Bugfix for xtcocoapi, an mmpose dependency
RUN git clone https://github.com/jin-s13/xtcocoapi.git && \
    cd xtcocoapi && \
    pip install -r requirements.txt && \
    python setup.py install && \
    cd .. && \
    rm -rf xtcocoapi && \
    pip install mmpose==0.29.0

# Prep torchserve
RUN mkdir -p /home/torchserve/model-store && \
    wget https://github.com/facebookresearch/AnimatedDrawings/releases/download/v0.0.1/drawn_humanoid_detector.mar -P /home/torchserve/model-store/ && \
    wget https://github.com/facebookresearch/AnimatedDrawings/releases/download/v0.0.1/drawn_humanoid_pose_estimator.mar -P /home/torchserve/model-store/

COPY torchserve/config.properties /home/torchserve/config.properties

# Copy application files
WORKDIR /app
COPY . /app

# Install Python dependencies from requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy supervisord configuration file
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Set environment variables
ENV FLASK_APP=app.py \
    DISPLAY=:99

# Start supervisor when the container launches
CMD ["/usr/bin/supervisord"]
